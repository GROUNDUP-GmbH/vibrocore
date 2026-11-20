#!/usr/bin/env python3
"""Build the QElectroTech cabinet schematic VC-SCH-5000, revision 0D.

The drawing uses IEC symbols from the QElectroTech 0.100 standard collection.
Those symbols are copied into symbols/ and embedded in the project, so the
file opens without the collection. Junction dots are connection points, not
components. Product names and article numbers come from the KiCad generator
and from annotate.PRODUCT. Nothing in this drawing is a new part.
"""

from __future__ import annotations

import os
import shutil
import sys
import textwrap
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KICAD = ROOT / "cad" / "kicad" / "vibrocore-control"
sys.path.insert(0, str(KICAD))

from annotate import PRODUCT  # noqa: E402
from generate_schematic import CABLES, TERMINALS, spec_of  # noqa: E402

NS = uuid.UUID("8f3a2c10-6b4e-5d21-9a77-1c0e5b8d6317")
FONT = "Liberation Sans,10,-1,5,50,0,0,0,0,0"
FONT12 = "Liberation Sans,12,-1,5,50,0,0,0,0,0"
COLS = 16
COLSIZE = 72
PAGE_W = COLS * COLSIZE
ROWSIZE = 64

# Feeder sections stated on the revision 0C notes. Wires that already have a
# section in SPEC keep that section, so the terminal plan matches.
NOTE_SECTION = {
    "110_L": "6 mm2",
    "111_N": "6 mm2",
    "120_L": "6 mm2",
    "121_N": "6 mm2",
    "130_L": "6 mm2",
    "131_N": "6 mm2",
    "140_L": "6 mm2",
    "141_N": "6 mm2",
    "150_L": "2.5 mm2",
    "151_N": "2.5 mm2",
    "201_24S": "1.0 mm2",
}

CATALOG = {
    "src": "10_electric/10_allpole/110_network_supplies/src_1p_pe_n.elmt",
    "iso2": "10_electric/10_allpole/200_fuses_protective_gears/20_disconnecting_switches/interrupteur_sectionneur_biphase.elmt",
    "rcd": "10_electric/10_allpole/200_fuses_protective_gears/50_residual_current_circuit_breaker/disjoncteur_differentiel_ph_n.elmt",
    "mcb1": "10_electric/10_allpole/200_fuses_protective_gears/11_circuit_breakers/disjonct-m_1f.elmt",
    "mcb2": "10_electric/10_allpole/200_fuses_protective_gears/11_circuit_breakers/disjonct-m_2f.elmt",
    "mcb3": "10_electric/10_allpole/200_fuses_protective_gears/11_circuit_breakers/disjonct-m_3f.elmt",
    "fuse": "10_electric/10_allpole/200_fuses_protective_gears/10_fuses/pojistka1p.elmt",
    "term": "10_electric/10_allpole/130_terminals_terminal_strips/borne_continuite.elmt",
    "earth": "10_electric/10_allpole/110_network_supplies/terre.elmt",
    "coil": "10_electric/10_allpole/310_relays_contactors_contacts/01_coils/bobine3.elmt",
    "no": "10_electric/10_allpole/310_relays_contactors_contacts/02_contacts_cross_referencing/01_auxiliary_contacts/con_simple.elmt",
    "nc": "10_electric/10_allpole/310_relays_contactors_contacts/02_contacts_cross_referencing/01_auxiliary_contacts/con_simple_nf.elmt",
    "motor": "10_electric/10_allpole/391_consumers_actuators/10_engines/moteur_tri_1.elmt",
    "psu": "10_electric/10_allpole/330_transformers_power_supplies/30_power_supplies/power_supply_1_phase_ac_dc.elmt",
    "estop": "10_electric/10_allpole/380_signaling_operating/20_push_buttons/e_stop_1p.elmt",
    "pb": "10_electric/10_allpole/380_signaling_operating/20_push_buttons/poussoir.elmt",
    "limnc": "10_electric/10_allpole/390_sensors_instruments/41_limit_switches/fin_de_course_nf.elmt",
    "limno": "10_electric/10_allpole/390_sensors_instruments/41_limit_switches/fin_de_course_no.elmt",
    "diode": "10_electric/10_allpole/395_electronics_semiconductors/11_diodes/diode.elmt",
    "res": "10_electric/10_allpole/395_electronics_semiconductors/01_resistors/resistance.elmt",
    "lamp": "10_electric/10_allpole/380_signaling_operating/11_optical_signaling/lampe_clignotante.elmt",
    "go": "10_electric/10_allpole/100_folio_referencing/02going_arrow.elmt",
    "come": "10_electric/10_allpole/100_folio_referencing/01coming_arrow.elmt",
    "bod": "10_electric/10_allpole/114_connections/bod.elmt",
}


