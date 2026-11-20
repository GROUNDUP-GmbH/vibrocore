"""Folio wiring for VC-SCH-5000 revision 0D.

Every conductor is straight. A corner is a junction dot.
Product names come from annotate.PRODUCT. Pin names are the revision 0C names.
"""

from __future__ import annotations

from generate_qet import CABLES, PRODUCT, TERMINALS, Folio, part, section_of

# Folio numbers. The cover is 1. These match the order in build().
MAINS, BRANCH, SUPPLY, ESTOP, OUTPUT, S200P, S200C = 2, 3, 4, 5, 6, 7, 8
ATVA, ATVB, ATVC, REVPI, DIO = 9, 10, 11, 12, 13
FIELD, TILT, LIFT, ROT, NET = 14, 15, 16, 17, 18
PLAN, CABLE, NOTES = 19, 20, 21

XREF: list[tuple] = []


def xref(master, slaves) -> None:
    XREF.append((master, list(slaves)))


def down(folio: Folio, node, key, gap: int, sym: str, newkey, ref: str, lines: list[str]):
    x, y = folio.xy(node, key)
    return folio.at(sym, newkey, x, y + gap, ref=ref, lines=lines)


def finish(folios: list[Folio]) -> None:
    for master, slaves in XREF:
        for slave in slaves:
            master.links.append(("slave", slave.uuid))
            slave.links.append(("master", master.uuid))


def build() -> list[Folio]:
    cover = Folio(1, "Cover and folio index", 768)
    folios = [cover]
    made = {
        "cover": cover,
        "mains": mains(folio(folios, "Mains incoming", 896)),
        "branch": branches(folio(folios, "Branch feeders", 1024)),
        "supply": supplies(folio(folios, "24 V supplies", 832)),
        "estop": estop(folio(folios, "E-stop and PNOZ inputs", 832)),
        "output": outputs(folio(folios, "PNOZ outputs")),
        "s200p": s200_power(folio(folios, "S200 power and motor", 896)),
        "s200c": s200_control(folio(folios, "S200 control", 1024)),
        "atva": atv_a(folio(folios, "ATV320 motor A", 896)),
        "atvb": atv_b(folio(folios, "ATV320 motor B", 896)),
        "atvc": atv_c(folio(folios, "ATV320 control", 1024)),
        "revpi": revpi(folio(folios, "RevPi supply")),
        "dio": dio(folio(folios, "DIO channels", 1024)),
        "field": field(folio(folios, "Field devices", 1408)),
        "tilt": tilt(folio(folios, "Tilt", 896)),
        "lift": lift(folio(folios, "Lift")),
        "rot": rotation(folio(folios, "Rotation proposal", 832)),
        "net": network(folio(folios, "Network")),
        "plan": plan(folio(folios, "Terminal plan", 1344)),
        "cable": cables(folio(folios, "Cable list")),
        "notes": notes(folio(folios, "Notes")),
    }
    cover_page(cover, folios)
    xref(made["estop"].coil, made["output"].contacts)
    finish(folios)
    return folios


def folio(folios: list[Folio], title: str, height: int = 768) -> Folio:
    item = Folio(len(folios) + 1, title, height)
    folios.append(item)
    return item


def cover_page(cover: Folio, folios: list[Folio]) -> None:
    cover.text(60, 50, "Vibrocore cabinet schematic", 12)
    cover.text(60, 74, "Ground UP GmbH    VC-SCH-5000    Rev 0D    2026-11-20")
    for item in folios:
        cover.text(60, 96 + item.number * 20, f"{item.number:02d}   {item.title}")
    cover.text(60, 540, "Power is at the top. Control is below. Flow is left to right.")
    cover.text(60, 564, "A junction dot is a connection. A crossing without a dot is not a connection.")


def _anchor(folio: Folio):
    return folio.dot(40, 40)


def mains(f: Folio) -> Folio:
    """Three columns. The top source pin feeds the right-hand column so the taps do not cross."""
    g0 = f.at("src", "L", 70, 90, ref="G0", lines=[], side="left", article="VC-PW-5100")
    f.text(160, 28, "G0   Instagrid ONE max   VC-PW-5100")
    columns = {"L": 760, "N": 520, "PE": 280}
    taps = {"L": (g0, "L", "100_L", "X1:1"), "N": (g0, "N", "101_N", "X1:2"), "PE": (g0, "PE", "102_PE", "X1:3")}
    wires = {}
    for name, x in columns.items():
        src, key, net, ref = taps[name]
        sx, sy = f.xy(src, key)
        # PE drops clear of the source before it runs across, so its label is not on L or N.
        drop_y = sy + (50 if name == "PE" else 0)
        if name == "PE":
            down = f.dot(sx, drop_y)
            f.link(src, key, down, "1", net)
            corner = f.dot(x, drop_y)
            f.link(down, "4", corner, "3", net)
        else:
            corner = f.dot(x, sy)
            f.link(src, key, corner, "3", net)
        term = f.at("term", "n", x, drop_y + 50, ref=ref, lines=[name])
        f.link(corner, "2", term, "n", net)
        wires[name] = term
    # Ganged poles. The product name sits above the row, not between the columns.
    def poles(y, ref, lines, top_net_l, top_net_n):
        live = f.at("mcb1", "IN.1", columns["L"], y, ref=ref, lines=["L"], article=next(line for line in lines if line.startswith("VC-")))
        neutral = f.at("mcb1", "IN.1", columns["N"], y, ref=ref, lines=["N"])
        f.text(36, y - 8, f"{ref}  {lines[0]}")
        if len(lines) > 1:
            f.text(36, y + 10, lines[1])
        f.dash(columns["N"] + 24, y, columns["L"] - 24, y)
        return live, neutral

    q_l, q_n = poles(f.xy(wires["L"], "s")[1] + 90, "Q1", part("VC-PW-5700"), "100_L", "101_N")
    f.link(wires["L"], "s", q_l, "IN.1", "100_L")
    f.link(wires["N"], "s", q_n, "IN.1", "101_N")
    qf_l, qf_n = poles(f.xy(q_l, "OUT.2")[1] + 80, "QF1", part("VC-PW-5720"), "110_L", "111_N")
    f.link(q_l, "OUT.2", qf_l, "IN.1", "110_L")
    f.link(q_n, "OUT.2", qf_n, "IN.1", "111_N")
    f_l, f_n = poles(f.xy(qf_l, "OUT.2")[1] + 80, "F1", part("VC-PW-5710"), "120_L", "121_N")
    f.link(qf_l, "OUT.2", f_l, "IN.1", "120_L")
    f.link(qf_n, "OUT.2", f_n, "IN.1", "121_N")
    for node, net in ((f_l, "130_L"), (f_n, "131_N")):
        ex, ey = f.xy(node, "OUT.2")
        low = f.dot(ex, ey + 70)
        f.link(node, "OUT.2", low, "1", net)
        arrow = f.out(min(ex + 160, 1000), ey + 70, net, BRANCH)
        f.link(low, "4", arrow, "w", net)
    earth = f.at("earth", "PE", columns["PE"], f.xy(wires["PE"], "s")[1] + 60, ref="PE1", lines=["PE"])
    f.link(wires["PE"], "s", earth, "PE", "102_PE")
    f.note("Instagrid ONE max is the only AC source. Continuous current is 15.7 A.", g0)
    f.note("Q1 does not switch PE. QF1 is type B, 30 mA. The dashed line is the mechanical link.", q_l)
    f.note("F4 feeds the S200 supply. F5 feeds the general 24 V supply. Both continue on folio 03.", f_l)
    f.note("A crossing without a dot is not a connection.", q_l)
    return f


