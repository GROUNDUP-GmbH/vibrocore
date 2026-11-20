"""Folio wiring for VC-SCH-5000 revision 0D.

Every conductor is straight. A corner is a junction dot.
Product names come from annotate.PRODUCT. Pin names are the revision 0C names.
"""

from __future__ import annotations

from generate_qet import CABLES, PRODUCT, TERMINALS, Folio, Node, part, section_of

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
        "mains": mains(folio(folios, "Mains incoming", 1152)),
        "branch": branches(folio(folios, "Branch feeders", 1024)),
        "supply": supplies(folio(folios, "24 V supplies", 1536)),
        "estop": estop(folio(folios, "E-stop and PNOZ inputs", 1664)),
        "output": outputs(folio(folios, "PNOZ outputs", 1024)),
        "s200p": s200_power(folio(folios, "S200 power and motor", 1024)),
        "s200c": s200_control(folio(folios, "S200 control", 1408)),
        "atva": atv_a(folio(folios, "ATV320 motor A", 1024)),
        "atvb": atv_b(folio(folios, "ATV320 motor B", 1024)),
        "atvc": atv_c(folio(folios, "ATV320 control", 1280)),
        "revpi": revpi(folio(folios, "RevPi supply", 1024)),
        "dio": dio(folio(folios, "DIO channels", 1408)),
        "field": field(folio(folios, "Field devices", 1408)),
        "tilt": tilt(folio(folios, "Tilt", 896)),
        "lift": lift(folio(folios, "Lift", 1280)),
        "rot": rotation(folio(folios, "Rotation proposal", 1152)),
        "net": network(folio(folios, "Network", 768)),
        "plan": plan(folio(folios, "Terminal plan", 1344)),
        "cable": cables(folio(folios, "Cable list")),
        "notes": notes(folio(folios, "Notes", 1024)),
    }
    cover_page(cover, folios)
    if getattr(made["estop"], "coil", None) is not None and getattr(made["output"], "contacts", None) is not None:
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


def device(f: Folio, ref: str, lines: list[str], x: int, y: int, w: int, h: int, pins, article: str = ""):
    """One device box. pins are (key, label, side, y). side is left or right. Wires meet the pin on a straight run."""
    f.rect(x, y, x + w, y + h)
    f.text(x + 12, y + 8, ref, 12)
    for index, line in enumerate(lines):
        f.text(x + 12, y + 28 + index * 16, line)
    out = {}
    for index, (key, label, side, py) in enumerate(pins):
        if side == "left":
            node = f.at("pinw", "1", x, py, ref=ref, lines=[label], side="right", article=article if index == 0 else "", hide_ref=True)
        else:
            node = f.at("pine", "1", x + w, py, ref=ref, lines=[label], side="left", article=article if index == 0 else "", hide_ref=True)
        out[key] = node
    return out


def mains(f: Folio) -> Folio:
    """Three columns. The top source pin feeds the right-hand column so the taps do not cross."""
    g0 = f.at("src", "L", 70, 140, ref="G0", lines=[], side="above", article="VC-PW-5100", hide_ref=True)
    f.text(160, 48, "G0   Instagrid ONE max   VC-PW-5100")
    columns = {"L": 760, "N": 520, "PE": 280}
    taps = {"L": (g0, "L", "100_L", "X1:1"), "N": (g0, "N", "101_N", "X1:2"), "PE": (g0, "PE", "102_PE", "X1:3")}
    wires = {}
    for name, x in columns.items():
        src, key, net, ref = taps[name]
        sx, sy = f.xy(src, key)
        # PE drops clear of the source before it runs across, so its label is not on L or N.
        drop_y = sy + (80 if name == "PE" else 0)
        if name == "PE":
            down = f.dot(sx, drop_y)
            f.link(src, key, down, "1", net)
            corner = f.dot(x, drop_y)
            f.link(down, "4", corner, "3", net)
        else:
            corner = f.dot(x, sy)
            f.link(src, key, corner, "3", net)
        term = f.at("term", "n", x, drop_y + 80, ref=ref, lines=[name])
        f.link(corner, "2", term, "n", net)
        wires[name] = term
    # Ganged poles. The product name sits above the row, not between the columns.
    def poles(y, ref, lines, top_net_l, top_net_n):
        live = f.at("mcb1", "IN.1", columns["L"], y, ref=ref, lines=["L"], article=next(line for line in lines if line.startswith("VC-")))
        neutral = f.at("mcb1", "IN.1", columns["N"], y, ref=ref, lines=["N"], side="left", hide_ref=True)
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
        low = f.dot(ex, ey + 80)
        f.link(node, "OUT.2", low, "1", net)
        arrow = f.out(min(ex + 160, 1000), ey + 80, net, BRANCH)
        f.link(low, "4", arrow, "w", net)
    earth = f.at("earth", "PE", columns["PE"], f.xy(wires["PE"], "s")[1] + 80, ref="PE1", lines=["PE"])
    f.link(wires["PE"], "s", earth, "PE", "102_PE")
    f.note("Instagrid ONE max is the only AC source. Continuous current is 15.7 A.", g0)
    f.note("Q1 does not switch PE. QF1 is type B, 30 mA. The dashed line is the mechanical link.", q_l)
    f.note("F4 feeds the S200 supply. F5 feeds the general 24 V supply. Both continue on folio 03.", f_l)
    f.note("A crossing without a dot is not a connection.", q_l)
    return f


def _dot_at(f: Folio, x: int, y: int) -> Node:
    return next(node for node in f.nodes if node.sym == "bod" and node.x == x and node.y == y)


