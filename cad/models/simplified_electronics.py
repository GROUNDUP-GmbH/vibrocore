"""Device shapes for the electronics enclosure.

Mean Well SDR-120 and SDR-480 come from the manufacturer STEP.
The full SDR-120 file is 14.7 MB. The stored exterior keeps the measured
outline and the terminal solids, and it is under 10 MB.
RevPi, RUT241, WAGO, PNOZ s4 and the S200 are built here.
Their manufacturer files are either above 10 MB or behind a login.
Each built solid uses the published envelope, a DIN groove, terminals and a colour.

Local axes: X is the rail direction, Y is the depth, Z is the height.
The solid is centred. The back face is the DIN side, at negative Y.
"""

from __future__ import annotations

from cad.tools.bom import ROOT

VENDOR = ROOT / "cad" / "vendor"

# width, depth, height. Millimetres. Centres match the enclosure layout.
SIZE_MM = {
    "VC-PW-5310": (40.0, 126.26, 128.96),
    "VC-PW-5320-PLACEHOLDER": (85.5, 129.2, 125.2),
    "VC-HB-2300": (60.0, 214.0, 207.0),
    "VC-SH-1200-STO": (140.0, 164.5, 160.0),
    "VC-CT-6100": (78.6, 71.9, 100.0),
    "VC-CT-6110": (12.0, 67.8, 100.0),
    "VC-CT-6120": (12.0, 67.8, 100.0),
    "VC-CT-6140": (12.0, 67.8, 100.0),
    "VC-CT-6150": (12.0, 67.8, 100.0),
    "VC-CT-6220-RESERVE": (22.5, 120.0, 98.0),
    "VC-CT-6600": (83.0, 32.0, 86.0),
    "VC-CT-6800": (45.0, 110.37, 96.0),
    "VC-CT-6810": (22.5, 110.37, 96.0),
}

# RAL-like colours. One part does not share a colour with its neighbour.
CASE = (168, 172, 166)
CASE_DARK = (146, 150, 144)
TERMINAL_GREEN = (28, 122, 74)
TERMINAL_BLACK = (28, 30, 32)
S200 = (32, 48, 72)
FIN = (176, 182, 188)
WAGO = (22, 24, 26)
WAGO_DI = (34, 92, 58)
WAGO_DO = (166, 92, 28)
WAGO_SERIAL = (36, 74, 122)
WAGO_END = (120, 124, 128)
PNOZ = (232, 186, 28)
PNOZ_PLUG = (48, 50, 46)
RUT = (18, 20, 22)
ANTENNA = (186, 154, 72)
REVPI = (34, 36, 40)
REVPI_FRONT = (210, 96, 42)
DIO = (48, 52, 58)
DIO_FACE = (58, 112, 148)
VFD = (196, 132, 48)
VFD_DARK = (42, 36, 30)
BREAKER = (214, 216, 210)
BREAKER_TOGGLE = (36, 78, 150)
DUCT = (118, 146, 164)
RAIL = (132, 136, 140)
GLAND = (176, 148, 78)
SMA = (198, 170, 96)


def _box(width, depth, height):
    from build123d import Box

    return Box(width, depth, height)


def _at(x, y, z, shape):
    from build123d import Pos

    return Pos(x, y, z) * shape


def _cut(body, *tools):
    shape = body
    for tool in tools:
        shape = shape - tool
    return shape


def _parts_from_vendor(part_id: str, filename: str, colours: tuple[tuple[int, int, int], ...]):
    """Manufacturer solid. File Y is the rail width. File X is the depth.

    The curved terminal cover is at minimum file X.
    Rot(0, 0, -90) maps that cover to positive local Y and the width to X.
    """
    from build123d import Pos, Rot

    from cad.tools.geometry import load_vendor_shape

    loaded = load_vendor_shape(part_id, filename, recenter=False)
    if loaded is None:
        raise FileNotFoundError(f"{part_id} / {filename}")
    turned = Rot(0, 0, -90) * loaded
    center = turned.bounding_box().center()
    turned = Pos(-float(center.X), -float(center.Y), -float(center.Z)) * turned
    solids = [item for item in turned.solids() if abs(float(item.volume)) > 1.0]
    solids.sort(key=lambda item: -abs(float(item.volume)))
    parts = []
    for index, solid in enumerate(solids):
        parts.append((solid, colours[min(index, len(colours) - 1)]))
    return parts