def branches(f: Folio) -> Folio:
    """One column per feeder. L and N are separate poles with a dashed link."""
    groups = [
        (200, "F2", part("VC-PW-5730"), "130_L", "131_N", "140_L", "141_N", True),
        (200, "F3", part("VC-PW-5740"), "130_L", "131_N", "150_L", "151_N", False),
        (640, "F4", part("VC-PW-5750"), "130_L", "131_N", "160_L", "161_N", False),
        (640, "F5", part("VC-PW-5760"), "130_L", "131_N", "170_L", "171_N", False),
    ]
    # Two rows on the left (F2, F3) and two on the right (F4, F5).
    rows = [150, 520, 150, 520]
    rails = [80, 80, 520, 520]
    for (x, ref, lines, net_l, net_n, out_l, out_n, pole3), y, rail in zip(groups, rows, rails):
        live = f.at("mcb1", "IN.1", x, y, ref=ref, lines=["L pole", *lines], side="above")
        neutral = f.at("mcb1", "IN.1", x, y + 150, ref=ref, lines=["N pole"])
        f.dash(x - 16, y, x - 16, y + 150)
        src_l = f.dot(rail, y)
        src_n = f.dot(rail + 50, y + 150)
        f.link(src_l, "4", live, "IN.1", net_l)
        f.link(src_n, "4", neutral, "IN.1", net_n)
        out_y = f.xy(live, "OUT.2")[1]
        arrow = f.out(x + 150, out_y, out_l, ATVA if ref == "F2" else S200P if ref == "F3" else SUPPLY)
        f.link(live, "OUT.2", arrow, "w", out_l)
        out_y = f.xy(neutral, "OUT.2")[1]
        arrow = f.out(x + 150, out_y, out_n, ATVA if ref == "F2" else S200P if ref == "F3" else SUPPLY)
        f.link(neutral, "OUT.2", arrow, "w", out_n)
        if pole3:
            f.at("mcb1", "IN.1", x, y + 240, ref="F2", lines=["pole 3 open"])
            f.dash(x - 22, y + 170, x - 22, y + 240)
    # Distribution rails. Left pair feeds F2 and F3. Right pair feeds F4 and F5.
    _bus(f, 80, [150, 520], "130_L", MAINS)
    _bus(f, 130, [300, 670], "131_N", MAINS)
    _bus(f, 520, [150, 520], "130_L", MAINS)
    _bus(f, 570, [300, 670], "131_N", MAINS)
    f.note("F2 is a Schneider GV2L20. NVE41289.09, enclosure, 240 V, one phase. Pole 3 is open.", f.nodes[0])
    f.note("The row is ATV320U15M2. Line current is 17.8 A at 200 V. Irm is 223 A.", f.nodes[0])
    f.note("The sonic feeder is 6 mm2. The S200 feeder is 2.5 mm2.", f.nodes[2])
    f.note("The dashed line is the mechanical link of one device.", f.nodes[0])
    return f


def _bus(f: Folio, x: int, ys: list[int], net: str, source: int) -> None:
    dots = []
    for y in ys:
        # Reuse a dot that is already at this point, if the feeder placed one.
        found = None
        for node in f.nodes:
            if node.sym == "bod" and node.x == x and node.y == y:
                found = node
                break
        dots.append(found or f.dot(x, y))
    for top, bot in zip(dots, dots[1:]):
        f.link(top, "2", bot, "1", net)
    incoming = f.inn(x - 40, ys[0], net, source)
    f.link(incoming, "e", dots[0], "3", net)


def supplies(f: Folio) -> Folio:
    g1 = f.at("psu", (-10, -30), 300, 180, ref="G1", lines=part("VC-PW-5310"))
    g2 = f.at("psu", (-10, -30), 700, 180, ref="G2", lines=part("VC-PW-5320"))
    for supply, article_fuse, net_in, net_out, target in (
        (g1, "VC-PW-5800", "200_24S", "201_24S", S200C),
        (g2, "VC-PW-5810", "210_24C", "211_24C", DIO),
    ):
        px, py = f.xy(supply, (10, 30))
        fuse = f.at("fuse", "1", px, py + 90, ref="F14" if supply is g1 else "F24", lines=[], side="left", article=article_fuse)
        f.text(px + 30, py + 150, " ".join(part(article_fuse)))
        f.link(supply, (10, 30), fuse, "1", net_in)
        ox, oy = f.xy(fuse, "2")
        arrow = f.out(ox + 220, oy, net_out, target)
        f.link(fuse, "2", arrow, "w", net_out)
    # L comes from the left. N comes from the gap between the L pin and the N pin.
    for supply, net_l, net_n in ((g1, "160_L", "161_N"), (g2, "170_L", "171_N")):
        lx, ly = f.xy(supply, (-10, -30))
        nx, ny = f.xy(supply, (30, -30))
        f.link(f.inn(lx - 90, ly, net_l, BRANCH), "e", supply, (-10, -30), net_l)
        corner = f.dot(nx, ny - 80)
        f.link(f.inn(nx - 200, ny - 80, net_n, BRANCH), "e", corner, "3", net_n)
        f.link(corner, "2", supply, (30, -30), net_n)
    # 0 V leaves each minus pin to the right, past that supply's fuse, then drops.
    drops = []
    for supply in (g1, g2):
        mx, my = f.xy(supply, (30, 30))
        land = f.dot(mx + 160, my)
        f.link(supply, (30, 30), land, "3", "001_0V")
        foot = f.dot(mx + 160, my + 220)
        f.link(land, "2", foot, "1", "001_0V")
        drops.append(foot)
    f.link(drops[0], "4", drops[1], "3", "001_0V")
    x14 = f.at("term", "n", drops[1].x + 70, drops[1].y, ref="X1:4", lines=["0V"])
    f.link(drops[1], "4", x14, "n", "001_0V")
    # PE rises above both supplies, then W1 drops to the 0 V terminal.
    pe_y = f.xy(g1, (50, -30))[1] - 120
    for supply in (g1, g2):
        px, py = f.xy(supply, (50, -30))
        top = f.dot(px, pe_y)
        f.link(supply, (50, -30), top, "2", "102_PE")
    left_pe = next(node for node in f.nodes if node.sym == "bod" and node.y == pe_y)
    right_pe = [node for node in f.nodes if node.sym == "bod" and node.y == pe_y][-1]
    f.link(left_pe, "4", right_pe, "3", "102_PE")
    bond = f.dot(x14.x, pe_y)
    f.link(right_pe, "4", bond, "3", "102_PE")
    f.link(bond, "2", x14, "n", "W1")
    earth = f.at("earth", "PE", x14.x - 80, pe_y, ref="PE2", lines=["PE"], side="left")
    f.link(earth, "PE", bond, "3", "102_PE")
    f.note("The general 24 V rail is 2.5 mm2. The S200 24 V feed is 1.0 mm2. There is no 48 V rail.", g1)
    f.note("G2 is an open 24 V slot. SDR-480-24 is the slot size, not a purchase.", g2)
    f.note("Both 0 V rails meet at X1 pin 4. W1 is the only bond to PE. Confirm W1 in the S200 PTI manual.", x14)
    f.note("F14 is 6 A on the S200 rail. F24 is 20 A on the general rail.", f.nodes[2])
    return f


