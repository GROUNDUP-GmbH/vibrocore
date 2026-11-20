#!/usr/bin/env python3
"""Generate the Vibrocore cabinet schematic (KiCad 8).

Wire numbers are global labels. The same label on two sheets is one net.
Terminal and cable lists are written from the same tables as the sheets.
"""

from __future__ import annotations

import argparse
import filecmp
import uuid
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXPORT = ROOT / "cad" / "export" / "kicad"
PROJECT = "vibrocore-control"
NS = uuid.UUID("6d5c1b2a-7e10-5a31-9c44-0b1a6e2f1301")


def uid(name: str) -> str:
    return str(uuid.uuid5(NS, name))


def f(steps: int) -> str:
    value = steps * 127
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


@dataclass
class Pin:
    num: str
    name: str
    x: int
    y: int
    angle: int
    etype: str


@dataclass
class Sym:
    name: str
    prefix: str
    pins: list[Pin]
    hw: int
    hh: int
    in_bom: bool = True


@dataclass
class Dev:
    ref: str
    sym: str
    x: int
    y: int
    value: str
    nets: dict[str, str | None]


def _ys(count: int) -> list[int]:
    if count <= 0:
        return []
    top = (count - 1) * 2
    return [top - 4 * i for i in range(count)]


def make_box(name: str, prefix: str, left: list[tuple], right: list[tuple], in_bom: bool = True) -> Sym:
    hw, length = 12, 2
    pins: list[Pin] = []
    for (num, pname, etype), y in zip(left, _ys(len(left))):
        pins.append(Pin(str(num), pname, -(hw + length), y, 180, etype))
    for (num, pname, etype), y in zip(right, _ys(len(right))):
        pins.append(Pin(str(num), pname, hw + length, y, 0, etype))
    span = max((abs(pin.y) for pin in pins), default=4)
    return Sym(name, prefix, pins, hw, span + 4, in_bom)


def make_pairs(name: str, prefix: str, rows: list[tuple[str, str, str, str]]) -> Sym:
    """rows: (left_num, left_name, right_num, right_name), one contact per row."""
    hw, length = 12, 2
    pins: list[Pin] = []
    for (nl, namel, nr, namer), y in zip(rows, _ys(len(rows))):
        pins.append(Pin(nl, namel, -(hw + length), y, 180, "passive"))
        pins.append(Pin(nr, namer, hw + length, y, 0, "passive"))
    span = max(abs(pin.y) for pin in pins)
    return Sym(name, prefix, pins, hw, span + 4, True)


SYMS: dict[str, Sym] = {}


def add(sym: Sym) -> None:
    SYMS[sym.name] = sym


P = "passive"
PI = "power_in"
PO = "power_out"
IN = "input"
OT = "output"