def branches(f: Folio) -> Folio:
    """F2 is one three-pole device. Pole 3 is open. F3, F4 and F5 stay two-pole."""
    f2 = device(
        f, "F2", ["Schneider GV2L20", "VC-PW-5730"], 280, 80, 280, 300,
        [("Lin", "L", "left", 140), ("Nin", "N", "left", 240), ("P3", "pole 3 open", "left", 340),
         ("Lout", "L", "right", 140), ("Nout", "N", "right", 240)],
        article="VC-PW-5730",
    )
    f.dash(430, 140, 430, 340)
    _bus(f, 160, [140, 560], "130_L", MAINS)
    _bus(f, 210, [240, 710], "131_N", MAINS)
    f.link(_dot_at(f, 160, 140), "4", f2["Lin"], "1", "130_L")
    f.link(_dot_at(f, 210, 240), "4", f2["Nin"], "1", "131_N")
    f.link(f2["Lout"], "1", f.out(660, 140, "140_L", ATVA), "w", "140_L")
    f.link(f2["Nout"], "1", f.out(660, 240, "141_N", ATVA), "w", "141_N")

    def pair(x, y, ref, lines, out_l, out_n, target, rail_l, rail_n):
        live = f.at("mcb1", "IN.1", x, y, ref=ref, lines=["L", *lines], side="above", article=next(line for line in lines if line.startswith("VC-")))
        neutral = f.at("mcb1", "IN.1", x, y + 150, ref=ref, lines=["N"])
        f.dash(x - 22, y, x - 22, y + 150)
        f.link(_dot_at(f, rail_l, y), "4", live, "IN.1", "130_L")
        f.link(_dot_at(f, rail_n, y + 150), "4", neutral, "IN.1", "131_N")
        ox, oy = f.xy(live, "OUT.2")
        f.link(live, "OUT.2", f.out(min(ox + 130, 1080), oy, out_l, target), "w", out_l)
        ox, oy = f.xy(neutral, "OUT.2")
        f.link(neutral, "OUT.2", f.out(min(ox + 130, 1080), oy, out_n, target), "w", out_n)

    pair(420, 560, "F3", part("VC-PW-5740"), "150_L", "151_N", S200P, 160, 210)
    _bus(f, 860, [140, 560], "130_L", MAINS)
    _bus(f, 900, [290, 710], "131_N", MAINS)
    pair(1000, 140, "F4", part("VC-PW-5750"), "160_L", "161_N", SUPPLY, 860, 900)
    pair(1000, 560, "F5", part("VC-PW-5760"), "170_L", "171_N", SUPPLY, 860, 900)
    f.note("F2 is a Schneider GV2L20. NVE41289.09, enclosure, 240 V, one phase. Pole 3 is open.", f2["Lin"])
    f.note("The row is ATV320U15M2. Line current is 17.8 A at 200 V. Irm is 223 A.", f2["Lin"])
    f.note("The sonic feeder is 6 mm2. The S200 feeder is 2.5 mm2.", f2["Lout"])
    f.note("The dashed line is the mechanical link of one device.", f2["P3"])
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
    incoming = f.inn(x - 100, ys[0], net, source)
    f.link(incoming, "e", dots[0], "3", net)


def supplies(f: Folio) -> Folio:
    """G1 above G2. 0 V stays on the right. PE drops on the far left and meets below the 0 V rail."""
    def pins_at(l_y, n_y, pe_y, p_y, m_y):
        return [
            ("L", "L", "left", l_y), ("N", "N", "left", n_y), ("PE", "PE", "left", pe_y),
            ("P", "+", "right", p_y), ("M", "-", "right", m_y),
        ]

    g1 = device(f, "G1", part("VC-PW-5310"), 260, 100, 260, 360, pins_at(160, 260, 400, 160, 260), article="VC-PW-5310")
    g2 = device(f, "G2", part("VC-PW-5320"), 260, 600, 260, 400, pins_at(680, 780, 940, 680, 860), article="VC-PW-5320")
    for supply, net_l, net_n in ((g1, "160_L", "161_N"), (g2, "170_L", "171_N")):
        for name, net in (("L", net_l), ("N", net_n)):
            x, y = f.xy(supply[name], "1")
            f.link(f.inn(160, y, net, BRANCH), "e", supply[name], "1", net)
    for supply, fuse_ref, article, net_in, net_out, target in (
        (g1, "F14", "VC-PW-5800", "200_24S", "201_24S", S200C),
        (g2, "F24", "VC-PW-5810", "210_24C", "211_24C", DIO),
    ):
        px, py = f.xy(supply["P"], "1")
        fuse = f.at("fuse", "1", px + 140, py, ref=fuse_ref, lines=["6 A" if fuse_ref == "F14" else "20 A"], side="left", article=article)
        f.link(supply["P"], "1", fuse, "1", net_in)
        ox, oy = f.xy(fuse, "2")
        f.link(fuse, "2", f.out(ox + 160, oy, net_out, target), "w", net_out)
    # 0 V. The upper drop stops above the fuse arrow, then runs to the right-hand column.
    g1m = f.xy(g1["M"], "1")
    turn = f.dot(760, g1m[1])
    bend = f.dot(760, 340)
    column = f.dot(1000, 340)
    foot = f.dot(1000, 960)
    f.link(g1["M"], "1", turn, "3", "001_0V")
    f.link(turn, "2", bend, "1", "001_0V")
    f.link(bend, "4", column, "3", "001_0V")
    f.link(column, "2", foot, "1", "001_0V")
    g2m = f.xy(g2["M"], "1")
    g2_turn = f.dot(760, g2m[1])
    g2_foot = f.dot(760, 960)
    f.link(g2["M"], "1", g2_turn, "3", "001_0V")
    f.link(g2_turn, "2", g2_foot, "1", "001_0V")
    x14 = f.at("term", "n", 880, 960, ref="X1:4", lines=["0V"])
    f.link(g2_foot, "4", x14, "n", "001_0V")
    f.link(x14, "n", foot, "3", "001_0V")
    # PE on the far left, so the feeder arrows stay to its right. The rail is below the 0 V rail.
    g1p = f.xy(g1["PE"], "1")
    pe_side = f.dot(80, g1p[1])
    pe_g2 = f.dot(80, f.xy(g2["PE"], "1")[1])
    pe_foot = f.dot(80, 1100)
    f.link(g1["PE"], "1", pe_side, "4", "102_PE")
    f.link(pe_side, "2", pe_g2, "1", "102_PE")
    f.link(g2["PE"], "1", pe_g2, "4", "102_PE")
    f.link(pe_g2, "2", pe_foot, "1", "102_PE")
    earth_tap = f.dot(200, 1100)
    bond = f.dot(1000, 1100)
    f.link(pe_foot, "4", earth_tap, "3", "102_PE")
    f.link(earth_tap, "4", bond, "3", "102_PE")
    f.link(foot, "2", bond, "1", "W1")
    earth = f.at("earth", "PE", 200, 1000, ref="PE2", lines=["PE"], side="left")
    f.link(earth, "PE", earth_tap, "1", "102_PE")
    f.note("The general 24 V rail is 2.5 mm2. The S200 24 V feed is 1.0 mm2. There is no 48 V rail.", g1["P"])
    f.note("G2 is an open 24 V slot. SDR-480-24 is the slot size, not a purchase.", g2["P"])
    f.note("Both 0 V rails meet at X1 pin 4. W1 is the only bond to PE. Confirm W1 in the S200 PTI manual.", x14)
    f.note("F14 is 6 A on the S200 rail. F24 is 20 A on the general rail.", g1["P"])
    return f