def estop(f: Folio) -> Folio:
    # Channel 1, left to right: S11, S1 11-12, then the split to S12 and to the reset.
    s11 = f.at("term", "n", 160, 80, ref="K1", lines=["S11"])
    s1a = f.at("estop", "n", 160, 180, ref="S1", lines=["11-12", *part("VC-CT-6210")])
    f.link(s11, "s", s1a, "n", "410_S11")
    s12 = f.at("term", "n", 300, f.xy(s1a, "s")[1], ref="K1", lines=["S12"])
    f.link(s1a, "s", s12, "n", "411_S12")
    s10 = f.at("pb", "n", 160, f.xy(s1a, "s")[1] + 80, ref="S10", lines=part("VC-CT-6270"))
    f.link(s1a, "s", s10, "n", "411_S12")
    s34 = f.at("term", "n", 160, f.xy(s10, "s")[1] + 50, ref="K1", lines=["S34"])
    f.link(s10, "s", s34, "n", "414_S34")
    # Channel 2.
    s21 = f.at("term", "n", 460, 80, ref="K1", lines=["S21"])
    s1b = f.at("estop", "n", 460, 180, ref="S1", lines=["21-22"])
    f.link(s21, "s", s1b, "n", "412_S21")
    s22 = f.at("term", "n", 600, f.xy(s1b, "s")[1], ref="K1", lines=["S22"])
    f.link(s1b, "s", s22, "n", "413_S22")
    f.dash(220, 180, 420, 180)
    # Third contact to the DIO only.
    s1c = f.at("estop", "n", 760, 180, ref="S1", lines=["31-32"], side="above")
    top = f.inn(760, 80, "211_24C", SUPPLY)
    f.link(top, "e", s1c, "n", "211_24C")
    arrow = f.out(900, f.xy(s1c, "s")[1], "420_ESTOP", DIO)
    f.link(s1c, "s", arrow, "w", "420_ESTOP")
    # Coil.
    coil = f.at("coil", "A1", 300, 520, ref="K1", lines=["A1 A2", *part("VC-CT-6220")])
    a1 = f.inn(180, f.xy(coil, "A1")[1], "211_24C", SUPPLY)
    f.link(a1, "e", coil, "A1", "211_24C")
    a2 = f.dot(180, f.xy(coil, "A2")[1])
    f.link(coil, "A2", a2, "4", "001_0V")
    zero = f.inn(80, f.xy(coil, "A2")[1], "001_0V", SUPPLY)
    f.link(zero, "e", a2, "3", "001_0V")
    f.note("Two NC channels go to the PNOZ s4, article 750104. The third NC is DIO input index 2 only.", s1a)
    f.note("Do not feed cabinet 24 V into S11 or S21. The PNOZ makes the test pulses.", s11)
    f.note("The reset sits between S12 and S34. Set a monitored reset. The detent text is TBC.", s10)
    f.note("OPEN: the E-stop contact block and the reset button are not chosen.", s1c)
    f.coil = coil  # type: ignore[attr-defined]
    return f


def outputs(f: Folio) -> Folio:
    coil_mark = None
    # Filled after we can see the estop folio's coil. The caller patches xref.
    y24 = 80
    contacts = [
        ("13-14", "NO", "430_F30", "431_STO1", "VC-PW-5820", True),
        ("23-24", "NO", "432_F31", "433_STO2", "VC-PW-5820", True),
        ("33-34", "NO", "", "", "", False),
        ("41-42", "NC", "", "421_PNOZ", "", False),
    ]
    nodes = []
    for index, (name, kind, mid, leave, fuse_article, fused) in enumerate(contacts):
        y = 80 + index * 140
        sym = "no" if kind == "NO" else "nc"
        if name == "33-34":
            contact = f.at(sym, "n", 420, y, ref="K1", lines=[name])
            nodes.append(contact)
            continue
        if fused:
            fuse = f.at("fuse", "1", 280, y, ref="F30" if index == 0 else "F31", lines=part(fuse_article), side="above")
            feed = f.inn(120, y, "211_24C", SUPPLY)
            f.link(feed, "e", fuse, "1", "211_24C")
            contact = f.at(sym, "n", 420, f.xy(fuse, "2")[1], ref="K1", lines=[name])
            f.link(fuse, "2", contact, "n", mid)
        else:
            contact = f.at(sym, "n", 420, y, ref="K1", lines=[name])
            feed = f.inn(120, y, "211_24C", SUPPLY)
            f.link(feed, "e", contact, "n", "211_24C")
        nodes.append(contact)
        dest = S200C if leave.startswith("43") else DIO
        exit_y = f.xy(contact, "s")[1]
        arrow = f.out(620, exit_y, leave, dest)
        f.link(contact, "s", arrow, "w", leave)
        if leave.startswith("43"):
            drop = f.dot(620, exit_y + 36)
            f.link(arrow, "w", drop, "1", leave)
            extra = f.out(760, f.xy(drop, "2")[1], leave, ATVC)
            f.link(drop, "2", extra, "w", leave)
    f.contacts = nodes  # type: ignore[attr-defined]
    f.note("Contact 13-14 is STO channel 1. Contact 23-24 is STO channel 2. The section is 0.75 mm2.", nodes[0])
    f.note("41-42 is the monitor. Do not use it in the safety path. Its state is TBC.", nodes[3])
    f.note("33-34 is spare. Do not load it.", nodes[2])
    f.note("Each STO wire goes to the S200 and to the ATV320.", nodes[0])
    return f