add(make_box("SRC", "G", [], [("1", "L", P), ("2", "N", P), ("3", "PE", P)]))
add(make_box("ISO", "Q", [("1", "L1", P), ("2", "N1", P)], [("3", "L2", P), ("4", "N2", P)]))
add(make_box("RCD", "QF", [("1", "L1", P), ("2", "N1", P)], [("3", "L2", P), ("4", "N2", P)]))
add(make_box("MCB", "F", [("1", "L1", P), ("2", "N1", P)], [("3", "L2", P), ("4", "N2", P)]))
add(make_box("FUSE", "F", [("1", "IN", P)], [("2", "OUT", P)]))
add(make_box("PSU_S", "G", [("1", "L", P), ("2", "N", P), ("3", "PE", P)], [("4", "+24", PO), ("5", "0V", PO)]))
add(make_box("PSU_C", "G", [("1", "L", P), ("2", "N", P), ("3", "PE", P)], [("4", "+24", PO), ("5", "0V", P)]))
add(make_box("FLAG", "PF", [("1", "PWR", PO)], [], in_bom=False))
add(make_box("BOND", "W", [("1", "0V", P)], [("2", "PE", P)], in_bom=False))
add(make_pairs("ESTOP", "S", [("11", "NC1a", "12", "NC1b"), ("21", "NC2a", "22", "NC2b"), ("31", "NC3a", "32", "NC3b")]))
add(make_pairs("NO", "S", [("1", "a", "2", "b")]))
add(make_pairs("NC", "S", [("1", "a", "2", "b")]))
add(make_box(
    "PNOZ", "K",
    [("A1", "A1", PI), ("A2", "A2", PI), ("S11", "S11", P), ("S12", "S12", P), ("S21", "S21", P), ("S22", "S22", P), ("S34", "S34", P)],
    [("13", "13", P), ("14", "14", P), ("23", "23", P), ("24", "24", P), ("33", "33", P), ("34", "34", P), ("41", "41", P), ("42", "42", P), ("Y32", "Y32", P)],
))
add(make_box(
    "S200", "A",
    [("1", "L", P), ("2", "N", P), ("3", "PE", P), ("4", "X124+", PI), ("5", "X124-", PI),
     ("6", "STO1+", IN), ("7", "STO1-", P), ("8", "STO2+", IN), ("9", "STO2-", P), ("10", "X130", OT)],
    [("11", "U", P), ("12", "V", P), ("13", "W", P), ("14", "PE", P), ("15", "BR+", P), ("16", "BR-", P),
     ("17", "X120", P), ("18", "PULS+", IN), ("19", "PULS-", IN), ("20", "SIGN+", IN), ("21", "SIGN-", IN),
     ("22", "A", P), ("23", "B", P)],
))
add(make_box(
    "M_HUB", "M",
    [("1", "U", P), ("2", "V", P), ("3", "W", P), ("4", "PE", P), ("5", "BR+", P), ("6", "BR-", P), ("7", "ENC", P)],
    [],
))
add(make_box("M_AC", "M", [("1", "U", P), ("2", "V", P), ("3", "W", P), ("4", "PE", P)], []))
add(make_box(
    "ATV", "A",
    [("1", "L", P), ("2", "N", P), ("3", "PE", P), ("4", "STO", IN), ("5", "LI3", IN), ("6", "LI1", IN),
     ("7", "COM", PI), ("8", "R1A", P), ("9", "R1B", P), ("10", "R1C", P),
     ("11", "LI2", P), ("12", "LI4", P), ("13", "LI5", P), ("14", "LI6", P), ("15", "P24", P)],
    [("16", "U", P), ("17", "V", P), ("18", "W", P), ("19", "PE", P), ("20", "A", P), ("21", "B", P),
     ("22", "R2A", P), ("23", "R2C", P)],
))
add(make_box(
    "MPROT", "F",
    [("1", "U1", P), ("2", "V1", P), ("3", "W1", P)],
    [("4", "U2", P), ("5", "V2", P), ("6", "W2", P)],
))
add(make_box(
    "REVPI", "A",
    [("1", "+24", PI), ("2", "0V", PI), ("3", "PE", P), ("4", "A", P), ("5", "B", P)],
    [("6", "ETH0", P), ("7", "ETH1", P), ("8", "BRIDGE", P)],
))
_dio_l = [("P", "+24", PI), ("M", "0V", PI), ("PE", "PE", P)] + [(str(i), f"I{i}", IN) for i in range(1, 15)]
_dio_r = [("B", "BRIDGE", P)] + [(f"O{i}", f"O{i}", OT) for i in range(1, 15)]
add(make_box("DIO", "A", _dio_l, _dio_r))
add(make_box("PNP", "B", [("1", "+24", PI), ("2", "0V", PI)], [("3", "OUT", OT)]))
add(make_box("LAMP", "H", [("1", "A", P), ("2", "B", P)], []))
add(make_box(
    "REL", "K",
    [("A1", "A1", P), ("A2", "A2", P)],
    [("11", "11", P), ("12", "12", P), ("14", "14", P), ("21", "21", P), ("22", "22", P), ("24", "24", P)],
))
add(make_box("DIODE", "D", [("A", "A", P)], [("K", "K", P)]))
add(make_box("ACT", "M", [("1", "A", P), ("2", "B", P)], []))
add(make_box(
    "HBR", "A",
    [("1", "+24", PI), ("2", "0V", PI), ("3", "EXT", IN), ("4", "RET", IN)],
    [("5", "M+", P), ("6", "M-", P)],
))
add(make_box(
    "NANO", "A",
    [("1", "+24", PI), ("2", "0V", PI), ("3", "PE", P), ("4", "ENA", IN), ("5", "USB", P)],
    [("6", "CLK+", IN), ("7", "CLK-", IN), ("8", "DIR+", IN), ("9", "DIR-", IN)],
))
add(make_box("PULSE", "U", [], [("1", "P+", OT), ("2", "P-", OT), ("3", "D+", OT), ("4", "D-", OT)], in_bom=False))
add(make_box("RUT", "A", [("1", "+24", PI), ("2", "0V", PI), ("3", "PE", P)], [("4", "LAN", P), ("5", "LTE", P)]))
add(make_box("RES", "R", [("1", "1", P)], [("2", "2", P)]))


def terminal(name: str, rows: list[tuple[str, str, str]]) -> None:
    left = [(num, label, P) for num, label, _net in rows]
    add(make_box(name, "X", left, []))


# strip, pin, wire, function
TERMINALS: list[tuple[str, str, str, str, str]] = []


def strip(ref: str, rows: list[tuple[str, str, str]], note: str) -> dict[str, str]:
    terminal(ref, rows)
    nets = {}
    for num, label, net in rows:
        TERMINALS.append((ref, num, net, label, note))
        nets[num] = net
    return nets


X1 = strip("X1", [("1", "L", "100_L"), ("2", "N", "101_N"), ("3", "PE", "102_PE"), ("4", "0V", "001_0V")],
           "Names are this drawing. The block print is not chosen.")
X2 = strip("X2", [("1", "U", "610_UA"), ("2", "V", "611_VA"), ("3", "W", "612_WA"), ("4", "PE", "102_PE")],
           "Motor A, straight phase order.")
X3 = strip("X3", [("1", "U", "620_UB"), ("2", "V", "622_WB"), ("3", "W", "621_VB"), ("4", "PE", "102_PE")],
           "Motor B. Cabinet V lands on motor W. Cabinet W lands on motor V.")
X4 = strip("X4", [("1", "U", "540_U"), ("2", "V", "541_V"), ("3", "W", "542_W"), ("4", "PE", "102_PE")],
           "1FL2104 power. Cable order code is TODO.")
X5 = strip("X5", [("1", "ENC", "510_ENC"), ("2", "SH", "102_PE")],
           "Encoder is one catalogue cable. Core names are not confirmed.")
X6 = strip("X6", [("1", "BR+", "543_BRP"), ("2", "BR-", "544_BRN")],
           "Brake pair to S200 X108. The RevPi does not drive this coil.")
