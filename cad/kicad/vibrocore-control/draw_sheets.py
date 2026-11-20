"""Sheet wiring for the Vibrocore cabinet schematic."""

from __future__ import annotations

import filecmp
from collections import defaultdict
from pathlib import Path

from schlib import IN, OT, P, PI, PO, SYMS, Sym, f, pin_sexpr, q

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
    s.notes = [
        "Instagrid ONE max is the only AC source. Continuous current is 15.7 A.",
        "Q1 does not switch PE. QF1 is type B, 30 mA.",
        "F2 stays C16. The ATV320 input is 17.8 A at 200 V.",
        "Confirm F2 before you order it. Its order code is not frozen.",
        "The S200 feeder is 2.5 mm2. The sonic feeder is 4 mm2.",
        "The general 24 V rail is 2.5 mm2. The S200 24 V feed is 1.0 mm2.",
        "Both 0 V rails meet at X1 pin 4. W1 is the only bond to PE.",
        "Confirm W1 in the S200 PTI manual. Remove W1 if that manual forbids the bond.",
        "There is no 48 V rail. SDR-120-24 feeds only S200 X124.",
        "A crossing without a dot is not a connection.",
    ]
    s.place("G0", "SRC", 22, 18, "VC-PW-5100 Instagrid")
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
    s.link("110_L", ("Q1", "2"), ("QF1", "1"))
    s.link("111_N", ("Q1", "4"), ("QF1", "3"))
    f_top = s.pin("QF1", "2")[1] + 6
    pair(s, "F1", "MCB2", lx, f_top, "VC-PW-5710 C20", dx=dx)
    s.link("120_L", ("QF1", "2"), ("F1", "1"))
    s.link("121_N", ("QF1", "4"), ("F1", "3"))
    bus_l = s.pin("F1", "2")[1] + 8
    bus_n = bus_l + 24
    s.wire("130_L", s.pin("F1", "2"), (lx, bus_l))
    s.wire("131_N", s.pin("F1", "4"), (nx, bus_n))
    branches = [
        ("F2", "VC-PW-5730 C16", "140_L", "141_N", "4 mm2", True),
        ("F3", "VC-PW-5740 C16", "150_L", "151_N", "2.5 mm2", True),
        ("F4", "VC-PW-5750 C4", "160_L", "161_N", "1.5 mm2", False),
        ("F5", "VC-PW-5760 C10", "170_L", "171_N", "2.5 mm2", False),
    ]
    bx = lx + 40
    for index, (ref, value, net_l, net_n, label, leaves) in enumerate(branches):
        x = bx + index * 46
        s.place_pin(ref, "MCB2", "1", x, bus_l, value, unit=1, val_dx=18, val_dy=-11, ref_dy=-11)
        s.place_pin(ref, "MCB2", "3", x + 16, bus_n, value, unit=2, hide_value=True, ref_dy=-11)
        s.dash(ref)
        if leaves:
            s.stub(net_l, (ref, "2"), dy=2)
            s.stub(net_n, (ref, "4"), dy=2)
            s.text(x - 2, s.pin(ref, "2")[1] + 6, label)
    refs = [row[0] for row in branches]
    s.hrail("130_L", bus_l, [(lx, bus_l)] + [(ref, "1") for ref in refs])
    s.hrail("131_N", bus_n, [(nx, bus_n)] + [(ref, "3") for ref in refs])
    s.text(lx + 2, bus_l - 4, "L  4 mm2 on the sonic branch, 2.5 mm2 on the S200 branch")
    s.place("G1", "PSU0", 150, 150, "VC-PW-5310 SDR-120-24")
    s.place("G2", "PSU", 250, 150, "VC-PW-5320 SDR-480-24 slot")
    gutter = nx + 8
    gutter2 = gutter + 8
    for ref, psu, net_l, net_n, gy, gx in (
        ("F4", "G1", "160_L", "161_N", bus_l + 18, gutter),
        ("F5", "G2", "170_L", "171_N", bus_l + 22, gutter2),
    ):
        load_l = s.pin(ref, "2")
        load_n = s.pin(ref, "4")
        dst_l = s.pin(psu, "L")
        dst_n = s.pin(psu, "N")
        s.wire(net_l, load_l, (load_l[0], gy), (dst_l[0], gy), dst_l)
        s.wire(net_n, load_n, (load_n[0], dst_n[1] + 8), (dst_n[0], dst_n[1] + 8), dst_n)
    for psu, net_in, net_out, fuse_ref, fuse_value, flag in (
        ("G1", "200_24S", "201_24S", "F14", "VC-PW-5800 6A", "PF1"),
        ("G2", "210_24C", "211_24C", "F24", "VC-PW-5810 20A", "PF2"),
    ):
        plus = s.pin(psu, "P")
        s.place_pin(fuse_ref, "FUSE", "1", plus[0] + 18, plus[1], fuse_value, ref_dx=8)
        s.link(net_in, (psu, "P"), (fuse_ref, "1"))
        out = s.pin(fuse_ref, "2")
        s.place_pin(flag, "PWR", "1", out[0], out[1] + 10, net_out, hide_value=True)
        s.link(net_out, (fuse_ref, "2"), (flag, "1"))
    zero = 186
    s.place_pin("X1.4", "TERM_H", "2", 120, zero, "X1:4", ref_dy=-6)
    s.place_pin("W1", "BOND", "1", 300, zero, "W1 bond", ref_dy=-8)
    s.hrail("001_0V", zero, [("G1", "M"), ("G2", "M"), ("X1.4", "1"), ("X1.4", "2"), ("W1", "1")])
    s.place_pin("PE1", "EARTH", "1", pe, zero + 12, "PE", hide_value=True, hide_ref=True)
    s.place_pin("PF0", "PWR", "1", pe + 12, zero + 12, "PE", hide_value=True, hide_ref=True)
    s.vrail("102_PE", pe, [("X1.3", "2"), ("PE1", "1"), ("PF0", "1"), (pe, zero + 8)])
    s.wire("102_PE", s.pin("W1", "2"), (s.pin("W1", "2")[0], zero + 12), (pe, zero + 12))
    s.hrail("102_PE", zero + 8, [("G1", "PE"), ("G2", "PE"), (pe, zero + 8)])
    s.text(78, zero - 4, "0 V star. W1 bonds 0 V to PE.")
    s.note_at = (190, 8)


