"""Electronics enclosure VC-ASM-5000. Parametric study model.

The box is Rittal AX 1181.000. It is not placed in the machine assembly.
The chain-shaft encoder is obsolete. This model has no gland and no module for it.
Position comes from the 1FL2 absolute encoder through the S200.
There is no 48 V rail. VC-PW-5310 is the dedicated SDR-120-24 for the S200 control
supply and the brake. VC-PW-5320 reserves an SDR-480-24 size slot. Its rating is open.
The safety relay slot is Pilz PNOZ s4 750104. The sonic inverter is an STO placeholder.
The filter fan is not fitted. Two door zones stay clear for a later fan.

Do not manufacture from this solid.
"""

from __future__ import annotations

from dataclasses import dataclass

from cad.tools.bom import ROOT

ASSEMBLY_ID = "VC-ASM-5000"
RENDER_DIR = ROOT / "cad" / "export" / "renders"
STEP_NAME = f"{ASSEMBLY_ID}.step"

# Rittal AX 1181.000. Sheet steel, IP66, one door, mounting plate included.
# https://www.rittal.com/pdf-creator/variant/com-en/1181000
# Technical detail: T3 is the distance from the inside of the door to the plate.
BOX_W_MM = 800.0
BOX_H_MM = 1000.0
BOX_D_MM = 400.0
WALL_MM = 1.5
DOOR_MM = 2.0
PLATE_W_MM = 745.0
PLATE_H_MM = 975.0
PLATE_T_MM = 2.5
T3_MM = 287.5
ORDER_CODE = "1181.000"

# IEC TR 60890 wall-mount effective surface, as published by nVent Hoffman.
# A = 1.4 * W * (H + D) + 1.8 * H * D, metres.
# The linear steel factor 5.5 W/m²K is the same check those guides use with that area.
STEEL_K_W_M2K = 5.5
AMBIENT_C = 40.0
INTERNAL_LIMIT_C = 50.0

# Nameplate heat inside the box, watts. Sources are the manufacturer sheets.
# machine_sdr480_24_nameplate is the ceiling if the open slot is later a full
# SDR-480-24. It is not a selected rating. Actuator current is still unknown.
# There is no 48 V supply and no 48 V to 12 V converter.
HEAT_W = {
    "sdr120_dedicated": 11.9,
    "machine_sdr480_24_nameplate": 30.6,
    "s200": 46.0,
    "vfd_candidate": 30.6,
    "wago_rack": 13.2,
    "rut241_bound": 6.5,
    "safety_relay": 2.5,
    "small_loads": 8.0,
}

# Option A rack along the rail, millimetres. The 750-637 pitch is not included.
# 78.6 + 12 + 12 + 12 + 12 + 12 + 12 = 150.6
# The old 186.6 mm sum counted a 24 mm encoder module and does not add up.
RACK_PITCH_MM = (
    ("VC-CT-6100", 78.6),
    ("VC-CT-6110-1", 12.0),
    ("VC-CT-6110-2", 12.0),
    ("VC-CT-6120-1", 12.0),
    ("VC-CT-6120-2", 12.0),
    ("VC-CT-6140", 12.0),
    ("VC-CT-6150", 12.0),
)
OPTION_B_RAIL_MM = 45.0 + 22.5  # Connect 4 width + DIO width
OPTION_B_RAIL_IF_LONG_AXIS_MM = 96.0 + 22.5

# Lapp SKINTOP MS-SC-M. https://products.lappgroup.com/online-catalogue/cable-glands/skintop-cable-glands-nickel-plated-brass-metric/emc/skintop-ms-sc-m.html
GLAND = {
    "M25": {"article": "53112640", "pitch": 42.0, "across": 29.0, "body": 20.0},
    "M20": {"article": "53112630", "pitch": 36.0, "across": 24.0, "body": 18.0},
    "M16": {"article": "53112620", "pitch": 30.0, "across": 20.0, "body": 16.0},
}


@dataclass(frozen=True)
class Item:
    name: str
    x: float
    y: float
    z: float
    sx: float
    sy: float
    sz: float
    kind: str


def rack_width_mm() -> float:
    return sum(width for _name, width in RACK_PITCH_MM)


def effective_area_m2() -> float:
    """IEC TR 60890 style area for one wall-mounted box. Metres."""
    width = BOX_W_MM / 1000.0
    height = BOX_H_MM / 1000.0
    depth = BOX_D_MM / 1000.0
    return 1.4 * width * (height + depth) + 1.8 * height * depth