def uid(name: str) -> str:
    return "{" + str(uuid.uuid5(NS, name)) + "}"


def section_of(wire: str) -> str:
    if wire == "W1":
        return "bond"
    if wire in NOTE_SECTION:
        return NOTE_SECTION[wire]
    return spec_of(wire)


def part(article: str, *extra: str) -> list[str]:
    name = PRODUCT.get(article)
    if not name:
        raise SystemExit(f"No product name for {article}")
    return [name, article, *extra]


@dataclass
class Pin:
    key: str
    x: int
    y: int
    ori: str
    uuid: str
    xml: ET.Element


@dataclass
class Symbol:
    key: str
    pins: list[Pin]
    ink: tuple[int, int, int, int]
    xml: ET.Element

    def pin(self, key) -> Pin:
        if isinstance(key, tuple):
            hits = [pin for pin in self.pins if (pin.x, pin.y) == key]
        elif key in ("n", "s", "e", "w"):
            hits = [pin for pin in self.pins if pin.ori == key]
        else:
            hits = [pin for pin in self.pins if pin.key == key]
        if len(hits) != 1:
            raise SystemExit(f"{self.key} pin {key!r} matches {len(hits)}")
        return hits[0]


@dataclass
class Node:
    sym: str
    x: int
    y: int
    ref: str
    lines: list[str]
    uuid: str
    links: list[tuple[str, str]] = field(default_factory=list)
    marks: list[int] = field(default_factory=list)
    side: str = "right"
    article: str = ""


@dataclass
class Wire:
    a: Node
    ap: Pin
    b: Node
    bp: Pin
    net: str