def build_safety(s: Sheet) -> None:
    s.notes = [
        "Two NC channels go to the PNOZ. The third NC is DIO input 3 only.",
        "Do not feed cabinet 24 V into S11 or S21. The PNOZ makes the test pulses.",
        "Set two channels, short detection and a monitored reset.",
        "The rotary-switch detent text is TBC. Do not adjust it during operation.",
        "Contact 13-14 is STO channel 1 for both drives.",
        "Contact 23-24 is STO channel 2 for both drives.",
        "41-42 is the monitor. Do not use it in the safety path. Its state is TBC.",
        "33-34 is spare. Do not load it. Y32 is not a safety output.",
        "OPEN: the E-stop contact block is not chosen. Confirm the printed numbers.",
        "OPEN: the reset button order code and colour are not chosen.",
        "The RevPi only reads feedback. Do not claim an ISO 13849 PL.",
    ]
    s.place("K1", "PNOZ", 168, 108, "VC-CT-6220 750104", unit=1)
    y11 = s.pin("K1", "S11")
    s.place_pin("S1", "ESTOP", "11", y11[0] - 16, y11[1], "VC-CT-6210 OPEN", unit=1, val_dy=-12)
    y21 = s.pin("K1", "S21")
    s.place_pin("S1", "ESTOP", "21", y21[0] - 16, y21[1], "VC-CT-6210 OPEN", unit=2, hide_value=True)
    s.place_pin("S1", "ESTOP", "31", 90, s.pin("K1", "S22")[1] + 24, "VC-CT-6210 OPEN", unit=3, hide_value=True)
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
    s.place_pin("K1", "PNOZ", "13", s.pin("F30", "2")[0] + 24, s.pin("F30", "2")[1], "13-14", unit=2, hide_value=True, ref_dy=-10)
    s.link("430_F30", ("F30", "2"), ("K1", "13"))
    s.stub("431_STO1", ("K1", "14"), dx=16)
    s.place_pin("F31", "FUSE", "2", 250, s.pin("K1", "14")[1] + 24, "VC-PW-5820 2A", ref_dx=8)
    s.place_pin("K1", "PNOZ", "23", s.pin("F31", "2")[0] + 24, s.pin("F31", "2")[1], "23-24", unit=3, hide_value=True, ref_dy=-10)
    s.link("432_F31", ("F31", "2"), ("K1", "23"))
    s.stub("433_STO2", ("K1", "24"), dx=16)
    s.place_pin("K1", "PNOZ", "33", 300, s.pin("K1", "24")[1] + 22, "33-34 spare", unit=4, hide_value=True, ref_dy=-10)
    s.text(300, s.pin("K1", "34")[1] + 6, "Spare. Do not load.")
    s.place_pin("K1", "PNOZ", "41", 250, s.pin("K1", "33")[1] + 20, "41-42", unit=5, hide_value=True, ref_dy=-10)
    s.stub("421_PNOZ", ("K1", "42"), dx=16)
    s.stub("420_ESTOP", ("S1", "31"), dx=16)
    rail = 28
    s.vrail("211_24C", rail, [("K1", "A1"), ("F30", "1"), ("F31", "1"), ("K1", "41"), ("S1", "32")])
    s.vrail("001_0V", rail + 12, [("K1", "A2")])
    s.text(250, s.pin("K1", "14")[1] - 4, "STO ch 1  0.75 mm2")
    s.text(250, s.pin("K1", "24")[1] - 4, "STO ch 2  0.75 mm2")
    s.note_at = (12, 200)


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
    s.notes = [
        "Order 6SL5510-1BB11-0AA0. This is the PTI standard drive, not the PROFINET code.",
        "X131 pins are 1 STO1+, 2 STO1-, 3 STO-VS, 4 STO-M, 5 STO2+, 6 STO2-.",
        "STO-VS and STO-M are TBC. Do not land 24 V on them until the figure is confirmed.",
        "X130 is not on this PTI drive. STO status is status word bit STO_EP.",
        "Do not land 440_S200FB until a digital output is assigned.",
        "X124 screws are marked 24 V and 0 V. They are not numbered. Both screws are one node.",
        "L2 is open. Mains uses L1 and L3. DCP, R1 and R2 stay open. Fit the blanking plug.",
        "U1 is not a DIO pin. Pulse form and scale are TBC.",
        "Encoder map, drive to motor: 7 A, 8 B, 4 C, 5 D, 1 E, 2 F.",
        "The catalogue cable carries those cores. Siemens order code is TODO.",
        "Power cable is 4G1.5 mm2 shielded. Brake pair is 2x0.75 mm2.",
        "There is no second holding brake. The coil stays on X108.",
    ]
    s.place("A2", "S200", 150, 118, "VC-HB-2300 6SL5510-1BB11-0AA0")
    for pin, net in (("L1", "150_L"), ("L3", "151_N"), ("1", "431_STO1"), ("5", "433_STO2"), ("FB", "440_S200FB")):
        _stub_left(s, net, "A2", pin)
    side_net(s, "201_24S", [("A2", "24V"), ("A2", "24Vb")], -12)
    side_net(s, "001_0V", [("A2", "0V"), ("A2", "0Vb"), ("A2", "2"), ("A2", "6")], -20)
    uy = s.pin("A2", "U")[1]
    s.place_pin("M1", "MSRV", "U", s.pin("A2", "U")[0] + 78, uy, "VC-HB-2100 1FL2104")
    s.place_pin("U1", "PULSE", "P", s.pin("A2", "36")[0] + 36, s.pin("A2", "36")[1], "pulse source TODO", in_bom=False)
    pairs = (("U", "X4.1", "540_U", "U"), ("V", "X4.2", "541_V", "V"), ("W", "X4.3", "542_W", "W"))
    for drive, term, net, motor in pairs:
        dx, dy = s.pin("A2", drive)
        s.place_pin(term, "TERM_H", "1", dx + 24, dy, term)
        s.join(net, ("A2", drive), (term, "1"), (term, "2"), ("M1", motor))
    s.place_pin("X4.4", "TERM_H", "1", s.pin("A2", "PE2")[0] + 24, s.pin("A2", "PE2")[1], "X4.4")
    s.join("102_PE", ("A2", "PE2"), ("X4.4", "1"), ("X4.4", "2"), ("M1", "PE"))
    s.place_pin("X6.1", "TERM_H", "1", s.pin("A2", "BRP")[0] + 24, s.pin("A2", "BRP")[1], "X6.1")
    s.place_pin("X6.2", "TERM_H", "1", s.pin("A2", "BRN")[0] + 24, s.pin("A2", "BRN")[1], "X6.2")
    s.join("543_BRP", ("A2", "BRP"), ("X6.1", "1"), ("X6.1", "2"), ("M1", "BRP"))
    s.join("544_BRN", ("A2", "BRN"), ("X6.2", "1"), ("X6.2", "2"), ("M1", "BRN"))
    s.place_pin("X5.1", "TERM_H", "1", s.pin("A2", "X120")[0] + 24, s.pin("A2", "X120")[1], "X5.1")
    s.place_pin("X5.2", "TERM_H", "1", s.pin("X5.1", "2")[0] + 20, s.pin("A2", "X120")[1] + 10, "X5.2")
    s.join("510_ENC", ("A2", "X120"), ("X5.1", "1"), ("X5.1", "2"))
    s.stub("510_ENC", ("X5.1", "2"), dx=14)
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
    shield = s.pin("X5.2", "1")
    s.wire("102_PE", s.pin("X5.2", "2"), shield, (shield[0], right_pe[1]), right_pe)
    s.text(s.pin("X5.1", "2")[0], s.pin("X5.1", "2")[1] - 6, "VC-HB-3450 catalogue cable. Order TODO.")
    for src, dst, net in (("P", "36", "520_PULSP"), ("N", "37", "521_PULSN"), ("D", "38", "522_SIGNP"), ("E", "39", "523_SIGNN")):
        s.link(net, ("U1", src), ("A2", dst))
    s.place_pin("R1", "RES", "1", s.pin("A2", "23")[0] + 28, s.pin("A2", "23")[1], "VC-CT-6790 120R")
    s.join("910_A", ("A2", "23"), ("R1", "1"))
    s.join("911_B", ("A2", "25"), ("R1", "2"))
    s.stub("910_A", ("R1", "1"), dy=16)
    s.stub("911_B", ("R1", "2"), dy=16)
    s.text(s.pin("A2", "U")[0] + 4, s.pin("A2", "U")[1] - 4, "4G1.5 shielded")
    s.note_at = (12, 214)