def s200_power(f: Folio) -> Folio:
    f.text(60, 12, "A2  Siemens 6SL5510  VC-HB-2300", 12)
    pins = {}
    for index, (name, lines) in enumerate((("L1", ["L1"]), ("L2", ["L2 open"]), ("L3", ["L3"]), ("PE", ["PE"]))):
        pins[name] = f.at("term", "n", 180, 130 + index * 70, ref="A2", lines=lines, article="VC-HB-2300" if name == "L1" else "")
    l_in = f.inn(60, f.xy(pins["L1"], "n")[1], "150_L", BRANCH)
    f.link(l_in, "e", pins["L1"], "n", "150_L")
    n_in = f.inn(60, f.xy(pins["L3"], "n")[1], "151_N", BRANCH)
    f.link(n_in, "e", pins["L3"], "n", "151_N")
    # Outputs W, V, U top to bottom so the fan does not cross.
    outs = {}
    for index, phase in enumerate(("W", "V", "U")):
        outs[phase] = f.at("term", "n", 460, 80 + index * 130, ref="A2", lines=[phase], side="left")
    motor = f.at("motor", "W1", 860, 560, ref="M1", lines=part("VC-HB-2100"))
    terms = {"U": "X4:1", "V": "X4:2", "W": "X4:3"}
    nets = {"U": "540_U", "V": "541_V", "W": "542_W"}
    motor_pin = {"U": "U1", "V": "V1", "W": "W1"}
    for phase in ("W", "V", "U"):
        south = f.xy(outs[phase], "s")
        term = f.at("term", "n", south[0], south[1] + 40, ref=terms[phase], lines=[phase])
        f.link(outs[phase], "s", term, "n", nets[phase])
        f.via_h(term, "s", motor, motor_pin[phase], nets[phase])
    # PE around the bottom, under the fan.
    pe_drive = pins["PE"]
    x44 = f.at("term", "n", 180, 430, ref="X4:4", lines=["PE"])
    f.link(pe_drive, "s", x44, "n", "102_PE")
    f.via_h(x44, "s", motor, "PE", "102_PE")
    # Brake. The motor symbol has no brake pins. Two terminals name the coil ends.
    brp = f.at("term", "n", 620, 80, ref="A2", lines=["X108 BR+"], side="left")
    brn = f.at("term", "n", 620, 180, ref="A2", lines=["X108 BR-"], side="left")
    x61 = f.at("term", "n", 760, f.xy(brp, "s")[1], ref="X6:1", lines=["BR+"])
    x62 = f.at("term", "n", 760, f.xy(brn, "s")[1], ref="X6:2", lines=["BR-"])
    f.link(brp, "s", x61, "n", "543_BRP")
    mbr = f.at("term", "n", 900, f.xy(x61, "s")[1], ref="M1", lines=["BR+"])
    f.link(x61, "s", mbr, "n", "543_BRP")
    f.link(brn, "s", x62, "n", "544_BRN")
    mbn = f.at("term", "n", 900, f.xy(x62, "s")[1], ref="M1", lines=["BR-"])
    f.link(x62, "s", mbn, "n", "544_BRN")
    f.note("Order 6SL5510-1BB11-0AA0. This is the PTI standard drive, not the PROFINET code.", pins["L1"])
    f.note("L2 is open. Mains uses L1 and L3. DCP, R1 and R2 stay open.", pins["L2"])
    f.note("Power cable is 4G1.5 mm2 shielded. Brake pair is 2x0.75 mm2. The coil stays on X108.", brp)
    f.note("The Siemens motor-cable order code is TODO.", motor)
    return f


def s200_control(f: Folio) -> Folio:
    f.text(60, 12, "A2  Siemens 6SL5510  VC-HB-2300", 12)
    rows = [
        ("1", "STO1+", "431_STO1", OUTPUT),
        ("2", "STO1-", "001_0V", SUPPLY),
        ("3", "STO-VS TBC", "", 0),
        ("4", "STO-M TBC", "", 0),
        ("5", "STO2+", "433_STO2", OUTPUT),
        ("6", "STO2-", "001_0V", SUPPLY),
        ("FB", "STO_EP not landed", "440_S200FB", DIO),
        ("24V", "X124 24 V", "201_24S", SUPPLY),
        ("24Vb", "X124 24 V", "201_24S", SUPPLY),
        ("0V", "X124 0 V", "001_0V", SUPPLY),
        ("0Vb", "X124 0 V", "001_0V", SUPPLY),
        ("X120", "encoder", "510_ENC", 0),
    ]
    pins = {}
    for index, (name, text, net, source) in enumerate(rows):
        y = 70 + index * 52
        pins[name] = f.at("term", "n", 360, y, ref="A2", lines=[text])
        if not net:
            continue
        if name == "X120":
            sx, sy = f.xy(pins[name], "s")
            x51 = f.at("term", "n", sx, sy + 46, ref="X5:1", lines=["ENC"])
            f.link(pins[name], "s", x51, "n", "510_ENC")
            continue
        arrow = f.inn(80, y, net, source) if source else None
        if arrow is not None:
            f.link(arrow, "e", pins[name], "n", net)
    x52 = f.at("term", "n", 200, f.xy(pins["X120"], "s")[1] + 70, ref="X5:2", lines=["shield"])
    f.note("X131 is 1 STO1+, 2 STO1-, 3 STO-VS, 4 STO-M, 5 STO2+, 6 STO2-. STO-VS and STO-M are TBC.", pins["1"])
    f.note("Do not land 24 V on STO-VS. X130 is not on this PTI drive.", pins["3"])
    f.note("STO status is status word bit STO_EP. Do not land 440_S200FB on a connector.", pins["FB"])
    f.note("X124 screws are marked 24 V and 0 V. Both screws of one mark are one node.", pins["24Vb"])
    f.note("VC-HB-3450 is the catalogue encoder cable. The Siemens order code is TODO.", pins["X120"])
    # Pulse source and the 120 ohm resistor sit to the right.
    pulse = [("36", "520_PULSP"), ("37", "521_PULSN"), ("38", "522_SIGNP"), ("39", "523_SIGNN")]
    u1 = []
    for index, (pin, net) in enumerate(pulse):
        y = 70 + index * 52
        dst = f.at("term", "n", 620, y, ref="A2", lines=[pin])
        src = f.at("term", "n", 780, f.xy(dst, "s")[1], ref="U1", lines=[pin])
        f.link(dst, "s", src, "n", net)
        u1.append(src)
    f.text(760, 12, "U1 pulse source TODO. Not a DIO pin.")
    r1 = f.at("res", "A1", 700, 760, ref="R1", lines=part("VC-CT-6790"))
    a = f.at("term", "s", 540, f.xy(r1, "A1")[1], ref="A2", lines=["23"])
    b = f.at("term", "n", 540, f.xy(r1, "A2")[1], ref="A2", lines=["25"])
    f.link(a, "s", r1, "A1", "910_A")
    f.link(r1, "A2", b, "n", "911_B")
    go_a = f.out(880, f.xy(r1, "A1")[1], "910_A", REVPI)
    go_b = f.out(880, f.xy(r1, "A2")[1], "911_B", REVPI)
    f.link(r1, "A1", go_a, "w", "910_A")
    f.link(r1, "A2", go_b, "w", "911_B")
    f.note("U1 is not a DIO pin. Pulse form and scale are TBC.", u1[0])
    f.note("Encoder map, drive to motor: 7 A, 8 B, 4 C, 5 D, 1 E, 2 F.", pins["X120"])
    f.note("R1 is 120 ohm at the S200. The shield lands on PE at the RevPi only.", r1)
    # Shield of the encoder to PE is a terminal only. The PE wire is on the power folio.
    f.note("X5 pin 2 is the shield. Land the shield at one end only.", x52)
    return f


def _phase_stack(f: Folio, columns: list[tuple[int, str, str]], motor, motor_y: int) -> None:
    """columns: (x, phase, net) top exit is the rightmost motor pin."""
    order = ["W", "V", "U"]
    exits = {}
    for x, phase, net in columns:
        exits[phase] = x
    # Exit heights: W highest, then V, then U.
    height = {phase: motor_y - 180 + order.index(phase) * 50 for phase in order}
    pin = {"U": "U1", "V": "V1", "W": "W1"}
    for x, phase, net in columns:
        _y = height[phase]
        # The stack above the exit is the caller's job. Here only the fan.
        pass
    return height


