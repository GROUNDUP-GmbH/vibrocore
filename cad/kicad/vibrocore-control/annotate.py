"""Product labels, the notes band, and the bounding-box overlap gate.

Text uses the KiCad 8 Newstroke metrics in kicad_font.py.
A text box may not meet a symbol, another text, a wire, a dashed link,
the sheet frame, or the title block. Net labels are exempt only where
they sit on their own wire end, because KiCad requires that anchor.
"""

from __future__ import annotations

import math
import re

from kicad_font import INTERLINE, LINE_H, SIZE, line_boxes, text_width
from schlib import SYMS

STEP = 1.27
CLEAR = 0.40
PIN_NAME = 1.016
ARTICLE = re.compile(r"VC-[A-Z]+-\d+")

# Manufacturer and short type. OPEN means the order code is not chosen.
# Nothing in this table is invented: each name is the BOM name, the
# manufacturer_pn, or the documented supplier.
PRODUCT = {
    "VC-PW-5100": "Instagrid ONE max",
    "VC-PW-5310": "Mean Well SDR-120-24",
    "VC-PW-5320": "OPEN 24 V supply",
    "VC-PW-5700": "OPEN isolator",
    "VC-PW-5710": "OPEN breaker C20",
    "VC-PW-5720": "OPEN RCD B 30 mA",
    "VC-PW-5730": "Schneider GV2L20",
    "VC-PW-5740": "OPEN breaker C16",
    "VC-PW-5750": "OPEN breaker C4",
    "VC-PW-5760": "OPEN breaker C10",
    "VC-PW-5770": "OPEN motor protection",
    "VC-PW-5790": "OPEN fuse 2 A",
    "VC-PW-5800": "OPEN fuse 6 A",
    "VC-PW-5810": "OPEN fuse 20 A",
    "VC-PW-5820": "OPEN fuse 2 A",
    "VC-CT-6200": "OPEN limit switch",
    "VC-CT-6210": "OPEN E-stop",
    "VC-CT-6220": "Pilz PNOZ s4",
    "VC-CT-6230": "OPEN beacon",
    "VC-CT-6250": "OPEN index sensor",
    "VC-CT-6260": "IDEC HE1B-M1",
    "VC-CT-6270": "OPEN reset",
    "VC-CT-6280": "Nanotec PD2-C4118",
    "VC-CT-6600": "Teltonika RUT241",
    "VC-CT-6780": "1N4007",
    "VC-CT-6790": "OPEN 120 ohm",
    "VC-CT-6800": "Kunbus RevPi 100378",
    "VC-CT-6810": "Kunbus DIO 100197",
    "VC-HB-2100": "Siemens 1FL2104",
    "VC-HB-2300": "Siemens 6SL5510",
    "VC-SH-1100": "OLI MVE 400/6-HF",
    "VC-SH-1210": "Schneider ATV320U15M2C",
    "VC-LT-9100": "OPEN lift actuator",
    "VC-LT-9110": "OPEN H-bridge",
    "VC-LT-9200": "OPEN tilt actuator",
    "VC-LT-9230": "Finder 62.32",
}

# One side per symbol type. The stack grows away from the body.
SIDE = {
    "ISO2": "right", "RCD2": "right", "MCB2": "right", "MCB3": "right",
    "FUSE": "right", "LAMP": "right", "DIODE": "right", "PWR": "right",
    "PSU": "below", "PSU0": "below", "REL": "right", "PNOZ": "above",
    "SW_NC": "above", "SW_NO": "above", "SW_PB": "above", "ESTOP": "above",
    "MPROT": "above", "RES": "above", "BOND": "above",
    "TERM_V": "right", "TERM_H": "above",
    "M3": "right", "MSRV": "right", "ACT": "above", "PNP": "above",
    "SRC": "above", "S200": "above", "ATV": "above", "REVPI": "above",
    "DIO": "above", "NANO": "above", "RUT": "above", "HBR": "above", "PULSE": "above",
}