X7 = strip("X7", [
    ("1", "LIM_UP", "460_LIM_UP"), ("2", "LIM_DN", "461_LIM_DN"), ("3", "ENABLE", "462_ENABLE"),
    ("4", "INDEX", "480_INDEX"), ("5", "TILT_V", "470_TILT_V"), ("6", "TILT_F", "471_TILT_F"),
    ("7", "LIFT_D", "472_LIFT_D"), ("8", "LIFT_R", "473_LIFT_R"), ("9", "BEACON", "494_BEACON"),
    ("10", "+24", "211_24C"), ("11", "0V", "001_0V"), ("12", "PE", "102_PE"),
], "Field signals. Pin numbers are this drawing.")
X8 = strip("X8", [
    ("1", "A", "498_ACT_A"), ("2", "B", "499_ACT_B"), ("3", "LIM_V", "470_TILT_V"),
    ("4", "LIM_F", "471_TILT_F"), ("5", "+24", "211_24C"), ("6", "0V", "001_0V"),
], "Tilt actuator. Integrated limit names are TODO.")
X9 = strip("X9", [
    ("1", "+24", "500_24R"), ("2", "0V", "001_0V"), ("3", "ENA", "495_ROT_EN"),
    ("4", "CLK+", "530_CLKP"), ("5", "CLK-", "531_CLKN"), ("6", "DIR+", "532_DIRP"),
    ("7", "DIR-", "533_DIRN"), ("8", "PE", "102_PE"),
], "Proposed rotation drive. Not a released selection.")
X10 = strip("X10", [("1", "M+", "550_LIFTP"), ("2", "M-", "551_LIFTN"), ("3", "+24", "211_24C"), ("4", "0V", "001_0V")],
            "Lift actuators. The H-bridge is VC-LT-9110.")


@dataclass
class Sheet:
    filename: str
    title: str
    page: str
    devs: list[Dev] = field(default_factory=list)
    notes: str = ""


def dev(ref: str, sym: str, x: int, y: int, value: str, **nets: str | None) -> Dev:
    symbol = SYMS[sym]
    missing = {pin.num for pin in symbol.pins} ^ set(nets)
    if missing:
        raise SystemExit(f"{ref} pin map does not match {sym}: {sorted(missing)}")
    return Dev(ref, sym, x, y, value, {key: nets[key] for key in nets})