@dataclass
class Folio:
    number: int
    title: str
    height: int
    nodes: list[Node] = field(default_factory=list)
    wires: list[Wire] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    inputs: list[tuple[int, int, str, int]] = field(default_factory=list)
    shapes: list[tuple] = field(default_factory=list)
    seq: int = 0

    def _add(self, sym: str, x: int, y: int, ref: str, lines: list[str], side: str, article: str) -> Node:
        self.seq += 1
        found = article or next((line for line in lines if line.startswith("VC-")), "")
        node = Node(sym, int(x), int(y), ref, list(lines), uid(f"{self.number}:{self.seq}:{ref}:{sym}"), side=side, article=found)
        self.nodes.append(node)
        return node

    def place(self, sym: str, x: int, y: int, ref: str = "", lines: list[str] | None = None, side: str = "right", article: str = "") -> Node:
        return self._add(sym, x, y, ref, lines or [], side, article)

    def at(self, sym: str, key, x: int, y: int, ref: str = "", lines: list[str] | None = None, side: str = "right", article: str = "") -> Node:
        pin = SYMS[sym].pin(key)
        return self._add(sym, x - pin.x, y - pin.y, ref, lines or [], side, article)

    def dot(self, x: int, y: int) -> Node:
        return self.place("bod", x, y)

    def xy(self, node: Node, key) -> tuple[int, int]:
        pin = SYMS[node.sym].pin(key)
        return node.x + pin.x, node.y + pin.y

    def link(self, a: Node, ap, b: Node, bp, net: str) -> None:
        pa = SYMS[a.sym].pin(ap)
        pb = SYMS[b.sym].pin(bp)
        ax, ay = a.x + pa.x, a.y + pa.y
        bx, by = b.x + pb.x, b.y + pb.y
        if ax != bx and ay != by:
            self.errors.append(f"{net} is not orthogonal ({ax},{ay})-({bx},{by})")
        self.wires.append(Wire(a, pa, b, pb, net))

    def via(self, a: Node, ap, b: Node, bp, net: str) -> Node:
        """One right angle. The corner is a junction dot, so both runs are straight."""
        pa = SYMS[a.sym].pin(ap)
        pb = SYMS[b.sym].pin(bp)
        ax, ay = a.x + pa.x, a.y + pa.y
        bx, by = b.x + pb.x, b.y + pb.y
        if ax == bx or ay == by:
            self.link(a, ap, b, bp, net)
            return a
        # Leave the first pin along its own direction.
        if pa.ori in ("e", "w"):
            corner = self.dot(bx, ay)
            self.link(a, ap, corner, "4" if bx > ax else "3", net)
            self.link(corner, "2" if by > ay else "1", b, bp, net)
        else:
            corner = self.dot(ax, by)
            self.link(a, ap, corner, "2" if by > ay else "1", net)
            self.link(corner, "4" if bx > ax else "3", b, bp, net)
        return corner

    def via_h(self, a: Node, ap, b: Node, bp, net: str) -> None:
        """Horizontal first, then vertical. Both runs are straight."""
        ax, ay = self.xy(a, ap)
        bx, by = self.xy(b, bp)
        if ax == bx or ay == by:
            self.link(a, ap, b, bp, net)
            return
        corner = self.dot(bx, ay)
        self.link(a, ap, corner, "3" if bx < ax else "4", net)
        self.link(corner, "1" if by < ay else "2", b, bp, net)

    def note(self, text: str, node: Node) -> None:
        self.notes.append(text)
        node.marks.append(len(self.notes))

    def text(self, x: int, y: int, value: str, size: int = 10) -> None:
        self.inputs.append((int(x), int(y), value, size))

    def rect(self, x1, y1, x2, y2, dash: bool = False) -> None:
        self.shapes.append(("Rectangle", int(x1), int(y1), int(x2), int(y2), dash))

    def dash(self, x1, y1, x2, y2) -> None:
        self.shapes.append(("Line", int(x1), int(y1), int(x2), int(y2), True))

    def out(self, x: int, y: int, net: str, target: int) -> Node:
        return self.at("go", "w", x, y, ref=net, lines=[f"to {target:02d}"])

    def inn(self, x: int, y: int, net: str, source: int) -> Node:
        return self.at("come", "e", x, y, ref=net, lines=[f"from {source:02d}"])


SYMS: dict[str, Symbol] = {}


def _ink(root: ET.Element) -> tuple[int, int, int, int]:
    xs: list[float] = []
    ys: list[float] = []
    for el in root.iter():
        if el.tag == "line":
            xs += [float(el.get("x1", 0)), float(el.get("x2", 0))]
            ys += [float(el.get("y1", 0)), float(el.get("y2", 0))]
        elif el.tag in ("rect", "ellipse", "arc"):
            x = float(el.get("x", 0))
            y = float(el.get("y", 0))
            xs += [x, x + float(el.get("width", 0))]
            ys += [y, y + float(el.get("height", 0))]
        elif el.tag == "polygon":
            for point in el.findall("point"):
                xs.append(float(point.get("x", 0)))
                ys.append(float(point.get("y", 0)))
        elif el.tag == "terminal":
            xs.append(float(el.get("x", 0)))
            ys.append(float(el.get("y", 0)))
    if not xs:
        return (0, 0, 0, 0)
    return (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))