def sdr120_parts():
    return _parts_from_vendor(
        "VC-PW-5310",
        "SDR-120-exterior.step",
        (CASE, CASE_DARK, TERMINAL_GREEN, TERMINAL_BLACK),
    )


def sdr480_parts():
    return _parts_from_vendor(
        "VC-PW-5320",
        "SDR-480.stp",
        (CASE, CASE_DARK, TERMINAL_GREEN, TERMINAL_BLACK, (196, 154, 42), (70, 78, 86)),
    )


def _groove(width, depth, height):
    groove_w = min(35.0, width - 1.2)
    return _at(0, -depth / 2.0 + 1.1, 0, _box(groove_w, 2.4, min(15.0, height * 0.22)))


def s200_parts():
    """Book-style servo drive. Fins on the sides. Connector row on the lower front."""
    width, depth, height = SIZE_MM["VC-HB-2300"]
    body = _cut(
        _box(width, depth, height),
        _groove(width, depth, height),
        _at(0, depth / 2.0 - 1.2, -height * 0.28, _box(width * 0.72, 2.6, height * 0.22)),
    )
    fins = []
    for index in range(8):
        z = -height * 0.18 + index * (height * 0.07)
        fins.append(_at(0, -depth * 0.02, z, _box(width + 6.0, 4.0, 5.0)))
    connector = _at(0, depth / 2.0 - 0.4, -height * 0.30, _box(width * 0.62, 6.0, height * 0.16))
    led = _at(0, depth / 2.0 + 0.4, height * 0.28, _box(width * 0.28, 1.6, 8.0))
    return [
        (body, S200),
        *[(fin, FIN) for fin in fins],
        (connector, TERMINAL_BLACK),
        (led, (64, 150, 96)),
    ]


def vfd_parts():
    """Unselected sonic inverter. The face is a drive. The order is open."""
    width, depth, height = SIZE_MM["VC-SH-1200-STO"]
    body = _cut(
        _box(width, depth, height),
        _groove(width, depth, height),
        _at(0, depth / 2.0 - 1.0, height * 0.16, _box(width * 0.42, 2.4, height * 0.22)),
    )
    display = _at(0, depth / 2.0 + 0.3, height * 0.16, _box(width * 0.36, 1.4, height * 0.16))
    keys = _at(0, depth / 2.0 + 0.3, -height * 0.02, _box(width * 0.34, 1.4, 10.0))
    terminals = _at(0, depth / 2.0 - 0.2, -height * 0.32, _box(width * 0.7, 8.0, height * 0.16))
    return [
        (body, VFD),
        (display, VFD_DARK),
        (keys, (70, 74, 78)),
        (terminals, TERMINAL_BLACK),
    ]


def _wago(width, depth, height, stripe, ports: int):
    body = _cut(
        _box(width, depth, height),
        _groove(width, depth, height),
        _at(0, depth / 2.0 - 1.3, -4.0, _box(max(width - 2.4, 4.0), 2.8, height * 0.58)),
    )
    stripe_bar = _at(0, depth / 2.0 + 0.35, height * 0.36, _box(max(width - 1.6, 3.0), 1.2, 7.0))
    levers = []
    count = ports
    span = height * 0.5
    for index in range(count):
        z = -span / 2.0 + (index + 0.5) * (span / count)
        levers.append(_at(0, depth / 2.0 - 0.2, z, _box(max(width * 0.46, 3.2), 3.4, 3.0)))
    parts = [(body, WAGO), (stripe_bar, stripe)]
    parts.extend((lever, stripe) for lever in levers)
    return parts