def build_sheets() -> list[Sheet]:
    power = Sheet("01-power.kicad_sch", "01 Mains and 24 V", "2", notes="\n".join([
        "Instagrid ONE max is the only AC source.",
        "Q1 does not switch PE. QF1 is type B, 30 mA.",
        "Both 0 V rails meet at X1:4. W1 is the only bond to PE.",
        "Confirm that bond in the S200 PTI manual.",
        "SDR-120-24 feeds only S200 X124. The brake driver is inside the drive.",
        "VC-PW-5200, the 48 V supply, is not on this drawing.",
    ]))
    power.devs = [
        dev("G0", "SRC", 40, 42, "VC-PW-5100 Instagrid", **{"1": "100_L", "2": "101_N", "3": "102_PE"}),
        dev("Q1", "ISO", 110, 42, "VC-PW-5700 isolator", **{"1": "100_L", "2": "101_N", "3": "110_L", "4": "111_N"}),
        dev("QF1", "RCD", 180, 42, "VC-PW-5720 type B", **{"1": "110_L", "2": "111_N", "3": "120_L", "4": "121_N"}),
        dev("F1", "MCB", 250, 42, "VC-PW-5710 C20", **{"1": "120_L", "2": "121_N", "3": "130_L", "4": "131_N"}),
        dev("F2", "MCB", 40, 95, "VC-PW-5730 C16", **{"1": "130_L", "2": "131_N", "3": "140_L", "4": "141_N"}),
        dev("F3", "MCB", 110, 95, "VC-PW-5740 C16", **{"1": "130_L", "2": "131_N", "3": "150_L", "4": "151_N"}),
        dev("F4", "MCB", 180, 95, "VC-PW-5750 C4", **{"1": "130_L", "2": "131_N", "3": "160_L", "4": "161_N"}),
        dev("F5", "MCB", 250, 95, "VC-PW-5760 C10", **{"1": "130_L", "2": "131_N", "3": "170_L", "4": "171_N"}),
        dev("G1", "PSU_S", 40, 148, "VC-PW-5310 SDR-120-24", **{"1": "160_L", "2": "161_N", "3": "102_PE", "4": "200_24S", "5": "001_0V"}),
        dev("F14", "FUSE", 120, 145, "VC-PW-5800 6A", **{"1": "200_24S", "2": "201_24S"}),
        dev("PF1", "FLAG", 175, 145, "24V_S", **{"1": "201_24S"}),
        dev("W1", "BOND", 220, 150, "single 0V-PE bond", **{"1": "001_0V", "2": "102_PE"}),
        dev("X1", "X1", 305, 150, "mains 0V PE", **X1),
        dev("G2", "PSU_C", 40, 188, "VC-PW-5210 SDR-480-24 slot", **{"1": "170_L", "2": "171_N", "3": "102_PE", "4": "210_24C", "5": "001_0V"}),
        dev("F24", "FUSE", 120, 185, "VC-PW-5810 20A", **{"1": "210_24C", "2": "211_24C"}),
        dev("PF2", "FLAG", 175, 185, "24V_C", **{"1": "211_24C"}),
    ]

    safety = Sheet("02-safety.kicad_sch", "02 E-stop and STO", "3", notes="\n".join([
        "Two NC channels go to the PNOZ. The third NC is DI2 only.",
        "Set the PNOZ for two channels, short detection, monitored reset.",
        "Confirm the rotary-switch mark in OM_PNOZ_s4.",
        "Contact 13-14 is STO channel 1 for both drives.",
        "Contact 23-24 is STO channel 2 for both drives.",
        "41-42 is the monitor. Do not use it in the safety path.",
        "33-34 is spare. Do not use it for a normal load.",
        "The RevPi only reads feedback.",
    ]))
    safety.devs = [
        dev("S1", "ESTOP", 50, 80, "VC-CT-6210 3x NC", **{
            "11": "410_S11", "12": "411_S12", "21": "412_S21", "22": "413_S22", "31": "211_24C", "32": "420_ESTOP"}),
        dev("S10", "NO", 50, 150, "VC-CT-6270 reset", **{"1": "411_S12", "2": "414_S34"}),
        dev("K1", "PNOZ", 150, 90, "VC-CT-6220 750104", **{
            "A1": "211_24C", "A2": "001_0V", "S11": "410_S11", "S12": "411_S12", "S21": "412_S21", "S22": "413_S22",
            "S34": "414_S34", "13": "430_F30", "14": "431_STO1", "23": "432_F31", "24": "433_STO2",
            "33": None, "34": None, "41": "211_24C", "42": "421_PNOZ", "Y32": None}),
        dev("F30", "FUSE", 250, 70, "VC-PW-5820 2A", **{"1": "211_24C", "2": "430_F30"}),
        dev("F31", "FUSE", 250, 120, "VC-PW-5820 2A", **{"1": "211_24C", "2": "432_F31"}),
    ]

    hub = Sheet("03-hub.kicad_sch", "03 S200 and 1FL2", "4", notes="\n".join([
        "Order 6SL5510-1BB11-0AA0. X131 and X108 are the PTI standard drive.",
        "STO pin order is taken from the S200 PN sheet. Confirm the PTI sheet.",
        "X130 is the STO feedback. The terminal name on X130 is TODO.",
        "U1 is not a DIO pin. The pulse scale is TODO.",
        "The brake coil stays on X108. There is no second holding means.",
    ]))
    hub.devs = [
        dev("A2", "S200", 70, 100, "VC-HB-2300 S200", **{
            "1": "150_L", "2": "151_N", "3": "102_PE", "4": "201_24S", "5": "001_0V",
            "6": "431_STO1", "7": "001_0V", "8": "433_STO2", "9": "001_0V", "10": "440_S200FB",
            "11": "540_U", "12": "541_V", "13": "542_W", "14": "102_PE", "15": "543_BRP", "16": "544_BRN",
            "17": "510_ENC", "18": "520_PULSP", "19": "521_PULSN", "20": "522_SIGNP", "21": "523_SIGNN",
            "22": "910_A", "23": "911_B"}),
        dev("U1", "PULSE", 190, 55, "pulse source TODO", **{"1": "520_PULSP", "2": "521_PULSN", "3": "522_SIGNP", "4": "523_SIGNN"}),
        dev("M1", "M_HUB", 190, 145, "VC-HB-2100 1FL2104", **{
            "1": "540_U", "2": "541_V", "3": "542_W", "4": "102_PE", "5": "543_BRP", "6": "544_BRN", "7": "510_ENC"}),
        dev("X4", "X4", 300, 55, "motor power", **X4),
        dev("X5", "X5", 300, 110, "encoder", **X5),
        dev("X6", "X6", 300, 155, "brake", **X6),
    ]

    sonic = Sheet("04-sonic.kicad_sch", "04 ATV320 and two MVE", "5", notes="\n".join([
        "One ATV320 output feeds both OLI motors.",
        "Motor B swaps V and W so the motors turn in opposite directions.",
        "F21 and F22 must tolerate a PWM output. The order code is open.",
        "STO uses the drive STO pin and LI3. Do not link P24 to the cabinet 24 V.",
        "Assign the second STO channel in SoMove. The parameter name is TODO.",
        "R2 is the STO monitor. The parameter is TODO. R1B opens on a fault.",
    ]))
    sonic.devs = [
        dev("A3", "ATV", 55, 105, "VC-SH-1210 ATV320", **{
            "1": "140_L", "2": "141_N", "3": "102_PE", "4": "431_STO1", "5": "433_STO2", "6": "450_RESET",
            "7": "001_0V", "8": "211_24C", "9": "451_FAULT", "10": None,
            "11": None, "12": None, "13": None, "14": None, "15": None,
            "16": "600_U", "17": "601_V", "18": "602_W", "19": "102_PE", "20": "910_A", "21": "911_B",
            "22": "211_24C", "23": "452_SONSTO"}),
        dev("F21", "MPROT", 165, 55, "VC-PW-5770 1.6A", **{
            "1": "600_U", "2": "601_V", "3": "602_W", "4": "610_UA", "5": "611_VA", "6": "612_WA"}),
        dev("M2", "M_AC", 235, 55, "VC-SH-1100 motor A", **{"1": "610_UA", "2": "611_VA", "3": "612_WA", "4": "102_PE"}),
        dev("X2", "X2", 300, 55, "motor A", **X2),
        dev("F22", "MPROT", 165, 130, "VC-PW-5770 1.6A", **{
            "1": "600_U", "2": "601_V", "3": "602_W", "4": "620_UB", "5": "621_VB", "6": "622_WB"}),
        dev("M3", "M_AC", 235, 130, "VC-SH-1100 motor B", **{"1": "620_UB", "2": "622_WB", "3": "621_VB", "4": "102_PE"}),
        dev("X3", "X3", 300, 130, "motor B swapped", **X3),
    ]

    revpi = Sheet("05-revpi.kicad_sch", "05 RevPi Connect 4 and DIO", "6", notes="\n".join([
        "Controller 100378, 4 GB, no WLAN. DIO 100197.",
        "Channel numbers are the I/O list indexes. I1 is index 0.",
        "Spare pins are I14 and O8 to O14.",
        "The PFC200 is not on this drawing.",
        "Index sensor B1 is drawn as PNP. The order code is not chosen.",
        "The rotation index is this sensor. Sheet 07 does not repeat it.",
    ]))
    dio_nets: dict[str, str | None] = {
        "P": "211_24C", "M": "001_0V", "PE": "102_PE", "B": "940_BRIDGE",
        "1": "460_LIM_UP", "2": "461_LIM_DN", "3": "420_ESTOP", "4": "421_PNOZ",
        "5": "440_S200FB", "6": "452_SONSTO", "7": "462_ENABLE", "8": "470_TILT_V",
        "9": "471_TILT_F", "10": "472_LIFT_D", "11": "473_LIFT_R", "12": "451_FAULT",
        "13": "480_INDEX", "14": None,
        "O1": "490_EXT", "O2": "491_RET", "O3": "492_TILTV", "O4": "493_TILTF",
        "O5": "494_BEACON", "O6": "450_RESET", "O7": "495_ROT_EN",
    }
    for index in range(8, 15):
        dio_nets[f"O{index}"] = None
    revpi.devs = [
        dev("A4", "REVPI", 45, 42, "VC-CT-6800 100378", **{
            "1": "211_24C", "2": "001_0V", "3": "102_PE", "4": "910_A", "5": "911_B",
            "6": "930_ETH", "7": None, "8": "940_BRIDGE"}),
        dev("A5", "DIO", 115, 108, "VC-CT-6810 100197", **dio_nets),
        dev("S4", "NC", 220, 42, "VC-CT-6200 up", **{"1": "211_24C", "2": "460_LIM_UP"}),
        dev("S5", "NC", 220, 72, "VC-CT-6200 down", **{"1": "211_24C", "2": "461_LIM_DN"}),
        dev("S6", "NO", 220, 102, "VC-CT-6260 HE1B-M1", **{"1": "211_24C", "2": "462_ENABLE"}),
        dev("B1", "PNP", 220, 140, "VC-CT-6250 index", **{"1": "211_24C", "2": "001_0V", "3": "480_INDEX"}),
        dev("H1", "LAMP", 270, 170, "VC-CT-6230 beacon", **{"1": "494_BEACON", "2": "001_0V"}),
        dev("S14", "NC", 40, 188, "lift 1 deployed", **{"1": "211_24C", "2": "474_DMID"}),
        dev("S15", "NC", 95, 188, "lift 2 deployed", **{"1": "474_DMID", "2": "472_LIFT_D"}),
        dev("S16", "NC", 150, 188, "lift 1 retracted", **{"1": "211_24C", "2": "475_RMID"}),
        dev("S17", "NC", 205, 188, "lift 2 retracted", **{"1": "475_RMID", "2": "473_LIFT_R"}),
        dev("X7", "X7", 310, 100, "field I/O", **X7),
    ]

    tilt = Sheet("06-tilt.kicad_sch", "06 Tilt and lift", "7", notes="\n".join([
        "Each tilt coil is in series with the NC contact of the other relay.",
        "Off state: both motor leads are on 0 V.",
        "Do not command both directions.",
        "DI7 and DI8 are drawn as separate contacts. Confirm the actuator terminals.",
        "The actuator current is not on a nameplate.",
        "The lift H-bridge is VC-LT-9110. Its limits are on sheet 05.",
    ]))
    tilt.devs = [
        dev("K2", "REL", 55, 70, "VC-LT-9230 vertical", **{
            "A1": "496_K2", "A2": "001_0V", "11": "493_TILTF", "12": "497_K3", "14": None,
            "21": "498_ACT_A", "22": "001_0V", "24": "211_24C"}),
        dev("K3", "REL", 155, 70, "VC-LT-9230 fold", **{
            "A1": "497_K3", "A2": "001_0V", "11": "492_TILTV", "12": "496_K2", "14": None,
            "21": "499_ACT_B", "22": "001_0V", "24": "211_24C"}),
        dev("D2", "DIODE", 55, 145, "VC-CT-6780", **{"A": "001_0V", "K": "496_K2"}),
        dev("D3", "DIODE", 130, 145, "VC-CT-6780", **{"A": "001_0V", "K": "497_K3"}),
        dev("S7", "NC", 230, 50, "tilt vertical", **{"1": "211_24C", "2": "470_TILT_V"}),
        dev("S8", "NC", 230, 85, "tilt folded", **{"1": "211_24C", "2": "471_TILT_F"}),
        dev("M4", "ACT", 230, 130, "VC-LT-9200", **{"1": "498_ACT_A", "2": "499_ACT_B"}),
        dev("X8", "X8", 310, 100, "tilt", **X8),
        dev("A10", "HBR", 55, 185, "VC-LT-9110 lift", **{
            "1": "211_24C", "2": "001_0V", "3": "490_EXT", "4": "491_RET", "5": "550_LIFTP", "6": "551_LIFTN"}),
        dev("M5", "ACT", 160, 175, "VC-LT-9100 A", **{"1": "550_LIFTP", "2": "551_LIFTN"}),
        dev("M6", "ACT", 160, 205, "VC-LT-9100 B", **{"1": "550_LIFTP", "2": "551_LIFTN"}),
        dev("X10", "X10", 250, 190, "lift", **X10),
    ]

    rotation = Sheet("07-rotation.kicad_sch", "07 Rod rotation proposal", "8", notes="\n".join([
        "Nanotec PD2-C4118L1804-E-01 is a proposal. It is not released.",
        "This order code is USB, not Modbus. USB is a service plug.",
        "Clock and direction are not DIO pins. U2 is TODO.",
        "The enable bit is DIO output 6.",
        "The index sensor is B1 on sheet 05.",
        "24 V is inside the 12 V to 48 V range.",
    ]))
    rotation.devs = [
        dev("F6", "FUSE", 50, 70, "VC-PW-5790 2A", **{"1": "211_24C", "2": "500_24R"}),
        dev("PF3", "FLAG", 120, 70, "24V_R", **{"1": "500_24R"}),
        dev("A6", "NANO", 80, 150, "VC-CT-6280 proposal", **{
            "1": "500_24R", "2": "001_0V", "3": "102_PE", "4": "495_ROT_EN", "5": None,
            "6": "530_CLKP", "7": "531_CLKN", "8": "532_DIRP", "9": "533_DIRN"}),
        dev("U2", "PULSE", 200, 80, "clock source TODO", **{
            "1": "530_CLKP", "2": "531_CLKN", "3": "532_DIRP", "4": "533_DIRN"}),
        dev("X9", "X9", 280, 140, "rotation", **X9),
    ]

    network = Sheet("08-network.kicad_sch", "08 RUT241 and Modbus", "9", notes="\n".join([
        "RUT241 runs from the general 24 V rail. No 9 V converter.",
        "ETH0 of the RevPi goes to the router LAN port. ETH1 is service.",
        "Modbus slaves: 1 ATV320, 2 S200. Baud and parity are TODO.",
        "R1, 120 ohm, is drawn at the S200 end. Move it if the bus order changes.",
        "The rotation drive is not on this bus.",
    ]))
    network.devs = [
        dev("A7", "RUT", 60, 80, "VC-CT-6600 RUT241", **{
            "1": "211_24C", "2": "001_0V", "3": "102_PE", "4": "930_ETH", "5": None}),
        dev("R1", "RES", 180, 80, "VC-CT-6790 120R", **{"1": "910_A", "2": "911_B"}),
    ]
    return [power, safety, hub, sonic, revpi, tilt, rotation, network]