def estop(f: Folio) -> Folio:
    """Three NC contacts of one mushroom, and the PNOZ s4 as one device box."""
    box = device(
        f, "K1", ["Pilz PNOZ s4", "750104", "VC-CT-6220"],
        760, 80, 320, 1260,
        [
            ("S11", "S11", "left", 180),
            ("S21", "S21", "left", 280),
            ("S22", "S22", "left", 700),
            ("S12", "S12", "left", 820),
            ("S34", "S34", "left", 1040),
            ("A1", "A1", "left", 1160),
            ("A2", "A2", "left", 1280),
        ],
        article="VC-CT-6220",
    )
    # Contacts in one row. The top wire drops furthest left, so the runs do not cross.
    contacts = []
    for x, label in ((200, "11-12"), (360, "21-22"), (520, "31-32")):
        contacts.append(f.at("estop", "n", x, 460, ref="S1", lines=[label], side="left", article="VC-CT-6210" if label == "11-12" else ""))
    s1a, s1b, s1c = contacts
    f.ellipse(60, 390, 130, 445)
    f.dash(95, 445, 95, 460)
    f.dash(95, 448, 560, 448)
    f.text(60, 368, "S1")
    # Channel 1 into the left contact. The higher row reaches the leftmost contact.
    corner = f.dot(f.xy(s1a, "n")[0], f.xy(box["S11"], "1")[1])
    f.link(box["S11"], "1", corner, "4", "410_S11")
    f.link(corner, "2", s1a, "n", "410_S11")
    south = f.xy(s1a, "s")
    join = f.dot(south[0], 820)
    f.link(s1a, "s", join, "1", "411_S12")
    f.link(join, "4", box["S12"], "1", "411_S12")
    s10 = f.at("pb", "n", south[0], 900, ref="S10", lines=part("VC-CT-6270"))
    f.link(join, "2", s10, "n", "411_S12")
    low = f.dot(south[0], 1040)
    f.link(s10, "s", low, "1", "414_S34")
    f.link(low, "4", box["S34"], "1", "414_S34")
    # Channel 2. Its row is below channel 1, and it turns down before the left contact.
    corner = f.dot(f.xy(s1b, "n")[0], f.xy(box["S21"], "1")[1])
    f.link(box["S21"], "1", corner, "4", "412_S21")
    f.link(corner, "2", s1b, "n", "412_S21")
    bsouth = f.xy(s1b, "s")
    bjoin = f.dot(bsouth[0], 700)
    f.link(s1b, "s", bjoin, "1", "413_S22")
    f.link(bjoin, "4", box["S22"], "1", "413_S22")
    # Third contact, DIO only. Its incoming row is below the two channel rows.
    feed = f.dot(520, 360)
    f.link(f.inn(640, 360, "211_24C", SUPPLY), "e", feed, "3", "211_24C")
    f.link(feed, "2", s1c, "n", "211_24C")
    cout = f.xy(s1c, "s")
    cjoin = f.dot(cout[0], 590)
    f.link(s1c, "s", cjoin, "1", "420_ESTOP")
    f.link(cjoin, "4", f.out(680, 590, "420_ESTOP", DIO), "w", "420_ESTOP")
    # Coil supply on its own row, under the contact wiring.
    ax, ay = f.xy(box["A1"], "1")
    f.link(f.inn(80, ay, "211_24C", SUPPLY), "e", box["A1"], "1", "211_24C")
    zx, zy = f.xy(box["A2"], "1")
    f.link(f.inn(80, zy, "001_0V", SUPPLY), "e", box["A2"], "1", "001_0V")
    f.note("Two NC channels go to the PNOZ s4, article 750104. The third NC is DIO input index 2 only.", s1a)
    f.note("Do not feed cabinet 24 V into S11 or S21. The PNOZ makes the test pulses.", box["S11"])
    f.note("The reset sits between S12 and S34. Set a monitored reset. The detent text is TBC.", s10)
    f.note("OPEN: the E-stop contact block and the reset button are not chosen.", s1c)
    return f


