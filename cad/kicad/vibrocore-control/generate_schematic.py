#!/usr/bin/env python3
"""Generate the Vibrocore cabinet schematic (KiCad 8).

Symbols are IEC graphics or device blocks with the printed terminal names.
Wires are real segments. A global label is used only when the net leaves the sheet.
"""

from __future__ import annotations

import argparse
import filecmp
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from schlib import IN, OT, PI, PO, SYMS, Sym, f, pin_sexpr, q

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXPORT = ROOT / "cad" / "export" / "kicad"
PROJECT = "vibrocore-control"
NS = uuid.UUID("6d5c1b2a-7e10-5a31-9c44-0b1a6e2f1301")

IO_NETS = (
    "460_LIM_UP", "461_LIM_DN", "420_ESTOP", "421_PNOZ", "440_S200FB", "452_SONSTO",
    "462_ENABLE", "470_TILT_V", "471_TILT_F", "472_LIFT_D", "473_LIFT_R", "451_FAULT",
    "480_INDEX", "490_EXT", "491_RET", "492_TILTV", "493_TILTF", "494_BEACON",
    "450_RESET", "495_ROT_EN", "431_STO1", "433_STO2", "201_24S", "211_24C", "001_0V",
)


def uid(name: str) -> str:
    return str(uuid.uuid5(NS, name))


@dataclass
class Inst:
    ref: str
    sym: str
    x: int
    y: int
    value: str
    unit: int = 1
    in_bom: bool = True
    hide_value: bool = False
    hide_ref: bool = False
    ref_dx: int = 0
    ref_dy: int = -8
    val_dx: int = 0
    val_dy: int = 8