def sym_body(sym: Sym, prefixed: bool) -> str:
    parent = f"vibrocore:{sym.name}" if prefixed else sym.name
    bom = "yes" if sym.in_bom else "no"
    lines = [
        f'  (symbol {q(parent)}',
        "    (pin_names (offset 1.016))",
        "    (exclude_from_sim no)",
        f"    (in_bom {bom})",
        "    (on_board yes)",
        f'    (property "Reference" {q(sym.prefix)} (at 0 {f(-(sym.hh + 4))} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" {q(sym.name)} (at 0 {f(sym.hh + 4)} 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'    (symbol "{sym.name}_0_1"',
        f"      (rectangle (start {f(-sym.hw)} {f(-sym.hh)}) (end {f(sym.hw)} {f(sym.hh)})",
        "        (stroke (width 0.254) (type default)) (fill (type background)))",
        "    )",
        f'    (symbol "{sym.name}_1_1"',
    ]
    for pin in sym.pins:
        lines.append(
            f"      (pin {pin.etype} line (at {f(pin.x)} {f(pin.y)} {pin.angle}) (length 2.54)"
            f" (name {q(pin.name)} (effects (font (size 1.27 1.27))))"
            f" (number {q(pin.num)} (effects (font (size 1.27 1.27)))))"
        )
    lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)