def atv_a(f: Folio) -> Folio:
    f.text(50, 12, "A3  Schneider ATV320U15M2C  VC-SH-1210", 12)
    # Supply.
    l1 = f.at("term", "n", 160, 80, ref="A3", lines=["L1"], article="VC-SH-1210")
    l2 = f.at("term", "n", 160, 150, ref="A3", lines=["L2"])
    pe = f.at("term", "n", 160, 220, ref="A3", lines=["PE"])
    f.link(f.inn(50, 80, "140_L", BRANCH), "e", l1, "n", "140_L")
    f.link(f.inn(50, 150, "141_N", BRANCH), "e", l2, "n", "141_N")
    # Phases in columns. W is the right-hand column and leaves first.
    spec = [("U", 300, "610_UA", "X2:1"), ("V", 470, "611_VA", "X2:2"), ("W", 640, "612_WA", "X2:3")]
    drive = {}
    guard = {}
    term = {}
    for phase, x, net, name in spec:
        drive[phase] = f.at("term", "n", x, 80, ref="A3", lines=[phase])
        guard[phase] = f.at("mcb1", "IN.1", x, 170, ref="F21", lines=["pole " + phase, *part("VC-PW-5770")] if phase == "U" else ["pole " + phase])
        f.link(drive[phase], "s", guard[phase], "IN.1", "600_" + phase)
        term[phase] = down(f, guard[phase], "OUT.2", 40, "term", "n", name, [phase])
        f.link(guard[phase], "OUT.2", term[phase], "n", net)
    f.dash(300 - 18, 170, 640 - 18, 170)
    motor = f.at("motor", "U1", 900, 560, ref="M2", lines=["motor A", *part("VC-SH-1100")])
    # Fan. W (right pin) leaves highest.
    leave = {"W": 400, "V": 460, "U": 520}
    for phase, _x, net, _name in spec:
        y = leave[phase]
        south = f.xy(term[phase], "s")
        if south[1] != y:
            dot = f.dot(south[0], y)
            f.link(term[phase], "s", dot, "1", net)
            f.via_h(dot, "2", motor, {"U": "U1", "V": "V1", "W": "W1"}[phase], net)
        else:
            f.via_h(term[phase], "s", motor, {"U": "U1", "V": "V1", "W": "W1"}[phase], net)
    x24 = f.at("term", "n", 160, 320, ref="X2:4", lines=["PE"])
    f.link(pe, "s", x24, "n", "102_PE")
    f.via_h(x24, "s", motor, "PE", "102_PE")
    f.note("One ATV320 output feeds both OLI MVE 400/6-HF motors. Each motor is 1.45 A.", drive["U"])
    f.note("Motor A keeps the drive phase order.", motor)
    f.note("OPEN: F21 needs a PWM-rated protector. Do not fit a standard GV2.", guard["U"])
    f.note("Supply wire is 6 mm2. The motor cable stays 4G1.5 shielded.", l1)
    return f


def atv_b(f: Folio) -> Folio:
    f.text(50, 12, "A3 output, motor B. V and W are swapped at X3.", 12)
    spec = [("U", 300, "620_UB", "X3:1", "U"), ("V", 470, "621_VB", "X3:3", "W"), ("W", 640, "622_WB", "X3:2", "V")]
    guard = {}
    term = {}
    for phase, x, net, name, _motor_phase in spec:
        src = f.inn(x, 70, "600_" + phase, ATVA)
        guard[phase] = f.at("mcb1", "IN.1", x, 160, ref="F22", lines=["pole " + phase, *part("VC-PW-5770")] if phase == "U" else ["pole " + phase])
        f.link(src, "e", guard[phase], "IN.1", "600_" + phase)
        term[phase] = down(f, guard[phase], "OUT.2", 40, "term", "n", name, [name[-1]])
        f.link(guard[phase], "OUT.2", term[phase], "n", net)
    f.dash(282, 160, 622, 160)
    motor = f.at("motor", "U1", 900, 560, ref="M3", lines=["motor B", *part("VC-SH-1100")])
    # Land on the motor pin named in the last column. Exit order follows the destination x: W pin, V pin, U pin.
    dest = {"U": "U1", "V": "W1", "W": "V1"}
    leave_y = {"W": 400, "V": 460, "U": 520}
    # Destination x order: motor W1 is the right pin, V1 middle, U1 left.
    # The highest exit must be the rightmost destination. 622_WB goes to motor V (middle).
    # Recompute exits by destination x, not by drive phase.
    dest_rank = {"U1": 520, "V1": 460, "W1": 400}
    for phase, _x, net, _name, _mp in spec:
        y = dest_rank[dest[phase]]
        south = f.xy(term[phase], "s")
        dot = f.dot(south[0], y)
        f.link(term[phase], "s", dot, "1", net)
        f.via_h(dot, "2", motor, dest[phase], net)
    x34 = f.at("term", "n", 160, 160, ref="X3:4", lines=["PE"])
    f.via_h(x34, "s", motor, "PE", "102_PE")
    f.note("Motor B swaps V and W at X3 so the motors turn in opposite directions.", motor)
    f.note("X3 pin 2 is cabinet W on motor V. X3 pin 3 is cabinet V on motor W.", term["W"])
    f.note("OPEN: F22 needs a PWM-rated protector. Do not fit a standard GV2.", guard["U"])
    f.note("The motor cable stays 4G1.5 shielded at the drive.", x34)
    return f


def atv_c(f: Folio) -> Folio:
    f.text(50, 12, "A3  Schneider ATV320U15M2C  VC-SH-1210", 12)
    rows = [
        ("STO", "STO", "431_STO1", OUTPUT),
        ("DI3", "DI3", "433_STO2", OUTPUT),
        ("DI1", "DI1", "450_RESET", DIO),
        ("COM", "COM", "001_0V", SUPPLY),
        ("R1A", "R1A open", "", 0),
        ("R1B", "R1B", "451_FAULT", DIO),
        ("R1C", "R1C", "211_24C", SUPPLY),
        ("R2A", "R2A", "211_24C", SUPPLY),
        ("R2C", "R2C", "452_SONSTO", DIO),
        ("RJA", "RJ45 A TBC", "910_A", S200C),
        ("RJB", "RJ45 B TBC", "911_B", S200C),
        ("P24", "P24 open", "", 0),
    ]
    pins = {}
    for index, (name, text, net, source) in enumerate(rows):
        y = 70 + index * 52
        pins[name] = f.at("term", "n", 240, y, ref="A3", lines=[text])
        if not net:
            continue
        arrow = f.inn(80, y, net, source)
        f.link(arrow, "e", pins[name], "n", net)
    f.note("The drive STO screw is one terminal. DI3 is the second channel. The SoMove parameter is TODO.", pins["DI3"])
    f.note("Do not tie P24 to the cabinet 24 V. There is no braking resistor.", pins["P24"])
    f.note("R1C is the fault-relay common. R1B is the NC contact. R1A is open.", pins["R1C"])
    f.note("RJ45 pin numbers are TBC. See the Modbus manual NVE41308.", pins["RJA"])
    return f


