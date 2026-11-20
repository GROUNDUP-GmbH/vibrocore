"""Sheet wiring for the Vibrocore cabinet schematic."""

from __future__ import annotations

import filecmp
from collections import defaultdict
from pathlib import Path

from schlib import IN, OT, P, PI, PO, SYMS, Sym, f, pin_sexpr, q


def sexpr_justify(justify: str) -> str:
    """KiCad's schematic parser accepts left, right, top and bottom only.

    Horizontal and vertical center are the defaults. The token ``center`` is a
    parse error, and a property that fails to parse drops the whole symbol.
    """
    tokens = [token for token in justify.split() if token != "center"]
    return " ".join(tokens)

from generate_schematic import (
    CABLES,
    EXPORT,
    IO_NETS,
    OUT,
    PROJECT,
    TERMINALS,
    Sheet,
    pair,
    uid,
)


def build_power(s: Sheet) -> None:
    s.place("G0", "SRC", 36, 34, "VC-PW-5100 Instagrid")
    order = sorted((s.pin("G0", name)[1], name) for name in ("L", "N", "PE"))
    pin_x = s.pin("G0", "L")[0]
    rail = {name: pin_x + 12 + (2 - index) * 18 for index, (_, name) in enumerate(order)}
    net_of = {"L": "100_L", "N": "101_N", "PE": "102_PE"}
    for name in ("L", "N", "PE"):
        px, py = s.pin("G0", name)
        s.wire(net_of[name], (px, py), (rail[name], py))
    lx, nx, pe = rail["L"], rail["N"], rail["PE"]
    for ref, name, net in (("X1.1", "L", "100_L"), ("X1.2", "N", "101_N"), ("X1.3", "PE", "102_PE")):
        src = s.pin("G0", name)
        s.place_pin(ref, "TERM_V", "1", rail[name], src[1] + 10, ref.replace(".", ":"), ref_dx=8, val_dx=8, val_dy=0, ref_dy=-6)
        s.wire(net, (rail[name], src[1]), s.pin(ref, "1"))
    dx = nx - lx
    q_top = max(s.pin("X1.1", "2")[1], s.pin("X1.2", "2")[1]) + 8
    pair(s, "Q1", "ISO2", lx, q_top, "VC-PW-5700", dx=dx)
    s.link("100_L", ("X1.1", "2"), ("Q1", "1"))
    s.link("101_N", ("X1.2", "2"), ("Q1", "3"))
    qf_top = s.pin("Q1", "2")[1] + 6
    pair(s, "QF1", "RCD2", lx, qf_top, "VC-PW-5720 type B 30 mA", dx=dx)
    _shelf(s, "110_L", ("Q1", "2"), ("QF1", "1"), 16)
    _shelf(s, "111_N", ("Q1", "4"), ("QF1", "3"), -16)
    f_top = s.pin("QF1", "2")[1] + 6
    pair(s, "F1", "MCB2", lx, f_top, "VC-PW-5710 C20", dx=dx)
    _shelf(s, "120_L", ("QF1", "2"), ("F1", "1"), 16)
    _shelf(s, "121_N", ("QF1", "4"), ("F1", "3"), -16)
    bus_l = s.pin("F1", "2")[1] + 8
    bus_n = bus_l + 24
    s.wire("130_L", s.pin("F1", "2"), (lx, bus_l))
    s.wire("131_N", s.pin("F1", "4"), (nx, bus_n))
    branches = [
        ("F2", "MCB3", "VC-PW-5730 GV2L20", "140_L", "141_N"),
        ("F3", "MCB2", "VC-PW-5740 C16", "150_L", "151_N"),
        ("F4", "MCB2", "VC-PW-5750 C4", "160_L", "161_N"),
        ("F5", "MCB2", "VC-PW-5760 C10", "170_L", "171_N"),
    ]
    bx = lx + 40
    for index, (ref, sym, value, net_l, net_n) in enumerate(branches):
        x = bx + index * 46
        s.place_pin(ref, sym, "1", x, bus_l, value, unit=1, hide_value=True, hide_ref=True)
        s.place_pin(ref, sym, "3", x + 16, bus_n, value, unit=2, hide_value=False, hide_ref=False)
        if sym == "MCB3":
            s.place_pin(ref, sym, "5", x + 32, bus_n + 18, value, unit=3, hide_value=True, hide_ref=True)
        s.dash(ref)
        s.stub(net_l, (ref, "2"), dy=8)
        s.stub(net_n, (ref, "4"), dy=8)
    refs = [row[0] for row in branches]
    s.hrail("130_L", bus_l, [(lx, bus_l)] + [(ref, "1") for ref in refs])
    s.hrail("131_N", bus_n, [(nx, bus_n)] + [(ref, "3") for ref in refs])
    pe_y = s.pin("X1.3", "2")[1] + 16
    s.place_pin("PE1", "EARTH", "1", pe, pe_y, "PE", hide_value=True, hide_ref=True)
    s.place_pin("PF0", "PWR", "1", pe - 16, pe_y, "PE", hide_value=True, hide_ref=True)
    s.vrail("102_PE", pe, [("X1.3", "2"), ("PE1", "1")])
    s.hrail("102_PE", pe_y, [("PF0", "1"), (pe, pe_y)])
    s.add_note("Instagrid ONE max is the only AC source. Continuous current is 15.7 A.", s.pin("G0", "L"))
    s.add_note("Q1 does not switch PE. QF1 is type B, 30 mA.", s.pin("Q1", "1"))
    s.add_note("F2 is a Schneider GV2L20. NVE41289.09, IEC breaker table, enclosure, 240 V, one phase.", s.pin("F2", "1"))
    s.add_note("The row is ATV320U15M2. Line current is 17.8 A at 200 V. Irm is 223 A. Pole 3 is open.", s.pin("F2", "5"))
    s.add_note("The sonic feeder is 6 mm2. The terminal maximum is 6 mm2. The S200 feeder is 2.5 mm2.", s.pin("F3", "1"))
    s.add_note("F4 feeds the S200 supply. F5 feeds the general 24 V supply. Both continue on the next sheet.", s.pin("F4", "2"))
    s.add_note("A crossing without a dot is not a connection.")


def build_supplies(s: Sheet) -> None:
    """The two 24 V supplies. Kept off the mains sheet so the feeder poles stay readable."""
    s.place("G1", "PSU0", 110, 56, "VC-PW-5310 SDR-120-24")
    s.place("G2", "PSU", 230, 56, "VC-PW-5320 SDR-480-24 slot")
    s.stub("160_L", ("G1", "L"), dx=-28)
    s.stub("161_N", ("G1", "N"), dx=-36)
    s.stub("170_L", ("G2", "L"), dx=-28)
    s.stub("171_N", ("G2", "N"), dx=-36)
    for psu, net_in, net_out, fuse_ref, fuse_value, flag in (
        ("G1", "200_24S", "201_24S", "F14", "VC-PW-5800 6A", "PF1"),
        ("G2", "210_24C", "211_24C", "F24", "VC-PW-5810 20A", "PF2"),
    ):
        plus = s.pin(psu, "P")
        s.place_pin(fuse_ref, "FUSE", "1", plus[0] + 22, plus[1], fuse_value)
        s.link(net_in, (psu, "P"), (fuse_ref, "1"))
        out = s.pin(fuse_ref, "2")
        s.place_pin(flag, "PWR", "1", out[0] + 16, out[1], net_out, hide_value=True)
        s.link(net_out, (fuse_ref, "2"), (flag, "1"))
    zero = 148
    s.place_pin("X1.4", "TERM_H", "2", 40, zero, "X1:4")
    s.place_pin("W1", "BOND", "1", 270, zero, "W1 bond")
    s.hrail("001_0V", zero, [("G1", "M"), ("G2", "M"), ("X1.4", "1"), ("X1.4", "2"), ("W1", "1")])
    pe_y = zero - 14
    s.hrail("102_PE", pe_y, [("G1", "PE"), ("G2", "PE")])
    bond = s.pin("W1", "2")
    s.wire("102_PE", bond, (bond[0], pe_y), (s.pin("G2", "PE")[0], pe_y))
    s.add_note("The general 24 V rail is 2.5 mm2. The S200 24 V feed is 1.0 mm2. There is no 48 V rail.", s.pin("G1", "P"))
    s.add_note("G2 is an open 24 V slot. SDR-480-24 is the slot size, not a purchase.", s.pin("G2", "P"))
    s.add_note("Both 0 V rails meet at X1 pin 4. W1 is the only bond to PE. Confirm W1 in the S200 PTI manual.", s.pin("W1", "1"))
    s.add_note("F14 is 6 A on the S200 rail. F24 is 20 A on the general rail.", s.pin("F14", "1"))