def library_text() -> str:
    body = "\n".join(sym_body(sym, False) for sym in SYMS.values())
    return (
        "(kicad_symbol_lib\n"
        "  (version 20231120)\n"
        '  (generator "eeschema")\n'
        '  (generator_version "8.0")\n'
        f"{body}\n"
        ")\n"
    )


def embedded_library() -> str:
    return "\n".join(sym_body(sym, True) for sym in SYMS.values())


def emit_dev(item: Dev, sheet_path: str) -> str:
    sym = SYMS[item.sym]
    chunks = []
    for pin in sym.pins:
        net = item.nets[pin.num]
        wx = item.x + pin.x
        wy = item.y - pin.y
        if net is None:
            chunks.append(f"  (no_connect (at {f(wx)} {f(wy)}) (uuid {q(uid(item.ref + pin.num + 'nc'))}))")
            continue
        far = wx + (6 if pin.x > 0 else -6)
        chunks.append(
            f"  (wire (pts (xy {f(wx)} {f(wy)}) (xy {f(far)} {f(wy)}))"
            f" (stroke (width 0) (type default)) (uuid {q(uid(item.ref + pin.num + 'w'))}))"
        )
        angle = 0 if pin.x > 0 else 180
        justify = "left" if angle == 0 else "right"
        chunks.append(
            f"  (global_label {q(net)} (shape bidirectional) (at {f(far)} {f(wy)} {angle})"
            f" (effects (font (size 1.27 1.27)) (justify {justify}))"
            f" (uuid {q(uid(item.ref + pin.num + 'l'))}))"
        )
    pin_lines = "\n".join(
        f'    (pin {q(pin.num)} (uuid {q(uid(item.ref + pin.num + "p"))}))' for pin in sym.pins
    )
    ref_y = item.y - sym.hh - 6
    val_y = item.y + sym.hh + 8
    chunks.append(
        f"""  (symbol (lib_id {q("vibrocore:" + item.sym)}) (at {f(item.x)} {f(item.y)} 0)
    (unit 1) (exclude_from_sim no) (in_bom {"yes" if sym.in_bom else "no"}) (on_board yes) (dnp no)
    (uuid {q(uid(item.ref + "sym"))})
    (property "Reference" {q(item.ref)} (at {f(item.x)} {f(ref_y)} 0) (effects (font (size 1.27 1.27))))
    (property "Value" {q(item.value)} (at {f(item.x)} {f(val_y)} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {f(item.x)} {f(item.y)} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at {f(item.x)} {f(item.y)} 0) (effects (font (size 1.27 1.27)) hide))
{pin_lines}
    (instances (project {q(PROJECT)} (path {q(sheet_path)} (reference {q(item.ref)}) (unit 1))))
  )"""
    )
    return "\n".join(chunks)