def revpi(f: Folio) -> Folio:
    f.text(50, 12, "A4  Kunbus RevPi 100378  VC-CT-6800", 12)
    rows = [("24", "211_24C", SUPPLY), ("0", "001_0V", SUPPLY), ("GND", "001_0V", SUPPLY), ("FG", "102_PE", MAINS), ("P", "910_A", S200C), ("N", "911_B", S200C)]
    pins = {}
    for index, (name, net, source) in enumerate(rows):
        y = 80 + index * 60
        pins[name] = f.at("term", "n", 200, y, ref="A4", lines=[name], article="VC-CT-6800" if name == "24" else "")
        f.link(f.inn(60, y, net, source), "e", pins[name], "n", net)
    eth = f.at("term", "n", 200, 80 + 6 * 60, ref="A4", lines=["ETH0"])
    f.link(eth, "s", f.out(400, f.xy(eth, "s")[1], "930_ETH", NET), "w", "930_ETH")
    f.at("term", "n", 200, 80 + 7 * 60, ref="A4", lines=["ETH1 service, no harness"])
    br = f.at("term", "n", 480, 80, ref="A4", lines=["PiBridge"])
    br2 = f.at("term", "n", 680, f.xy(br, "s")[1], ref="A5", lines=["PiBridge"])
    f.link(br, "s", br2, "n", "940_BRIDGE")
    f.text(460, 12, "A5  Kunbus DIO 100197  VC-CT-6810")
    f.note("Controller order 100378. DIO order 100197. The PiBridge plug is 100204.", br)
    f.note("ETH1 is a service port. Do not put it in the harness.", f.nodes[-3])
    f.note("X4 order 24 V, 0 V, NC, FG is TBC. RS-485 order GND, N, P is TBC.", pins["FG"])
    return f


def dio(f: Folio) -> Folio:
    f.text(40, 12, "A5  Kunbus DIO 100197  VC-CT-6810", 12)
    inputs = [
        ("I1", "460_LIM_UP", FIELD),
        ("I2", "461_LIM_DN", FIELD),
        ("I3", "420_ESTOP", ESTOP),
        ("I4", "421_PNOZ", OUTPUT),
        ("I5", "440_S200FB", S200C),
        ("I6", "452_SONSTO", ATVC),
        ("I7", "462_ENABLE", FIELD),
        ("I8", "470_TILT_V", FIELD),
        ("I9", "471_TILT_F", FIELD),
        ("I10", "472_LIFT_D", FIELD),
        ("I11", "473_LIFT_R", FIELD),
        ("I12", "451_FAULT", ATVC),
        ("I13", "480_INDEX", FIELD),
    ]
    outputs = [
        ("O1", "490_EXT", LIFT),
        ("O2", "491_RET", LIFT),
        ("O3", "492_TILTV", TILT),
        ("O4", "493_TILTF", TILT),
        ("O5", "494_BEACON", FIELD),
        ("O6", "450_RESET", ATVC),
        ("O7", "495_ROT_EN", ROT),
    ]
    for index, (name, net, other) in enumerate(inputs):
        y = 70 + index * 52
        pin = f.at("term", "n", 340, y, ref="A5", lines=[name], article="VC-CT-6810" if name == "I1" else "")
        f.link(f.inn(180, y, net, other), "e", pin, "n", net)
    for index, (name, net, other) in enumerate(outputs):
        y = 70 + index * 52
        pin = f.at("term", "n", 560, y, ref="A5", lines=[name])
        f.link(pin, "s", f.out(760, f.xy(pin, "s")[1], net, other), "w", net)
    f.note("I1 is I/O-list index 0. Channel names are not a confirmed plug order.", f.nodes[0])
    f.note("Spare inputs and outputs stay open.", f.nodes[0])
    return f


def field(f: Folio) -> Folio:
    f.text(40, 12, "Field devices. X7 is the field strip.", 12)
    rows = [
        ("S4", "limnc", part("VC-CT-6200"), "460_LIM_UP", "X7:1"),
        ("S5", "limnc", part("VC-CT-6200"), "461_LIM_DN", "X7:2"),
        ("S6", "limno", part("VC-CT-6260"), "462_ENABLE", "X7:3"),
    ]
    y0 = 80
    pitch = 70
    contacts = []
    for index, (ref, sym, lines, net, term) in enumerate(rows):
        y = y0 + index * pitch
        contact = f.at(sym, "n", 220, y, ref=ref, lines=lines)
        contacts.append(contact)
        terminal = f.at("term", "n", 420, f.xy(contact, "s")[1], ref=term, lines=[net])
        f.link(contact, "s", terminal, "n", net)
        f.link(terminal, "s", f.out(820, f.xy(terminal, "s")[1], net, DIO), "w", net)
        dot = f.dot(80, y)
        f.link(dot, "4", contact, "n", "211_24C")
    _rail(f, 80, [y0 + i * pitch for i in range(3)], "211_24C")
    # Index sensor. Three terminals, PNP, order code open.
    y = y0 + 3 * pitch
    b24 = f.at("term", "n", 220, y, ref="B1", lines=["24 V"], article="VC-CT-6250")
    f.text(560, y + 8, "OPEN index sensor  VC-CT-6250")
    bout = f.at("term", "n", 220, y + 80, ref="B1", lines=["OUT"])
    b0 = f.at("term", "n", 220, y + 160, ref="B1", lines=["0 V"])
    x74 = f.at("term", "n", 420, f.xy(bout, "s")[1], ref="X7:4", lines=["480_INDEX"])
    f.link(bout, "s", x74, "n", "480_INDEX")
    f.link(x74, "s", f.out(600, f.xy(x74, "s")[1], "480_INDEX", DIO), "w", "480_INDEX")
    f.link(f.dot(80, y), "4", b24, "n", "211_24C")
    f.link(b0, "s", f.dot(f.xy(b0, "s")[0] - 140, f.xy(b0, "s")[1]), "4", "001_0V")
    # Tilt limits only leave the cabinet here.
    for index, (term, net) in enumerate((("X7:5", "470_TILT_V"), ("X7:6", "471_TILT_F"))):
        yy = y + 250 + index * 70
        terminal = f.at("term", "n", 420, yy, ref=term, lines=[net])
        f.link(f.inn(220, yy, net, TILT), "e", terminal, "n", net)
        f.link(terminal, "s", f.out(820, f.xy(terminal, "s")[1], net, DIO), "w", net)
    # Lift limits, two NC in series.
    base = y + 460
    for index, (first, second, mid, net, term) in enumerate(
        (("S14", "S15", "474_DMID", "472_LIFT_D", "X7:7"), ("S16", "S17", "475_RMID", "473_LIFT_R", "X7:8"))
    ):
        yy = base + index * 130
        a = f.at("limnc", "n", 120, yy, ref=first, lines=["OPEN limit"], side="above")
        b = f.at("limnc", "n", 380, f.xy(a, "s")[1], ref=second, lines=["OPEN limit"], side="above")
        terminal = f.at("term", "n", 560, f.xy(b, "s")[1], ref=term, lines=[net])
        f.link(f.dot(80, yy), "4", a, "n", "211_24C")
        f.link(a, "s", b, "n", mid)
        f.link(b, "s", terminal, "n", net)
        f.link(terminal, "s", f.out(820, f.xy(terminal, "s")[1], net, DIO), "w", net)
    # Beacon and the power terminals.
    yy = base + 240
    x79 = f.at("term", "n", 420, yy, ref="X7:9", lines=["494_BEACON"])
    lamp = f.at("lamp", "A1", 620, f.xy(x79, "s")[1], ref="H1", lines=part("VC-CT-6230"))
    f.link(f.inn(220, yy, "494_BEACON", DIO), "e", x79, "n", "494_BEACON")
    f.link(x79, "s", lamp, "A1", "494_BEACON")
    f.note("S4 and S5 are OPEN limit switches. S6 is an IDEC HE1B-M1.", contacts[0])
    f.note("OPEN: the index sensor order code is not chosen. The output is PNP.", b24)
    f.note("S14 to S17 are lift limit contacts. The order code is not chosen.", f.nodes[-8])
    f.note("X7 is the field terminal strip. The purchased block is not chosen.", x74)
    return f