def build_sonic(s: Sheet) -> None:
    s.notes = [
        "One ATV320 output feeds both OLI MVE 400/6-HF motors. Each motor is 1.45 A.",
        "Motor B swaps V and W at X3 so the motors turn in opposite directions.",
        "OPEN: F21 and F22 need a PWM-rated protector. The order code is not chosen.",
        "Do not fit a standard GV2. Do not invent an order code.",
        "The drive STO screw is one terminal. DI3 is the second channel.",
        "Assign DI3 in SoMove. The parameter name is TODO.",
        "Do not tie P24 to the cabinet 24 V.",
        "R1C is the fault-relay common. R1B is the NC contact. R1A is open.",
        "The R1 logic assignment is still TODO. R2 parameter is TODO.",
        "RJ45 pin numbers are TBC. See the Modbus manual NVE41308.",
        "PA, PB, PC and P0 stay open. There is no braking resistor.",
        "Output cable is 4G1.5 mm2 shielded. Shield at the drive end.",
    ]
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
        s.place_pin("F21", "MPROT", ypin, px + 40, py, "VC-PW-5770 OPEN", unit=unit, hide_value=unit != 1, ref_dy=-8)
    s.dash("F21")
    for unit, drive, ypin in ((1, "U", "1"), (2, "V", "3"), (3, "W", "5")):
        px, py = s.pin("A3", drive)
        s.place_pin("F22", "MPROT", ypin, px + 40, py + 36, "VC-PW-5770 OPEN", unit=unit, hide_value=True, ref_dy=-8)
    s.dash("F22")
    s.place_pin("M2", "M3", "U", s.pin("F21", "2")[0] + 70, s.pin("A3", "U")[1], "VC-SH-1100 motor A")
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
    s.place_pin("X2.4", "TERM_H", "1", s.pin("M2", "PE")[0] - 24, s.pin("M2", "PE")[1], "X2.4")
    s.join("102_PE", ("A3", "PE2"), ("X2.4", "1"), ("X2.4", "2"), ("M2", "PE"))
    s.place_pin("M3", "M3", "U", s.pin("F22", "2")[0] + 78, s.pin("F22", "2")[1], "VC-SH-1100 motor B")
    # Swap V and W on the way to motor B. The jogs sit side by side.
    lanes = {"V": s.pin("F22", "4")[0] + 16, "W": s.pin("F22", "4")[0] + 24}
    mapping = (
        ("6", "X3.2", "622_WB", "V", "W"),
        ("4", "X3.3", "621_VB", "W", "V"),
        ("2", "X3.1", "620_UB", "U", None),
    )
    for fout, term, net, motor, lane in mapping:
        dest = s.pin("M3", motor)
        src = s.pin("F22", fout)
        s.place_pin(term, "TERM_H", "1", dest[0] - 28, dest[1], term)
        if lane is None:
            s.join(net, ("F22", fout), (term, "1"))
        else:
            s.wire(net, src, (lanes[lane], src[1]), (lanes[lane], dest[1]), s.pin(term, "1"))
        s.link(net, (term, "2"), ("M3", motor))
    s.place_pin("X3.4", "TERM_H", "1", s.pin("M3", "PE")[0] - 24, s.pin("M3", "PE")[1], "X3.4")
    s.join("102_PE", ("X3.4", "1"), ("X3.4", "2"), ("M3", "PE"), ("A3", "PE2"))
    s.text(s.pin("M3", "U")[0] - 20, s.pin("M3", "U")[1] - 8, "Swap V and W at X3")
    s.text(s.pin("M2", "U")[0] - 10, s.pin("M2", "U")[1] - 8, "4G1.5 shielded")
    s.note_at = (12, 220)