def passive_watts(delta_k: float) -> float:
    return STEEL_K_W_M2K * effective_area_m2() * delta_k


def heat_total_w(*, include_machine_psu: bool) -> float:
    """Closed heat omits the open machine-supply nameplate."""
    total = 0.0
    for key, watts in HEAT_W.items():
        if key == "machine_sdr480_24_nameplate" and not include_machine_psu:
            continue
        total += watts
    return total


def temperature_rise_k(watts: float) -> float:
    return watts / (STEEL_K_W_M2K * effective_area_m2())


def internal_c(watts: float) -> float:
    return AMBIENT_C + temperature_rise_k(watts)


def _plate_front_y() -> float:
    door_inner = BOX_D_MM / 2.0 - DOOR_MM
    return door_inner - T3_MM


def _item(name, x, y, z, sx, sy, sz, kind) -> Item:
    return Item(name, x, y, z, sx, sy, sz, kind)


def _on_plate(name, x, z, sx, sz, depth, kind="device") -> Item:
    """Center a part whose back face is on the mounting plate."""
    y0 = _plate_front_y()
    return _item(name, x, y0 + depth / 2.0, z, sx, depth, sz, kind)


def _rail(specs: list[tuple[str, float, float, float]], x0: float, z_bottom: float) -> list[Item]:
    """Bottoms share one DIN rail. Each tuple is name, width, height, depth."""
    items = []
    x = x0
    for name, width, height, depth in specs:
        items.append(_on_plate(name, x + width / 2.0, z_bottom + height / 2.0, width, height, depth))
        x += width
    return items


def layout_items() -> list[Item]:
    """Device, duct, gland, bracket and reserved-fan boxes. Millimetres, box centre at 0."""
    items: list[Item] = []
    # Drives. STEP envelope of the S200 is 60 x 207 x 214 mm, larger than 60 x 170 x 195.
    # The long axis is treated as the depth so the door clearance stays honest.
    items.append(_on_plate("VC-HB-2300", 330.5, 374.0, 60.0, 207.0, 214.0))
    # STO is required. The order is not selected. This box is only a placeholder.
    items.append(_on_plate("VC-SH-1200-STO", 210.5, 397.5, 140.0, 160.0, 164.5, "placeholder"))
    # Dedicated 24 V supply for S200 control and the brake. SDR-120-24, 5 A.
    items.append(_on_plate("VC-PW-5310", -240.0, 383.02, 40.0, 128.96, 126.26))
    # Machine 24 V slot. The solid is the SDR-480 STEP. The rating is not frozen.
    # Measured outline: width 85.5, depth 129.2, height 125.2. Bottom stays at 320.3.
    items.append(_on_plate("VC-PW-5320-PLACEHOLDER", -317.75, 382.9, 85.5, 125.2, 129.2, "device"))
    # Switchgear placeholders. Order codes are still open.
    items.append(_on_plate("VC-PW-5700", -333.5, 253.5, 54.0, 90.0, 70.0, "placeholder"))
    items.append(_on_plate("VC-PW-5710", -282.5, 253.5, 36.0, 90.0, 70.0, "placeholder"))
    items.append(_on_plate("VC-PW-5720", -222.5, 253.5, 72.0, 90.0, 80.0, "placeholder"))
    # Duct under the drives only. The left side is the switchgear.
    items.append(_on_plate("DUCT-DRIVES", 240.0, 238.5, 230.0, 40.0, 40.0, "duct"))
    z_rail = 96.5
    items.extend(
        _rail(
            [
                ("VC-CT-6100", 78.6, 100.0, 71.9),
                ("VC-CT-6110-1", 12.0, 100.0, 67.8),
                ("VC-CT-6110-2", 12.0, 100.0, 67.8),
                ("VC-CT-6120-1", 12.0, 100.0, 67.8),
                ("VC-CT-6120-2", 12.0, 100.0, 67.8),
                ("VC-CT-6140", 12.0, 100.0, 67.8),
                ("VC-CT-6150", 12.0, 100.0, 67.8),
            ],
            -160.0,
            z_rail,
        )
    )
    # Reserved DIN space for Pilz PNOZ s4 750104. 22.5 x 98 x 120 mm.
    items.append(_on_plate("VC-CT-6220-RESERVE", 36.0, z_rail + 49.0, 22.5, 98.0, 120.0, "placeholder"))
    # RUT241 stands on the rail. 83 wide, 32 deep, 86 tall with the antennas.
    items.append(_on_plate("VC-CT-6600", 120.0, z_rail + 43.0, 83.0, 86.0, 32.0))
    # Option B is drawn on the same rail so the fit is visible. It is not a second order.
    items.append(_on_plate("VC-CT-6800", 230.0, z_rail + 48.0, 45.0, 96.0, 110.37))
    items.append(_on_plate("VC-CT-6810", 268.0, z_rail + 48.0, 22.5, 96.0, 110.37))
    items.append(_on_plate("VC-CT-6400", -280.0, -250.0, 30.0, 40.0, 20.0, "placeholder"))
    items.append(_on_plate("VC-LT-9110", -210.0, -240.0, 45.0, 70.0, 60.0, "placeholder"))
    items.extend(_rails())
    items.append(_on_plate("DUCT-CONTROL", 0.0, 64.5, 700.0, 40.0, 40.0, "duct"))
    items.append(_on_plate("DUCT-TERMINAL", 0.0, -378.0, 680.0, 40.0, 40.0, "duct"))
    items.append(_on_plate("VC-CT-6340", -20.0, -436.5, 360.0, 52.0, 48.0))
    items.extend(_glands())
    items.extend(_mounts())
    items.extend(_fan_reserves())
    return items