# Notes band, millimetres, Y down. It sits above the title block.
BAND = (248.0, 220.0, 408.0, 258.0)
FRAME = (12.0, 12.0, 408.0, 284.0)
TITLE = (308.0, 261.0, 420.0, 297.0)


def product_text(value: str) -> str:
    match = ARTICLE.search(value)
    if not match:
        return value
    article = match.group(0)
    name = PRODUCT.get(article)
    if name is None:
        raise SystemExit(f"No product name for {article}. Add it to annotate.PRODUCT.")
    return f"{name}\n{article}"


def _mm(steps: float) -> float:
    return steps * STEP


def _steps(mm: float) -> float:
    return mm / STEP


def ink_box(inst) -> tuple[float, float, float, float]:
    """Symbol ink in millimetres, Y down, including pin stubs."""
    sym = SYMS[inst.sym]
    xs: list[float] = []
    ys: list[float] = []

    def add(sx: float, sy: float) -> None:
        xs.append(_mm(inst.x) + sx)
        ys.append(_mm(inst.y) - sy)

    graphic = " ".join(sym.gfx.get(inst.unit, []))
    for raw_x, raw_y in re.findall(
        r"(?:xy|start|end|center|at)\s+([+-]?[\d.]+)\s+([+-]?[\d.]+)", graphic
    ):
        add(float(raw_x), float(raw_y))
    for cx, cy, radius in re.findall(
        r"center\s+([+-]?[\d.]+)\s+([+-]?[\d.]+)\).*?radius\s+([+-]?[\d.]+)", graphic
    ):
        center_x, center_y, reach = float(cx), float(cy), float(radius)
        add(center_x - reach, center_y)
        add(center_x + reach, center_y)
        add(center_x, center_y - reach)
        add(center_x, center_y + reach)
    for pin in sym.pins:
        if pin.unit != inst.unit:
            continue
        px, py = pin.x * STEP, pin.y * STEP
        add(px, py)
        angle = math.radians(pin.ang)
        add(px + math.cos(angle) * 1.27, py + math.sin(angle) * 1.27)
    if not xs:
        add(0.0, 0.0)
    pad = 0.20
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def _intersects(a, b) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def _grow(box, pad: float = CLEAR):
    return (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)


def _dash_boxes(sheet) -> list[tuple]:
    """Small boxes along each dash, so the empty corner of a diagonal stays free."""
    boxes = []
    for left, right in sheet.dashes:
        x0, y0 = _mm(left[0]), _mm(left[1])
        x1, y1 = _mm(right[0]), _mm(right[1])
        length = math.hypot(x1 - x0, y1 - y0)
        steps = max(1, int(length / 1.2))
        for index in range(steps + 1):
            t = index / steps
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            boxes.append((x - 0.25, y - 0.25, x + 0.25, y + 0.25, "dash"))
    return boxes


def _wire_boxes(sheet) -> list[tuple]:
    boxes = []
    for net, pts in sheet.wires:
        width = _stroke(net)
        for left, right in zip(pts, pts[1:]):
            x0, x1 = sorted((_mm(left[0]), _mm(right[0])))
            y0, y1 = sorted((_mm(left[1]), _mm(right[1])))
            boxes.append((x0 - width, y0 - width, x1 + width, y1 + width, net))
    return boxes