def wago_head_parts():
    width, depth, height = SIZE_MM["VC-CT-6100"]
    parts = _wago(width, depth, height, (64, 122, 170), 2)
    # Two Ethernet openings on the upper front of the controller.
    jack_l = _at(-16, depth / 2.0 + 0.6, 18, _box(14, 3.0, 12))
    jack_r = _at(16, depth / 2.0 + 0.6, 18, _box(14, 3.0, 12))
    return parts + [(jack_l, (20, 60, 110)), (jack_r, (20, 60, 110))]


def wago_di_parts():
    width, depth, height = SIZE_MM["VC-CT-6110"]
    return _wago(width, depth, height, WAGO_DI, 8)


def wago_do_parts():
    width, depth, height = SIZE_MM["VC-CT-6120"]
    return _wago(width, depth, height, WAGO_DO, 8)


def wago_serial_parts():
    width, depth, height = SIZE_MM["VC-CT-6140"]
    parts = _wago(width, depth, height, WAGO_SERIAL, 4)
    port = _at(0, depth / 2.0 + 0.5, 8, _box(7.5, 2.4, 14))
    return parts + [(port, WAGO_SERIAL)]


def wago_end_parts():
    width, depth, height = SIZE_MM["VC-CT-6150"]
    body = _cut(_box(width, depth, height), _groove(width, depth, height))
    return [(body, WAGO_END)]


def pnoz_parts():
    """Pilz PNOZ s4 envelope. Yellow body, plug rows at the top and the bottom."""
    width, depth, height = SIZE_MM["VC-CT-6220-RESERVE"]
    body = _cut(_box(width, depth, height), _groove(width, depth, height))
    top = _at(0, depth / 2.0 - 6.0, height / 2.0 - 16.0, _box(width - 2.0, 18.0, 24.0))
    bottom = _at(0, depth / 2.0 - 6.0, -height / 2.0 + 16.0, _box(width - 2.0, 18.0, 24.0))
    leds = _at(0, depth / 2.0 + 0.4, 6.0, _box(4.0, 1.4, 28.0))
    return [
        (body, PNOZ),
        (top, PNOZ_PLUG),
        (bottom, PNOZ_PLUG),
        (leds, (40, 140, 70)),
    ]


def rut241_parts():
    """Router standing on the rail. Antennas leave the top face."""
    width, depth, height = SIZE_MM["VC-CT-6600"]
    body_h = 74.0
    body = _at(0, 0, (body_h - height) / 2.0, _box(width, 25.0, body_h))
    body = _cut(body, _at(0, -25.0 / 2.0 + 1.0, (body_h - height) / 2.0, _box(min(35.0, width - 4), 2.2, 12.0)))
    left = _at(-22, 0, height / 2.0 + 2.0, _cylinder(3.4, 18.0))
    right = _at(22, 0, height / 2.0 + 2.0, _cylinder(3.4, 18.0))
    ports = _at(8, depth / 2.0 - 1.0, (body_h - height) / 2.0, _box(28.0, 6.0, 16.0))
    leds = _at(-24, depth / 2.0 + 0.3, 8 + (body_h - height) / 2.0, _box(16.0, 1.2, 4.0))
    return [
        (body, RUT),
        (left, ANTENNA),
        (right, ANTENNA),
        (ports, (70, 78, 86)),
        (leds, (64, 150, 210)),
    ]


def _cylinder(radius, length):
    from build123d import Cylinder

    return Cylinder(radius, length)


def revpi_parts():
    """Connect 4 outline from the Kunbus STEP. Front is split. Vents are on the top."""
    width, depth, height = SIZE_MM["VC-CT-6800"]
    body = _cut(
        _box(width, depth, height),
        _groove(width, depth, height),
        _at(0, 0, height / 2.0 - 1.2, _box(width * 0.72, depth * 0.55, 3.0)),
    )
    front = _at(0, depth / 2.0 - 8.0, 0, _box(width - 1.2, 14.0, height * 0.72))
    ports = _at(0, depth / 2.0 + 0.4, -6.0, _box(width * 0.62, 2.2, height * 0.42))
    return [(body, REVPI), (front, REVPI_FRONT), (ports, TERMINAL_BLACK)]