def build_safety(s: Sheet) -> None:
    s.place("K1", "PNOZ", 168, 108, "VC-CT-6220 750104", unit=1)
    y11 = s.pin("K1", "S11")
    s.place_pin("S1", "ESTOP", "11", y11[0] - 16, y11[1], "VC-CT-6210 OPEN", unit=1, val_dy=-12)
    y21 = s.pin("K1", "S21")
    s.place_pin("S1", "ESTOP", "21", y21[0] - 16, y21[1], "VC-CT-6210 OPEN", unit=2, hide_value=True, hide_ref=True)
    s.place_pin("S1", "ESTOP", "31", 90, s.pin("K1", "S22")[1] + 24, "VC-CT-6210 OPEN", unit=3, hide_value=True, hide_ref=True)
    s.dash("S1")
    s.link("410_S11", ("S1", "11"), ("K1", "S11"))
    s.link("412_S21", ("S1", "21"), ("K1", "S21"))
    s.place_pin("S10", "SW_PB", "2", s.pin("K1", "S34")[0] - 36, s.pin("K1", "S34")[1], "VC-CT-6270 OPEN")
    for src, dst, net in (("12", "S12", "411_S12"), ("22", "S22", "413_S22")):
        a = s.pin("S1", src)
        b = s.pin("K1", dst)
        s.wire(net, a, (a[0] - 10, a[1]), (a[0] - 10, b[1]), b)
    s.link("414_S34", ("S10", "2"), ("K1", "S34"))
    s.wire("411_S12", s.pin("S10", "1"), (s.pin("S10", "1")[0], s.pin("K1", "S12")[1]), s.pin("K1", "S12"))
    s.place_pin("F30", "FUSE", "2", 250, s.pin("K1", "A1")[1], "VC-PW-5820 2A", ref_dx=8)
    s.place_pin("K1", "PNOZ", "13", s.pin("F30", "2")[0] + 24, s.pin("F30", "2")[1], "13-14", unit=2, hide_value=False, hide_ref=False)
    s.link("430_F30", ("F30", "2"), ("K1", "13"))
    s.stub("431_STO1", ("K1", "14"), dx=16)
    s.place_pin("F31", "FUSE", "2", 250, s.pin("K1", "14")[1] + 24, "VC-PW-5820 2A", ref_dx=8)
    s.place_pin("K1", "PNOZ", "23", s.pin("F31", "2")[0] + 24, s.pin("F31", "2")[1], "23-24", unit=3, hide_value=False, hide_ref=False)
    s.link("432_F31", ("F31", "2"), ("K1", "23"))
    s.stub("433_STO2", ("K1", "24"), dx=16)
    s.place_pin("K1", "PNOZ", "33", 300, s.pin("K1", "24")[1] + 22, "33-34", unit=4, hide_value=False, hide_ref=False)
    s.place_pin("K1", "PNOZ", "41", 250, s.pin("K1", "33")[1] + 20, "41-42", unit=5, hide_value=False, hide_ref=False)
    s.stub("421_PNOZ", ("K1", "42"), dx=16)
    s.stub("420_ESTOP", ("S1", "31"), dx=16)
    rail = 28
    s.vrail("211_24C", rail, [("K1", "A1"), ("F30", "1"), ("F31", "1"), ("K1", "41"), ("S1", "32")])
    s.vrail("001_0V", rail + 12, [("K1", "A2")])
    s.add_note("Two NC channels go to the PNOZ. The third NC is DIO input index 2 only.", s.pin("S1", "11"))
    s.add_note("Do not feed cabinet 24 V into S11 or S21. The PNOZ makes the test pulses.", s.pin("K1", "S11"))
    s.add_note("Set two channels, short detection and a monitored reset. The detent text is TBC.", s.pin("S10", "1"))
    s.add_note("Contact 13-14 is STO channel 1. Contact 23-24 is STO channel 2. The section is 0.75 mm2.", s.pin("K1", "14"))
    s.add_note("41-42 is the monitor. Do not use it in the safety path. Its state is TBC.", s.pin("K1", "41"))
    s.add_note("33-34 is spare. Do not load it. Y32 is not a safety output.", s.pin("K1", "33"))
    s.add_note("OPEN: the E-stop contact block and the reset button are not chosen.", s.pin("S1", "31"))
    s.add_note("The RevPi only reads feedback. Do not claim an ISO 13849 PL.")


def _shelf(s: Sheet, net: str, src, dst, dx: int) -> None:
    """A side step between two pins, so the net name has a clear run."""
    a = s.pin(*src)
    b = s.pin(*dst)
    s.wire(net, a, (a[0] + dx, a[1]), (b[0] + dx, b[1]), b)


def side_net(s: Sheet, net: str, nodes, dx: int) -> None:
    """Tie device pins with a gutter beside the symbol, not along the pin column."""
    pts = [s.resolve(node) for node in nodes]
    gutter = pts[0][0] + dx
    for px, py in pts:
        if px != gutter:
            s.wire(net, (px, py), (gutter, py))
    ys = sorted({py for _, py in pts})
    for top, bot in zip(ys, ys[1:]):
        s.wire(net, (gutter, top), (gutter, bot))


def _stub_left(s: Sheet, net: str, ref: str, pin: str, dx: int = -28) -> None:
    s.stub(net, (ref, pin), dx=dx)


def build_hub(s: Sheet) -> None:
    s.place("A2", "S200", 150, 118, "VC-HB-2300 6SL5510-1BB11-0AA0")
    for pin, net in (("L1", "150_L"), ("L3", "151_N"), ("1", "431_STO1"), ("5", "433_STO2"), ("FB", "440_S200FB")):
        _stub_left(s, net, "A2", pin)
    side_net(s, "201_24S", [("A2", "24V"), ("A2", "24Vb")], -12)
    side_net(s, "001_0V", [("A2", "0V"), ("A2", "0Vb"), ("A2", "2"), ("A2", "6")], -20)
    uy = s.pin("A2", "U")[1]
    s.place_pin("M1", "MSRV", "U", s.pin("A2", "U")[0] + 96, uy, "VC-HB-2100 1FL2104")
    fan = (
        ("X4.1", "U", "540_U", "U"),
        ("X4.2", "V", "541_V", "V"),
        ("X4.3", "W", "542_W", "W"),
        ("X4.4", "PE2", "102_PE", "PE"),
        ("X6.1", "BRP", "543_BRP", "BRP"),
        ("X6.2", "BRN", "544_BRN", "BRN"),
    )
    for index, (term, pin, net, motor) in enumerate(fan):
        src = s.pin("A2", pin)
        ty = 40 + index * 16
        lane = 184 + index * 4
        s.place_pin(term, "TERM_H", "1", 220, ty, term)
        s.wire(net, src, (lane, src[1]), (lane, ty), s.pin(term, "1"))
        dest = s.pin("M1", motor)
        out = s.pin(term, "2")
        drop = dest[0] - 10 - index * 3
        s.wire(net, out, (drop, out[1]), (drop, dest[1]), dest)
    s.place_pin("X5.1", "TERM_H", "1", 220, 150, "X5.1")
    s.place_pin("X5.2", "TERM_H", "1", 220, 168, "X5.2")
    enc = s.pin("A2", "X120")
    s.wire("510_ENC", enc, (174, enc[1]), (174, 150), s.pin("X5.1", "1"))
    s.stub("510_ENC", ("X5.1", "2"), dy=12)
    left_pe = s.pin("A2", "PE")
    right_pe = s.pin("A2", "PE2")
    top = s.pin("A2", "L1")[1] - 10
    s.wire(
        "102_PE",
        left_pe,
        (left_pe[0] - 36, left_pe[1]),
        (left_pe[0] - 36, top),
        (right_pe[0] + 8, top),
        (right_pe[0] + 8, right_pe[1]),
        right_pe,
    )
    shield = s.pin("X5.2", "2")
    motor_pe = s.pin("M1", "PE")
    s.wire("102_PE", shield, (248, shield[1]), (248, motor_pe[1]), motor_pe)
    s.add_note("VC-HB-3450 is the catalogue encoder cable. The Siemens order code is TODO.", s.pin("X5.1", "2"))
    s.place("U1", "PULSE", 78, 196, "pulse source TODO", in_bom=False)
    for index, (src, dst, net) in enumerate((("P", "36", "520_PULSP"), ("N", "37", "521_PULSN"), ("D", "38", "522_SIGNP"), ("E", "39", "523_SIGNN"))):
        a = s.pin("A2", dst)
        b = s.pin("U1", src)
        lane = 176 + index * 2
        s.wire(net, a, (lane, a[1]), (lane, b[1]), b)
    s.place_pin("R1", "RES", "1", 250, 142, "VC-CT-6790 120R")
    a = s.pin("A2", "23")
    b = s.pin("R1", "1")
    s.wire("910_A", a, (250, a[1]), (250, b[1]), b)
    a = s.pin("A2", "25")
    c = s.pin("R1", "2")
    s.wire("911_B", a, (c[0] + 14, a[1]), (c[0] + 14, c[1]), c)
    s.stub("910_A", ("R1", "1"), dy=12)
    s.stub("911_B", ("R1", "2"), dy=12)
    s.add_note("Order 6SL5510-1BB11-0AA0. This is the PTI standard drive, not the PROFINET code.", s.pin("A2", "L1"))
    s.add_note("X131 is 1 STO1+, 2 STO1-, 3 STO-VS, 4 STO-M, 5 STO2+, 6 STO2-. STO-VS and STO-M are TBC.", s.pin("A2", "3"))
    s.add_note("X130 is not on this PTI drive. STO status is status word bit STO_EP. Do not land 440_S200FB yet.", s.pin("A2", "FB"))
    s.add_note("X124 screws are marked 24 V and 0 V. They are not numbered. Both screws are one node.", s.pin("A2", "24Vb"))
    s.add_note("L2 is open. Mains uses L1 and L3. DCP, R1 and R2 stay open. Fit the blanking plug.", s.pin("A2", "L2"))
    s.add_note("U1 is not a DIO pin. Pulse form and scale are TBC.", s.pin("A2", "36"))
    s.add_note("Encoder map, drive to motor: 7 A, 8 B, 4 C, 5 D, 1 E, 2 F.", s.pin("A2", "X120"))
    s.add_note("Power cable is 4G1.5 mm2 shielded. Brake pair is 2x0.75 mm2. The coil stays on X108.", s.pin("A2", "U"))