def _glands() -> list[Item]:
    """Bottom face. No chain-encoder gland."""
    specs = (
        [("M25", "230V")]
        + [("M20", name) for name in (
            "servo-power",
            "servo-encoder",
            "sonic-1",
            "sonic-2",
            "lift-1",
            "lift-2",
            "tilt",
            "spare-1",
            "spare-2",
        )]
    )
    back = _gland_row(specs, y=-80.0, z=-BOX_H_MM / 2.0)
    front_specs = [("M16", name) for name in (
        "limit-up",
        "limit-down",
        "estop",
        "load-cell",
        "beacon",
        "spare-1",
        "spare-2",
    )]
    front = _gland_row(front_specs, y=20.0, z=-BOX_H_MM / 2.0, x0=-250.0)
    extras = []
    # Telegärtner bulkheads and the vent sit on the same bottom face.
    x = 80.0
    for name in ("GNSS", "LTE-1", "LTE-2"):
        extras.append(_item(f"SMA-{name}", x, 70.0, -BOX_H_MM / 2.0 - 6.0, 12.0, 12.0, 22.0, "gland"))
        x += 22.0
    extras.append(_item("RPSMA-WIFI", x, 70.0, -BOX_H_MM / 2.0 - 6.0, 12.0, 12.0, 22.0, "gland"))
    extras.append(_item("VENT", 200.0, 70.0, -BOX_H_MM / 2.0 - 5.0, 16.0, 16.0, 18.0, "gland"))
    extras.append(_item("PE-STUD", 250.0, 20.0, -BOX_H_MM / 2.0 - 8.0, 14.0, 14.0, 24.0, "gland"))
    return back + front + extras


def _gland_row(specs, y: float, z: float, x0: float | None = None) -> list[Item]:
    widths = [GLAND[size]["pitch"] for size, _name in specs]
    total = sum(widths)
    x = -total / 2.0 if x0 is None else x0
    items = []
    for (size, name), pitch in zip(specs, widths):
        body = GLAND[size]["body"]
        items.append(
            _item(
                f"{size}-{name}",
                x + pitch / 2.0,
                y,
                z - body / 2.0,
                GLAND[size]["across"],
                GLAND[size]["across"],
                body + 8.0,
                "gland",
            )
        )
        x += pitch
    return items


def _mounts() -> list[Item]:
    """Four brackets, four buffers and four T-slot nuts on the rear face."""
    items = []
    for index, (x, z) in enumerate(((-280, 280), (280, 280), (-280, -280), (280, -280)), start=1):
        items.append(_item(f"BUFFER-{index}", x, -215.0, z, 40.0, 30.0, 40.0, "mount"))
        items.append(_item(f"BRACKET-{index}", x, -268.0, z, 40.0, 76.0, 80.0, "mount"))
        items.append(_item(f"TNUT-{index}", x, -312.0, z, 20.0, 12.0, 10.0, "mount"))
    return items