def _stroke(net: str) -> float:
    head = net[:3]
    if head in {"100", "101", "102", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171"}:
        return 0.25
    if head in {"540", "541", "542", "543", "544", "600", "601", "602", "610", "611", "612", "620", "621", "622"}:
        return 0.20
    if net in {"200_24S", "201_24S", "210_24C", "211_24C", "500_24R", "001_0V"}:
        return 0.15
    return 0.08


def _frame_boxes() -> list[tuple]:
    return [
        (-20.0, -20.0, FRAME[0], 400.0, "frame"),
        (FRAME[2], -20.0, 440.0, 400.0, "frame"),
        (-20.0, -20.0, 440.0, FRAME[1], "frame"),
        (-20.0, FRAME[3], 440.0, 400.0, "frame"),
        TITLE + ("title block",),
    ]


def _blocked(boxes, obstacles) -> str | None:
    for box in boxes:
        grown = _grow(box)
        for item in obstacles:
            if _intersects(grown, item):
                return item[-1]
    return None


def _stack(body, lines: list[str], side: str, extra: float):
    """Top-aligned stack. Above the body, the anchor moves up by the stack height."""
    x0, y0, x1, y1 = body
    gap = 1.0 + extra
    count = len(lines)
    block = LINE_H + (count - 1) * INTERLINE if count else 0.0
    if side == "left":
        anchor = (x0 - gap, y0 + 2.2)
        justify = "right top"
    elif side == "right":
        anchor = (x1 + gap, y0 + 2.2)
        justify = "left top"
    elif side == "above":
        anchor = ((x0 + x1) / 2.0, y0 - gap - block)
        justify = "center top"
    else:
        anchor = ((x0 + x1) / 2.0, y1 + gap)
        justify = "center top"
    boxes = line_boxes(anchor[0], anchor[1], "\n".join(lines), justify)
    return boxes, anchor, justify


def _apply_stack(inst, lines: list[str], anchor, justify: str) -> None:
    """Write Reference and Value anchors so KiCad draws the same stack."""
    has_ref = not inst.hide_ref
    inst.ref_justify = justify
    inst.val_justify = justify
    inst.ref_dx = _steps(anchor[0] - _mm(inst.x))
    inst.ref_dy = _steps(anchor[1] - _mm(inst.y))
    value_y = anchor[1] + (INTERLINE if has_ref else 0.0)
    inst.val_dx = inst.ref_dx
    inst.val_dy = _steps(value_y - _mm(inst.y))
    if not inst.hide_value:
        inst.value = "\n".join(lines[(1 if has_ref else 0) :])


def _label_lines(inst) -> list[str]:
    lines = []
    if not inst.hide_ref:
        lines.append(inst.ref)
    if not inst.hide_value:
        text = product_text(inst.value)
        lines.extend(line for line in text.split("\n") if line)
    return lines


def _place_labels(sheet, obstacles) -> list[str]:
    errors = []
    placed = []
    for inst in sheet.insts:
        lines = _label_lines(inst)
        if not lines:
            continue
        if ARTICLE.search(inst.value) and not inst.hide_value:
            inst.value = product_text(inst.value)
        body = ink_box(inst)
        side = inst.ref_justify if inst.ref_justify in {"left", "right", "above", "below"} else SIDE.get(inst.sym, "right")
        # ref_justify may already be "left" from an older placement. Prefer the type side
        # unless the caller set label_side on the instance via ref_justify being a side word
        # before prepare. place() sets "left" for terminals. Override with the type table.
        side = SIDE.get(inst.sym, "right")
        chosen = None
        hit = "sheet"
        for extra in (i * 1.2 for i in range(0, 18)):
            boxes, anchor, justify = _stack(body, lines, side, extra)
            hit = _blocked(boxes, obstacles)
            if hit is None:
                chosen = (boxes, anchor, justify)
                break
        if chosen is None:
            errors.append(f"{sheet.filename} {inst.ref} unit {inst.unit} does not fit on the {side} ({hit})")
            continue
        boxes, anchor, justify = chosen
        _apply_stack(inst, lines, anchor, justify)
        for box in boxes:
            obstacles.append(box + (f"text {inst.ref}",))
        placed.append(inst.ref)
    return errors


def _note_items(sheet) -> list[tuple]:
    items = []
    for item in sheet.notes:
        if isinstance(item, str):
            items.append((None, item))
        else:
            items.append(item)
    return items


def _wrap(text: str, limit: float, size: float = SIZE) -> list[str]:
    words = text.split()
    if not words:
        return [text]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        if text_width(trial, size) <= limit:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _place_band(sheet, obstacles, pointer: str | None) -> list[str]:
    """Fill the bottom-right band. Overflow is kept for the notes sheet."""
    x0, y0, x1, y1 = BAND
    obstacles.append((x0, y0, x1, y1, "notes band"))
    inner_left = x0 + 1.6
    inner_top = y0 + 1.4
    inner_right = x1 - 1.6
    limit = inner_right - inner_left
    usable = y1 - y0 - 3.0
    capacity = max(1, int((usable - (LINE_H)) / INTERLINE) + 1)
    items = _note_items(sheet)
    numbered = []
    for index, (at, text) in enumerate(items, start=1):
        numbered.append((index, at, text))
    kept = []
    overflow = []
    reserve = 1 if pointer else 0
    for index, at, text in numbered:
        wrapped = _wrap(f"({index}) {text}", limit)
        if len(kept) + len(wrapped) + reserve <= capacity:
            kept.extend(wrapped)
        else:
            overflow.append(f"({index}) {text}")
    if pointer and len(kept) < capacity:
        kept.append(pointer)
    elif pointer:
        overflow.insert(0, pointer)
    sheet.band_lines = kept
    sheet.overflow = overflow
    errors = []
    if kept:
        body = "\n".join(kept)
        boxes = line_boxes(inner_left, inner_top, body, "left top")
        for box in boxes:
            if box[2] > inner_right or box[3] > y1 - 1.2:
                errors.append(f"{sheet.filename} notes band text leaves the band")
                break
            obstacles.append(box + ("notes text",))
    sheet.band_origin = (inner_left, inner_top)
    # Markers for notes that stayed on this sheet.
    sheet.markers = []
    for index, at, _text in numbered:
        if at is None:
            continue
        marker = f"({index})"
        origin = (_mm(at[0]), _mm(at[1]))
        found = None
        offsets = []
        for radius in (4.0, 6.0, 9.0, 12.0, 16.0, 21.0):
            for dx, dy in (
                (radius, -3.0), (radius, 3.0), (-radius, -3.0), (-radius, 3.0),
                (0.0, -radius), (0.0, radius), (radius, 0.0), (-radius, 0.0),
            ):
                offsets.append((dx, dy))
        for dx, dy in offsets:
            boxes = line_boxes(origin[0] + dx, origin[1] + dy, marker, "left")
            if _blocked(boxes, obstacles) is None:
                found = (origin[0] + dx, origin[1] + dy, boxes)
                break
        if found is None:
            errors.append(f"{sheet.filename} note ({index}) has no free marker position")
            continue
        mx, my, boxes = found
        sheet.markers.append((mx, my, marker))
        for box in boxes:
            obstacles.append(box + (f"marker {marker}",))
    return errors


def _terminal_policy(inst) -> None:
    if not inst.sym.startswith("TERM"):
        return
    if inst.ref.endswith(".1") or inst.ref.endswith(":1"):
        inst.value = "OPEN terminal"
        inst.hide_value = False
    else:
        inst.hide_value = True


def prepare(sheet, pointer: str | None) -> list[str]:
    """Place product labels and the notes band. Return placement errors."""
    if sheet.filename.startswith("10-notes"):
        return []
    for inst in sheet.insts:
        _terminal_policy(inst)
        if not inst.hide_value and ARTICLE.search(inst.value):
            inst.value = product_text(inst.value)
    obstacles = []
    for inst in sheet.insts:
        obstacles.append(ink_box(inst) + (f"symbol {inst.ref}",))
    for box in _wire_boxes(sheet):
        obstacles.append(box)
    obstacles.extend(_dash_boxes(sheet))
    obstacles.extend(_frame_boxes())
    errors = _place_labels(sheet, obstacles)
    errors.extend(_place_band(sheet, obstacles, pointer))
    # Free texts (the terminal table) stay where the sheet put them.
    for x, y, text in sheet.texts:
        boxes = line_boxes(_mm(x), _mm(y), text, "left")
        hit = _blocked(boxes, obstacles)
        if hit:
            errors.append(f"{sheet.filename} table text hits {hit}: {text[:40]}")
        else:
            for box in boxes:
                obstacles.append(box + ("table",))
    sheet._obstacles = obstacles
    errors.extend(_place_net_labels(sheet))
    return errors


def _blocked_except(boxes, obstacles, own: str) -> str | None:
    for box in boxes:
        grown = _grow(box)
        for item in obstacles:
            if item[-1] == own or item[-1] == f"wire {own}":
                continue
            if _intersects(grown, item):
                return item[-1]
    return None


def _pin_points(sheet) -> set[tuple]:
    points = set()
    for inst in sheet.insts:
        for pin in SYMS[inst.sym].pins:
            if pin.unit != inst.unit:
                continue
            points.add((inst.x + pin.x, inst.y - pin.y))
    return points


def _outward(end, other) -> str:
    """KiCad keeps the connection on the anchor for left-bottom text.

    Centered text moves the connection off the wire end, so every net name
    uses the same anchor.
    """
    return "left bottom"


def _place_net_labels(sheet) -> list[str]:
    """Park each net name on its wire.

    A free end that is not a pin would dangle in ERC, so the name sits on
    that end. A net whose every end is a pin keeps the name on the wire.
    """
    obstacles = list(sheet._obstacles)
    pins = _pin_points(sheet)
    sheet.net_labels = {}
    for net in sorted({name for name, _pts in sheet.wires}):
        segments = []
        for name, pts in sheet.wires:
            if name != net:
                continue
            segments.extend(zip(pts, pts[1:]))
        if not segments:
            continue
        degree: dict[tuple, int] = {}
        neighbour: dict[tuple, tuple] = {}
        for left, right in segments:
            degree[left] = degree.get(left, 0) + 1
            degree[right] = degree.get(right, 0) + 1
            neighbour.setdefault(left, right)
            neighbour.setdefault(right, left)
        free = [pt for pt, count in degree.items() if count == 1 and pt not in pins]
        chosen = None
        if free:
            for end in free:
                justify = _outward(end, neighbour[end])
                boxes = line_boxes(_mm(end[0]), _mm(end[1]), net, justify)
                if _blocked_except(boxes, obstacles, net) is None:
                    chosen = (end[0], end[1], justify, boxes)
                    break
            if chosen is None:
                end = free[0]
                justify = _outward(end, neighbour[end])
                boxes = line_boxes(_mm(end[0]), _mm(end[1]), net, justify)
                chosen = (end[0], end[1], justify, boxes)
        else:
            segments.sort(key=lambda seg: abs(seg[0][0] - seg[1][0]) + abs(seg[0][1] - seg[1][1]), reverse=True)
            for left, right in segments:
                for frac in (0.5, 0.32, 0.68):
                    sx = left[0] + (right[0] - left[0]) * frac
                    sy = left[1] + (right[1] - left[1]) * frac
                    boxes = line_boxes(_mm(sx), _mm(sy), net, "left bottom")
                    if _blocked_except(boxes, obstacles, net) is None:
                        chosen = (sx, sy, "left bottom", boxes)
                        break
                if chosen:
                    break
            if chosen is None:
                left, right = segments[0]
                sx = (left[0] + right[0]) / 2
                sy = (left[1] + right[1]) / 2
                boxes = line_boxes(_mm(sx), _mm(sy), net, "left bottom")
                chosen = (sx, sy, "left bottom", boxes)
        sx, sy, justify, boxes = chosen
        sheet.net_labels[net] = (sx, sy, justify)
        for box in boxes:
            obstacles.append(box + (f"label {net}",))
    sheet._obstacles = obstacles
    return []


def _pin_name_boxes(inst) -> list[tuple]:
    boxes = []
    sym = SYMS[inst.sym]
    for pin in sym.pins:
        if pin.unit != inst.unit or pin.name in {"", "~"}:
            continue
        px = _mm(inst.x) + pin.x * STEP
        py = _mm(inst.y) - pin.y * STEP
        angle = pin.ang % 360
        inset = 1.27 + 0.508
        if angle == 180:
            boxes.extend(line_boxes(px + inset, py, pin.name, "left", PIN_NAME))
        elif angle == 0:
            boxes.extend(line_boxes(px - inset, py, pin.name, "right", PIN_NAME))
        elif angle == 270:
            boxes.extend(line_boxes(px, py + inset, pin.name, "center top", PIN_NAME))
        else:
            boxes.extend(line_boxes(px, py - inset, pin.name, "center bottom", PIN_NAME))
    return boxes


def _net_label_boxes(sheet) -> list[tuple]:
    boxes = []
    for net, (x, y, justify) in getattr(sheet, "net_labels", {}).items():
        boxes.append((net, line_boxes(_mm(x), _mm(y), net, justify)))
    return boxes


def overlap_errors(sheet) -> list[str]:
    """Final gate. Every visible text box is tested again."""
    if sheet.filename.startswith("10-notes"):
        return _notes_page_errors(sheet)
    errors = []
    obstacles = []
    owners = []
    for inst in sheet.insts:
        box = ink_box(inst)
        obstacles.append(box + (f"symbol {inst.ref}.{inst.unit}",))
        owners.append(inst)
    wires = _wire_boxes(sheet)
    obstacles.extend(wires)
    obstacles.extend(_dash_boxes(sheet))
    obstacles.extend(_frame_boxes())
    texts = []
    for inst in sheet.insts:
        lines = _label_lines(inst)
        if not lines:
            continue
        body_anchor_x = _mm(inst.x + inst.ref_dx)
        body_anchor_y = _mm(inst.y + inst.ref_dy)
        # Rebuild from the anchors prepare stored. Reference and value are separate.
        if not inst.hide_ref:
            texts.append((f"{inst.ref} reference", line_boxes(body_anchor_x, body_anchor_y, inst.ref, inst.ref_justify or "center"), None))
        if not inst.hide_value and inst.value:
            value_x = _mm(inst.x + inst.val_dx)
            value_y = _mm(inst.y + inst.val_dy)
            texts.append((f"{inst.ref} value", line_boxes(value_x, value_y, inst.value, inst.val_justify or "center"), None))
    for x, y, text in sheet.texts:
        texts.append((f"text {text[:24]}", line_boxes(_mm(x), _mm(y), text, "left"), None))
    for mx, my, marker in getattr(sheet, "markers", []):
        texts.append((f"marker {marker}", line_boxes(mx, my, marker, "left"), None))
    if getattr(sheet, "band_lines", None):
        ox, oy = sheet.band_origin
        texts.append(("notes band", line_boxes(ox, oy, "\n".join(sheet.band_lines), "left top"), "band"))
    for net, boxes in _net_label_boxes(sheet):
        texts.append((f"label {net}", boxes, f"wire {net}"))

    seen = []
    for name, boxes, skip in texts:
        for box in boxes:
            grown = _grow(box, 0.25)
            for item in obstacles:
                if skip and item[-1] == skip:
                    continue
                if skip and skip.startswith("wire") and item[-1] == skip.replace("wire ", ""):
                    continue
                if _intersects(grown, item):
                    errors.append(f"{sheet.filename} {name} hits {item[-1]}")
                    break
            else:
                seen.append(grown + (name,))
                continue
            break
        else:
            continue
    # Text against text.
    for index, left in enumerate(seen):
        for right in seen[index + 1 :]:
            if _intersects(left, right):
                errors.append(f"{sheet.filename} {left[-1]} hits {right[-1]}")
    # Unique, stable, short.
    unique = []
    for error in errors:
        if error not in unique:
            unique.append(error)
    return unique[:60]


def layout_notes_page(sheet) -> None:
    """A full-page notes frame. The lines are already numbered."""
    sheet.texts = []
    sheet.band_lines = []
    sheet.markers = []
    sheet.overflow = []
    x0, y0, x1, y1 = 16.0, 16.0, 404.0, 250.0
    sheet.frames = [(x0, y0, x1, y1)]
    limit = (x1 - x0) / 2.0 - 6.0
    lines = []
    for item in _note_items(sheet):
        lines.extend(_wrap(item[1], limit))
    mid = (len(lines) + 1) // 2
    columns = (lines[:mid], lines[mid:])
    sheet.notes_columns = []
    for column, chunk in enumerate(columns):
        if not chunk:
            continue
        x = x0 + 3.0 + column * ((x1 - x0) / 2.0)
        y = y0 + 3.0
        sheet.notes_columns.append((x, y, "\n".join(chunk)))


def _notes_page_errors(sheet) -> list[str]:
    errors = []
    if not getattr(sheet, "notes_columns", None):
        layout_notes_page(sheet)
    obstacles = _frame_boxes()
    frame = sheet.frames[0]
    # The frame stroke is an obstacle. Text sits inside with padding.
    x0, y0, x1, y1 = frame
    obstacles.append((x0 - 0.4, y0 - 0.4, x1 + 0.4, y0 + 0.5, "notes frame"))
    obstacles.append((x0 - 0.4, y1 - 0.5, x1 + 0.4, y1 + 0.4, "notes frame"))
    obstacles.append((x0 - 0.4, y0, x0 + 0.5, y1, "notes frame"))
    obstacles.append((x1 - 0.5, y0, x1 + 0.4, y1, "notes frame"))
    seen = []
    for x, y, text in sheet.notes_columns:
        boxes = line_boxes(x, y, text, "left top")
        for box in boxes:
            grown = _grow(box, 0.25)
            for item in obstacles:
                if _intersects(grown, item):
                    errors.append(f"{sheet.filename} notes text hits {item[-1]}")
                    break
            seen.append(grown + ("notes",))
    return errors


def index_positions(count: int) -> list[tuple[float, float]]:
    """Sheet-symbol origins on the index, in millimetres."""
    spots = []
    for index in range(count):
        column = 0 if index < 5 else 1
        row = index if index < 5 else index - 5
        x = 18.0 if column == 0 else 200.0
        y = 22.0 + row * 22.0
        spots.append((x, y))
    return spots


def index_errors(titles: list[str], filenames: list[str]) -> list[str]:
    """The index sheet has no circuit. Check its sheet boxes, names, and notes band."""
    errors = []
    obstacles = list(_frame_boxes())
    x0, y0, x1, y1 = BAND
    obstacles.append((x0, y0, x1, y1, "notes band"))
    seen = []
    for (x, y), title, filename in zip(index_positions(len(titles)), titles, filenames):
        box = (x, y, x + 150.0, y + 16.0, f"sheet {title}")
        obstacles.append(box)
        name_boxes = line_boxes(x, y - 0.6, title, "left bottom")
        file_boxes = line_boxes(x, y + 16.0, filename, "left top")
        for label, boxes in ((title, name_boxes), (filename, file_boxes)):
            for item in boxes:
                grown = _grow(item, 0.25)
                for obstacle in obstacles:
                    if obstacle[-1] == f"sheet {title}":
                        continue
                    if _intersects(grown, obstacle):
                        errors.append(f"index {label} hits {obstacle[-1]}")
                        break
                seen.append(grown + (label,))
    intro = "\n".join([
        "(1) VC-SCH-5000 revision 0C. Wires are drawn on the circuit sheets.",
        "(2) A global label is a wire that continues on another sheet.",
        "(3) OPEN means the order code is not chosen. TBC means the pin is not confirmed.",
        "(4) Product text is the maker and the short type, then the Ground UP article.",
        "(5) Numbered notes sit in this band. A marker such as (1) is the only note in the circuit.",
        "(6) The notes sheet lists the nets that leave a sheet.",
    ])
    boxes = line_boxes(x0 + 1.6, y0 + 1.4, intro, "left top")
    for box in boxes:
        if box[3] > y1 - 1.0 or box[2] > x1 - 1.4:
            errors.append("index notes band overflows")
            break
    return errors