def build_sonic(s: Sheet) -> None:
    s.place("A3", "ATV", 120, 130, "VC-SH-1210 ATV320U15M2C")
    for pin, net in (("L1", "140_L"), ("L2", "141_N"), ("STO", "431_STO1"), ("DI3", "433_STO2"), ("DI1", "450_RESET"), ("COM", "001_0V")):
        _stub_left(s, net, "A3", pin)
    pe = s.pin("A3", "PE")
    pe2 = s.pin("A3", "PE2")
    below = pe2[1] + 10
    s.wire("102_PE", pe, (pe[0] - 36, pe[1]), (pe[0] - 36, below), (pe2[0], below), pe2)
    s.stub("451_FAULT", ("A3", "R1B"), dx=-16)
    s.stub("452_SONSTO", ("A3", "R2C"), dx=-16)
    s.stub("910_A", ("A3", "RJA"), dx=-16)
    s.stub("911_B", ("A3", "RJB"), dx=-16)
    rail = s.pin("A3", "R1C")[0] - 30
    s.vrail("211_24C", rail, [("A3", "R1C"), ("A3", "R2A")])
    for unit, drive, ypin in ((1, "U", "1"), (2, "V", "3"), (3, "W", "5")):
        px, py = s.pin("A3", drive)
        s.place_pin("F21", "MPROT", ypin, px + 40, py, "VC-PW-5770 OPEN", unit=unit, hide_value=unit != 1, hide_ref=unit != 1, ref_dy=-8)
    s.dash("F21")
    for unit, drive, ypin in ((1, "U", "1"), (2, "V", "3"), (3, "W", "5")):
        px, py = s.pin("A3", drive)
        s.place_pin("F22", "MPROT", ypin, px + 40, py + 36, "VC-PW-5770 OPEN", unit=unit, hide_value=unit != 1, hide_ref=unit != 1, ref_dy=-8)
    s.dash("F22")
    s.place_pin(
        "M2", "M3", "U", s.pin("F21", "2")[0] + 70, s.pin("A3", "U")[1],
        "VC-SH-1100 motor A", val_dx=14, val_dy=0, val_justify="left",
    )
    for drive, fin, fout, term, net, motor in (
        ("U", "1", "2", "X2.1", "610_UA", "U"),
        ("V", "3", "4", "X2.2", "611_VA", "V"),
        ("W", "5", "6", "X2.3", "612_WA", "W"),
    ):
        src = s.pin("A3", drive)
        dst = s.pin("F21", fin)
        low = s.pin("F22", fin)
        lane = src[0] + 8 + {"U": 0, "V": 4, "W": 8}[drive]
        s.wire("600_" + drive, src, (lane, src[1]), dst)
        s.wire("600_" + drive, (lane, src[1]), (lane, low[1]), low)
        dx, dy = s.pin("F21", fout)
        s.place_pin(term, "TERM_H", "1", dx + 22, dy, term)
        s.join(net, ("F21", fout), (term, "1"), (term, "2"), ("M2", motor))
    s.place_pin("X2.4", "TERM_H", "1", 230, s.pin("M2", "PE")[1] + 18, "X2.4")
    s.join("102_PE", ("A3", "PE2"), ("X2.4", "1"), ("X2.4", "2"))
    shield = s.pin("X2.4", "2")
    motor = s.pin("M2", "PE")
    s.wire("102_PE", shield, (shield[0], 100), (motor[0], 100), motor)
    s.place_pin(
        "M3", "M3", "U", s.pin("F22", "2")[0] + 78, s.pin("F22", "2")[1],
        "VC-SH-1100 motor B", val_dx=14, val_dy=0, val_justify="left",
    )
    # Swap V and W on the way to motor B. The jogs sit side by side.
    mapping = (
        ("6", "X3.2", "622_WB", "V", "W"),
        ("4", "X3.3", "621_VB", "W", "V"),
        ("2", "X3.1", "620_UB", "U", "U"),
    )
    fan_y = {"U": 50, "V": 62, "W": 74}
    side = {"U": 204, "V": 212, "W": 228}
    hop_x = {"U": 251, "V": 257, "W": 263}
    for fout, term, net, motor, lane in mapping:
        dest = s.pin("M3", motor)
        src = s.pin("F22", fout)
        ty = fan_y[motor]
        s.place_pin(term, "TERM_H", "1", dest[0] - 46, ty, term)
        s.wire(net, src, (side[lane], src[1]), (side[lane], ty), s.pin(term, "1"))
        out = s.pin(term, "2")
        s.wire(net, out, (hop_x[motor], ty), (hop_x[motor], dest[1]), dest)
    s.place_pin("X3.4", "TERM_H", "1", s.pin("M3", "PE")[0] - 24, s.pin("M3", "PE")[1], "X3.4", ref_dx=0, ref_dy=-8)
    s.join("102_PE", ("X3.4", "1"), ("X3.4", "2"), ("M3", "PE"), ("A3", "PE2"))
    s.add_note("One ATV320 output feeds both OLI MVE 400/6-HF motors. Each motor is 1.45 A.", s.pin("A3", "U"))
    s.add_note("Motor B swaps V and W at X3 so the motors turn in opposite directions.", s.pin("M3", "U"))
    s.add_note("OPEN: F21 and F22 need a PWM-rated protector. Do not fit a standard GV2.", s.pin("F21", "1"))
    s.add_note("The drive STO screw is one terminal. DI3 is the second channel. The SoMove parameter is TODO.", s.pin("A3", "DI3"))
    s.add_note("Do not tie P24 to the cabinet 24 V. PA, PB, PC and P0 stay open. There is no braking resistor.", s.pin("A3", "P24"))
    s.add_note("R1C is the fault-relay common. R1B is the NC contact. R1A is open. The logic assignment is TODO.", s.pin("A3", "R1C"))
    s.add_note("RJ45 pin numbers are TBC. See the Modbus manual NVE41308.", s.pin("A3", "RJA"))
    s.add_note("Supply wire is 6 mm2. Each motor cable stays 4G1.5 shielded at the drive. The drive is below rated current.", s.pin("M2", "U"))


def _contact_24(s: Sheet, ref: str, sym: str, signal: str, y: int, x_signal: int, value: str) -> None:
    s.place_pin(ref, sym, "2", x_signal, y, value)
    s.vrail("211_24C", 24, [(ref, "1")])