def check_nets(sheets: list[Sheet]) -> None:
    types: dict[str, list[str]] = {}
    for sheet in sheets:
        for item in sheet.devs:
            sym = SYMS[item.sym]
            for pin in sym.pins:
                net = item.nets[pin.num]
                if net is None:
                    continue
                types.setdefault(net, []).append(pin.etype)
    errors = []
    for net, kinds in sorted(types.items()):
        if kinds.count(PO) > 1:
            errors.append(f"{net}: more than one power output")
        if PI in kinds and PO not in kinds:
            errors.append(f"{net}: power input is not driven")
        if IN in kinds and not any(kind in kinds for kind in (OT, P, PO)):
            errors.append(f"{net}: input is not driven")
        if kinds.count(OT) > 1:
            errors.append(f"{net}: two outputs")
    if errors:
        raise SystemExit("Net check failed:\n- " + "\n- ".join(errors))


def sheet_text(sheet: Sheet, sheet_uuid: str) -> str:
    path = "/" + sheet_uuid
    body = [emit_dev(item, path) for item in sheet.devs]
    notes = (
        f"  (text {q(sheet.notes)} (exclude_from_sim no) (at 10.16 12.70 0)"
        f" (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid(sheet.filename + 'note'))}))"
    )
    return f"""(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (generator_version "8.0")
  (uuid {q(uid(sheet.filename + 'file'))})
  (paper "A3")
  (title_block
    (title {q(sheet.title)})
    (date "2026-11-20")
    (rev "0A")
    (company "Ground UP GmbH")
    (comment 1 "Wire numbers are the global labels.")
    (comment 2 "VC-SCH-5000. Safety is hard-wired. The RevPi only reads feedback.")
  )
  (lib_symbols
{embedded_library()}
  )
{notes}
{chr(10).join(body)}
  (sheet_instances (path {q(path)} (page {q(sheet.page)})))
)
"""


def root_text(sheets: list[Sheet], uuids: dict[str, str], columns: tuple[str, str]) -> str:
    blocks = []
    for index, sheet in enumerate(sheets):
        y = 18 + index * 22
        su = uuids[sheet.filename]
        blocks.append(
            f"""  (sheet (at {f(16)} {f(y)} ) (size {f(100)} {f(16)})
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid {q(su)})
    (property "Sheetname" {q(sheet.title)} (at {f(16)} {f(y - 2)} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" {q(sheet.filename)} (at {f(16)} {f(y + 16)} 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances (project {q(PROJECT)} (path "/" (page {q(sheet.page)}))))
  )"""
        )
    intro = "\n".join([
        "Vibrocore cabinet schematic VC-SCH-5000.",
        "Controller: RevPi Connect 4, order 100378, plus DIO 100197.",
        "The PFC200 is not on this drawing.",
        "Safety: PNOZ s4 750104 drops STO on the S200 and on the ATV320.",
        "Global labels are the wire numbers. A label used on two sheets is one net.",
        "Cross references:",
    ])
    return f"""(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (generator_version "8.0")
  (uuid {q(uid('root'))})
  (paper "A3")
  (title_block
    (title "Vibrocore cabinet schematic")
    (date "2026-11-20")
    (rev "0A")
    (company "Ground UP GmbH")
    (comment 1 "VC-SCH-5000 sheet 01 of 09")
    (comment 2 "Hard-wired STO. RevPi reads feedback only.")
  )
  (lib_symbols)
  (text {q(intro)} (exclude_from_sim no) (at 160.02 15.24 0)
    (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid('root-intro'))}))
  (text {q(columns[0])} (exclude_from_sim no) (at 160.02 45.72 0)
    (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid('root-xref-a'))}))
  (text {q(columns[1])} (exclude_from_sim no) (at 290.83 45.72 0)
    (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid('root-xref-b'))}))
{chr(10).join(blocks)}
  (sheet_instances (path "/" (page "1")))
)
"""