def load_symbols() -> None:
    local = HERE / "symbols"
    local.mkdir(exist_ok=True)
    source = Path(os.environ.get("QET_ELEMENTS", "/tmp/qet/squashfs-root/usr/share/elements"))
    for key, rel in CATALOG.items():
        dest = local / f"{key}.elmt"
        if not dest.exists():
            origin = source / rel
            if not origin.exists():
                raise SystemExit(f"Missing symbol {origin}")
            shutil.copyfile(origin, dest)
        root = ET.parse(dest).getroot()
        # The collection prints its own reference. This drawing prints one reference, in our text.
        for parent in root.iter():
            for text in list(parent.findall("dynamic_text")):
                parent.remove(text)
            for text in parent.findall("text"):
                font = text.get("font") or ""
                parts = font.split(",")
                if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) < 9:
                    parts[1] = "9"
                    text.set("font", ",".join(parts))
        pins = []
        for index, term in enumerate(root.findall(".//terminal")):
            name = term.get("name") or f"t{index}"
            pins.append(
                Pin(name, int(float(term.get("x"))), int(float(term.get("y"))), term.get("orientation") or "n", term.get("uuid"), term)
            )
        SYMS[key] = Symbol(key, pins, _ink(root), root)


def _color(net: str) -> str:
    if "PE" in net or net == "W1":
        return "#008000"
    if net.endswith("_N") or net == "001_0V":
        return "#000080"
    if "24" in net:
        return "#aa0000"
    return "#000000"


def _seg(wire: Wire) -> tuple[tuple[int, int], tuple[int, int]]:
    a = (wire.a.x + wire.ap.x, wire.a.y + wire.ap.y)
    b = (wire.b.x + wire.bp.x, wire.b.y + wire.bp.y)
    return a, b


def _interior(point, segment) -> bool:
    (x1, y1), (x2, y2) = segment
    px, py = point
    if x1 == x2:
        if px != x1:
            return False
        lo, hi = sorted((y1, y2))
        return lo < py < hi
    if y1 == y2:
        if py != y1:
            return False
        lo, hi = sorted((x1, x2))
        return lo < px < hi
    return False


def _overlap(s1, s2) -> bool:
    (a1, a2), (b1, b2) = s1, s2
    if a1[0] == a2[0] == b1[0] == b2[0]:
        lo = max(min(a1[1], a2[1]), min(b1[1], b2[1]))
        hi = min(max(a1[1], a2[1]), max(b1[1], b2[1]))
        return hi - lo > 1
    if a1[1] == a2[1] == b1[1] == b2[1]:
        lo = max(min(a1[0], a2[0]), min(b1[0], b2[0]))
        hi = min(max(a1[0], a2[0]), max(b1[0], b2[0]))
        return hi - lo > 1
    return False


def _shown(node: Node) -> list[str]:
    shown = []
    if node.marks:
        shown.append("".join(f"({mark})" for mark in node.marks))
    if node.ref and node.sym not in ("bod", "go", "come"):
        shown.append(node.ref)
    shown.extend(node.lines)
    return shown


def _text_box(node: Node, ink_box: tuple[int, int, int, int], shown: list[str]) -> tuple[int, int, int, int]:
    x1, y1, x2, _y2 = ink_box
    width = int(7 * max(len(line) for line in shown)) + 4
    height = 15 * len(shown)
    if node.sym == "come":
        left = max(8, x2 - width)
        return (left, y1 - height - 16, left + width, y1 - 16)
    if node.sym == "go" or node.side == "above":
        return (x1, y1 - height - 16, x1 + width, y1 - 16)
    if node.side == "left":
        return (x1 - width - 6, y1, x1 - 6, y1 + height)
    return (x2 + 6, y1, x2 + 6 + width, y1 + height)


def _hits(box, items) -> bool:
    return any(box[0] < item[2] - 1 and box[2] > item[0] + 1 and box[1] < item[3] - 1 and box[3] > item[1] + 1 for item in items)