def _rails() -> list[Item]:
    """DIN rails on the plate. The clip of each device wraps the rail."""
    y = _plate_front_y() + 3.8
    rails = (
        ("RAIL-POWER", -290.0, 383.0, 200.0),
        ("RAIL-DRIVE", 250.0, 380.0, 280.0),
        ("RAIL-CONTROL", 70.0, 146.5, 520.0),
        ("RAIL-FEED", -270.0, 253.5, 200.0),
    )
    return [_item(name, x, y, z, length, 7.5, 35.0, "rail") for name, x, z, length in rails]


def _fan_reserves() -> list[Item]:
    """Empty door zones. The fan is not fitted. IP66 stays closed."""
    return [
        _item("FAN-RESERVE-LOW", -106.0, 171.5, -206.0, 148.5, 53.0, 148.5, "reserve"),
        _item("FAN-RESERVE-HIGH", 114.0, 171.5, 154.0, 148.5, 53.0, 148.5, "reserve"),
    ]


def _hits(a: Item, b: Item, gap: float = 0.2) -> bool:
    return (
        abs(a.x - b.x) * 2.0 < (a.sx + b.sx) - gap
        and abs(a.y - b.y) * 2.0 < (a.sy + b.sy) - gap
        and abs(a.z - b.z) * 2.0 < (a.sz + b.sz) - gap
    )


def layout_conflicts() -> list[tuple[str, str]]:
    """Pairs of solid items whose boxes intersect. Reserves must also stay clear."""
    items = [item for item in layout_items() if item.kind != "mount"]
    hits = []
    for index, left in enumerate(items):
        for right in items[index + 1 :]:
            if left.kind == "gland" and right.kind == "gland":
                continue
            if left.kind == "reserve" and right.kind == "reserve":
                continue
            if left.kind == "rail" or right.kind == "rail":
                continue
            if _hits(left, right):
                hits.append((left.name, right.name))
    return hits


def s200_door_clearance_mm() -> float:
    drive = next(item for item in layout_items() if item.name == "VC-HB-2300")
    door_inner = BOX_D_MM / 2.0 - DOOR_MM
    return door_inner - (drive.y + drive.sy / 2.0)


def validate_layout() -> None:
    conflicts = layout_conflicts()
    if conflicts:
        raise ValueError(f"enclosure items intersect: {conflicts[:8]}")
    if s200_door_clearance_mm() < 20.0:
        raise ValueError("S200 is closer than 20 mm to the door")
    if T3_MM <= 200.0:
        raise ValueError("installation depth is not above 200 mm")
    if rack_width_mm() < OPTION_B_RAIL_IF_LONG_AXIS_MM:
        raise ValueError("Option B does not fit the Option A rail")
    plate_front = _plate_front_y()
    for item in layout_items():
        if item.kind in {"device", "placeholder", "duct"}:
            if item.y - item.sy / 2.0 < plate_front - 0.2:
                raise ValueError(f"{item.name} is behind the mounting plate")
            if item.y + item.sy / 2.0 > BOX_D_MM / 2.0 - DOOR_MM - 5.0:
                raise ValueError(f"{item.name} meets the door")


def _coloured_parts(item: Item):
    """World-space solids for one item. Each entry is shape, colour, label."""
    from build123d import Pos

    from cad.models.simplified_electronics import parts_for

    local = parts_for(item.name, item.sx, item.sy, item.sz)
    placed = []
    for index, (shape, colour) in enumerate(local):
        world = Pos(item.x, item.y, item.z) * shape
        world.label = item.name
        label = item.name if index == 0 else ""
        placed.append((world, colour, label))
    return placed


def _shell():
    from build123d import Box, Pos

    outer = Box(BOX_W_MM, BOX_D_MM, BOX_H_MM)
    opening = BOX_D_MM - WALL_MM
    y = -BOX_D_MM / 2.0 + WALL_MM + opening / 2.0
    cavity = Pos(0, y, 0) * Box(BOX_W_MM - 2 * WALL_MM, opening, BOX_H_MM - 2 * WALL_MM)
    shell = outer - cavity
    shell.label = "VC-CT-6300-BODY"
    return shell


def _door(open_deg: float = 0.0):
    from build123d import Box, Pos, Rot

    leaf = Box(BOX_W_MM - 16.0, DOOR_MM, BOX_H_MM - 16.0)
    leaf.label = "VC-CT-6300-DOOR"
    placed = Pos(0, BOX_D_MM / 2.0 - DOOR_MM / 2.0, 0) * leaf
    if open_deg:
        hinge_x = -BOX_W_MM / 2.0
        hinge_y = BOX_D_MM / 2.0
        placed = Pos(hinge_x, hinge_y, 0) * Rot(0, 0, -open_deg) * Pos(-hinge_x, -hinge_y, 0) * placed
    return placed