def build_revpi(s: Sheet) -> None:
    s.place("A4", "REVPI", 48, 36, "VC-CT-6800 100378")
    s.place("A5", "DIO", 210, 120, "VC-CT-6810 100197")
    s.link("940_BRIDGE", ("A4", "BR"), ("A5", "BR"))
    s.stub("930_ETH", ("A4", "ETH0"), dx=14)
    s.vrail("211_24C", 16, [("A4", "24"), ("A5", "X2_1"), ("A5", "X2_4"), ("A5", "X4_1")])
    s.vrail("001_0V", 28, [("A4", "0"), ("A4", "GND"), ("A5", "X2_2"), ("A5", "X2_3"), ("A5", "X4_2")])
    s.vrail("102_PE", 40, [("A4", "FG"), ("A5", "X4_4")])
    s.stub("910_A", ("A4", "P"), dx=-8)
    s.stub("911_B", ("A4", "N"), dx=-8)
    for pin, net in (
        ("I1", "460_LIM_UP"), ("I2", "461_LIM_DN"), ("I7", "462_ENABLE"), ("I13", "480_INDEX"),
        ("I8", "470_TILT_V"), ("I9", "471_TILT_F"), ("I10", "472_LIFT_D"), ("I11", "473_LIFT_R"),
        ("I3", "420_ESTOP"), ("I4", "421_PNOZ"), ("I5", "440_S200FB"),
        ("I6", "452_SONSTO"), ("I12", "451_FAULT"),
    ):
        _stub_left(s, net, "A5", pin)
    for pin, net in (
        ("O1", "490_EXT"), ("O2", "491_RET"), ("O3", "492_TILTV"), ("O4", "493_TILTF"),
        ("O5", "494_BEACON"), ("O6", "450_RESET"), ("O7", "495_ROT_EN"),
    ):
        s.stub(net, ("A5", pin), dx=16)
    s.add_note("Controller order 100378. DIO order 100197. The PiBridge plug is 100204.", s.pin("A4", "BR"))
    s.add_note("I1 is I/O-list index 0. Channel names are not a confirmed plug order.", s.pin("A5", "I1"))
    s.add_note("X4 order 24 V, 0 V, NC, FG is TBC. RS-485 order GND, N, P is TBC.", s.pin("A4", "FG"))
    s.add_note("ETH1 is a service port. Do not put it in the harness. There is no PFC200 on this drawing.", s.pin("A4", "ETH1"))
    s.add_note("Field devices and X7 are on the field sheet. Spare inputs and outputs stay open.", s.pin("A5", "O14"))


def build_field(s: Sheet) -> None:
    """Field contacts on a 18-step pitch so each product label has its own band."""
    y = 28
    step = 18

    def contact(ref: str, sym: str, value: str, net: str, term: str, row: int) -> None:
        py = y + row * step
        s.place_pin(ref, sym, "2", 78, py, value)
        s.place_pin(term, "TERM_H", "1", 118, py, term)
        s.link(net, (ref, "2"), (term, "1"))
        s.stub(net, (term, "2"), dx=14)
        s.vrail("211_24C", 16, [(ref, "1")])

    contact("S4", "SW_NC", "VC-CT-6200", "460_LIM_UP", "X7.1", 0)
    contact("S5", "SW_NC", "VC-CT-6200", "461_LIM_DN", "X7.2", 1)
    contact("S6", "SW_NO", "VC-CT-6260", "462_ENABLE", "X7.3", 2)
    row_b = y + 3 * step
    s.place("B1", "PNP", 70, row_b, "VC-CT-6250")
    s.place_pin("X7.4", "TERM_H", "1", 118, s.pin("B1", "OUT")[1], "X7.4")
    s.link("480_INDEX", ("B1", "OUT"), ("X7.4", "1"))
    s.stub("480_INDEX", ("X7.4", "2"), dx=14)
    s.vrail("211_24C", 16, [("B1", "24")])
    b0 = s.pin("B1", "0")
    s.wire("001_0V", b0, (10, b0[1]), (10, 192))
    # Tilt limits are on the tilt sheet. These terminals only leave the cabinet.
    for row, term, net in ((4, "X7.5", "470_TILT_V"), (5, "X7.6", "471_TILT_F")):
        py = y + row * step
        s.place_pin(term, "TERM_H", "1", 118, py, term)
        s.stub(net, (term, "1"), dx=-16)
        s.stub(net, (term, "2"), dx=14)
    for row, first, second, mid, net, term in (
        (6, "S14", "S15", "474_DMID", "472_LIFT_D", "X7.7"),
        (7, "S16", "S17", "475_RMID", "473_LIFT_R", "X7.8"),
    ):
        py = y + row * step
        s.place_pin(second, "SW_NC", "2", 78, py, "OPEN limit")
        s.place_pin(term, "TERM_H", "1", 118, py, term)
        s.link(net, (second, "2"), (term, "1"))
        s.stub(net, (term, "2"), dx=14)
        s.place_pin(first, "SW_NC", "2", 36, py, "OPEN limit")
        s.link(mid, (first, "2"), (second, "1"))
        s.vrail("211_24C", 16, [(first, "1")])
    beacon = y + 8 * step
    s.place_pin("X7.9", "TERM_H", "1", 118, beacon, "X7.9")
    s.place_pin("H1", "LAMP", "1", 168, beacon, "VC-CT-6230")
    s.stub("494_BEACON", ("X7.9", "1"), dx=-16)
    s.link("494_BEACON", ("X7.9", "2"), ("H1", "1"))
    h0 = s.pin("H1", "2")
    s.wire("001_0V", h0, (h0[0], 192), (10, 192))
    s.place_pin("X7.10", "TERM_V", "1", 16, 196, "X7.10")
    s.vrail("211_24C", 16, [("X7.10", "1"), ("X7.10", "2")])
    s.place_pin("X7.11", "TERM_V", "1", 36, 196, "X7.11")
    s.wire("001_0V", s.pin("X7.11", "1"), (36, 192), (10, 192))
    s.vrail("001_0V", 36, [("X7.11", "1"), ("X7.11", "2")])
    s.place_pin("X7.12", "TERM_V", "1", 56, 196, "X7.12")
    s.stub("102_PE", ("X7.12", "2"), dy=6)
    s.vrail("102_PE", 56, [("X7.12", "1"), ("X7.12", "2")])
    s.add_note("S4 and S5 are OPEN limit switches, article VC-CT-6200. S6 is an IDEC HE1B-M1.", s.pin("S4", "2"))
    s.add_note("OPEN: the index sensor order code is not chosen. The symbol is PNP.", s.pin("B1", "OUT"))
    s.add_note("S14 to S17 are lift limit contacts. The order code is not chosen.", s.pin("S14", "2"))
    s.add_note("X7 is the field terminal strip. The purchased block is not chosen.", s.pin("X7.1", "1"))
    s.add_note("DIO channel names are not a confirmed plug order. Confirm them on the Kunbus drawing.")