def cross_reference(sheets: list[Sheet]) -> tuple[str, str]:
    where: dict[str, list[str]] = {}
    for sheet in sheets:
        page = sheet.title[:2]
        for item in sheet.devs:
            for net in item.nets.values():
                if not net:
                    continue
                pages = where.setdefault(net, [])
                if page not in pages:
                    pages.append(page)
    lines = [f"{net}  {' '.join(pages)}" for net, pages in sorted(where.items()) if len(pages) > 1]
    mid = (len(lines) + 1) // 2
    return "\n".join(lines[:mid]), "\n".join(lines[mid:])


CABLES = [
    ("W-MAINS", "VC-PW-5600", "Instagrid", "X1", "3G6, length TODO", "no", "Existing power cable set."),
    ("W-SON-A", "VC-SH-1700", "X2", "M2", "3x1.5 mm2 + PE, shielded", "yes", "Straight phases."),
    ("W-SON-B", "VC-SH-1700", "X3", "M3", "3x1.5 mm2 + PE, shielded", "yes", "V and W are swapped at X3."),
    ("W-HUB-P", "VC-HB-3440", "X4 and X6", "M1", "Power and brake pair", "no", "Siemens order code TODO. Brake ends on X108."),
    ("W-HUB-E", "VC-HB-3450", "X5", "M1 encoder", "Catalogue encoder cable", "no", "Connector pinout is the Siemens cable."),
    ("W-STO", "VC-CT-6730", "K1", "A2 and A3", "One twisted pair per STO channel", "no", "Do not mix the two channels in one pair."),
    ("W-IO", "VC-CT-6740", "X7 and X8", "Field devices", "0.5 mm2 or 0.75 mm2", "part", "Carriage limits and the head run in the energy chain."),
    ("W-ETH", "VC-CT-6750", "A4 ETH0", "A7 LAN", "Cat5e patch", "no", "Length assumed 0.5 m."),
    ("W-485", "VC-CT-6760", "A4", "A3 then A2", "Shielded twisted pair", "no", "120 ohm at the S200. Shield to PE at the RevPi only."),
    ("W-ROT", "VC-CT-6770", "X9", "A6", "24 V plus clock, direction, enable", "yes", "Proposal. Not on the live BOM."),
    ("W-TILT", "VC-CT-6740", "X8", "M4", "Two power cores and two limit cores", "no", "Actuator current is not confirmed."),
    ("W-LIFT", "VC-LT-9120", "X10 and X7", "M5 and M6", "Power pair and series NC limits", "no", "Existing lift wiring line."),
    ("W-GNSS", "VC-CT-6500", "Head", "Receiver", "Antenna cable", "yes", "Runs in VC-HB-3430."),
    ("W-CHAIN", "VC-HB-3430", "Frame", "Carriage", "igus 2400.05.075.0", "yes", "Bend radius 75 mm. Length for 1300 mm stroke is TODO."),
]


def write_lists(directory: Path) -> None:
    import csv

    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "terminal-list.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["strip", "pin", "wire", "function", "note"])
        writer.writerows(TERMINALS)
    md = ["# Terminal list", "", "Pin names are the names on this drawing.", "The purchased block is not chosen.", ""]
    md.append("| Strip | Pin | Wire | Function | Note |")
    md.append("| --- | --- | --- | --- | --- |")
    for ref, pin, wire, func, note in TERMINALS:
        md.append(f"| {ref} | {pin} | {wire} | {func} | {note} |")
    md.append("")
    (directory / "terminal-list.md").write_text("\n".join(md), encoding="utf-8")
    with (directory / "cable-list.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cable", "part", "from", "to", "spec", "energy_chain", "note"])
        writer.writerows(CABLES)
    cmd = ["# Cable list", "", "The energy chain is VC-HB-3430.", "A slip ring is not used.", ""]
    cmd.append("| Cable | Part | From | To | Spec | In the chain | Note |")
    cmd.append("| --- | --- | --- | --- | --- | --- | --- |")
    for row in CABLES:
        cmd.append("| " + " | ".join(row) + " |")
    cmd.append("")
    (directory / "cable-list.md").write_text("\n".join(cmd), encoding="utf-8")


def project_text() -> str:
    return """{
  "board": {
    "design_settings": {
      "defaults": {},
      "meta": { "version": 2 }
    }
  },
  "meta": {
    "filename": "vibrocore-control.kicad_pro",
    "version": 1
  },
  "net_settings": {},
  "schematic": {
    "legacy_lib_dir": "",
    "legacy_lib_list": []
  },
  "sheets": [],
  "text_variables": {}
}
"""


def write_tree(directory: Path) -> None:
    sheets = build_sheets()
    check_nets(sheets)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "vibrocore.kicad_sym").write_text(library_text(), encoding="utf-8")
    (directory / "sym-lib-table").write_text(
        "(sym_lib_table\n"
        '  (lib (name "vibrocore")(type "KiCad")(uri "${KIPRJMOD}/vibrocore.kicad_sym")(options "")(descr "Vibrocore cabinet symbols"))\n'
        ")\n",
        encoding="utf-8",
    )
    uuids = {sheet.filename: uid("sheet-" + sheet.filename) for sheet in sheets}
    for sheet in sheets:
        (directory / sheet.filename).write_text(sheet_text(sheet, uuids[sheet.filename]), encoding="utf-8")
    (directory / "vibrocore-control.kicad_sch").write_text(
        root_text(sheets, uuids, cross_reference(sheets)), encoding="utf-8"
    )
    (directory / "vibrocore-control.kicad_pro").write_text(project_text(), encoding="utf-8")


def main() -> None:
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
                *[sheet.filename for sheet in build_sheets()],
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