def _contact_24(s: Sheet, ref: str, sym: str, signal: str, y: int, x_signal: int, value: str) -> None:
    s.place_pin(ref, sym, "2", x_signal, y, value)
    s.vrail("211_24C", 24, [(ref, "1")])


def build_revpi(s: Sheet) -> None:
    s.notes = [
        "Controller 100378. DIO 100197. PiBridge plug is 100204.",
        "I1 is I/O-list index 0. Channel names are not a confirmed plug order.",
        "Confirm the 14-pin plug order on the Kunbus drawing before you wire it.",
        "X4 order 24 V, 0 V, NC, FG is TBC. RS-485 order GND, N, P is TBC.",
        "The signal names 24 V, 0 V, FG, P, N and GND are the documented names.",
        "OPEN: the index sensor order code is not chosen. The symbol is PNP.",
        "Spare inputs and outputs stay open.",
        "ETH1 is a service port. Do not put it in the harness.",
        "There is no PFC200 and no CODESYS target on this drawing.",
    ]
    s.place("A4", "REVPI", 48, 36, "VC-CT-6800 100378")
    s.place("A5", "DIO", 210, 120, "VC-CT-6810 100197")
    s.link("940_BRIDGE", ("A4", "BR"), ("A5", "BR"))
    s.stub("930_ETH", ("A4", "ETH0"), dx=14)
    s.vrail("211_24C", 16, [("A4", "24"), ("A5", "X2_1"), ("A5", "X2_4"), ("A5", "X4_1")])
    s.vrail("001_0V", 28, [("A4", "0"), ("A4", "GND"), ("A5", "X2_2"), ("A5", "X2_3"), ("A5", "X4_2")])
    s.vrail("102_PE", 40, [("A4", "FG"), ("A5", "X4_4")])
    s.stub("910_A", ("A4", "P"), dx=-14)
    s.stub("911_B", ("A4", "N"), dx=-14)
    field = [
        ("I1", "460_LIM_UP", "SW_NC", "S4", "VC-CT-6200", "X7.1"),
        ("I2", "461_LIM_DN", "SW_NC", "S5", "VC-CT-6200", "X7.2"),
        ("I7", "462_ENABLE", "SW_NO", "S6", "VC-CT-6260 HE1B-M1", "X7.3"),
    ]
    for dio, net, sym, ref, value, term in field:
        y = s.pin("A5", dio)[1]
        x = s.pin("A5", dio)[0]
        s.place_pin(term, "TERM_H", "2", x - 22, y, term)
        s.place_pin(ref, sym, "2", x - 52, y, value)
        s.join(net, ("A5", dio), (term, "2"), (term, "1"), (ref, "2"))
        s.vrail("211_24C", 16, [(ref, "1")])
    y = s.pin("A5", "I13")[1]
    x = s.pin("A5", "I13")[0]
    s.place_pin("X7.4", "TERM_H", "2", x - 22, y, "X7.4")
    s.place_pin("B1", "PNP", "OUT", x - 60, y, "VC-CT-6250 OPEN")
    s.join("480_INDEX", ("A5", "I13"), ("X7.4", "2"), ("X7.4", "1"), ("B1", "OUT"))
    s.vrail("211_24C", 16, [("B1", "24")])
    s.vrail("001_0V", 28, [("B1", "0")])
    for dio, net, term in (("I8", "470_TILT_V", "X7.5"), ("I9", "471_TILT_F", "X7.6")):
        x, y = s.pin("A5", dio)
        s.place_pin(term, "TERM_H", "2", x - 22, y, term)
        s.join(net, ("A5", dio), (term, "2"), (term, "1"))
        s.stub(net, (term, "1"), dx=-12)
    # Lift limits, two NC in series, then the terminal and the DIO pin.
    for dio, net, mid, first, second, term in (
        ("I10", "472_LIFT_D", "474_DMID", "S14", "S15", "X7.7"),
        ("I11", "473_LIFT_R", "475_RMID", "S16", "S17", "X7.8"),
    ):
        x, y = s.pin("A5", dio)
        s.place_pin(term, "TERM_H", "2", x - 20, y, term)
        s.place_pin(second, "SW_NC", "2", x - 46, y, second + " NC")
        s.place_pin(first, "SW_NC", "2", x - 74, y, first + " NC")
        s.join(net, ("A5", dio), (term, "2"), (term, "1"), (second, "2"))
        s.link(mid, (second, "1"), (first, "2"))
        s.vrail("211_24C", 16, [(first, "1")])
    for dio, net in (
        ("I3", "420_ESTOP"), ("I4", "421_PNOZ"), ("I5", "440_S200FB"),
        ("I6", "452_SONSTO"), ("I12", "451_FAULT"),
    ):
        _stub_left(s, net, "A5", dio)
    outs = [
        ("O1", "490_EXT", None), ("O2", "491_RET", None), ("O3", "492_TILTV", None),
        ("O4", "493_TILTF", None), ("O6", "450_RESET", None), ("O7", "495_ROT_EN", None),
    ]
    for dio, net, _ in outs:
        s.stub(net, ("A5", dio), dx=16)
    x, y = s.pin("A5", "O5")
    s.place_pin("X7.9", "TERM_H", "1", x + 24, y, "X7.9")
    s.place_pin("H1", "LAMP", "1", x + 48, y - 8, "VC-CT-6230")
    s.join("494_BEACON", ("A5", "O5"), ("X7.9", "1"), ("X7.9", "2"), ("H1", "1"))
    s.vrail("001_0V", s.pin("H1", "2")[0], [("H1", "2")])
    for ref, net, xrail in (("X7.10", "211_24C", 16), ("X7.11", "001_0V", 28), ("X7.12", "102_PE", 40)):
        s.place_pin(ref, "TERM_V", "1", xrail, 188, ref, ref_dx=8, ref_dy=-6)
        s.vrail(net, xrail, [(ref, "1"), (ref, "2")])
    s.text(16, 8, "OPEN index sensor. DIO plug order is TBC.")
    s.note_at = (230, 8)