def build_tilt(s: Sheet) -> None:
    s.place("K2", "REL", 80, 36, "VC-LT-9230", unit=1)
    s.place("K3", "REL", 170, 36, "VC-LT-9230", unit=1)
    s.place_pin("K2", "REL", "11", 80, 70, "11-14", unit=2, hide_value=False, hide_ref=False)
    s.place_pin("K3", "REL", "11", 170, 86, "11-14", unit=2, hide_value=False, hide_ref=False)
    s.place_pin("K2", "REL", "21", 80, 112, "21-24", unit=3, hide_value=False, hide_ref=False)
    s.place_pin("K3", "REL", "21", 170, 128, "21-24", unit=3, hide_value=False, hide_ref=False)
    s.place_pin("D2", "DIODE", "1", s.pin("K2", "A1")[0] + 16, s.pin("K2", "A1")[1], "VC-CT-6780")
    s.place_pin("D3", "DIODE", "1", s.pin("K3", "A1")[0] + 16, s.pin("K3", "A1")[1], "VC-CT-6780")
    s.link("496_K2", ("K2", "A1"), ("D2", "1"))
    s.link("497_K3", ("K3", "A1"), ("D3", "1"))
    a = s.pin("K3", "12")
    b = s.pin("K2", "A1")
    s.wire("496_K2", a, (230, a[1]), (230, 14), (b[0], 14), b)
    a = s.pin("K2", "12")
    b = s.pin("K3", "A1")
    s.wire("497_K3", a, (244, a[1]), (244, 10), (b[0], 10), b)
    s.vrail("001_0V", 36, [("K2", "A2"), ("K3", "A2"), ("D2", "2"), ("D3", "2"), ("K2", "22"), ("K3", "22")])
    s.vrail("211_24C", 20, [("K2", "24"), ("K3", "24")])
    s.stub("493_TILTF", ("K2", "11"), dx=-14)
    s.stub("492_TILTV", ("K3", "11"), dx=-14)
    s.place_pin("X8.1", "TERM_H", "1", 240, s.pin("K2", "21")[1], "X8.1")
    s.place_pin("M4", "ACT", "1", 290, s.pin("K2", "21")[1], "VC-LT-9200")
    s.join("498_ACT_A", ("K2", "21"), ("X8.1", "1"), ("X8.1", "2"), ("M4", "1"))
    s.place_pin("X8.2", "TERM_H", "1", 240, s.pin("K3", "21")[1], "X8.2")
    my = s.pin("M4", "2")
    s.wire("499_ACT_B", s.pin("K3", "21"), (240, s.pin("K3", "21")[1]), s.pin("X8.2", "1"))
    s.link("499_ACT_B", ("X8.2", "2"), (s.pin("X8.2", "2")[0], my[1]))
    s.link("499_ACT_B", (s.pin("X8.2", "2")[0], my[1]), ("M4", "2"))
    s.place_pin("S7", "SW_NC", "1", 120, 156, "tilt vertical")
    s.place_pin("S8", "SW_NC", "1", 120, 172, "tilt folded")
    s.place_pin("X8.3", "TERM_H", "1", s.pin("S7", "2")[0] + 16, s.pin("S7", "2")[1], "X8.3")
    s.place_pin("X8.4", "TERM_H", "1", s.pin("S8", "2")[0] + 16, s.pin("S8", "2")[1], "X8.4")
    s.join("470_TILT_V", ("S7", "2"), ("X8.3", "1"), ("X8.3", "2"))
    s.stub("470_TILT_V", ("X8.3", "2"), dx=12)
    s.join("471_TILT_F", ("S8", "2"), ("X8.4", "1"), ("X8.4", "2"))
    s.stub("471_TILT_F", ("X8.4", "2"), dx=12)
    s.vrail("211_24C", 20, [("S7", "1"), ("S8", "1")])
    s.place("A10", "HBR", 80, 138, "VC-LT-9110")
    s.stub("490_EXT", ("A10", "E"), dx=-14)
    s.stub("491_RET", ("A10", "R"), dx=-14)
    s.vrail("211_24C", 20, [("A10", "P")])
    s.vrail("001_0V", 36, [("A10", "M")])
    s.place_pin("X10.1", "TERM_H", "1", 160, s.pin("A10", "MP")[1], "X10.1")
    s.place_pin("X10.2", "TERM_H", "1", 160, s.pin("A10", "MN")[1], "X10.2")
    s.place_pin("M5", "ACT", "1", 200, s.pin("A10", "MP")[1] + 24, "VC-LT-9100 A")
    s.place_pin("M6", "ACT", "1", 250, s.pin("A10", "MP")[1] + 24, "VC-LT-9100 B")
    s.join("550_LIFTP", ("A10", "MP"), ("X10.1", "1"), ("X10.1", "2"))
    s.wire("551_LIFTN", s.pin("A10", "MN"), s.pin("X10.2", "1"))
    plus = s.pin("M5", "1")
    minus = s.pin("M5", "2")
    out_p = s.pin("X10.1", "2")
    out_n = s.pin("X10.2", "2")
    s.wire("550_LIFTP", out_p, (190, out_p[1]), (190, plus[1]), plus, s.pin("M6", "1"))
    s.wire("551_LIFTN", out_n, (194, out_n[1]), (194, minus[1]), minus, s.pin("M6", "2"))
    low24, low0 = 164, 176
    s.place_pin("X8.5", "TERM_H", "1", 48, low24, "X8.5")
    s.place_pin("X10.3", "TERM_H", "1", 88, low24, "X10.3")
    feed = s.pin("A10", "P")
    s.wire("211_24C", (20, feed[1]), (20, low24))
    s.hrail("211_24C", low24, [(20, low24), ("X8.5", "1"), ("X8.5", "2"), ("X10.3", "1"), ("X10.3", "2")])
    s.place_pin("X8.6", "TERM_H", "1", 48, low0, "X8.6")
    s.place_pin("X10.4", "TERM_H", "1", 88, low0, "X10.4")
    ret = s.pin("A10", "M")
    s.wire("001_0V", (36, ret[1]), (36, low0))
    s.hrail("001_0V", low0, [(36, low0), ("X8.6", "1"), ("X8.6", "2"), ("X10.4", "1"), ("X10.4", "2")])
    s.add_note("K2 is the vertical tilt contactor. Each coil is in series with the NC contact of the other relay.", s.pin("K2", "A1"))
    s.add_note("K3 is the fold contactor. The off state puts both motor leads on 0 V.", s.pin("K3", "A1"))
    s.add_note("Do not command both tilt directions. Do not command both lift directions.", s.pin("A10", "E"))
    s.add_note("Confirm that Finder 62.32 .4000 has no internal diode. D2 and D3 stay fitted.", s.pin("D2", "1"))
    s.add_note("The actuator current is not on a nameplate. The power section is TBC.", s.pin("M4", "1"))
    s.add_note("S7 and S8 order codes are not chosen. Limit names inside the actuator are TODO.", s.pin("S7", "1"))
    s.add_note("Lift limits are on the field sheet. The H-bridge is VC-LT-9110. The lift cable section is TBC.", s.pin("A10", "MP"))


def build_rotation(s: Sheet) -> None:
    s.place("A6", "NANO", 160, 90, "VC-CT-6280 proposal")
    s.place_pin("F6", "FUSE", "1", 40, 40, "VC-PW-5790 2A", val_dx=8, val_dy=0, val_justify="left", ref_dy=-10)
    s.place_pin("PF3", "PWR", "1", s.pin("F6", "2")[0], s.pin("F6", "2")[1] + 12, "24V R", hide_value=True, ref_dx=8, ref_justify="left")
    s.link("500_24R", ("F6", "2"), ("PF3", "1"))
    s.vrail("211_24C", 24, [("F6", "1")])
    s.place_pin("X9.1", "TERM_H", "1", 90, s.pin("A6", "a2")[1], "X9.1")
    s.join("500_24R", ("PF3", "1"), ("X9.1", "1"), ("X9.1", "2"), ("A6", "a2"))
    bx = s.pin("A6", "b8")[0]
    s.place_pin("U2", "PULSE", "P", bx + 56, s.pin("A6", "b8")[1], "OPEN clock", in_bom=False)
    s.place_pin("X9.3", "TERM_H", "2", s.pin("A6", "b4")[0] - 50, s.pin("A6", "b4")[1], "X9.3")
    s.stub("495_ROT_EN", ("X9.3", "1"), dx=-14)
    s.link("495_ROT_EN", ("X9.3", "2"), ("A6", "b4"))
    s.place_pin("X9.4", "TERM_H", "1", bx + 22, s.pin("A6", "b8")[1], "X9.4")
    s.join("530_CLKP", ("A6", "b8"), ("X9.4", "1"), ("X9.4", "2"), ("U2", "P"))
    s.place_pin("X9.6", "TERM_H", "1", bx + 22, s.pin("A6", "b6")[1], "X9.6")
    s.link("532_DIRP", ("A6", "b6"), ("X9.6", "1"))
    ud = s.pin("U2", "D")
    gutter = ud[0] - 8
    s.wire("532_DIRP", ud, (gutter, ud[1]), (gutter, s.pin("X9.6", "2")[1]), s.pin("X9.6", "2"))
    s.vrail("001_0V", 36, [("A6", "a1"), ("A6", "b1")])
    s.place_pin("X9.2", "TERM_H", "1", 80, 150, "X9.2")
    s.place_pin("X9.5", "TERM_H", "1", 110, 150, "X9.5")
    s.place_pin("X9.7", "TERM_H", "1", 140, 150, "X9.7")
    s.place_pin("X9.8", "TERM_H", "1", 180, 150, "X9.8")
    s.hrail("001_0V", 150, [(36, 150), ("X9.2", "1"), ("X9.2", "2"), ("X9.5", "1"), ("X9.5", "2"), ("X9.7", "1"), ("X9.7", "2")])
    s.place_pin("PE2", "EARTH", "1", 210, 150, "PE", hide_value=True, hide_ref=True)
    s.join("102_PE", ("X9.8", "1"), ("X9.8", "2"), ("PE2", "1"))
    s.add_note("Nanotec PD2-C4118L1804-E-01 is a proposal. It is not released. This order code speaks USB, not Modbus.", s.pin("A6", "a2"))
    s.add_note("Clock and direction come from U2. U2 is not a DIO pin. Enable is DIO output 7, on +Release b4.", s.pin("U2", "P"))
    s.add_note("CLK- and DIR- are parked on 0 V at X9. Do not land them on b5 or b7.", s.pin("X9.2", "1"))
    s.add_note("24 V is inside the 12 V to 48 V range. The fuse is 2 A. The wire is 0.75 mm2.", s.pin("F6", "1"))
    s.add_note("The drive PE screw is TBC. The cable shield uses X9 pin 8. The index sensor is B1 on the field sheet.", s.pin("X9.8", "1"))


def build_network(s: Sheet) -> None:
    s.place("A7", "RUT", 80, 60, "VC-CT-6600 RUT241")
    s.vrail("211_24C", 30, [("A7", "1")])
    s.vrail("001_0V", 42, [("A7", "2")])
    s.stub("930_ETH", ("A7", "LAN"), dx=18)
    s.add_note("RUT241 runs from the general 24 V rail. There is no 9 V converter and no PE screw.", s.pin("A7", "1"))
    s.add_note("Cat5e from RevPi ETH0 to the router LAN. Assume 0.5 m. ETH1 is service.", s.pin("A7", "LAN"))
    s.add_note("Modbus slave 1 is the ATV320. Slave 2 is the S200. Baud and parity are TODO.", s.pin("A7", "1"))
    s.add_note("R1, 120 ohm, is drawn at the S200. The shield lands on PE at the RevPi only.", s.pin("A7", "LAN"))
    s.add_note("The rotation drive is not on this bus.")