def _find_label(wires, width, occupied, wire_boxes, height) -> tuple[int, int, int, int] | None:
    ranked = sorted(wires, key=lambda wire: abs(_seg(wire)[0][0] - _seg(wire)[1][0]) + abs(_seg(wire)[0][1] - _seg(wire)[1][1]), reverse=True)
    for wire in ranked:
        (a, b) = _seg(wire)
        if a[1] == b[1]:
            span = abs(b[0] - a[0])
            start = min(a[0], b[0])
            for frac in (0.5, 0.3, 0.7, 0.15, 0.85):
                left = int(start + span * frac - width / 2)
                for dy in (-24, -42, 18):
                    box = (left, a[1] + dy, left + width, a[1] + dy + 14)
                    if box[1] < 16 or box[3] > height - 160 or box[0] < 8 or box[2] > PAGE_W - 8:
                        continue
                    if _hits(box, occupied) or _hits(box, wire_boxes):
                        continue
                    return box
        else:
            span = abs(b[1] - a[1])
            start = min(a[1], b[1])
            for frac in (0.5, 0.3, 0.7):
                top = int(start + span * frac - 7)
                for dx in (-width - 12, 14):
                    box = (a[0] + dx, top, a[0] + dx + width, top + 14)
                    if box[1] < 16 or box[3] > height - 160 or box[0] < 8 or box[2] > PAGE_W - 8:
                        continue
                    if _hits(box, occupied) or _hits(box, wire_boxes):
                        continue
                    return box
    return None


def _boxes(folio: Folio) -> list[str]:
    errors = []
    ink = {}
    for node in folio.nodes:
        x1, y1, x2, y2 = SYMS[node.sym].ink
        ink[node.uuid] = (node.x + x1, node.y + y1, node.x + x2, node.y + y2)
    texts = []
    for node in folio.nodes:
        shown = _shown(node)
        if not shown or node.sym == "bod":
            continue
        box = _text_box(node, ink[node.uuid], shown)
        texts.append((node.uuid, *box, "label " + (node.ref or node.sym)))
    for x, y, value, _size in folio.inputs:
        width = int(7 * len(value)) + 4
        texts.append(("", x, y, x + width, y + 14, "text"))
    # One wire label per net, on a clear part of any of its segments.
    groups: dict[str, list[Wire]] = {}
    for wire in folio.wires:
        groups.setdefault(wire.net, []).append(wire)
    occupied = [item[1:5] for item in texts]
    occupied += [ink[node.uuid] for node in folio.nodes if node.sym != "bod"]
    wire_boxes = []
    for wire in folio.wires:
        (a, b) = _seg(wire)
        x1, x2 = sorted((a[0], b[0]))
        y1, y2 = sorted((a[1], b[1]))
        wire_boxes.append((x1 - 4, y1 - 4, x2 + 4, y2 + 4))
    for net, wires in groups.items():
        label = f"{net}  {section_of(net)}"
        width = int(7 * len(label)) + 4
        placed = _find_label(wires, width, occupied, wire_boxes, folio.height)
        if placed is None:
            (a, b) = _seg(wires[0])
            placed = (a[0] + 8, a[1] - 18, a[0] + 8 + width, a[1] - 4)
        texts.append(("", *placed, "wire " + net))
        occupied.append(placed)
        folio.text(placed[0], placed[1], label)
    band_top = folio.height - 150
    for uuid_, x1, y1, x2, y2, name in texts:
        if y2 > band_top and x2 > 590:
            errors.append(f"{name} enters the notes field")
        if x2 > PAGE_W - 8 or y2 > folio.height - 8 or x1 < 4 or y1 < 4:
            errors.append(f"{name} leaves the sheet ({x1},{y1})-({x2},{y2})")
        for other, box in ink.items():
            if other == uuid_:
                continue
            if x1 < box[2] and x2 > box[0] and y1 < box[3] and y2 > box[1]:
                owner = next((item for item in folio.nodes if item.uuid == other), None)
                if owner is not None and owner.sym == "bod":
                    continue
                errors.append(f"{name} hits {owner.ref if owner else '?'} {int(x1)},{int(y1)}-{int(x2)},{int(y2)} vs {box}")
                break
    for index, item in enumerate(texts):
        for other in texts[index + 1 :]:
            if item[1] < other[3] and item[3] > other[1] and item[2] < other[4] and item[4] > other[2]:
                errors.append(f"{item[5]} overlaps {other[5]} {int(item[1])},{int(item[2])}")
                break
    # Symbol ink against the notes field and against other symbols.
    for node in folio.nodes:
        box = ink[node.uuid]
        if box[3] > band_top and box[2] > 590:
            errors.append(f"{node.ref or node.sym} enters the notes field")
        for other in folio.nodes:
            if other.uuid <= node.uuid:
                continue
            ob = ink[other.uuid]
            if box[0] < ob[2] and box[2] > ob[0] and box[1] < ob[3] and box[3] > ob[1]:
                # Dots may sit on a terminal. Allow a dot to touch the pin it connects.
                if "bod" in (node.sym, other.sym):
                    continue
                errors.append(f"{node.ref or node.sym} hits {other.ref or other.sym}")
    return errors