def build_tilt(s: Sheet) -> None:
    s.notes = [
        "Each tilt coil is in series with the NC contact of the other relay.",
        "The off state puts both motor leads on 0 V.",
        "Do not command both tilt directions.",
        "Do not command both lift directions.",
        "The actuator current is not on a nameplate. Power section is TBC.",
        "Confirm that both leads may sit on 0 V.",
        "Confirm that Finder .4000 has no internal diode. D2 and D3 stay fitted.",
        "Limit names inside the actuator are TODO.",
        "The lift limits are on sheet 05. The H-bridge is VC-LT-9110.",
        "Lift cable section is TBC.",
    ]
    s.place("K2", "REL", 80, 36, "VC-LT-9230 vertical", unit=1)
    s.place("K3", "REL", 170, 36, "VC-LT-9230 fold", unit=1)
    s.place_pin("K2", "REL", "11", 80, 70, "K2 contacts", unit=2, hide_value=True)
    s.place_pin("K3", "REL", "11", 170, 86, "K3 contacts", unit=2, hide_value=True)
    s.place_pin("K2", "REL", "21", 80, 112, "K2 power", unit=3, hide_value=True)
    s.place_pin("K3", "REL", "21", 170, 128, "K3 power", unit=3, hide_value=True)
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
    s.place("A10", "HBR", 80, 200, "VC-LT-9110")
    s.stub("490_EXT", ("A10", "E"), dx=-14)
    s.stub("491_RET", ("A10", "R"), dx=-14)
    s.vrail("211_24C", 20, [("A10", "P")])
    s.vrail("001_0V", 36, [("A10", "M")])
    s.place_pin("X10.1", "TERM_H", "1", 160, s.pin("A10", "MP")[1], "X10.1")
    s.place_pin("X10.2", "TERM_H", "1", 160, s.pin("A10", "MN")[1], "X10.2")
    s.place_pin("M5", "ACT", "1", 230, s.pin("A10", "MP")[1], "VC-LT-9100 A")
    s.place_pin("M6", "ACT", "1", 280, s.pin("A10", "MP")[1], "VC-LT-9100 B")
    s.join("550_LIFTP", ("A10", "MP"), ("X10.1", "1"), ("X10.1", "2"), ("M5", "1"), ("M6", "1"))
    s.wire(
        "551_LIFTN",
        s.pin("A10", "MN"),
        s.pin("X10.2", "1"),
    )
    s.link("551_LIFTN", ("X10.2", "2"), ("M5", "2"))
    s.link("551_LIFTN", ("M5", "2"), ("M6", "2"))
    s.place_pin("X8.5", "TERM_H", "1", 100, 230, "X8.5")
    s.place_pin("X10.3", "TERM_H", "1", 160, 230, "X10.3")
    s.hrail("211_24C", 230, [(20, 230), ("X8.5", "1"), ("X8.5", "2"), ("X10.3", "1"), ("X10.3", "2")])
    s.place_pin("X8.6", "TERM_H", "1", 100, 242, "X8.6")
    s.place_pin("X10.4", "TERM_H", "1", 160, 242, "X10.4")
    s.hrail("001_0V", 242, [(36, 242), ("X8.6", "1"), ("X8.6", "2"), ("X10.4", "1"), ("X10.4", "2")])
    s.text(40, 34, "K2 coil")
    s.text(120, 34, "K3 coil")
    s.note_at = (250, 16)