def outputs(f: Folio) -> Folio:
    rows = [
        ("13", "14", 180, "F30", "430_F30", "431_STO1", True),
        ("23", "24", 340, "F31", "432_F31", "433_STO2", True),
        ("33", "34", 500, "", "", "", False),
        ("41", "42", 660, "", "421_PNOZ", "421_PNOZ", False),
    ]
    pins = []
    for left, right, y, *_rest in rows:
        pins.append((left, left, "left", y))
        pins.append((right, right, "right", y))
    box = device(
        f, "K1", ["Pilz PNOZ s4", "750104", "VC-CT-6220"],
        400, 100, 300, 640, pins, article="VC-CT-6220",
    )
    f.dash(520, 180, 520, 660)
    for left, right, y, fuse_ref, mid, leave, fused in rows:
        if left == "33":
            continue
        if fused:
            fuse = f.at("fuse", "2", 250, y, ref=fuse_ref, lines=part("VC-PW-5820"), side="above", article="VC-PW-5820")
            ix, iy = f.xy(fuse, "1")
            f.link(f.inn(70, iy, "211_24C", SUPPLY), "e", fuse, "1", "211_24C")
            f.link(fuse, "2", box[left], "1", mid)
        else:
            f.link(f.inn(80, y, "211_24C", SUPPLY), "e", box[left], "1", "211_24C")
        if not leave:
            continue
        ox, oy = f.xy(box[right], "1")
        branch = f.dot(ox + 90, oy)
        f.link(box[right], "1", branch, "3", leave)
        dest = S200C if leave.startswith("43") else DIO
        f.link(branch, "4", f.out(ox + 180, oy, leave, dest), "w", leave)
        if leave.startswith("43"):
            low = f.dot(ox + 90, oy + 80)
            f.link(branch, "2", low, "1", leave)
            f.link(low, "4", f.out(ox + 180, oy + 80, leave, ATVC), "w", leave)
    f.note("Contact 13-14 is STO channel 1. Contact 23-24 is STO channel 2. The section is 0.75 mm2.", box["13"])
    f.note("41-42 is the monitor. Do not use it in the safety path. Its state is TBC.", box["41"])
    f.note("33-34 is spare. Do not load it.", box["33"])
    f.note("Each STO wire goes to the S200 and to the ATV320.", box["14"])
    return f


def s200_power(f: Folio) -> Folio:
    a2 = device(
        f, "A2", ["Siemens 6SL5510", "VC-HB-2300"],
        180, 70, 280, 560,
        [
            ("L1", "L1", "left", 140), ("L2", "L2 open", "left", 240), ("L3", "L3", "left", 340),
            ("U", "U", "right", 140), ("V", "V", "right", 240), ("W", "W", "right", 340),
            ("PE", "PE", "right", 440), ("BRP", "X108 BR+", "right", 540), ("BRN", "X108 BR-", "right", 640),
        ],
        article="VC-HB-2300",
    )
    f.link(f.inn(60, 140, "150_L", BRANCH), "e", a2["L1"], "1", "150_L")
    f.link(f.inn(60, 340, "151_N", BRANCH), "e", a2["L3"], "1", "151_N")
    motor = device(
        f, "M1", ["Siemens 1FL2104", "VC-HB-2100"],
        860, 90, 250, 590,
        [
            ("U", "U", "left", 160), ("V", "V", "left", 260), ("W", "W", "left", 360),
            ("PE", "PE", "left", 460), ("BRP", "BR+", "left", 560), ("BRN", "BR-", "left", 660),
        ],
        article="VC-HB-2100",
    )
    for key, net, ref in (
        ("U", "540_U", "X4:1"), ("V", "541_V", "X4:2"), ("W", "542_W", "X4:3"), ("PE", "102_PE", "X4:4"),
        ("BRP", "543_BRP", "X6:1"), ("BRN", "544_BRN", "X6:2"),
    ):
        dx, dy = f.xy(a2[key], "1")
        term = f.at("term", "n", 680, dy, ref=ref, lines=[key if key not in ("BRP", "BRN") else key[-1:]])
        f.link(a2[key], "1", term, "n", net)
        f.link(term, "s", motor[key], "1", net)
    f.note("Order 6SL5510-1BB11-0AA0. This is the PTI standard drive, not the PROFINET code.", a2["L1"])
    f.note("L2 is open. Mains uses L1 and L3. DCP, R1 and R2 stay open.", a2["L2"])
    f.note("Power cable is 4G1.5 mm2 shielded. Brake pair is 2x0.75 mm2. The coil stays on X108.", a2["BRP"])
    f.note("The Siemens motor-cable order code is TODO.", motor["U"])
    return f