def build_terminals(s: Sheet) -> None:
    s.add_note("This sheet is the terminal plan. The symbols are on the circuit sheets. Do not fit a second symbol.")
    s.add_note("The purchased terminal block is not chosen. Wire numbers match the circuit sheets.")
    s.text(12, 16, "Strip  Pin  Wire          Section                 Function")
    col_x = (12, 190)
    rows = list(TERMINALS)
    mid = (len(rows) + 1) // 2
    for column, chunk in enumerate((rows[:mid], rows[mid:])):
        y = 24
        x = col_x[column]
        for strip, pin, wire, function, note in chunk:
            s.text(x, y, f"{strip}.{pin}  {wire}  {note}")
            y += 4


def build_sheets() -> list[Sheet]:
    sheets = [
        Sheet("01-power.kicad_sch", "01 Mains distribution", "2"),
        Sheet("01b-supplies.kicad_sch", "02 24 V supplies", "3"),
        Sheet("02-safety.kicad_sch", "03 E-stop and STO", "4"),
        Sheet("03-hub.kicad_sch", "04 S200 and 1FL2", "5"),
        Sheet("04-sonic.kicad_sch", "05 ATV320 and two MVE", "6"),
        Sheet("05-revpi.kicad_sch", "06 RevPi Connect 4 and DIO", "7"),
        Sheet("06-field.kicad_sch", "07 Field devices", "8"),
        Sheet("06-tilt.kicad_sch", "08 Tilt and lift", "9"),
        Sheet("07-rotation.kicad_sch", "09 Rod rotation proposal", "10"),
        Sheet("08-network.kicad_sch", "10 RUT241 and Modbus", "11"),
        Sheet("09-terminals.kicad_sch", "11 Terminal strips", "12"),
    ]
    builders = (
        build_power, build_supplies, build_safety, build_hub, build_sonic, build_revpi,
        build_field, build_tilt, build_rotation, build_network, build_terminals,
    )
    for sheet, builder in zip(sheets, builders):
        builder(sheet)
    return sheets


def _segments(sheet: Sheet):
    for net, pts in sheet.wires:
        for left, right in zip(pts, pts[1:]):
            yield net, left, right


def _on_open(pt, left, right) -> bool:
    if left[0] == right[0]:
        x = left[0]
        y0, y1 = sorted((left[1], right[1]))
        return pt[0] == x and y0 < pt[1] < y1
    if left[1] == right[1]:
        y = left[1]
        x0, x1 = sorted((left[0], right[0]))
        return pt[1] == y and x0 < pt[0] < x1
    return False


def _component(sheet: Sheet, net: str, start):
    seen = {start}
    stack = [start]
    while stack:
        pt = stack.pop()
        for name, left, right in _segments(sheet):
            if name != net:
                continue
            other = right if left == pt else left if right == pt else None
            if other is not None and other not in seen:
                seen.add(other)
                stack.append(other)
    return seen


def _foreign_between(sheet: Sheet, net: str, a, b) -> bool:
    for name, left, right in _segments(sheet):
        if name == net:
            continue
        for pt in (left, right):
            if _on_open(pt, a, b):
                return True
    return False


def close_rails(sheet: Sheet) -> None:
    """Join a feed-through terminal, then join every tap of one power rail."""
    ends = defaultdict(set)
    for net, left, right in _segments(sheet):
        ends[left].add(net)
        ends[right].add(net)
    for inst in sheet.insts:
        if inst.sym not in ("TERM_H", "TERM_V"):
            continue
        pts = []
        for pin in SYMS[inst.sym].pins:
            if pin.unit == inst.unit:
                pts.append((inst.x + pin.x, inst.y - pin.y))
        if len(pts) != 2:
            continue
        left, right = ends.get(pts[0], set()), ends.get(pts[1], set())
        if len(left) == 1 and left == right and pts[1] not in _component(sheet, next(iter(left)), pts[0]):
            sheet.wire(next(iter(left)), pts[0], pts[1])
    ends = defaultdict(set)
    for net, left, right in _segments(sheet):
        ends[left].add(net)
        ends[right].add(net)

    def stitch(net: str, points):
        points = sorted(set(points))
        for a, b in zip(points, points[1:]):
            if b in _component(sheet, net, a):
                continue
            if _foreign_between(sheet, net, a, b):
                raise SystemExit(f"{sheet.filename} {net} rail {a} to {b} crosses another net")
            sheet.wire(net, a, b)

    for net, x in sheet.rail_x:
        stitch(net, [pt for pt, owners in ends.items() if net in owners and pt[0] == x])
    for net, y in sheet.rail_y:
        stitch(net, [pt for pt, owners in ends.items() if net in owners and pt[1] == y])


def validate(sheets: list[Sheet]) -> None:
    for sheet in sheets:
        close_rails(sheet)
    errors = []
    seen = {}
    for sheet in sheets:
        for inst in sheet.insts:
            key = (inst.ref, inst.unit)
            if key in seen:
                errors.append(f"duplicate {key} on {sheet.filename} and {seen[key]}")
            seen[key] = sheet.filename
        by_ref = defaultdict(set)
        sym_of = {}
        for inst in sheet.insts:
            by_ref[inst.ref].add(inst.unit)
            sym_of[inst.ref] = inst.sym
        for ref, units in by_ref.items():
            needed = set(SYMS[sym_of[ref]].units())
            if units != needed:
                errors.append(f"{sheet.filename} {ref} units {sorted(units)} need {sorted(needed)}")
        ends = defaultdict(set)
        for net, left, right in _segments(sheet):
            ends[left].add(net)
            ends[right].add(net)
            if left[0] != right[0] and left[1] != right[1]:
                errors.append(f"{sheet.filename} slanted {net}")
        for pt, nets in ends.items():
            if len(nets) > 1:
                errors.append(f"{sheet.filename} short at {pt} between {sorted(nets)}")
        segs = list(_segments(sheet))
        for net, left, right in segs:
            for pt, nets in ends.items():
                if _on_open(pt, left, right) and (net not in nets or nets != {net}):
                    errors.append(f"{sheet.filename} {net} endpoint {pt} sits in {sorted(nets)}")
        parent = {}

        def find(pt):
            parent.setdefault(pt, pt)
            while parent[pt] != pt:
                parent[pt] = parent[parent[pt]]
                pt = parent[pt]
            return pt

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for net, left, right in segs:
            union(left, right)
        roots = defaultdict(set)
        for pt, nets in ends.items():
            for net in nets:
                roots[net].add(find(pt))
        for net, parts in roots.items():
            if len(parts) > 1:
                errors.append(f"{sheet.filename} {net} has {len(parts)} separate wires")
        pins = {}
        for inst in sheet.insts:
            for pin in SYMS[inst.sym].pins:
                if pin.unit == inst.unit:
                    pins[(inst.ref, pin.num)] = (inst.x + pin.x, inst.y - pin.y)
        for (ref, num), pt in pins.items():
            owners = ends.get(pt, set())
            if len(owners) > 1:
                errors.append(f"{sheet.filename} {ref}.{num} on {sorted(owners)}")
    if errors:
        raise SystemExit("Layout check failed:\n- " + "\n- ".join(errors[:40]))
    from annotate import overlap_errors, prepare

    pages = defaultdict(list)
    for sheet in sheets:
        for net in {name for name, _pts in sheet.wires}:
            if sheet.page not in pages[net]:
                pages[net].append(sheet.page)
    gate = []
    for sheet in sheets:
        pointer = "Nets that leave this sheet are listed on the notes sheet."
        gate.extend(prepare(sheet, pointer))
        gate.extend(overlap_errors(sheet))
    if gate:
        raise SystemExit("Overlap gate failed (" + str(len(gate)) + " hits):\n- " + "\n- ".join(gate[:40]))


def net_map(sheet: Sheet) -> dict[str, list[tuple[str, str]]]:
    ends = defaultdict(set)
    parent = {}

    def find(pt):
        parent.setdefault(pt, pt)
        while parent[pt] != pt:
            parent[pt] = parent[parent[pt]]
            pt = parent[pt]
        return pt

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for net, pts in sheet.wires:
        for left, right in zip(pts, pts[1:]):
            union(left, right)
            ends[left].add(net)
            ends[right].add(net)
    groups = defaultdict(list)
    for inst in sheet.insts:
        for pin in SYMS[inst.sym].pins:
            if pin.unit != inst.unit:
                continue
            pt = (inst.x + pin.x, inst.y - pin.y)
            if pt in ends:
                groups[find(pt)].append((inst.ref, pin.num, pin.etype, ends[pt]))
    named = {}
    for members in groups.values():
        nets = set()
        for _, _, _, owners in members:
            nets |= owners
        if len(nets) != 1:
            raise SystemExit(f"{sheet.filename} group has nets {nets}")
        net = nets.pop()
        named.setdefault(net, [])
        for ref, num, etype, _ in members:
            named[net].append((ref, num, etype))
    return named