def build_rotation(s: Sheet) -> None:
    s.notes = [
        "Nanotec PD2-C4118L1804-E-01 is a proposal. It is not released.",
        "This order code speaks USB, not Modbus. USB is a service plug.",
        "Clock and direction come from U2. U2 is not a DIO pin.",
        "Enable is DIO output 7, on +Release b4.",
        "Minus clock and minus direction stay open at the drive.",
        "Park those two cores on 0 V at X9. Do not land them on b5 or b7.",
        "24 V is inside the 12 V to 48 V range. The fuse is 2 A. The wire is 0.75 mm2.",
        "The drive PE screw is TBC. The cable shield uses X9 pin 8.",
        "The index sensor is B1 on sheet 05.",
    ]
    s.place("A6", "NANO", 160, 90, "VC-CT-6280 proposal")
    s.place_pin("F6", "FUSE", "1", 40, 40, "VC-PW-5790 2A")
    s.place_pin("PF3", "PWR", "1", s.pin("F6", "2")[0], s.pin("F6", "2")[1] + 12, "24V R", hide_value=True)
    s.link("500_24R", ("F6", "2"), ("PF3", "1"))
    s.vrail("211_24C", 24, [("F6", "1")])
    s.place_pin("X9.1", "TERM_H", "1", 90, s.pin("A6", "a2")[1], "X9.1")
    s.join("500_24R", ("PF3", "1"), ("X9.1", "1"), ("X9.1", "2"), ("A6", "a2"))
    bx = s.pin("A6", "b8")[0]
    s.place_pin("U2", "PULSE", "P", bx + 56, s.pin("A6", "b8")[1], "clock source TODO", in_bom=False)
    s.place_pin("X9.3", "TERM_H", "2", s.pin("A6", "b4")[0] - 24, s.pin("A6", "b4")[1], "X9.3")
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
    s.text(80, 144, "CLK- and DIR- are parked on 0 V.")
    s.note_at = (12, 180)