@dataclass
class Sheet:
    filename: str
    title: str
    page: str
    insts: list[Inst] = field(default_factory=list)
    wires: list[tuple[str, list[tuple[int, int]]]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    texts: list[tuple[int, int, str]] = field(default_factory=list)
    dashes: list[tuple[tuple[int, int], tuple[int, int]]] = field(default_factory=list)
    note_at: tuple[int, int] = (12, 188)
    rail_x: list[tuple[str, int]] = field(default_factory=list)
    rail_y: list[tuple[str, int]] = field(default_factory=list)

    def place(self, ref: str, sym: str, x: int, y: int, value: str, unit: int = 1, **kw) -> Inst:
        symbol = SYMS[sym]
        ys = [pin.y for pin in symbol.pins if pin.unit == unit]
        span = (max(abs(v) for v in ys) if ys else 4) + 4
        inst = Inst(
            ref, sym, x, y, value, unit,
            in_bom=kw.get("in_bom", symbol.in_bom),
            hide_value=kw.get("hide_value", False),
            hide_ref=kw.get("hide_ref", False),
            ref_dx=kw.get("ref_dx", 0),
            ref_dy=kw.get("ref_dy", -(span + 2)),
            val_dx=kw.get("val_dx", 0),
            val_dy=kw.get("val_dy", span + 3),
        )
        self.insts.append(inst)
        return inst

    def place_pin(self, ref: str, sym: str, pin: str, ax: int, ay: int, value: str, unit: int = 1, **kw) -> Inst:
        found = SYMS[sym].pin(pin, unit)
        return self.place(ref, sym, ax - found.x, ay + found.y, value, unit, **kw)

    def pin(self, ref: str, num: str) -> tuple[int, int]:
        for inst in self.insts:
            if inst.ref != ref:
                continue
            for pin in SYMS[inst.sym].pins:
                if pin.num == num and pin.unit == inst.unit:
                    return (inst.x + pin.x, inst.y - pin.y)
        raise KeyError(f"{self.filename} {ref} pin {num}")

    def resolve(self, node):
        if isinstance(node, tuple) and len(node) == 2 and isinstance(node[0], str):
            return self.pin(node[0], node[1])
        return node

    def wire(self, net: str, *pts: tuple[int, int]) -> None:
        clean = [pts[0]]
        for pt in pts[1:]:
            if pt != clean[-1]:
                clean.append(pt)
        if len(clean) < 2:
            return
        for left, right in zip(clean, clean[1:]):
            if left[0] != right[0] and left[1] != right[1]:
                raise SystemExit(f"{self.filename} {net} bend is not orthogonal {left} {right}")
        self.wires.append((net, clean))

    def join(self, net: str, *nodes) -> None:
        pts = [self.resolve(node) for node in nodes]
        seq = [pts[0]]
        for pt in pts[1:]:
            last = seq[-1]
            if last == pt:
                continue
            if last[0] != pt[0] and last[1] != pt[1]:
                seq.append((pt[0], last[1]))
            if seq[-1] != pt:
                seq.append(pt)
        self.wire(net, *seq)

    def link(self, net: str, a, b) -> None:
        self.join(net, a, b)

    def hrail(self, net: str, y: int, nodes) -> None:
        drops = []
        xs = []
        for node in nodes:
            px, py = self.resolve(node)
            xs.append(px)
            if py != y:
                drops.append((px, py))
        self.rail_y.append((net, y))
        xs = sorted(set(xs))
        for left, right in zip(xs, xs[1:]):
            self.wire(net, (left, y), (right, y))
        for px, py in drops:
            self.wire(net, (px, y), (px, py))

    def vrail(self, net: str, x: int, nodes) -> None:
        drops = []
        ys = []
        for node in nodes:
            px, py = self.resolve(node)
            ys.append(py)
            if px != x:
                drops.append((px, py))
        self.rail_x.append((net, x))
        ys = sorted(set(ys))
        for top, bot in zip(ys, ys[1:]):
            self.wire(net, (x, top), (x, bot))
        for px, py in drops:
            self.wire(net, (x, py), (px, py))

    def stub(self, net: str, node, dx: int = 0, dy: int = 0) -> None:
        px, py = self.resolve(node)
        end = (px + dx, py + dy)
        if end == (px, py):
            raise SystemExit(f"zero stub {net}")
        self.wire(net, (px, py), end)

    def text(self, x: int, y: int, text: str) -> None:
        self.texts.append((x, y, text))

    def dash(self, ref: str) -> None:
        centers = [(inst.x, inst.y) for inst in self.insts if inst.ref == ref]
        centers.sort()
        for left, right in zip(centers, centers[1:]):
            self.dashes.append((left, right))


def pair(sheet: Sheet, ref: str, sym: str, x: int, y: int, value: str, dx: int = 20) -> None:
    sheet.place_pin(ref, sym, "1", x, y, value, unit=1, val_dx=dx + 8, val_dy=-10, ref_dy=-10)
    sheet.place_pin(ref, sym, "3", x + dx, y, value, unit=2, hide_value=True, ref_dy=-10)
    sheet.dash(ref)


# --- terminal and cable tables -------------------------------------------------

SPEC = {
    "100_L": "6 mm2", "101_N": "6 mm2", "102_PE": "6 mm2", "001_0V": "2.5 mm2",
    "610_UA": "1.5 mm2", "611_VA": "1.5 mm2", "612_WA": "1.5 mm2",
    "620_UB": "1.5 mm2", "621_VB": "1.5 mm2", "622_WB": "1.5 mm2",
    "540_U": "1.5 mm2", "541_V": "1.5 mm2", "542_W": "1.5 mm2",
    "510_ENC": "catalogue encoder cable", "543_BRP": "0.75 mm2", "544_BRN": "0.75 mm2",
    "211_24C": "1.0 mm2", "500_24R": "0.75 mm2",
    "498_ACT_A": "1.5 mm2, current TBC", "499_ACT_B": "1.5 mm2, current TBC",
    "550_LIFTP": "section TBC", "551_LIFTN": "section TBC",
}


def spec_of(wire: str) -> str:
    return SPEC.get(wire, "0.75 mm2")


TERMINALS: list[tuple[str, str, str, str, str]] = []


def add_term(strip: str, pin: str, wire: str, function: str, note: str) -> None:
    TERMINALS.append((strip, pin, wire, function, note + " " + spec_of(wire)))


add_term("X1", "1", "100_L", "L", "Supply L. Block print is not chosen.")
add_term("X1", "2", "101_N", "N", "Supply N.")
add_term("X1", "3", "102_PE", "PE", "Supply PE.")
add_term("X1", "4", "001_0V", "0V", "0 V star. W1 bonds this point to PE.")
add_term("X2", "1", "610_UA", "U", "Motor A, straight phase order.")
add_term("X2", "2", "611_VA", "V", "Motor A.")
add_term("X2", "3", "612_WA", "W", "Motor A.")
add_term("X2", "4", "102_PE", "PE", "Motor A PE.")
add_term("X3", "1", "620_UB", "U", "Motor B.")
add_term("X3", "2", "622_WB", "V", "Cabinet W lands on motor V.")
add_term("X3", "3", "621_VB", "W", "Cabinet V lands on motor W.")
add_term("X3", "4", "102_PE", "PE", "Motor B PE.")
add_term("X4", "1", "540_U", "U", "1FL2104 power. Siemens cable order is TODO.")
add_term("X4", "2", "541_V", "V", "1FL2104 power.")
add_term("X4", "3", "542_W", "W", "1FL2104 power.")
add_term("X4", "4", "102_PE", "PE", "1FL2104 PE.")
add_term("X5", "1", "510_ENC", "ENC", "One catalogue cable. Core map is on sheet 03.")
add_term("X5", "2", "102_PE", "SH", "Shield. Land the shield at one end only.")
add_term("X6", "1", "543_BRP", "BR+", "Brake pair to S200 X108 pin 2.")
add_term("X6", "2", "544_BRN", "BR-", "Brake pair to S200 X108 pin 1.")
add_term("X7", "1", "460_LIM_UP", "LIM_UP", "Field signal.")
add_term("X7", "2", "461_LIM_DN", "LIM_DN", "Field signal.")
add_term("X7", "3", "462_ENABLE", "ENABLE", "Enabling switch. Not in the PNOZ.")
add_term("X7", "4", "480_INDEX", "INDEX", "Index sensor. Order code is OPEN.")
add_term("X7", "5", "470_TILT_V", "TILT_V", "Tilt limit.")
add_term("X7", "6", "471_TILT_F", "TILT_F", "Tilt limit.")
add_term("X7", "7", "472_LIFT_D", "LIFT_D", "Lift deployed, two NC in series.")
add_term("X7", "8", "473_LIFT_R", "LIFT_R", "Lift retracted, two NC in series.")
add_term("X7", "9", "494_BEACON", "BEACON", "Beacon, 24 V, 0.5 A maximum.")
add_term("X7", "10", "211_24C", "+24", "Field 24 V.")
add_term("X7", "11", "001_0V", "0V", "Field 0 V.")
add_term("X7", "12", "102_PE", "PE", "Field PE.")
add_term("X8", "1", "498_ACT_A", "A", "Tilt motor lead. Current is TBC.")
add_term("X8", "2", "499_ACT_B", "B", "Tilt motor lead. Current is TBC.")
add_term("X8", "3", "470_TILT_V", "LIM_V", "Integrated limit name is TODO.")
add_term("X8", "4", "471_TILT_F", "LIM_F", "Integrated limit name is TODO.")
add_term("X8", "5", "211_24C", "+24", "Tilt 24 V.")
add_term("X8", "6", "001_0V", "0V", "Tilt 0 V.")
add_term("X9", "1", "500_24R", "+24", "Proposal. Not released.")
add_term("X9", "2", "001_0V", "0V", "Proposal.")
add_term("X9", "3", "495_ROT_EN", "ENA", "DIO output 7 to +Release.")
add_term("X9", "4", "530_CLKP", "CLK+", "Single-ended clock to b8.")
add_term("X9", "5", "531_CLKN", "CLK-", "Park on 0 V. Do not land on b7.")
add_term("X9", "6", "532_DIRP", "DIR+", "Single-ended direction to b6.")
add_term("X9", "7", "533_DIRN", "DIR-", "Park on 0 V. Do not land on b5.")
add_term("X9", "8", "102_PE", "PE", "Cable shield. Drive PE screw is TBC.")
add_term("X10", "1", "550_LIFTP", "M+", "Lift. Section is TBC.")
add_term("X10", "2", "551_LIFTN", "M-", "Lift. Section is TBC.")
add_term("X10", "3", "211_24C", "+24", "Lift logic supply.")
add_term("X10", "4", "001_0V", "0V", "Lift 0 V.")

CABLES = [
    ("W-MAINS", "VC-PW-5600", "Instagrid", "X1", "3G6 mm2, 15.7 A", "no", "PE is 6 mm2."),
    ("W-SON-A", "VC-SH-1700", "X2", "M2", "4G1.5 mm2 shielded, 1.45 A", "yes", "Straight phases. Shield at the drive."),
    ("W-SON-B", "VC-SH-1700", "X3", "M3", "4G1.5 mm2 shielded, 1.45 A", "yes", "V and W are swapped at X3."),
    ("W-HUB-P", "VC-HB-3440", "X4 and X6", "M1", "4G1.5 mm2 shielded plus 2x0.75 mm2 brake", "no", "Siemens order code is TODO."),
    ("W-HUB-E", "VC-HB-3450", "X5", "M1 encoder", "Catalogue encoder cable", "no", "Siemens order code is TODO."),
    ("W-STO", "VC-CT-6730", "K1", "A2 and A3", "2x0.75 mm2 per channel", "no", "Do not mix the two channels in one pair."),
    ("W-IO", "VC-CT-6740", "X7 and X8", "Field devices", "0.75 mm2", "part", "24 V field feed is 1.0 mm2."),
    ("W-ETH", "VC-CT-6750", "A4 ETH0", "A7 LAN", "Cat5e patch", "no", "Length assumed 0.5 m."),
    ("W-485", "VC-CT-6760", "A4", "A3 then A2", "Shielded pair 0.75 mm2", "no", "120 ohm at the S200. Shield to PE at the RevPi only."),
    ("W-ROT", "VC-CT-6770", "X9", "A6", "0.75 mm2", "yes", "Proposal. Not on the live BOM."),
    ("W-TILT", "VC-CT-6740", "X8", "M4", "1.5 mm2 power TBC, 0.75 mm2 limits", "no", "Actuator current is not confirmed."),
    ("W-LIFT", "VC-LT-9120", "X10 and X7", "M5 and M6", "Section TBC", "no", "Nameplate current is not known."),
    ("W-GNSS", "VC-CT-6500", "Head", "Receiver", "Antenna cable", "yes", "Runs in VC-HB-3430."),
    ("W-CHAIN", "VC-HB-3430", "Frame", "Carriage", "igus 2400.05.075.0", "yes", "Bend radius 75 mm. Length for 1300 mm stroke is TODO."),
]


def main() -> None:
    from draw_sheets import sheet_names, write_lists, write_tree

    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Compare a fresh tree with the files in git")
    args = parser.parse_args()
    if args.check:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            write_tree(tmp_path)
            write_lists(tmp_path / "lists")
            names = [
                "vibrocore.kicad_sym",
                "sym-lib-table",
                "vibrocore-control.kicad_sch",
                "vibrocore-control.kicad_pro",
                *sheet_names(),
            ]
            bad = [name for name in names if not filecmp.cmp(tmp_path / name, OUT / name, shallow=False)]
            for name in ("terminal-list.csv", "terminal-list.md", "cable-list.csv", "cable-list.md"):
                if not filecmp.cmp(tmp_path / "lists" / name, EXPORT / name, shallow=False):
                    bad.append("lists/" + name)
            if bad:
                raise SystemExit("Schematic is stale:\n- " + "\n- ".join(bad))
        print("Schematic matches the generator.")
        return
    write_tree(OUT)
    write_lists(EXPORT)
    print(f"Wrote schematic in {OUT}")


if __name__ == "__main__":
    main()