def check_electrical(sheets: list[Sheet]) -> None:
    kinds = defaultdict(list)
    for sheet in sheets:
        for net, members in net_map(sheet).items():
            for _, _, etype in members:
                kinds[net].append(etype)
    errors = []
    for net, items in sorted(kinds.items()):
        if items.count(PO) > 1:
            errors.append(f"{net}: more than one power output")
        if PI in items and PO not in items:
            errors.append(f"{net}: power input is not driven")
        if IN in items and not any(kind in items for kind in (OT, P, PO)):
            errors.append(f"{net}: input is not driven")
        if items.count(OT) > 1:
            errors.append(f"{net}: two outputs")
    missing = [net for net in IO_NETS if net not in kinds]
    if missing:
        errors.append("missing nets " + ", ".join(missing))
    placed = {inst.ref for sheet in sheets for inst in sheet.insts}
    for strip, pin, *_ in TERMINALS:
        ref = f"{strip}.{pin}"
        if ref not in placed:
            errors.append(f"terminal {ref} is not on a sheet")
    if errors:
        raise SystemExit("Electrical check failed:\n- " + "\n- ".join(errors))


def label_spot(sheet: Sheet, net: str):
    """The anchor chosen while the sheet was placed. It lies on the wire."""
    stored = getattr(sheet, "net_labels", {}).get(net)
    if stored is None:
        return None
    x, y, justify = stored
    return (x, y, 0, justify)


def sym_body(sym: Sym, prefixed: bool) -> str:
    parent = f"vibrocore:{sym.name}" if prefixed else sym.name
    bom = "yes" if sym.in_bom else "no"
    lines = [
        f"  (symbol {q(parent)}",
        "    (pin_names (offset 0.508))",
        "    (pin_numbers hide)",
        "    (exclude_from_sim no)",
        f"    (in_bom {bom})",
        "    (on_board yes)",
        f'    (property "Reference" {q(sym.prefix)} (at 0 {f(-(sym.hh + 2))} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" {q(sym.name)} (at 0 {f(sym.hh + 2)} 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
    ]
    for unit in sym.units():
        lines.append(f'    (symbol "{sym.name}_{unit}_1"')
        for graphic in sym.gfx.get(unit, []):
            lines.append("      " + graphic)
        for pin in sym.pins:
            if pin.unit == unit:
                lines.append("      " + pin_sexpr(pin))
        lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)


def library_text() -> str:
    body = "\n".join(sym_body(sym, False) for sym in SYMS.values())
    return (
        "(kicad_symbol_lib\n  (version 20231120)\n  (generator \"eeschema\")\n"
        "  (generator_version \"8.0\")\n" + body + "\n)\n"
    )


def embedded_library() -> str:
    return "\n".join(sym_body(sym, True) for sym in SYMS.values())


def wire_width(net: str) -> str:
    if net[:3] in {"100", "101", "102", "110", "111", "120", "121", "130", "131", "140", "141", "150", "151", "160", "161", "170", "171"}:
        return "0.5"
    if net[:3] in {"540", "541", "542", "543", "544", "600", "601", "602", "610", "611", "612", "620", "621", "622"}:
        return "0.4"
    if net in {"200_24S", "201_24S", "210_24C", "211_24C", "500_24R", "001_0V"}:
        return "0.3"
    return "0.15"


def emit_sheet(sheet: Sheet, path: str, global_nets: dict[str, list[str]]) -> str:
    chunks = []
    # KiCad 8 loads a wire only when it has exactly two points.
    seg_index = 0
    for net, pts in sheet.wires:
        for left, right in zip(pts, pts[1:]):
            chunks.append(
                f"  (wire (pts (xy {f(left[0])} {f(left[1])}) (xy {f(right[0])} {f(right[1])})) "
                f"(stroke (width {wire_width(net)}) (type default)) "
                f"(uuid {q(uid(sheet.filename + net + str(seg_index)))}))"
            )
            seg_index += 1
    degree = defaultdict(int)
    for _, pts in sheet.wires:
        for left, right in zip(pts, pts[1:]):
            degree[left] += 1
            degree[right] += 1
    for pt, count in degree.items():
        if count >= 3:
            chunks.append(
                f"  (junction (at {f(pt[0])} {f(pt[1])}) (diameter 0) (color 0 0 0 0) "
                f"(uuid {q(uid(sheet.filename + 'j' + str(pt)))}))"
            )
    labelled = set()
    for net in sorted({name for name, _ in sheet.wires}):
        spot = label_spot(sheet, net)
        if spot is None:
            continue
        x, y, angle, justify = spot
        labelled.add(net)
        kind = "global" if net in global_nets else "local"
        shown = sexpr_justify(justify)
        clause = f" (justify {shown})" if shown else ""
        if kind == "global":
            chunks.append(
                f"  (global_label {q(net)} (shape passive) (at {f(x)} {f(y)} {angle}) "
                f"(effects (font (size 1.27 1.27)){clause}) "
                f"(uuid {q(uid(sheet.filename + 'g' + net))}))"
            )
        else:
            chunks.append(
                f"  (label {q(net)} (at {f(x)} {f(y)} {angle}) "
                f"(effects (font (size 1.27 1.27)){clause}) "
                f"(uuid {q(uid(sheet.filename + 'l' + net))}))"
            )
    wired = defaultdict(set)
    for net, pts in sheet.wires:
        for left, right in zip(pts, pts[1:]):
            wired[left].add(net)
            wired[right].add(net)
    for inst in sheet.insts:
        for pin in SYMS[inst.sym].pins:
            if pin.unit != inst.unit:
                continue
            pt = (inst.x + pin.x, inst.y - pin.y)
            if pt not in wired:
                chunks.append(
                    f"  (no_connect (at {f(pt[0])} {f(pt[1])}) "
                    f"(uuid {q(uid(sheet.filename + inst.ref + str(inst.unit) + pin.num))}))"
                )
    for inst in sheet.insts:
        symbol = SYMS[inst.sym]
        pins = [pin for pin in symbol.pins if pin.unit == inst.unit]
        pin_lines = "\n".join(
            f"    (pin {q(pin.num)} (uuid {q(uid(sheet.filename + inst.ref + str(inst.unit) + pin.num + 'p'))}))"
            for pin in pins
        )
        bom = "yes" if inst.in_bom else "no"
        ref_hide = " hide" if inst.hide_ref else ""
        val_hide = " hide" if inst.hide_value else ""
        ref_shown = sexpr_justify(inst.ref_justify)
        val_shown = sexpr_justify(inst.val_justify)
        ref_just = f" (justify {ref_shown})" if ref_shown else ""
        val_just = f" (justify {val_shown})" if val_shown else ""
        chunks.append(
            f"""  (symbol (lib_id {q("vibrocore:" + inst.sym)}) (at {f(inst.x)} {f(inst.y)} 0) (unit {inst.unit})
    (exclude_from_sim no) (in_bom {bom}) (on_board yes) (dnp no)
    (uuid {q(uid(sheet.filename + inst.ref + str(inst.unit) + "sym"))})
    (property "Reference" {q(inst.ref)} (at {f(inst.x + inst.ref_dx)} {f(inst.y + inst.ref_dy)} 0) (effects (font (size 1.27 1.27)){ref_just}{ref_hide}))
    (property "Value" {q(inst.value)} (at {f(inst.x + inst.val_dx)} {f(inst.y + inst.val_dy)} 0) (effects (font (size 1.27 1.27)){val_just}{val_hide}))
    (property "Footprint" "" (at {f(inst.x)} {f(inst.y)} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (at {f(inst.x)} {f(inst.y)} 0) (effects (font (size 1.27 1.27)) hide))
{pin_lines}
    (instances (project {q(PROJECT)} (path {q(path)} (reference {q(inst.ref)}) (unit {inst.unit}))))
  )"""
        )
    for index, (left, right) in enumerate(sheet.dashes):
        chunks.append(
            f"  (polyline (pts (xy {f(left[0])} {f(left[1])}) (xy {f(right[0])} {f(right[1])})) "
            f"(stroke (width 0.15) (type dash)) (uuid {q(uid(sheet.filename + 'd' + str(index)))}))"
        )
    for index, (x, y, text) in enumerate(sheet.texts):
        chunks.append(
            f"  (text {q(text)} (exclude_from_sim no) (at {f(x)} {f(y)} 0) "
            f"(effects (font (size 1.27 1.27)) (justify left)) "
            f"(uuid {q(uid(sheet.filename + 't' + str(index) + text[:12]))}))"
        )
    note_chunks = []
    for index, (x0, y0, x1, y1) in enumerate(getattr(sheet, "frames", [])):
        note_chunks.append(
            "  (polyline (pts "
            f"(xy {x0:.2f} {y0:.2f}) (xy {x1:.2f} {y0:.2f}) "
            f"(xy {x1:.2f} {y1:.2f}) (xy {x0:.2f} {y1:.2f}) "
            f"(xy {x0:.2f} {y0:.2f})) "
            f"(stroke (width 0.3) (type default)) (uuid {q(uid(sheet.filename + 'frame' + str(index)))}))"
        )
    if getattr(sheet, "band_lines", None):
        from annotate import BAND
        x0, y0, x1, y1 = BAND
        note_chunks.append(
            "  (polyline (pts "
            f"(xy {x0:.2f} {y0:.2f}) (xy {x1:.2f} {y0:.2f}) "
            f"(xy {x1:.2f} {y1:.2f}) (xy {x0:.2f} {y1:.2f}) "
            f"(xy {x0:.2f} {y0:.2f})) "
            "(stroke (width 0.3) (type default)) "
            f"(uuid {q(uid(sheet.filename + 'band'))}))"
        )
        ox, oy = sheet.band_origin
        note_chunks.append(
            f"  (text {q(chr(10).join(sheet.band_lines))} (exclude_from_sim no) (at {ox:.2f} {oy:.2f} 0) "
            f"(effects (font (size 1.27 1.27)) (justify left top)) "
            f"(uuid {q(uid(sheet.filename + 'note'))}))"
        )
    for index, (mx, my, marker) in enumerate(getattr(sheet, "markers", [])):
        note_chunks.append(
            f"  (text {q(marker)} (exclude_from_sim no) (at {mx:.2f} {my:.2f} 0) "
            f"(effects (font (size 1.27 1.27)) (justify left)) "
            f"(uuid {q(uid(sheet.filename + 'm' + str(index)))}))"
        )
    for index, (x, y, text) in enumerate(getattr(sheet, "notes_columns", []) or []):
        note_chunks.append(
            f"  (text {q(text)} (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) "
            f"(effects (font (size 1.27 1.27)) (justify left top)) "
            f"(uuid {q(uid(sheet.filename + 'col' + str(index)))}))"
        )
    note = "\n".join(note_chunks)
    return f"""(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (generator_version "8.0")
  (uuid {q(uid(sheet.filename + "file"))})
  (paper "A3")
  (title_block
    (title {q(sheet.title)})
    (date "2026-11-20")
    (rev "0C")
    (company "Ground UP GmbH")
    (comment 1 "VC-SCH-5000. Notes are numbered in the band above the title block.")
    (comment 2 "Safety is hard-wired. The RevPi only reads feedback.")
  )
  (lib_symbols
{embedded_library()}
  )
{note}
{chr(10).join(chunks)}
  (sheet_instances (path {q(path)} (page {q(sheet.page)})))
)
"""