def s200_control(f: Folio) -> Folio:
    rows = [
        ("p1", "STO1+", "431_STO1", OUTPUT),
        ("p2", "STO1-", "001_0V", SUPPLY),
        ("p3", "STO-VS TBC", "", 0),
        ("p4", "STO-M TBC", "", 0),
        ("p5", "STO2+", "433_STO2", OUTPUT),
        ("p6", "STO2-", "001_0V", SUPPLY),
        ("fb", "STO_EP not landed", "440_S200FB", DIO),
        ("s24", "X124 24 V", "201_24S", SUPPLY),
        ("s24b", "X124 24 V", "201_24S", SUPPLY),
        ("s0", "X124 0 V", "001_0V", SUPPLY),
        ("s0b", "X124 0 V", "001_0V", SUPPLY),
        ("x120", "X120 encoder", "", 0),
    ]
    pins = []
    y = 120
    ys = {}
    for key, label, _net, _src in rows:
        pins.append((key, label, "left", y))
        ys[key] = y
        y += 80
    pins += [
        ("n23", "23", "right", 200),
        ("n25", "25", "right", 240),
        ("n36", "36", "right", 400),
        ("n37", "37", "right", 480),
        ("n38", "38", "right", 560),
        ("n39", "39", "right", 640),
    ]
    a2 = device(f, "A2", ["Siemens 6SL5510", "VC-HB-2300"], 240, 60, 500, 1000, pins, article="VC-HB-2300")
    for key, _label, net, source in rows:
        if not net:
            continue
        x, py = f.xy(a2[key], "1")
        f.link(f.inn(60, py, net, source), "e", a2[key], "1", net)
    sx, sy = f.xy(a2["x120"], "1")
    x51 = f.at("term", "n", 900, sy, ref="X5:1", lines=["ENC"])
    f.link(a2["x120"], "1", x51, "n", "510_ENC")
    f.at("term", "n", 900, sy + 200, ref="X5:2", lines=["shield"])
    r1 = f.at("res", "A1", 880, 200, ref="R1", lines=part("VC-CT-6790"), side="above")
    f.link(a2["n23"], "1", r1, "A1", "910_A")
    f.link(r1, "A2", a2["n25"], "1", "911_B")
    f.link(r1, "A1", f.out(1040, 200, "910_A", REVPI), "w", "910_A")
    f.link(r1, "A2", f.out(1040, 240, "911_B", REVPI), "w", "911_B")
    for key, pin in (("n36", "36"), ("n37", "37"), ("n38", "38"), ("n39", "39")):
        px, py = f.xy(a2[key], "1")
        src = f.at("term", "n", px + 160, py, ref="U1", lines=[pin])
        f.link(a2[key], "1", src, "n", {"36": "520_PULSP", "37": "521_PULSN", "38": "522_SIGNP", "39": "523_SIGNN"}[pin])
    f.text(860, 740, "U1 pulse source TODO")
    f.note("X131 is 1 STO1+, 2 STO1-, 3 STO-VS, 4 STO-M, 5 STO2+, 6 STO2-. STO-VS and STO-M are TBC.", a2["p1"])
    f.note("Do not land 24 V on STO-VS. X130 is not on this PTI drive.", a2["p3"])
    f.note("STO status is status word bit STO_EP. Do not land 440_S200FB on a connector.", a2["fb"])
    f.note("X124 screws are marked 24 V and 0 V. Both screws of one mark are one node.", a2["s24b"])
    f.note("VC-HB-3450 is the catalogue encoder cable. The Siemens order code is TODO.", a2["x120"])
    f.note("U1 is not a DIO pin. Pulse form and scale are TBC.", a2["n36"])
    f.note("Encoder map, drive to motor: 7 A, 8 B, 4 C, 5 D, 1 E, 2 F.", a2["x120"])
    f.note("R1 is 120 ohm at the S200. The shield lands on PE at the RevPi only.", r1)
    f.note("X5 pin 2 is the shield. Land the shield at one end only.", a2["x120"])
    return f


def atv_a(f: Folio) -> Folio:
    a3 = device(
        f, "A3", ["ATV320U15M2C", "VC-SH-1210"],
        220, 80, 200, 420,
        [
            ("L1", "L1", "left", 180), ("L2", "L2", "left", 280),
            ("U", "U", "right", 180), ("V", "V", "right", 280), ("W", "W", "right", 380), ("PE", "PE", "right", 460),
        ],
        article="VC-SH-1210",
    )
    for name, net in (("L1", "140_L"), ("L2", "141_N")):
        x, y = f.xy(a3[name], "1")
        f.link(f.inn(60, y, net, BRANCH), "e", a3[name], "1", net)
    guard = device(
        f, "F21", ["VC-PW-5770"],
        620, 100, 150, 340,
        [
            ("Ui", "U", "left", 180), ("Vi", "V", "left", 280), ("Wi", "W", "left", 380),
            ("Uo", "U", "right", 180), ("Vo", "V", "right", 280), ("Wo", "W", "right", 380),
        ],
        article="VC-PW-5770",
    )
    f.dash(695, 180, 695, 380)
    motor = device(
        f, "M2", ["MVE 400", "VC-SH-1100"],
        1020, 120, 120, 400,
        [("U", "U", "left", 200), ("V", "V", "left", 300), ("W", "W", "left", 400), ("PE", "PE", "left", 480)],
        article="VC-SH-1100",
    )
    for phase, net_in, net_out, ref in (
        ("U", "600_U", "610_UA", "X2:1"),
        ("V", "600_V", "611_VA", "X2:2"),
        ("W", "600_W", "612_WA", "X2:3"),
    ):
        f.link(a3[phase], "1", guard[phase + "i"], "1", net_in)
        ox, oy = f.xy(guard[phase + "o"], "1")
        term = f.at("term", "n", 860, oy, ref=ref, lines=[phase])
        f.link(guard[phase + "o"], "1", term, "n", net_out)
        f.link(term, "s", motor[phase], "1", net_out)
    px, py = f.xy(a3["PE"], "1")
    x24 = f.at("term", "n", 860, py, ref="X2:4", lines=["PE"])
    f.link(a3["PE"], "1", x24, "n", "102_PE")
    f.link(x24, "s", motor["PE"], "1", "102_PE")
    f.note("One ATV320 output feeds both OLI MVE 400/6-HF motors. Each motor is 1.45 A.", a3["U"])
    f.note("Motor A keeps the drive phase order.", motor["U"])
    f.note("OPEN: F21 needs a PWM-rated protector. Do not fit a standard GV2.", guard["Ui"])
    f.note("Supply wire is 6 mm2. 600_U, 600_V and 600_W are the drive-to-F21 run at 1.5 mm2, the same section as the 4G1.5 motor cable.", a3["L1"])
    return f


