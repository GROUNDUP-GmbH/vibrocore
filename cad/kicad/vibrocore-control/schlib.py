"""Project symbols for the Vibrocore cabinet schematic.

Graphics follow the IEC shapes in the KiCad 8 Device, Switch and power
libraries. Pin numbers that are not printed on the part are marked TBC.
"""

from __future__ import annotations

P = "passive"
PI = "power_in"
PO = "power_out"
IN = "input"
OT = "output"


def f(steps: float) -> str:
    value = int(round(float(steps) * 127))
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}{value // 100}.{value % 100:02d}"


def q(text: str) -> str:
    out = []
    for char in text:
        if char == "\\":
            out.append("\\\\")
        elif char == '"':
            out.append('\\"')
        elif char == "\n":
            out.append("\\n")
        else:
            out.append(char)
    return '"' + "".join(out) + '"'


class Pin:
    def __init__(self, num: str, name: str, x: int, y: int, ang: int, etype: str, unit: int = 1):
        self.num = num
        self.name = name
        self.x = x
        self.y = y
        self.ang = ang
        self.etype = etype
        self.unit = unit


class Sym:
    def __init__(
        self,
        name: str,
        prefix: str,
        pins: list[Pin],
        gfx: dict[int, list[str]],
        hh: int,
        hw: int,
        in_bom: bool = True,
        hide_numbers: bool = True,
    ):
        self.name = name
        self.prefix = prefix
        self.pins = pins
        self.gfx = gfx
        self.hh = hh
        self.hw = hw
        self.in_bom = in_bom
        self.hide_numbers = hide_numbers

    def pin(self, num: str, unit: int | None = None) -> Pin:
        hits = [pin for pin in self.pins if pin.num == num and (unit is None or pin.unit == unit)]
        if len(hits) != 1:
            raise KeyError(f"{self.name} pin {num} unit {unit}: {len(hits)} hits")
        return hits[0]

    def units(self) -> list[int]:
        return sorted({pin.unit for pin in self.pins} | set(self.gfx))


def rect(x1: int, y1: int, x2: int, y2: int) -> str:
    return (
        f"(rectangle (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) "
        "(stroke (width 0.254) (type default)) (fill (type none)))"
    )


def poly(pts: list[tuple[int, int]], width: str = "0.254") -> str:
    body = " ".join(f"(xy {f(x)} {f(y)})" for x, y in pts)
    return f"(polyline (pts {body}) (stroke (width {width}) (type default)) (fill (type none)))"


def circ(cx: int, cy: int, r: int) -> str:
    return (
        f"(circle (center {f(cx)} {f(cy)}) (radius {f(r)}) "
        "(stroke (width 0.254) (type default)) (fill (type none)))"
    )


def stext(x: int, y: int, text: str, size: str = "1.27") -> str:
    return (
        f"(text {q(text)} (at {f(x)} {f(y)} 0) "
        f"(effects (font (size {size} {size}))))"
    )


def pin_sexpr(pin: Pin) -> str:
    return (
        f'(pin {pin.etype} line (at {f(pin.x)} {f(pin.y)} {pin.ang}) (length 1.27) '
        f"(name {q(pin.name)} (effects (font (size 1.016 1.016)))) "
        f"(number {q(pin.num)} (effects (font (size 1.016 1.016)))))"
    )


def breaker_gfx(horizontal: bool = False) -> list[str]:
    """IEC circuit-breaker. Same geometry as KiCad Device:CircuitBreaker_1P, scaled to the grid."""
    if horizontal:
        return [
            poly([(6, 0), (4, 0)]),
            poly([(-6, 0), (-4, 0)]),
            poly([(-4, 0), (4, 3)]),
            poly([(3, 4), (5, 2)]),
        ]
    return [
        poly([(0, 4), (0, 2)]),
        poly([(0, -4), (0, -2)]),
        poly([(0, -2), (-3, 2)]),
        poly([(-1, 3), (1, 1)]),
    ]


def contact_gfx(kind: str) -> list[str]:
    lines = [
        poly([(-6, 0), (-2, 0)]),
        poly([(4, 0), (6, 0)]),
        poly([(-2, 0), (3, 3)]),
    ]
    if kind == "NC":
        lines.append(poly([(1, 2), (4, 2)]))
    if kind == "PB":
        lines.append(circ(0, 4, 1))
    return lines


SYMS: dict[str, Sym] = {}


def add(sym: Sym) -> Sym:
    SYMS[sym.name] = sym
    return sym


def two_pin(name: str, prefix: str, gfx: list[str], etype: str = P, in_bom: bool = True, horizontal: bool = False) -> None:
    if horizontal:
        pins = [Pin("1", "1", -8, 0, 180, etype), Pin("2", "2", 8, 0, 0, etype)]
        hh, hw = 6, 8
    else:
        pins = [Pin("1", "1", 0, 6, 270, etype), Pin("2", "2", 0, -6, 90, etype)]
        hh, hw = 8, 6
    add(Sym(name, prefix, pins, {1: gfx}, hh, hw, in_bom))


two_pin("FUSE", "F", [rect(-2, -3, 2, 3), poly([(0, -3), (0, 3)])])
two_pin("RES", "R", [rect(-4, -1, 4, 1), poly([(-6, 0), (-4, 0)]), poly([(4, 0), (6, 0)])], horizontal=True)
two_pin(
    "DIODE",
    "D",
    [poly([(-3, -2), (3, -2), (0, 3), (-3, -2)]), poly([(-3, 4), (3, 4)]), poly([(0, 4), (0, 6)]), poly([(0, -2), (0, -6)])],
)
two_pin("SW_NC", "S", contact_gfx("NC"), horizontal=True)
two_pin("SW_NO", "S", contact_gfx("NO"), horizontal=True)
two_pin("SW_PB", "S", contact_gfx("PB"), horizontal=True)
two_pin("BOND", "W", [circ(-3, 0, 1), circ(3, 0, 1), poly([(-2, 0), (2, 0)])], in_bom=False, horizontal=True)

add(
    Sym(
        "CBV",
        "F",
        [Pin("1", "1", 0, 8, 270, P), Pin("2", "2", 0, -8, 90, P)],
        {1: breaker_gfx(False)},
        10,
        6,
    )
)
add(
    Sym(
        "CBH",
        "F",
        [Pin("1", "1", -8, 0, 180, P), Pin("2", "2", 8, 0, 0, P)],
        {1: breaker_gfx(True)},
        6,
        10,
    )
)


def multi_breaker(name: str, prefix: str, poles: int, horizontal: bool, mark: list[str] | None = None) -> None:
    pins: list[Pin] = []
    gfx: dict[int, list[str]] = {}
    half = 8 if horizontal else 6
    for pole in range(poles):
        unit = pole + 1
        base = breaker_gfx(horizontal)
        if mark and pole == 0:
            base = base + mark
        gfx[unit] = base
        if horizontal:
            pins.append(Pin(str(pole * 2 + 1), str(pole * 2 + 1), -half, 0, 180, P, unit))
            pins.append(Pin(str(pole * 2 + 2), str(pole * 2 + 2), half, 0, 0, P, unit))
        else:
            pins.append(Pin(str(pole * 2 + 1), str(pole * 2 + 1), 0, half, 270, P, unit))
            pins.append(Pin(str(pole * 2 + 2), str(pole * 2 + 2), 0, -half, 90, P, unit))
    add(Sym(name, prefix, pins, gfx, half + 2, half + 2))


multi_breaker("ISO2", "Q", 2, False, [poly([(-4, -2), (4, -2)]), stext(6, 0, "ISO", "0.8")])
multi_breaker("RCD2", "QF", 2, False, [circ(6, 0, 2), stext(6, 0, "B", "1.27")])
multi_breaker("MCB2", "F", 2, False)
multi_breaker("MCB3", "F", 3, False, [stext(6, 0, "M", "1.0")])
multi_breaker("MPROT", "F", 3, True, [stext(0, 5, "PWM", "0.8")])

add(
    Sym(
        "EARTH",
        "PE",
        [Pin("1", "PE", 0, 0, 90, PI)],
        {1: [poly([(0, 0), (0, -2)]), poly([(-4, -2), (4, -2)]), poly([(-3, -4), (3, -4)]), poly([(-1, -6), (1, -6)])]},
        8,
        4,
        in_bom=False,
    )
)
add(
    Sym(
        "PWR",
        "PF",
        [Pin("1", "P", 0, 0, 90, PO)],
        {1: [poly([(0, 0), (0, -5), (5, -3), (0, 0)])]},
        6,
        6,
        in_bom=False,
    )
)
add(
    Sym(
        "TERM_V",
        "X",
        [Pin("1", "1", 0, 4, 270, P), Pin("2", "2", 0, -4, 90, P)],
        {1: [rect(-2, -2, 2, 2)]},
        4,
        3,
    )
)
add(
    Sym(
        "TERM_H",
        "X",
        [Pin("1", "1", -5, 0, 180, P), Pin("2", "2", 5, 0, 0, P)],
        {1: [rect(-2, -2, 2, 2)]},
        3,
        5,
    )
)
add(
    Sym(
        "LAMP",
        "H",
        [Pin("1", "A", 0, 6, 270, P), Pin("2", "B", 0, -6, 90, P)],
        {1: [circ(0, 0, 4), poly([(-3, -3), (3, 3)]), poly([(-3, 3), (3, -3)])]},
        8,
        6,
    )
)
add(
    Sym(
        "M3",
        "M",
        [
            Pin("U", "U", -12, 6, 180, P),
            Pin("V", "V", -12, 0, 180, P),
            Pin("W", "W", -12, -6, 180, P),
            Pin("PE", "PE", 0, -12, 90, PI),
        ],
        {1: [circ(0, 0, 8), stext(0, 0, "M", "2.54"), poly([(-10, 6), (-8, 6)]), poly([(-10, 0), (-8, 0)]), poly([(-10, -6), (-8, -6)])]},
        14,
        12,
    )
)
add(
    Sym(
        "MSRV",
        "M",
        [
            Pin("U", "U", -14, 26, 180, P),
            Pin("V", "V", -14, 22, 180, P),
            Pin("W", "W", -14, 18, 180, P),
            Pin("PE", "PE", -14, 12, 180, PI),
            Pin("BRN", "BR-", -14, 4, 180, P),
            Pin("BRP", "BR+", -14, 0, 180, P),
        ],
        {1: [circ(0, 0, 8), stext(0, 2, "M", "2.54"), stext(0, -4, "1FL2", "1.016")]},
        30,
        16,
    )
)
add(
    Sym(
        "COIL",
        "K",
        [Pin("A1", "A1", 0, 8, 270, P, 1), Pin("A2", "A2", 0, -8, 90, P, 1)],
        {1: [rect(-6, -6, 6, 6), stext(0, 0, "K", "1.524")]},
        10,
        8,
    )
)
add(
    Sym(
        "CHANGE",
        "K",
        [
            Pin("11", "11", -10, 0, 180, P, 1),
            Pin("12", "12", 10, 4, 0, P, 1),
            Pin("14", "14", 10, -4, 0, P, 1),
        ],
        {
            1: [
                poly([(-8, 0), (-2, 0)]),
                poly([(-2, 0), (6, 4)]),
                poly([(6, 4), (8, 4)]),
                poly([(2, 3), (6, 5)]),
                poly([(-2, -1), (8, -4)]),
                stext(-2, -6, "NO", "0.8"),
            ]
        },
        8,
        10,
    )
)


def estop() -> None:
    pins = []
    gfx = {}
    pairs = [("11", "12", 1), ("21", "22", 2), ("31", "32", 3)]
    for left, right, unit in pairs:
        # The higher terminal faces the PNOZ on this drawing.
        pins.append(Pin(left, left, 8, 0, 0, P, unit))
        pins.append(Pin(right, right, -8, 0, 180, P, unit))
        gfx[unit] = contact_gfx("NC") + [circ(0, 5, 2), stext(0, 5, "E", "1.016")]
    add(Sym("ESTOP", "S", pins, gfx, 8, 8))


estop()


def pnoz() -> None:
    left = [
        ("A1", "A1", PI, 18),
        ("A2", "A2", PI, 12),
        ("S11", "S11", P, 4),
        ("S12", "S12", P, 0),
        ("S21", "S21", P, -4),
        ("S22", "S22", P, -8),
        ("S34", "S34", P, -14),
        ("Y32", "Y32", P, -20),
    ]
    pins = [Pin(num, name, -16, y, 180, etype, 1) for num, name, etype, y in left]
    gfx = {
        1: [rect(-14, -24, 14, 22), stext(0, 16, "PNOZ s4", "1.27"), stext(0, 10, "750104", "1.016")],
    }
    contacts = [("13", "14", 2), ("23", "24", 3), ("33", "34", 4), ("41", "42", 5)]
    for left_n, right_n, unit in contacts:
        pins.append(Pin(left_n, left_n, -8, 0, 180, P, unit))
        pins.append(Pin(right_n, right_n, 8, 0, 0, P, unit))
        kind = "NC" if unit == 5 else "NO"
        gfx[unit] = contact_gfx(kind)
    add(Sym("PNOZ", "K", pins, gfx, 24, 16))


pnoz()


def finder() -> None:
    pins = [
        Pin("A1", "A1", 0, 8, 270, P, 1),
        Pin("A2", "A2", 0, -8, 90, P, 1),
        Pin("11", "11", -10, 0, 180, P, 2),
        Pin("12", "12", 10, 4, 0, P, 2),
        Pin("14", "14", 10, -4, 0, P, 2),
        Pin("21", "21", -10, 0, 180, P, 3),
        Pin("22", "22", 10, 4, 0, P, 3),
        Pin("24", "24", 10, -4, 0, P, 3),
    ]
    gfx = {
        1: [rect(-6, -6, 6, 6), stext(0, 0, "K", "1.524")],
        2: [
            poly([(-8, 0), (-2, 0)]),
            poly([(-2, 0), (6, 4)]),
            poly([(6, 4), (8, 4)]),
            poly([(2, 3), (6, 5)]),
            poly([(-2, -1), (8, -4)]),
        ],
        3: [
            poly([(-8, 0), (-2, 0)]),
            poly([(-2, 0), (6, 4)]),
            poly([(6, 4), (8, 4)]),
            poly([(2, 3), (6, 5)]),
            poly([(-2, -1), (8, -4)]),
        ],
    }
    add(Sym("REL", "K", pins, gfx, 10, 10))


finder()


def block(name: str, prefix: str, left: list[tuple], right: list[tuple], title: str, extra: list[Pin] | None = None) -> None:
    def rows(items: list[tuple], x: int, ang: int) -> list[Pin]:
        pins = []
        for num, pname, etype, y in items:
            pins.append(Pin(num, pname, x, y, ang, etype))
        return pins

    pins = rows(left, -22, 180) + rows(right, 22, 0) + (extra or [])
    ys = [pin.y for pin in pins] or [0]
    hh = max(abs(min(ys)), abs(max(ys))) + 6
    gfx = [rect(-20, -(hh - 2), 20, hh - 2), stext(0, hh - 5, title, "1.27")]
    add(Sym(name, prefix, pins, {1: gfx}, hh, 22))


block(
    "SRC",
    "G",
    [],
    [("L", "L", P, 4), ("N", "N", P, 0), ("PE", "PE", PI, -4)],
    "AC",
)
def add_psu(name: str, zero: str) -> None:
    pins = [
        Pin("L", "L", 0, 14, 270, P),
        Pin("N", "N", 0, -14, 90, P),
        Pin("PE", "PE", -16, 0, 180, PI),
        Pin("P", "+V", 16, 6, 0, PO),
        Pin("M", "0V", 16, -6, 0, zero),
    ]
    add(Sym(name, "G", pins, {1: [rect(-12, -10, 12, 10), stext(0, 0, "PSU", "1.27")]}, 16, 16))


add_psu("PSU", PI)
add_psu("PSU0", PO)
block(
    "PNP",
    "B",
    [("24", "+24", PI, 4), ("0", "0V", PI, 0)],
    [("OUT", "OUT", OT, 2)],
    "PNP",
)
block(
    "ACT",
    "M",
    [("1", "A", P, 3), ("2", "B", P, -3)],
    [],
    "M",
)
block(
    "HBR",
    "A",
    [("P", "+24", PI, 8), ("M", "0V", PI, 4), ("E", "EXT", IN, -2), ("R", "RET", IN, -6)],
    [("MP", "M+", P, 4), ("MN", "M-", P, -4)],
    "H",
)
block(
    "PULSE",
    "U",
    [("P", "CLK+", OT, 6), ("N", "CLK-", OT, 2), ("D", "DIR+", OT, -2), ("E", "DIR-", OT, -6)],
    [],
    "PLS",
)

# S200 PTI. Terminal names are the printed names. X124 screws are not numbered.
S200_L = [
    ("L1", "L1", P, 48),
    ("L2", "L2", P, 44),
    ("L3", "L3", P, 40),
    ("DCP", "DCP", P, 34),
    ("R1", "R1", P, 30),
    ("R2", "R2", P, 26),
    ("PE", "PE", PI, 18),
    ("24V", "X124 24V", PI, 10),
    ("0V", "X124 0V", PI, 6),
    ("24Vb", "X124 24V", PI, 2),
    ("0Vb", "X124 0V", PI, -2),
    ("1", "STO1+", IN, -10),
    ("2", "STO1-", P, -14),
    ("3", "STO-VS", P, -18),
    ("4", "STO-M", P, -22),
    ("5", "STO2+", IN, -26),
    ("6", "STO2-", P, -30),
    ("FB", "STO_EP TBC", OT, -38),
]
S200_R = [
    ("U", "U", P, 48),
    ("V", "V", P, 44),
    ("W", "W", P, 40),
    ("PE2", "PE", PI, 34),
    ("BRN", "BRN", P, 26),
    ("BRP", "BRP", P, 22),
    ("X120", "X120", P, 14),
    ("36", "PTIA_P", IN, 4),
    ("37", "PTIA_M", IN, 0),
    ("38", "PTIB_P", IN, -4),
    ("39", "PTIB_M", IN, -8),
    ("23", "RS485+", P, -16),
    ("25", "RS485-", P, -20),
]
block("S200", "A", S200_L, S200_R, "S200")

ATV_L = [
    ("L1", "R/L1", P, 52),
    ("L2", "S/L2", P, 48),
    ("L3", "T/L3", P, 44),
    ("PE", "PE", PI, 36),
    ("P0", "P0", P, 28),
    ("PB", "PB", P, 24),
    ("PA", "PA/+", P, 20),
    ("PC", "PC/-", P, 16),
    ("STO", "STO", IN, 6),
    ("DI3", "DI3", IN, 2),
    ("DI1", "DI1", IN, -2),
    ("COM", "COM", PI, -6),
    ("R1A", "R1A", P, -14),
    ("R1B", "R1B", P, -18),
    ("R1C", "R1C", P, -22),
    ("R2A", "R2A", P, -28),
    ("R2C", "R2C", P, -32),
    ("P24", "P24", P, -38),
    ("RJA", "RJ45 D+ TBC", P, -46),
    ("RJB", "RJ45 D- TBC", P, -50),
]
ATV_R = [
    ("U", "U", P, 52),
    ("V", "V", P, 48),
    ("W", "W", P, 44),
    ("PE2", "PE", PI, 36),
]
block("ATV", "A", ATV_L, ATV_R, "ATV320")

REV_L = [
    ("24", "X4 24V TBC", PI, 16),
    ("0", "X4 0V TBC", PI, 12),
    ("NC", "X4 NC TBC", P, 8),
    ("FG", "X4 FG TBC", PI, 4),
    ("GND", "485 GND TBC", P, -4),
    ("N", "485 N", P, -8),
    ("P", "485 P", P, -12),
]
REV_R = [
    ("ETH0", "ETH0", P, 12),
    ("ETH1", "ETH1", P, 8),
    ("BR", "PiBridge", P, 0),
]
block("REVPI", "A", REV_L, REV_R, "RevPi")

DIO_L = [
    ("X2_1", "X2-1 24VI", PI, 44),
    ("X2_2", "X2-2 0VI", PI, 40),
    ("X2_3", "X2-3 0VO", PI, 36),
    ("X2_4", "X2-4 24VO", PI, 32),
    ("X4_1", "X4-1 24V TBC", PI, 24),
    ("X4_2", "X4-2 0V TBC", PI, 20),
    ("X4_3", "X4-3 NC TBC", P, 16),
    ("X4_4", "X4-4 FG TBC", PI, 12),
] + [(f"I{i}", f"I{i}", IN, 4 - (i - 1) * 4) for i in range(1, 15)]
DIO_R = [("BR", "PiBridge", P, 44)] + [(f"O{i}", f"O{i}", OT, 36 - (i - 1) * 4) for i in range(1, 15)]
block("DIO", "A", DIO_L, DIO_R, "DIO")

NANO_L = [
    ("a1", "GND", PI, 16),
    ("a2", "+Ub", PI, 12),
    ("a3", "DI1", P, 8),
    ("a4", "DI2", P, 4),
    ("a5", "DI3", P, 0),
    ("a6", "AIN", P, -4),
    ("a7", "DO1", P, -8),
    ("a8", "DO2", P, -12),
]
NANO_R = [
    ("b1", "GND", PI, 16),
    ("b2", "+10V", P, 12),
    ("b3", "-Rel", P, 8),
    ("b4", "+Rel", IN, 4),
    ("b5", "-Dir", P, 0),
    ("b6", "+Dir", IN, -4),
    ("b7", "-Clk", P, -8),
    ("b8", "+Clk", IN, -12),
]
block("NANO", "A", NANO_L, NANO_R, "PD2", extra=[Pin("USB", "USB", 0, -22, 90, P)])

RUT_L = [
    ("1", "1 +V", PI, 8),
    ("2", "2 0V", PI, 4),
    ("3", "3 DIN", P, 0),
    ("4", "4 DOUT", P, -4),
]
RUT_R = [
    ("LAN", "LAN", P, 6),
    ("ANT", "ANT", P, 0),
]
block("RUT", "A", RUT_L, RUT_R, "RUT241")