def _diode_return(f: Folio, diode: Node) -> None:
    ax, ay = f.xy(diode, "A")
    side = f.dot(ax + 70, ay)
    f.link(diode, "A", side, "3", "001_0V")
    foot = f.dot(ax + 70, 420)
    f.link(side, "2", foot, "1", "001_0V")


def _rail(f: Folio, x: int, ys: list[int], net: str) -> None:
    dots = []
    for y in ys:
        found = next((node for node in f.nodes if node.sym == "bod" and node.x == x and node.y == y), None)
        dots.append(found or f.dot(x, y))
    for top, bot in zip(dots, dots[1:]):
        f.link(top, "2", bot, "1", net)


def tilt(f: Folio) -> Folio:
    # Vertical command: K3 NC in series with the K2 coil.
    k3nc = f.at("nc", "n", 180, 80, ref="K3", lines=["11-12 NC"])
    k2 = f.at("coil", "A1", 180, 200, ref="K2", lines=["vertical", *part("VC-LT-9230")])
    f.link(f.inn(60, 80, "492_TILTV", DIO), "e", k3nc, "n", "492_TILTV")
    f.link(k3nc, "s", k2, "A1", "496_K2")
    d2 = f.at("diode", "K", 320, f.xy(k2, "A1")[1], ref="D2", lines=part("VC-CT-6780"))
    f.link(k2, "A1", d2, "K", "496_K2")
    _diode_return(f, d2)
    # Fold command.
    k2nc = f.at("nc", "n", 480, 80, ref="K2", lines=["11-12 NC"])
    k3 = f.at("coil", "A1", 480, 200, ref="K3", lines=["fold", *part("VC-LT-9230")])
    f.link(f.inn(360, 80, "493_TILTF", DIO), "e", k2nc, "n", "493_TILTF")
    f.link(k2nc, "s", k3, "A1", "497_K3")
    d3 = f.at("diode", "K", 620, f.xy(k3, "A1")[1], ref="D3", lines=part("VC-CT-6780"))
    f.link(k3, "A1", d3, "K", "497_K3")
    _diode_return(f, d3)
    # 0 V under both coils. The diode return is beside the diode, not through it.
    for node in (k2, k3):
        x, y = f.xy(node, "A2")
        dot = f.dot(x, 420)
        f.link(node, "A2", dot, "1", "001_0V")
    zeros = [node for node in f.nodes if node.sym == "bod" and node.y == 420]
    zeros.sort(key=lambda node: node.x)
    for left, right in zip(zeros, zeros[1:]):
        f.link(left, "4", right, "3", "001_0V")
    f.link(f.inn(40, 420, "001_0V", SUPPLY), "e", zeros[0], "3", "001_0V")
    # Power contacts. Off state puts both leads on 0 V.
    k2no = f.at("no", "n", 180, 500, ref="K2", lines=["21-24 NO"])
    x81 = f.at("term", "n", 360, f.xy(k2no, "s")[1], ref="X8:1", lines=["A"])
    motor = f.at("term", "n", 520, f.xy(x81, "s")[1], ref="M4", lines=["A", *part("VC-LT-9200")])
    f.link(f.inn(60, 500, "211_24C", SUPPLY), "e", k2no, "n", "211_24C")
    f.link(k2no, "s", x81, "n", "498_ACT_A")
    f.link(x81, "s", motor, "n", "498_ACT_A")
    k2nc_p = f.at("nc", "n", 180, f.xy(x81, "n")[1] + 80, ref="K2", lines=["21-22 NC"])
    f.via_h(k2nc_p, "n", x81, "n", "498_ACT_A")
    f.link(k2nc_p, "s", f.dot(180, f.xy(k2nc_p, "s")[1] + 40), "1", "001_0V")
    k3no = f.at("no", "n", 700, 500, ref="K3", lines=["21-24 NO"])
    x82 = f.at("term", "n", 860, f.xy(k3no, "s")[1], ref="X8:2", lines=["B"])
    motor_b = f.at("term", "n", 1000, f.xy(x82, "s")[1], ref="M4", lines=["B"])
    f.link(f.inn(560, 500, "211_24C", SUPPLY), "e", k3no, "n", "211_24C")
    f.link(k3no, "s", x82, "n", "499_ACT_B")
    f.link(x82, "s", motor_b, "n", "499_ACT_B")
    k3nc_p = f.at("nc", "n", 700, f.xy(x82, "n")[1] + 80, ref="K3", lines=["21-22 NC"])
    f.via_h(k3nc_p, "n", x82, "n", "499_ACT_B")
    f.link(k3nc_p, "s", f.dot(700, f.xy(k3nc_p, "s")[1] + 40), "1", "001_0V")
    xref(k2, [k2nc, k2no, k2nc_p])
    xref(k3, [k3nc, k3no, k3nc_p])
    f.note("Each coil is in series with the NC contact of the other relay.", k2)
    f.note("The off state puts both motor leads on 0 V. Do not command both directions.", k2no)
    f.note("Confirm that Finder 62.32 .4000 has no internal diode. D2 and D3 stay fitted.", d2)
    f.note("The actuator current is not on a nameplate. The power section is TBC. Pin 14 is open.", motor)
    return f