def _plate():
    from build123d import Box, Pos

    y = _plate_front_y() - PLATE_T_MM / 2.0
    plate = Pos(0, y, 0) * Box(PLATE_W_MM, PLATE_T_MM, PLATE_H_MM)
    plate.label = "VC-CT-6300-PLATE"
    return plate


def assembly_parts(open_door: bool = False):
    """Shell, door, plate and devices. Reserves stay empty."""
    validate_layout()
    shell = _shell()
    door = _door(130.0 if open_door else 0.0)
    plate = _plate()
    parts = [
        (shell, (198, 200, 196), ""),
        (door, (186, 188, 184), ""),
        (plate, (168, 170, 166), ""),
    ]
    for item in layout_items():
        if item.kind == "reserve":
            continue
        parts.extend(_coloured_parts(item))
    return parts


def assembly_shape(open_door: bool = False):
    from build123d import Compound

    parts = [shape for shape, _colour, _label in assembly_parts(open_door)]
    shape = Compound(children=parts)
    shape.label = ASSEMBLY_ID
    return shape


def export_electronics_enclosure(bom, step_dir, render_dir) -> list:
    from build123d import export_step

    from cad.tools.geometry import _freeze_step_header

    step_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    shape = assembly_shape(open_door=False)
    step_path = step_dir / STEP_NAME
    export_step(shape, step_path)
    _freeze_step_header(step_path, ASSEMBLY_ID, bom.meta["cad_baseline_date"])
    _drop_negative_zero(step_path)
    written = [step_path]
    views = {
        "iso": True,
        "front-open": True,
        "bottom": False,
    }
    for view, door_open in views.items():
        path = render_dir / f"{ASSEMBLY_ID}-{view}.png"
        _render(assembly_parts(door_open), view, path)
        written.append(path)
    return written


def _drop_negative_zero(path) -> None:
    import re

    text = path.read_text(encoding="utf-8")
    cleaned = re.sub(r"-0\.(?!\d)", "0.", text)
    if "DIRECTION('',(0.,0.,1.))" not in cleaned:
        raise ValueError(f"{path} has no +Z axis direction")
    path.write_text(cleaned, encoding="utf-8")


LABELS = {
    "VC-HB-2300": "S200",
    "VC-SH-1200-STO": "STO open",
    "VC-PW-5310": "SDR-120",
    "VC-PW-5320-PLACEHOLDER": "SDR-480",
    "VC-CT-6100": "PFC200",
    "VC-CT-6110-1": "DI",
    "VC-CT-6110-2": "DI",
    "VC-CT-6120-1": "DO",
    "VC-CT-6120-2": "DO",
    "VC-CT-6140": "485",
    "VC-CT-6150": "END",
    "VC-CT-6220-RESERVE": "PNOZ s4",
    "VC-CT-6600": "RUT241",
    "VC-CT-6800": "RevPi",
    "VC-CT-6810": "DIO",
    "VC-PW-5700": "isolator",
    "VC-PW-5710": "MCB",
    "VC-PW-5720": "RCD",
}