def globals_of(sheets: list[Sheet]) -> dict[str, list[str]]:
    found = defaultdict(list)
    for sheet in sheets:
        for net in sorted({name for name, _ in sheet.wires}):
            if sheet.page not in found[net]:
                found[net].append(sheet.page)
    return {net: pages for net, pages in found.items() if len(pages) > 1}


def root_text(sheets: list[Sheet], uuids: dict[str, str]) -> str:
    from annotate import BAND, index_positions

    blocks = []
    for (x, y), sheet in zip(index_positions(len(sheets)), sheets):
        su = uuids[sheet.filename]
        blocks.append(
            f"""  (sheet (at {x:.2f} {y:.2f}) (size 150.00 16.00)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid {q(su)})
    (property "Sheetname" {q(sheet.title)} (at {x:.2f} {y - 0.60:.2f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" {q(sheet.filename)} (at {x:.2f} {y + 16.00:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances (project {q(PROJECT)} (path "/" (page {q(sheet.page)}))))
  )"""
        )
    intro = "\n".join([
        "(1) VC-SCH-5000 revision 0C. Wires are drawn on the circuit sheets.",
        "(2) A global label is a wire that continues on another sheet.",
        "(3) OPEN means the order code is not chosen. TBC means the pin is not confirmed.",
        "(4) Product text is the maker and the short type, then the Ground UP article.",
        "(5) Numbered notes sit in this band. A marker such as (1) is the only note in the circuit.",
        "(6) The notes sheet lists the nets that leave a sheet.",
    ])
    x0, y0, x1, y1 = BAND
    band = (
        "  (polyline (pts "
        f"(xy {x0:.2f} {y0:.2f}) (xy {x1:.2f} {y0:.2f}) "
        f"(xy {x1:.2f} {y1:.2f}) (xy {x0:.2f} {y1:.2f}) (xy {x0:.2f} {y0:.2f})) "
        f"(stroke (width 0.3) (type default)) (uuid {q(uid('root-band'))}))\n"
        f"  (text {q(intro)} (exclude_from_sim no) (at {x0 + 1.6:.2f} {y0 + 1.4:.2f} 0)\n"
        f"    (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid('root-intro'))}))"
    )
    total = len(sheets) + 1
    return f"""(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (generator_version "8.0")
  (uuid {q(uid("root"))})
  (paper "A3")
  (title_block
    (title "Vibrocore cabinet schematic")
    (date "2026-11-20")
    (rev "0C")
    (company "Ground UP GmbH")
    (comment 1 "VC-SCH-5000 sheet 01 of {total}")
    (comment 2 "Hard-wired STO. RevPi reads feedback only.")
  )
  (lib_symbols)
{band}
{chr(10).join(blocks)}
  (sheet_instances (path "/" (page "1")))
)
"""


def cross_columns(global_nets: dict[str, list[str]]) -> tuple[str, str]:
    lines = [f"{net}  {' '.join(pages)}" for net, pages in sorted(global_nets.items())]
    mid = (len(lines) + 1) // 2
    return "\n".join(lines[:mid]), "\n".join(lines[mid:])


def project_text() -> str:
    return """{
  "meta": {"filename": "vibrocore-control.kicad_pro", "version": 1},
  "board": {"design_settings": {"defaults": {}, "meta": {"version": 2}}},
  "net_settings": {},
  "schematic": {
    "legacy_lib_dir": "",
    "legacy_lib_list": [],
    "meta": {"version": 1},
    "drawing": {
      "intersheets_ref_show": true,
      "intersheets_ref_own_page": false,
      "intersheets_ref_prefix": "[",
      "intersheets_ref_suffix": "]",
      "intersheets_ref_short": false
    }
  },
  "sheets": [],
  "text_variables": {}
}
"""


def build_notes_sheet(sheets: list[Sheet]) -> Sheet:
    from annotate import layout_notes_page

    page = len(sheets) + 2
    sheet = Sheet("10-notes.kicad_sch", f"{page - 1:02d} Notes and net list", str(page))
    for source in sheets:
        for line in source.overflow:
            sheet.add_note(f"{source.title}. {line}")
    nets = globals_of(sheets)
    sheet.add_note("Nets that leave their sheet. The numbers are the sheet pages.")
    for net, pages in sorted(nets.items()):
        sheet.add_note(f"{net} is also on sheet {', '.join(pages)}.")
    layout_notes_page(sheet)
    return sheet


def write_tree(directory: Path) -> None:
    from annotate import index_errors, overlap_errors

    sheets = build_sheets()
    validate(sheets)
    check_electrical(sheets)
    notes = build_notes_sheet(sheets)
    gate = overlap_errors(notes)
    gate.extend(index_errors([sheet.title for sheet in sheets + [notes]], [sheet.filename for sheet in sheets + [notes]]))
    if gate:
        raise SystemExit("Overlap gate failed:\n- " + "\n- ".join(gate[:40]))
    sheets.append(notes)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "vibrocore.kicad_sym").write_text(library_text(), encoding="utf-8")
    (directory / "sym-lib-table").write_text(
        "(sym_lib_table\n"
        '  (lib (name "vibrocore")(type "KiCad")(uri "${KIPRJMOD}/vibrocore.kicad_sym")(options "")(descr "Vibrocore cabinet symbols"))\n'
        ")\n",
        encoding="utf-8",
    )
    global_nets = globals_of(sheets)
    uuids = {sheet.filename: uid("sheet-" + sheet.filename) for sheet in sheets}
    for sheet in sheets:
        path = "/" + uuids[sheet.filename]
        (directory / sheet.filename).write_text(emit_sheet(sheet, path, global_nets), encoding="utf-8")
    (directory / "vibrocore-control.kicad_sch").write_text(
        root_text(sheets, uuids), encoding="utf-8"
    )
    (directory / "vibrocore-control.kicad_pro").write_text(project_text(), encoding="utf-8")


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


def sheet_names() -> list[str]:
    return [sheet.filename for sheet in build_sheets()]