def build_network(s: Sheet) -> None:
    s.notes = [
        "RUT241 runs from the general 24 V rail. There is no 9 V converter.",
        "Power pins are 1 +V and 2 0 V. DIN and DOUT are open.",
        "There is no PE screw on the router.",
        "ETH0 of the RevPi goes to the router LAN port. ETH1 is service.",
        "The cable is Cat5e. Assume 0.5 m.",
        "Modbus slave 1 is the ATV320. Modbus slave 2 is the S200.",
        "Baud and parity are TODO.",
        "R1, 120 ohm, is drawn at the S200 on sheet 03.",
        "The shield lands on PE at the RevPi only.",
        "The rotation drive is not on this bus.",
    ]
    s.place("A7", "RUT", 80, 60, "VC-CT-6600 RUT241")
    s.vrail("211_24C", 30, [("A7", "1")])
    s.vrail("001_0V", 42, [("A7", "2")])
    s.stub("930_ETH", ("A7", "LAN"), dx=18)
    s.text(s.pin("A7", "LAN")[0] + 4, s.pin("A7", "LAN")[1] - 4, "Cat5e to RevPi ETH0")
    s.note_at = (12, 120)


def build_terminals(s: Sheet) -> None:
    s.notes = [
        "This sheet is the terminal plan. The terminal symbols are on the circuit sheets.",
        "Do not fit a second symbol with the same reference.",
        "The purchased terminal block is not chosen.",
        "Wire numbers match the labels on the circuit sheets.",
    ]
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
    s.note_at = (12, 200)