def _render(parts, view: str, path) -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    eyes = {
        "iso": (np.array([0.48, 0.92, 0.72]), np.array([0.0, 0.0, 1.0])),
        "front-open": (np.array([0.22, 1.05, 0.58]), np.array([0.0, 0.0, 1.0])),
        "bottom": (np.array([0.18, 0.22, -1.0]), np.array([0.0, 1.0, 0.0])),
    }
    eye, up = eyes[view]
    eye = eye / np.linalg.norm(eye)
    forward = -eye
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    true_up = np.cross(right, forward)
    key = eye * 0.55 + np.array([0.05, 0.1, 0.75])
    key = key / np.linalg.norm(key)
    fill = np.array([-0.45, 0.25, 0.15])
    fill = fill / np.linalg.norm(fill)
    triangles = []
    shades = []
    anchors = []
    for shape, colour, label in parts:
        fine = (shape.label or "").startswith("VC-PW-53")
        try:
            vertices, faces = shape.tessellate(0.55 if fine else 1.6, 0.35 if fine else 0.6)
        except Exception:
            continue
        if not faces:
            continue
        points = np.array([(vertex.X, vertex.Y, vertex.Z) for vertex in vertices], dtype=np.float64)
        for face in faces:
            tri = points[list(face)]
            normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            norm = np.linalg.norm(normal)
            if norm < 1e-9:
                continue
            unit = normal / norm
            shade = 0.30 + 0.62 * max(0.0, float(np.dot(unit, key))) + 0.22 * max(0.0, float(np.dot(unit, fill)))
            shade = min(shade, 1.35)
            cam = np.column_stack((tri @ right, tri @ true_up, tri @ -forward))
            triangles.append(cam)
            shades.append(tuple(min(255.0, channel * shade) for channel in colour))
        text = LABELS.get(label or "")
        if text:
            center = shape.bounding_box().center()
            size = shape.bounding_box().size
            point = np.array(
                [
                    float(center.X),
                    float(center.Y) + float(size.Y) * 0.2,
                    float(center.Z) + float(size.Z) * 0.22,
                ]
            )
            anchors.append((point, text))
    width, height = 1100, 820
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:, :] = (244, 243, 238)
    depth = np.full((height, width), -1e30, dtype=np.float64)
    cloud = np.concatenate(triangles, axis=0)
    span_x = max(float(cloud[:, 0].max() - cloud[:, 0].min()), 1.0)
    span_y = max(float(cloud[:, 1].max() - cloud[:, 1].min()), 1.0)
    scale = min((width * 0.88) / span_x, (height * 0.86) / span_y)
    center_x = float(cloud[:, 0].min() + cloud[:, 0].max()) / 2.0
    center_y = float(cloud[:, 1].min() + cloud[:, 1].max()) / 2.0
    for tri, color in zip(triangles, shades):
        px = width / 2.0 + (tri[:, 0] - center_x) * scale
        py = height / 2.0 - (tri[:, 1] - center_y) * scale
        _paint(image, depth, px, py, tri[:, 2], color)
    picture = Image.fromarray(image, mode="RGB")
    if view != "bottom":
        _draw_labels(picture, anchors, right, true_up, forward, scale, center_x, center_y, width, height)
    path.parent.mkdir(parents=True, exist_ok=True)
    picture.save(path, format="PNG", compress_level=9, optimize=False)


def _draw_labels(picture, anchors, right, true_up, forward, scale, center_x, center_y, width, height) -> None:
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(picture)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    used = []
    for point, text in anchors:
        cam_x = float(point @ right)
        cam_y = float(point @ true_up)
        px = width / 2.0 + (cam_x - center_x) * scale
        py = height / 2.0 - (cam_y - center_y) * scale
        if px < 8 or py < 8 or px > width - 8 or py > height - 8:
            continue
        while any(abs(px - other_x) < 62 and abs(py - other_y) < 18 for other_x, other_y in used):
            py -= 16
        used.append((px, py))
        box = draw.textbbox((px, py), text, font=font, anchor="mm")
        draw.rectangle((box[0] - 2, box[1] - 1, box[2] + 2, box[3] + 1), fill=(244, 243, 238))
        draw.text((px, py), text, font=font, fill=(24, 26, 28), anchor="mm")


def _paint(image, depth, px, py, z, color) -> None:
    import numpy as np

    height, width = depth.shape
    min_x = max(int(np.floor(px.min())), 0)
    max_x = min(int(np.ceil(px.max())), width - 1)
    min_y = max(int(np.floor(py.min())), 0)
    max_y = min(int(np.ceil(py.max())), height - 1)
    if min_x > max_x or min_y > max_y:
        return
    xs = np.arange(min_x, max_x + 1, dtype=np.float64) + 0.5
    ys = np.arange(min_y, max_y + 1, dtype=np.float64) + 0.5
    grid_x, grid_y = np.meshgrid(xs, ys)
    x0, x1, x2 = px
    y0, y1, y2 = py
    denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(float(denom)) < 1e-8:
        return
    w0 = ((y1 - y2) * (grid_x - x2) + (x2 - x1) * (grid_y - y2)) / denom
    w1 = ((y2 - y0) * (grid_x - x2) + (x0 - x2) * (grid_y - y2)) / denom
    w2 = 1.0 - w0 - w1
    inside = (w0 >= -0.001) & (w1 >= -0.001) & (w2 >= -0.001)
    if not inside.any():
        return
    zee = w0 * z[0] + w1 * z[1] + w2 * z[2]
    window = depth[min_y : max_y + 1, min_x : max_x + 1]
    update = inside & (zee > window)
    window[update] = zee[update]
    patch = image[min_y : max_y + 1, min_x : max_x + 1]
    patch[update] = np.clip(np.array(color), 0, 255).astype(np.uint8)