def dio_parts():
    width, depth, height = SIZE_MM["VC-CT-6810"]
    body = _cut(_box(width, depth, height), _groove(width, depth, height))
    face = _at(0, depth / 2.0 - 1.0, -4.0, _box(width - 2.4, 8.0, height * 0.62))
    return [(body, DIO), (face, DIO_FACE)]


def breaker_parts(width, depth, height):
    body = _cut(_box(width, depth, height), _groove(width, depth, height))
    toggle = _at(0, depth / 2.0 + 0.6, 8.0, _box(min(12.0, width * 0.45), 3.0, 16.0))
    return [(body, BREAKER), (toggle, BREAKER_TOGGLE)]


def small_module_parts(width, depth, height, colour):
    body = _cut(_box(width, depth, height), _groove(width, depth, height))
    return [(body, colour)]


def duct_parts(width, depth, height):
    outer = _box(width, depth, height)
    opening = _at(0, depth * 0.16, height * 0.08, _box(max(width - 8.0, 4.0), depth * 0.7, height * 0.62))
    return [(_cut(outer, opening), DUCT)]


def rail_parts(width, depth, height):
    web = _box(width, depth * 0.4, height)
    hat = _at(0, depth * 0.22, 0, _box(width, depth * 0.55, height * 0.7))
    return [(web, RAIL), (hat, (112, 116, 120))]


def gland_parts(name: str, across: float, length: float):
    from build123d import Cylinder, Pos, RegularPolygon, extrude

    radius = across / 2.0
    barrel = Cylinder(radius * 0.62, length)
    nut = Pos(0, 0, length * 0.18) * extrude(RegularPolygon(radius, 6), length * 0.34)
    colour = SMA if name.startswith("SMA") or name.startswith("RPSMA") else GLAND
    return [(barrel, colour), (nut, colour)]


def parts_for(name: str, width: float, depth: float, height: float):
    """Coloured solids for one layout item. Empty when the item is only a reserve."""
    if name == "VC-PW-5310":
        return sdr120_parts()
    if name == "VC-PW-5320-PLACEHOLDER":
        return sdr480_parts()
    if name == "VC-HB-2300":
        return s200_parts()
    if name == "VC-SH-1200-STO":
        return vfd_parts()
    if name == "VC-CT-6100":
        return wago_head_parts()
    if name.startswith("VC-CT-6110"):
        return wago_di_parts()
    if name.startswith("VC-CT-6120"):
        return wago_do_parts()
    if name == "VC-CT-6140":
        return wago_serial_parts()
    if name == "VC-CT-6150":
        return wago_end_parts()
    if name == "VC-CT-6220-RESERVE":
        return pnoz_parts()
    if name == "VC-CT-6600":
        return rut241_parts()
    if name == "VC-CT-6800":
        return revpi_parts()
    if name == "VC-CT-6810":
        return dio_parts()
    if name.startswith("VC-PW-57"):
        return breaker_parts(width, depth, height)
    if name == "VC-CT-6400":
        return small_module_parts(width, depth, height, (40, 44, 48))
    if name == "VC-LT-9110":
        return small_module_parts(width, depth, height, (90, 96, 70))
    if name.startswith("DUCT"):
        return duct_parts(width, depth, height)
    if name.startswith("RAIL"):
        return rail_parts(width, depth, height)
    if name.startswith("M") or name.startswith("SMA") or name.startswith("RPSMA") or name in {"VENT", "PE-STUD"}:
        return gland_parts(name, min(width, depth), height)
    if name.startswith("BRACKET") or name.startswith("TNUT"):
        return [(_box(width, depth, height), (90, 98, 108))]
    if name.startswith("BUFFER"):
        return [(_box(width, depth, height), (64, 72, 80))]
    if name.startswith("VC-CT-6340"):
        return small_module_parts(width, depth, height, (150, 154, 148))
    return [(_box(width, depth, height), (90, 110, 130))]