def build_sheets() -> list[Sheet]:
    sheets = [
        Sheet("01-power.kicad_sch", "01 Mains and 24 V", "2"),
        Sheet("02-safety.kicad_sch", "02 E-stop and STO", "3"),
        Sheet("03-hub.kicad_sch", "03 S200 and 1FL2", "4"),
        Sheet("04-sonic.kicad_sch", "04 ATV320 and two MVE", "5"),
        Sheet("05-revpi.kicad_sch", "05 RevPi Connect 4 and DIO", "6"),
        Sheet("06-tilt.kicad_sch", "06 Tilt and lift", "7"),
        Sheet("07-rotation.kicad_sch", "07 Rod rotation proposal", "8"),
        Sheet("08-network.kicad_sch", "08 RUT241 and Modbus", "9"),
        Sheet("09-terminals.kicad_sch", "09 Terminal strips", "10"),
    ]
    builders = (
        build_power, build_safety, build_hub, build_sonic, build_revpi,
        build_tilt, build_rotation, build_network, build_terminals,
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
    """Put the label on a real wire end. A label in the middle leaves that end dangling."""
    degree = defaultdict(int)
    segments = []
    for name, left, right in _segments(sheet):
        if name != net:
            continue
        degree[left] += 1
        degree[right] += 1
        segments.append((left, right))
    if not segments:
        return None
    pins = set()
    for inst in sheet.insts:
        for pin in SYMS[inst.sym].pins:
            if pin.unit == inst.unit:
                pins.add((inst.x + pin.x, inst.y - pin.y))
    free = [pt for pt, count in degree.items() if count == 1 and pt not in pins]
    candidates = free or [pt for pt, count in degree.items() if count == 1]
    if not candidates:
        candidates = [segments[0][0]]
    point = candidates[0]
    for left, right in segments:
        other = right if left == point else left if right == point else None
        if other is None:
            continue
        angle = 0 if left[1] == right[1] else 90
        return (point[0], point[1], angle)
    return (point[0], point[1], 0)


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
        x, y, angle = spot
        labelled.add(net)
        kind = "global" if net in global_nets else "local"
        if kind == "global":
            chunks.append(
                f"  (global_label {q(net)} (shape passive) (at {f(x)} {f(y)} {angle}) "
                f"(effects (font (size 1.27 1.27)) (justify left bottom)) "
                f"(uuid {q(uid(sheet.filename + 'g' + net))}))"
            )
        else:
            chunks.append(
                f"  (label {q(net)} (at {f(x)} {f(y)} {angle}) "
                f"(effects (font (size 1.27 1.27)) (justify left bottom)) "
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
        chunks.append(
            f"""  (symbol (lib_id {q("vibrocore:" + inst.sym)}) (at {f(inst.x)} {f(inst.y)} 0) (unit {inst.unit})
    (exclude_from_sim no) (in_bom {bom}) (on_board yes) (dnp no)
    (uuid {q(uid(sheet.filename + inst.ref + str(inst.unit) + "sym"))})
    (property "Reference" {q(inst.ref)} (at {f(inst.x + inst.ref_dx)} {f(inst.y + inst.ref_dy)} 0) (effects (font (size 1.27 1.27)){ref_hide}))
    (property "Value" {q(inst.value)} (at {f(inst.x + inst.val_dx)} {f(inst.y + inst.val_dy)} 0) (effects (font (size 1.27 1.27)){val_hide}))
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
    xref = []
    for net, pages in sorted(global_nets.items()):
        if sheet.page in pages and len(pages) > 1:
            others = [page for page in pages if page != sheet.page]
            xref.append(f"{net} also on sheet {', '.join(others)}.")
    notes = "\n".join(sheet.notes + xref)
    nx, ny = sheet.note_at
    note = (
        f"  (text {q(notes)} (exclude_from_sim no) (at {f(nx)} {f(ny)} 0) "
        f"(effects (font (size 1.27 1.27)) (justify left top)) "
        f"(uuid {q(uid(sheet.filename + 'note'))}))"
    )
    return f"""(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (generator_version "8.0")
  (uuid {q(uid(sheet.filename + "file"))})
  (paper "A3")
  (title_block
    (title {q(sheet.title)})
    (date "2026-11-20")
    (rev "0B")
    (company "Ground UP GmbH")
    (comment 1 "VC-SCH-5000. Wires are drawn. Global labels leave the sheet.")
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


def root_text(sheets: list[Sheet], uuids: dict[str, str], columns: tuple[str, str]) -> str:
    blocks = []
    for index, sheet in enumerate(sheets):
        y = 16 + index * 18
        su = uuids[sheet.filename]
        blocks.append(
            f"""  (sheet (at {f(12)} {f(y)}) (size {f(120)} {f(14)})
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid {q(su)})
    (property "Sheetname" {q(sheet.title)} (at {f(12)} {f(y - 2)} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" {q(sheet.filename)} (at {f(12)} {f(y + 14)} 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances (project {q(PROJECT)} (path "/" (page {q(sheet.page)}))))
  )"""
        )
    intro = "\n".join([
        "Vibrocore cabinet schematic VC-SCH-5000, revision 0B.",
        "Controller: RevPi Connect 4, order 100378, plus DIO 100197.",
        "The PFC200 is not on this drawing.",
        "Safety: PNOZ s4 750104 drops STO on the S200 and on the ATV320.",
        "Wires are drawn on each sheet.",
        "A global label is a wire that continues on another sheet.",
        "A crossing without a dot is not a connection.",
        "OPEN marks an order code that is not chosen.",
        "TBC marks a pin whose landing is not confirmed.",
        "Cross references:",
    ])
    return f"""(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (generator_version "8.0")
  (uuid {q(uid("root"))})
  (paper "A3")
  (title_block
    (title "Vibrocore cabinet schematic")
    (date "2026-11-20")
    (rev "0B")
    (company "Ground UP GmbH")
    (comment 1 "VC-SCH-5000 sheet 01 of 10")
    (comment 2 "Hard-wired STO. RevPi reads feedback only.")
  )
  (lib_symbols)
  (text {q(intro)} (exclude_from_sim no) (at 190.50 15.24 0)
    (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid("root-intro"))}))
  (text {q(columns[0])} (exclude_from_sim no) (at 190.50 50.80 0)
    (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid("root-xref-a"))}))
  (text {q(columns[1])} (exclude_from_sim no) (at 292.10 50.80 0)
    (effects (font (size 1.27 1.27)) (justify left top)) (uuid {q(uid("root-xref-b"))}))
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


def write_tree(directory: Path) -> None:
    sheets = build_sheets()
    validate(sheets)
    check_electrical(sheets)
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
        root_text(sheets, uuids, cross_columns(global_nets)), encoding="utf-8"
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