def _wire_errors(folio: Folio) -> list[str]:
    errors = []
    segs = [(_seg(wire), wire.net) for wire in folio.wires]
    for index, (seg, net) in enumerate(segs):
        for other, onet in segs[index + 1 :]:
            shared = seg[0] in other or seg[1] in other
            if _overlap(seg, other) and net != onet:
                errors.append(f"{net} overlaps {onet}")
            if not shared:
                if _interior(seg[0], other) or _interior(seg[1], other) or _interior(other[0], seg) or _interior(other[1], seg):
                    if net != onet:
                        errors.append(f"{net} crosses {onet}")
    return errors


def check(folios: list[Folio]) -> None:
    bad = []
    for folio in folios:
        bad.extend(f"folio {folio.number:02d} {folio.title}: {message}" for message in folio.errors)
    for folio in folios:
        for message in _wire_errors(folio) + _boxes(folio):
            bad.append(f"folio {folio.number:02d} {folio.title}: {message}")
    if bad:
        raise SystemExit("Layout check failed:\n- " + "\n- ".join(bad[:40]))


def _titleblock() -> ET.Element:
    templates = ET.Element("titleblocktemplates")
    template = ET.SubElement(templates, "titleblocktemplate", {"name": "vc"})
    ET.SubElement(template, "information")
    ET.SubElement(template, "logos")
    grid = ET.SubElement(template, "grid", {"rows": "24;24;", "cols": "t28%;r44%;t28%;"})
    fields = [
        ("author", "0", "0", "Company", "%author", "12"),
        ("title", "0", "1", "", "%title", "12"),
        ("folio", "0", "2", "Folio", "%folio", "12"),
        ("file", "1", "0", "File", "%filename", "12"),
        ("date", "1", "1", "Date", "2026-11-20", "12"),
        ("rev", "1", "2", "Rev", "%indexrev", "12"),
    ]
    for name, row, col, label, value, size in fields:
        field_el = ET.SubElement(
            grid,
            "field",
            {
                "name": name,
                "row": row,
                "col": col,
                "align": "left" if col != "1" else "center",
                "valign": "center",
                "displaylabel": "true" if label else "false",
                "fontsize": size,
                "hadjust": "true",
            },
        )
        value_el = ET.SubElement(field_el, "value")
        ET.SubElement(value_el, "translation", {"lang": "en"}).text = value
        label_el = ET.SubElement(field_el, "label")
        ET.SubElement(label_el, "translation", {"lang": "en"}).text = label or name
    return templates


def _newdiagrams() -> ET.Element:
    block = ET.Element("newdiagrams")
    xrefs = ET.SubElement(block, "xrefs")
    ET.SubElement(
        xrefs,
        "xref",
        {
            "type": "coil",
            "slave_label": "(%f-%l%c)",
            "master_label": "%f-%l%c",
            "displayhas": "cross",
            "offset": "0",
            "xrefpos": "AlignBottom",
            "snapto": "bottom",
            "showpowerctc": "true",
            "powerprefix": "K",
            "delayprefix": "",
            "switchprefix": "",
        },
    )
    return block