def lift(f: Folio) -> Folio:
    f.text(40, 12, "A10  OPEN H-bridge  VC-LT-9110", 12)
    pins = {}
    for index, (name, net, source) in enumerate(
        (("E", "490_EXT", DIO), ("R", "491_RET", DIO), ("P", "211_24C", SUPPLY), ("M", "001_0V", SUPPLY), ("MP", "550_LIFTP", 0), ("MN", "551_LIFTN", 0))
    ):
        y = 80 + index * 60
        pins[name] = f.at("term", "n", 200, y, ref="A10", lines=[name])
        if source:
            f.link(f.inn(60, y, net, source), "e", pins[name], "n", net)
    x101 = f.at("term", "n", 400, f.xy(pins["MP"], "s")[1], ref="X10:1", lines=["M+"])
    x102 = f.at("term", "n", 400, f.xy(pins["MN"], "s")[1], ref="X10:2", lines=["M-"])
    f.link(pins["MP"], "s", x101, "n", "550_LIFTP")
    f.link(pins["MN"], "s", x102, "n", "551_LIFTN")
    m5 = f.at("term", "n", 620, f.xy(x101, "s")[1], ref="M5", lines=["A", *part("VC-LT-9100")])
    m5b = f.at("term", "n", 620, f.xy(x102, "s")[1], ref="M5", lines=["B"])
    m6 = f.at("term", "n", 820, f.xy(m5, "s")[1], ref="M6", lines=["A", *part("VC-LT-9100")])
    m6b = f.at("term", "n", 820, f.xy(m5b, "s")[1], ref="M6", lines=["B"])
    f.link(x101, "s", m5, "n", "550_LIFTP")
    f.link(m5, "s", m6, "n", "550_LIFTP")
    f.link(x102, "s", m5b, "n", "551_LIFTN")
    f.link(m5b, "s", m6b, "n", "551_LIFTN")
    f.note("Do not command both lift directions.", pins["E"])
    f.note("The H-bridge is VC-LT-9110. The lift cable section is TBC.", pins["MP"])
    f.note("Lift limits are on the field folio.", pins["E"])
    return f


def rotation(f: Folio) -> Folio:
    f.text(40, 12, "A6  Nanotec PD2-C4118  VC-CT-6280  proposal, not released", 12)
    fuse = f.at("fuse", "1", 160, 80, ref="F6", lines=part("VC-PW-5790"))
    f.link(f.inn(50, 80, "211_24C", SUPPLY), "e", fuse, "1", "211_24C")
    x91 = f.at("term", "n", 360, f.xy(fuse, "2")[1], ref="X9:1", lines=["+24"])
    f.link(fuse, "2", x91, "n", "500_24R")
    a2 = f.at("term", "n", 560, f.xy(x91, "s")[1], ref="A6", lines=["a2"], article="VC-CT-6280")
    f.link(x91, "s", a2, "n", "500_24R")
    rows = [("b4", "495_ROT_EN", "X9:3", DIO), ("b8", "530_CLKP", "X9:4", 0), ("b6", "532_DIRP", "X9:6", 0)]
    for index, (pin, net, term, source) in enumerate(rows):
        y = 240 + index * 80
        if source:
            terminal = f.at("term", "n", 360, y, ref=term, lines=[net])
            f.link(f.inn(160, y, net, source), "e", terminal, "n", net)
        else:
            clock = f.at("term", "n", 160, y, ref="U2", lines=[pin, "OPEN clock"])
            terminal = f.at("term", "n", 360, f.xy(clock, "s")[1], ref=term, lines=[net])
            f.link(clock, "s", terminal, "n", net)
        drive = f.at("term", "n", 560, f.xy(terminal, "s")[1], ref="A6", lines=[pin])
        f.link(terminal, "s", drive, "n", net)
    # Parked returns and PE.
    for index, (term, text) in enumerate((("X9:2", "0V"), ("X9:5", "CLK-"), ("X9:7", "DIR-"), ("X9:8", "PE"))):
        y = 460 + index * 50
        pin = f.at("term", "n", 200 + index * 140, 500, ref=term, lines=[text])
        if text == "PE":
            f.link(pin, "s", f.at("earth", "PE", f.xy(pin, "s")[0], 600, ref="PE3", lines=["PE"]), "PE", "102_PE")
        else:
            f.link(pin, "s", f.dot(f.xy(pin, "s")[0], 580), "1", "001_0V")
    f.note("Nanotec PD2-C4118L1804-E-01 is a proposal. It speaks USB, not Modbus.", a2)
    f.note("Clock and direction come from U2. U2 is not a DIO pin. Enable is DIO output 7.", f.nodes[6])
    f.note("CLK- and DIR- are parked on 0 V at X9. Do not land them on b5 or b7.", f.nodes[-4])
    f.note("24 V is inside the 12 V to 48 V range. The fuse is 2 A. The wire is 0.75 mm2.", fuse)
    return f


def network(f: Folio) -> Folio:
    f.text(40, 12, "A7  Teltonika RUT241  VC-CT-6600", 12)
    pwr = f.at("term", "n", 200, 100, ref="A7", lines=["1  +24"], article="VC-CT-6600")
    zero = f.at("term", "n", 200, 180, ref="A7", lines=["2  0V"])
    lan = f.at("term", "n", 200, 260, ref="A7", lines=["LAN"])
    f.link(f.inn(60, 100, "211_24C", SUPPLY), "e", pwr, "n", "211_24C")
    f.link(f.inn(60, 180, "001_0V", SUPPLY), "e", zero, "n", "001_0V")
    f.link(f.inn(60, 260, "930_ETH", REVPI), "e", lan, "n", "930_ETH")
    f.note("RUT241 runs from the general 24 V rail. There is no 9 V converter and no PE screw.", pwr)
    f.note("Cat5e from RevPi ETH0 to the router LAN. Assume 0.5 m.", lan)
    f.note("Modbus slave 1 is the ATV320. Slave 2 is the S200. Baud and parity are TODO.", pwr)
    f.note("The rotation drive is not on this bus.", lan)
    return f


def plan(f: Folio) -> Folio:
    f.text(40, 36, "Terminal plan. The symbols are on the circuit folios.", 12)
    for index, (strip, pin, wire, function, note) in enumerate(TERMINALS):
        f.text(40, 64 + index * 20, f"{strip}.{pin}    {wire}    {function}    {note}")
    f.note("The purchased terminal block is not chosen. Wire numbers match the circuit folios.", _anchor(f))
    return f


def cables(f: Folio) -> Folio:
    f.text(40, 36, "Cable list.", 12)
    f.text(40, 64, "Cable    Article    From    To    Section    Shield    Note")
    for index, (name, article, src, dst, section, shield, note) in enumerate(CABLES):
        f.text(40, 96 + index * 28, f"{name}   {article}   {src}   {dst}   {section}   shield {shield}   {note}")
    return f


def notes(f: Folio) -> Folio:
    lines = [
        "This folio holds the points that do not sit in a folio notes field.",
        "OPEN: the E-stop contact block VC-CT-6210 is not chosen.",
        "OPEN: the reset button VC-CT-6270 is not chosen.",
        "OPEN: the index sensor VC-CT-6250 is not chosen. The output is PNP.",
        "OPEN: F21 and F22 have no PWM-rated order code.",
        "TBC: S200 X131 STO-VS and STO-M. Do not land 24 V on STO-VS.",
        "TBC: 440_S200FB is STO_EP and is not landed on a connector.",
        "TBC: ATV320 RJ45 pin numbers, manual NVE41308. DI3 SoMove parameter is TODO.",
        "TBC: RevPi X4 order and the RS-485 printed order.",
        "TBC: W1 is the only 0 V to PE bond. Remove it if the S200 PTI manual forbids it.",
        "The Instagrid source is 15.7 A continuous. The drive rated input is 17.8 A at 200 V.",
        "The drive does not run at rated input on this source.",
        "The Nanotec rotation drive is a proposal and is not on Modbus.",
        "Tilt actuator current and the lift cable section are TBC.",
        "No new price is sourced.",
    ]
    for index, line in enumerate(lines):
        f.text(40, 40 + index * 28, line)
    return f


def cover_note_fix() -> None:
    return None