def atv_b(f: Folio) -> Folio:
    a3 = device(
        f, "A3", ["ATV320 output", "motor B"],
        220, 80, 180, 360,
        [("U", "U", "left", 180), ("V", "V", "left", 280), ("W", "W", "left", 380)],
    )
    for name in ("U", "V", "W"):
        x, y = f.xy(a3[name], "1")
        f.link(f.inn(60, y, "600_" + name, ATVA), "e", a3[name], "1", "600_" + name)
    guard = device(
        f, "F22", ["VC-PW-5770"],
        600, 100, 150, 340,
        [
            ("Ui", "U", "left", 180), ("Vi", "V", "left", 280), ("Wi", "W", "left", 380),
            ("Uo", "U", "right", 180), ("Vo", "V", "right", 280), ("Wo", "W", "right", 380),
        ],
        article="VC-PW-5770",
    )
    f.dash(675, 180, 675, 380)
    # The swap is the terminal assignment. Row V goes to motor W. Row W goes to motor V.
    motor = device(
        f, "M3", ["MVE 400", "VC-SH-1100"],
        1020, 120, 120, 400,
        [("U", "U", "left", 200), ("W", "W", "left", 300), ("V", "V", "left", 400), ("PE", "PE", "left", 480)],
        article="VC-SH-1100",
    )
    plan = (
        ("U", "Uo", "620_UB", "X3:1", "U"),
        ("V", "Vo", "621_VB", "X3:3", "W"),
        ("W", "Wo", "622_WB", "X3:2", "V"),
    )
    for phase, out_key, net, ref, motor_key in plan:
        f.link(a3[phase], "1", guard[phase + "i"], "1", "600_" + phase)
        ox, oy = f.xy(guard[out_key], "1")
        term = f.at("term", "n", 860, oy, ref=ref, lines=[ref[-1]])
        f.link(guard[out_key], "1", term, "n", net)
        f.link(term, "s", motor[motor_key], "1", net)
    x34 = f.at("term", "n", 860, 460, ref="X3:4", lines=["PE"])
    f.link(x34, "s", motor["PE"], "1", "102_PE")
    f.note("Motor B swaps V and W at X3 so the motors turn in opposite directions.", motor["U"])
    f.note("X3 pin 2 is cabinet W on motor V. X3 pin 3 is cabinet V on motor W.", guard["Wi"])
    f.note("OPEN: F22 needs a PWM-rated protector. Do not fit a standard GV2.", guard["Ui"])
    f.note("The motor cable stays 4G1.5 shielded at the drive.", x34)
    return f


def atv_c(f: Folio) -> Folio:
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
    pins = []
    y = 120
    for key, label, _net, _src in rows:
        pins.append((key, label, "left", y))
        y += 80
    a3 = device(f, "A3", ["Schneider ATV320U15M2C", "VC-SH-1210"], 240, 60, 420, y - 40, pins, article="VC-SH-1210")
    for key, _label, net, source in rows:
        if not net:
            continue
        px, py = f.xy(a3[key], "1")
        f.link(f.inn(80, py, net, source), "e", a3[key], "1", net)
    f.note("The drive STO screw is one terminal. DI3 is the second channel. The SoMove parameter is TODO.", a3["DI3"])
    f.note("Do not tie P24 to the cabinet 24 V. There is no braking resistor.", a3["P24"])
    f.note("R1C is the fault-relay common. R1B is the NC contact. R1A is open.", a3["R1C"])
    f.note("RJ45 pin numbers are TBC. See the Modbus manual NVE41308.", a3["RJA"])
    return f


def revpi(f: Folio) -> Folio:
    a4 = device(
        f, "A4", ["Kunbus RevPi", "100378", "VC-CT-6800"],
        200, 80, 360, 560,
        [
            ("24", "24", "left", 160), ("0", "0", "left", 240), ("GND", "GND", "left", 320),
            ("FG", "FG", "left", 400), ("P", "P", "left", 480), ("N", "N", "left", 560),
            ("ETH0", "ETH0", "right", 160), ("ETH1", "ETH1 service", "right", 260), ("BR", "PiBridge", "right", 360),
        ],
        article="VC-CT-6800",
    )
    for name, net, source in (
        ("24", "211_24C", SUPPLY), ("0", "001_0V", SUPPLY), ("GND", "001_0V", SUPPLY),
        ("FG", "102_PE", MAINS), ("P", "910_A", S200C), ("N", "911_B", S200C),
    ):
        x, y = f.xy(a4[name], "1")
        f.link(f.inn(70, y, net, source), "e", a4[name], "1", net)
    ex, ey = f.xy(a4["ETH0"], "1")
    f.link(a4["ETH0"], "1", f.out(ex + 120, ey, "930_ETH", NET), "w", "930_ETH")
    a5 = device(f, "A5", ["Kunbus DIO", "100197", "VC-CT-6810"], 780, 280, 220, 160, [("BR", "PiBridge", "left", 360)], article="VC-CT-6810")
    f.link(a4["BR"], "1", a5["BR"], "1", "940_BRIDGE")
    f.note("Controller order 100378. DIO order 100197. The PiBridge plug is 100204.", a4["BR"])
    f.note("ETH1 is a service port. Do not put it in the harness.", a4["ETH1"])
    f.note("X4 order 24 V, 0 V, NC, FG is TBC. RS-485 order GND, N, P is TBC.", a4["FG"])
    return f