def write_project(folios: list[Folio], path: Path) -> None:
    project = ET.Element("project", {"version": "0.100", "title": "VC-SCH-5000"})
    project.append(_titleblock())
    project.append(_newdiagrams())
    collection = ET.SubElement(project, "collection")
    category = ET.SubElement(collection, "category", {"name": "import"})
    for key, symbol in SYMS.items():
        element = ET.SubElement(category, "element", {"name": f"{key}.elmt"})
        element.append(symbol.xml)
    for folio in folios:
        diagram = ET.SubElement(
            project,
            "diagram",
            {
                "titleblocktemplate": "vc",
                "titleblocktemplateCollection": "embedded",
                "cols": str(COLS),
                "rows": str(folio.height // ROWSIZE),
                "colsize": str(COLSIZE),
                "rowsize": str(ROWSIZE),
                "height": str(folio.height),
                "folio": "%id/%total",
                "title": folio.title,
                "author": "Ground UP GmbH",
                "filename": "VC-SCH-5000",
                "date": "2026-11-20",
                "indexrev": "0D",
                "displaycols": "true",
                "displayrows": "true",
                "displayAt": "bottom",
                "order": str(folio.number),
                "version": "0.100",
            },
        )
        ET.SubElement(
            diagram,
            "defaultconductor",
            {
                "type": "single",
                "condsize": "1",
                "numsize": "10",
                "displaytext": "0",
                "conductor_color": "#000000",
                "text_color": "#000000",
                "horizontal-alignment": "AlignBottom",
                "vertical-alignment": "AlignRight",
                "function": "",
                "num": "",
                "formula": "",
                "conductor_section": "",
                "tension_protocol": "",
                "onetextperfolio": "0",
                "cable": "",
                "bus": "",
                "bicolor": "false",
                "dash-size": "2",
                "color2": "#000000",
                "horizrotatetext": "0",
                "vertirotatetext": "0",
            },
        )
        elements = ET.SubElement(diagram, "elements")
        for node in folio.nodes:
            element = ET.SubElement(
                elements,
                "element",
                {
                    "x": str(node.x),
                    "y": str(node.y),
                    "type": f"embed://import/{node.sym}.elmt",
                    "orientation": "0",
                    "uuid": node.uuid,
                    "z": "10",
                    "prefix": "",
                    "freezeLabel": "false",
                },
            )
            terminals = ET.SubElement(element, "terminals")
            for pin in SYMS[node.sym].pins:
                terminals.append(ET.fromstring(ET.tostring(pin.xml)))
            infos = ET.SubElement(element, "elementInformations")
            real = node.sym not in ("bod", "go", "come")
            if node.ref and real:
                ET.SubElement(infos, "elementInformation", {"show": "1", "name": "label"}).text = node.ref
            if node.lines and real:
                ET.SubElement(infos, "elementInformation", {"show": "0", "name": "designation"}).text = node.lines[0]
            if node.article and real:
                ET.SubElement(infos, "elementInformation", {"show": "0", "name": "manufacturer_reference"}).text = node.article
            if node.links:
                links = ET.SubElement(element, "links")
                for kind, target in node.links:
                    ET.SubElement(links, "link", {"type": kind, "uuid": target})
            texts = ET.SubElement(element, "dynamic_texts")
            shown = []
            if node.marks:
                shown.append("".join(f"({mark})" for mark in node.marks))
            if node.ref and node.sym not in ("go", "come"):
                shown.append(node.ref)
            shown.extend(node.lines)
            if shown and node.sym != "bod":
                x1, y1, x2, y2 = SYMS[node.sym].ink
                box = _text_box(node, (node.x + x1, node.y + y1, node.x + x2, node.y + y2), shown)
                text_x = box[0] - node.x
                text_y = box[1] - node.y
                text = ET.SubElement(
                    texts,
                    "dynamic_elmt_text",
                    {
                        "x": str(text_x),
                        "y": str(text_y),
                        "z": "1",
                        "text_width": "240",
                        "rotation": "0",
                        "Halignment": "AlignLeft",
                        "Valignment": "AlignTop",
                        "frame": "false",
                        "text_from": "UserText",
                        "font": FONT,
                        "uuid": uid(node.uuid + ":text"),
                    },
                )
                ET.SubElement(text, "text").text = "\n".join(shown)
        conductors = ET.SubElement(diagram, "conductors")
        for index, wire in enumerate(folio.wires):
            (x1, y1), (x2, y2) = _seg(wire)
            ET.SubElement(
                conductors,
                "conductor",
                {
                    "type": "single",
                    "num": wire.net,
                    "formula": "",
                    "conductor_section": section_of(wire.net),
                    "numsize": "10",
                    "condsize": "2" if section_of(wire.net).startswith("6") else "1",
                    "displaytext": "0",
                    "element1": wire.a.uuid,
                    "terminal1": wire.ap.uuid,
                    "element2": wire.b.uuid,
                    "terminal2": wire.bp.uuid,
                    "conductor_color": _color(wire.net),
                    "text_color": "#000000",
                    "horizontal-alignment": "AlignBottom",
                    "vertical-alignment": "AlignRight",
                    "function": "",
                    "tension_protocol": "",
                    "onetextperfolio": "0",
                    "cable": "",
                    "bus": "",
                    "bicolor": "false",
                    "dash-size": "2",
                    "color2": "#000000",
                    "horizrotatetext": "0",
                    "vertirotatetext": "0",
                    "freezeLabel": "false",
                    "x": str((x1 + x2) // 2),
                    "y": str((y1 + y2) // 2),
                },
            ).append(ET.Element("sequentialNumbers"))
        # Notes field. The drawing area stays above it.
        band_top = folio.height - 150
        shapes = ET.SubElement(diagram, "shapes")
        for kind, x1, y1, x2, y2, dash in folio.shapes + [("Rectangle", 590, band_top, PAGE_W - 16, folio.height - 16, False)]:
            shape = ET.SubElement(
                shapes,
                "shape",
                {
                    "type": kind,
                    "x1": str(x1),
                    "y1": str(y1),
                    "x2": str(x2),
                    "y2": str(y2),
                    "closed": "1" if kind == "Rectangle" else "0",
                    "rx": "0",
                    "ry": "0",
                    "z": "1",
                    "is_movable": "1",
                    "antialias": "false",
                },
            )
            ET.SubElement(shape, "pen", {"color": "#000080" if not dash else "#000000", "widthF": "1", "style": "DashLine" if dash else "SolidLine"})
            ET.SubElement(shape, "brush", {"color": "#ffffff", "style": "NoBrush"})
        inputs = ET.SubElement(diagram, "inputs")
        folio.text(600, band_top + 6, "Notes")
        y = band_top + 22
        room = folio.height - 18
        overflow = []
        for number, note in enumerate(folio.notes, 1):
            wrapped = textwrap.wrap(f"({number}) {note}", width=68) or [f"({number})"]
            for line in wrapped:
                if y + 14 > room:
                    overflow.append((folio.number, number, note))
                    break
                folio.text(600, y, line)
                y += 14
        folio.overflow = overflow  # type: ignore[attr-defined]
        for x, yy, value, size in folio.inputs:
            ET.SubElement(inputs, "input", {"x": str(x), "y": str(yy), "rotation": "0", "font": FONT12 if size == 12 else FONT, "text": value})
    tree = ET.ElementTree(project)
    ET.indent(tree, space="  ")
    path.write_bytes(ET.tostring(project, encoding="utf-8", xml_declaration=True))


def main() -> None:
    # Running this file as a script makes it __main__. The folio module must
    # use the same module object, so the symbols are loaded there.
    import generate_qet

    generate_qet.load_symbols()
    from sheets_qet import build

    folios = build()
    generate_qet.check(folios)
    out = generate_qet.HERE / "VC-SCH-5000.qet"
    generate_qet.write_project(folios, out)
    print(f"Wrote {out} ({len(folios)} folios)")


if __name__ == "__main__":
    main()