def dio(f: Folio) -> Folio:
    inputs = [
        ("I1", "460_LIM_UP", FIELD), ("I2", "461_LIM_DN", FIELD), ("I3", "420_ESTOP", ESTOP),
        ("I4", "421_PNOZ", OUTPUT), ("I5", "440_S200FB", S200C), ("I6", "452_SONSTO", ATVC),
        ("I7", "462_ENABLE", FIELD), ("I8", "470_TILT_V", FIELD), ("I9", "471_TILT_F", FIELD),
        ("I10", "472_LIFT_D", FIELD), ("I11", "473_LIFT_R", FIELD), ("I12", "451_FAULT", ATVC),
        ("I13", "480_INDEX", FIELD),
    ]
    outputs = [
        ("O1", "490_EXT", LIFT), ("O2", "491_RET", LIFT), ("O3", "492_TILTV", TILT),
        ("O4", "493_TILTF", TILT), ("O5", "494_BEACON", FIELD), ("O6", "450_RESET", ATVC),
        ("O7", "495_ROT_EN", ROT),
    ]
    pins = []
    for index, (name, _net, _other) in enumerate(inputs):
        pins.append((name, name, "left", 200 + index * 80))
    for index, (name, _net, _other) in enumerate(outputs):
        pins.append((name, name, "right", 200 + index * 80))
    box = device(f, "A5", ["Kunbus DIO", "100197", "VC-CT-6810"], 280, 60, 420, 1180, pins, article="VC-CT-6810")
    for name, net, other in inputs:
        x, y = f.xy(box[name], "1")
        f.link(f.inn(80, y, net, other), "e", box[name], "1", net)
    for name, net, other in outputs:
        x, y = f.xy(box[name], "1")
        f.link(box[name], "1", f.out(min(x + 140, 1080), y, net, other), "w", net)
    f.note("I1 is I/O-list index 0. Channel names are not a confirmed plug order.", box["I1"])
    f.note("Spare inputs and outputs stay open.", box["I1"])
    return f


def field(f: Folio) -> Folio:
    f.text(48, 48, "Field devices. X7 is the field strip.", 12)
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
        a = f.at("limnc", "n", 200, yy, ref=first, lines=["OPEN limit"], side="above")
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
    f.link(k2nc_p, "s", f.dot(180, f.xy(k2nc_p, "s")[1] + 80), "1", "001_0V")
    k3no = f.at("no", "n", 700, 500, ref="K3", lines=["21-24 NO"])
    x82 = f.at("term", "n", 860, f.xy(k3no, "s")[1], ref="X8:2", lines=["B"])
    motor_b = f.at("term", "n", 1000, f.xy(x82, "s")[1], ref="M4", lines=["B"])
    f.link(f.inn(560, 500, "211_24C", SUPPLY), "e", k3no, "n", "211_24C")
    f.link(k3no, "s", x82, "n", "499_ACT_B")
    f.link(x82, "s", motor_b, "n", "499_ACT_B")
    k3nc_p = f.at("nc", "n", 700, f.xy(x82, "n")[1] + 80, ref="K3", lines=["21-22 NC"])
    f.via_h(k3nc_p, "n", x82, "n", "499_ACT_B")
    f.link(k3nc_p, "s", f.dot(700, f.xy(k3nc_p, "s")[1] + 80), "1", "001_0V")
    xref(k2, [k2nc, k2no, k2nc_p])
    xref(k3, [k3nc, k3no, k3nc_p])
    f.note("Each coil is in series with the NC contact of the other relay.", k2)
    f.note("The off state puts both motor leads on 0 V. Do not command both directions.", k2no)
    f.note("Confirm that Finder 62.32 .4000 has no internal diode. D2 and D3 stay fitted.", d2)
    f.note("The actuator current is not on a nameplate. The power section is TBC. Pin 14 is open.", motor)
    return f


def lift(f: Folio) -> Folio:
    f.text(48, 48, "A10  OPEN H-bridge  VC-LT-9110", 12)
    pins = {}
    for index, (name, net, source) in enumerate(
        (("E", "490_EXT", DIO), ("R", "491_RET", DIO), ("P", "211_24C", SUPPLY), ("M", "001_0V", SUPPLY), ("MP", "550_LIFTP", 0), ("MN", "551_LIFTN", 0))
    ):
        y = 180 + index * 80
        pins[name] = f.at("term", "n", 200, y, ref="A10", lines=[name])
        if source:
            f.link(f.inn(60, y, net, source), "e", pins[name], "n", net)
    x101 = f.at("term", "n", 400, f.xy(pins["MP"], "s")[1], ref="X10:1", lines=["M+"])
    x102 = f.at("term", "n", 400, f.xy(pins["MN"], "s")[1], ref="X10:2", lines=["M-"])
    f.link(pins["MP"], "s", x101, "n", "550_LIFTP")
    f.link(pins["MN"], "s", x102, "n", "551_LIFTN")
    m5 = f.at("term", "n", 620, f.xy(x101, "s")[1], ref="M5", lines=["A"], article="VC-LT-9100")
    m5b = f.at("term", "n", 620, f.xy(x102, "s")[1], ref="M5", lines=["B"], hide_ref=True)
    m6 = f.at("term", "n", 820, f.xy(m5, "s")[1], ref="M6", lines=["A"], article="VC-LT-9100")
    m6b = f.at("term", "n", 820, f.xy(m5b, "s")[1], ref="M6", lines=["B"], hide_ref=True)
    f.text(640, m5.y - 36, "M5 / M6  VC-LT-9100")
    f.link(x101, "s", m5, "n", "550_LIFTP")
    f.link(m5, "s", m6, "n", "550_LIFTP")
    f.link(x102, "s", m5b, "n", "551_LIFTN")
    f.link(m5b, "s", m6b, "n", "551_LIFTN")
    f.note("Do not command both lift directions.", pins["E"])
    f.note("The H-bridge is VC-LT-9110. The lift cable section is TBC.", pins["MP"])
    f.note("Lift limits are on the field folio.", pins["E"])
    return f


def rotation(f: Folio) -> Folio:
    f.text(48, 48, "A6  Nanotec PD2-C4118  VC-CT-6280  proposal, not released", 12)
    fuse = f.at("fuse", "1", 240, 200, ref="F6", lines=["2 A"], side="right", article="VC-PW-5790")
    f.link(f.inn(60, 200, "211_24C", SUPPLY), "e", fuse, "1", "211_24C")
    x91 = f.at("term", "n", 400, f.xy(fuse, "2")[1], ref="X9:1", lines=["+24"])
    f.link(fuse, "2", x91, "n", "500_24R")
    a2 = f.at("term", "n", 700, f.xy(x91, "s")[1], ref="A6", lines=["a2"], article="VC-CT-6280")
    f.link(x91, "s", a2, "n", "500_24R")
    rows = [("b4", "495_ROT_EN", "X9:3", DIO), ("b8", "530_CLKP", "X9:4", 0), ("b6", "532_DIRP", "X9:6", 0)]
    for index, (pin, net, term, source) in enumerate(rows):
        y = 400 + index * 100
        if source:
            terminal = f.at("term", "n", 360, y, ref=term, lines=[net])
            f.link(f.inn(160, y, net, source), "e", terminal, "n", net)
        else:
            clock = f.at("term", "n", 160, y, ref="U2", lines=[pin, "OPEN clock"])
            terminal = f.at("term", "n", 360, f.xy(clock, "s")[1], ref=term, lines=[net])
            f.link(clock, "s", terminal, "n", net)
        drive = f.at("term", "n", 700, f.xy(terminal, "s")[1], ref="A6", lines=[pin])
        f.link(terminal, "s", drive, "n", net)
    # Parked returns and PE, below the signal rows.
    for index, (term, text) in enumerate((("X9:2", "0V"), ("X9:5", "CLK-"), ("X9:7", "DIR-"), ("X9:8", "PE"))):
        x = 160 + index * 180
        pin = f.at("term", "n", x, 800, ref=term, lines=[text])
        if text == "PE":
            f.link(pin, "s", f.at("earth", "PE", x, 920, ref="PE3", lines=["PE"], side="right"), "PE", "102_PE")
        else:
            f.link(pin, "s", f.dot(x, 920), "1", "001_0V")
    f.note("Nanotec PD2-C4118L1804-E-01 is a proposal. It speaks USB, not Modbus.", a2)
    f.note("Clock and direction come from U2. U2 is not a DIO pin. Enable is DIO output 7.", f.nodes[6])
    f.note("CLK- and DIR- are parked on 0 V at X9. Do not land them on b5 or b7.", f.nodes[-4])
    f.note("24 V is inside the 12 V to 48 V range. The fuse is 2 A. The wire is 0.75 mm2.", fuse)
    return f


def network(f: Folio) -> Folio:
    a7 = device(
        f, "A7", ["Teltonika RUT241", "VC-CT-6600"],
        240, 80, 360, 320,
        [("p1", "1  +24", "left", 160), ("p2", "2  0V", "left", 250), ("lan", "LAN", "left", 340)],
        article="VC-CT-6600",
    )
    for key, net in (("p1", "211_24C"), ("p2", "001_0V"), ("lan", "930_ETH")):
        x, y = f.xy(a7[key], "1")
        source = SUPPLY if net != "930_ETH" else REVPI
        f.link(f.inn(80, y, net, source), "e", a7[key], "1", net)
    f.note("RUT241 runs from the general 24 V rail. There is no 9 V converter and no PE screw.", a7["p1"])
    f.note("Cat5e from RevPi ETH0 to the router LAN. Assume 0.5 m.", a7["lan"])
    f.note("Modbus slave 1 is the ATV320. Slave 2 is the S200. Baud and parity are TODO.", a7["p1"])
    f.note("The rotation drive is not on this bus.", a7["lan"])
    return f


def plan(f: Folio) -> Folio:
    f.text(48, 48, "Terminal plan. The symbols are on the circuit folios.", 12)
    for index, (strip, pin, wire, function, note) in enumerate(TERMINALS):
        f.text(48, 80 + index * 20, f"{strip}.{pin}    {wire}    {function}    {note}")
    f.note("The purchased terminal block is not chosen. Wire numbers match the circuit folios.", _anchor(f))
    return f


def cables(f: Folio) -> Folio:
    f.text(48, 48, "Cable list.", 12)
    f.text(48, 76, "Cable    Article    From    To    Section    Shield    Note")
    for index, (name, article, src, dst, section, shield, note) in enumerate(CABLES):
        f.text(48, 108 + index * 28, f"{name}   {article}   {src}   {dst}   {section}   shield {shield}   {note}")
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
        f.text(48, 48 + index * 22, line)
    f.tail = 48 + len(lines) * 22 + 20
    return f


def cover_note_fix() -> None:
    return None
