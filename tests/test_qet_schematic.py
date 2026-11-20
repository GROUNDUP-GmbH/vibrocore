"""VC-SCH-5000 revision 0D stays valid and matches the component list.

The check parses the QElectroTech project. It does not run QElectroTech.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from cad.tools.bom import ROOT

QET = ROOT / "cad" / "electrical" / "VC-SCH-5000" / "VC-SCH-5000.qet"

# Articles that revision 0C already assigned. OPEN stays OPEN. No new code.
ARTICLES = (
    "VC-PW-5100",
    "VC-PW-5310",
    "VC-PW-5320",
    "VC-PW-5700",
    "VC-PW-5710",
    "VC-PW-5720",
    "VC-PW-5730",
    "VC-PW-5740",
    "VC-PW-5750",
    "VC-PW-5760",
    "VC-PW-5770",
    "VC-PW-5800",
    "VC-PW-5810",
    "VC-PW-5820",
    "VC-CT-6220",
    "VC-CT-6800",
    "VC-CT-6810",
    "VC-CT-6600",
    "VC-HB-2300",
    "VC-SH-1210",
    "VC-SH-1100",
    "VC-LT-9230",
)

WIRES = ("100_L", "101_N", "102_PE", "001_0V", "211_24C", "431_STO1", "433_STO2", "W1")
STRIPS = tuple(f"X{number}" for number in range(1, 11))


def _project() -> ET.Element:
    return ET.parse(QET).getroot()


def test_project_parses_and_names_the_drawing():
    root = _project()
    assert root.tag == "project"
    assert root.get("version") == "0.100"
    diagrams = root.findall("diagram")
    assert len(diagrams) == 21
    info = diagrams[0]
    assert info.get("author") == "Ground UP GmbH"
    assert info.get("filename") == "VC-SCH-5000"
    assert info.get("indexrev") == "0D"
    assert info.get("date") == "2026-11-20"


def test_every_symbol_and_terminal_resolves():
    root = _project()
    embedded = {element.get("name") for element in root.findall("collection/category/element")}
    for diagram in root.findall("diagram"):
        terminals = {}
        for element in diagram.findall("elements/element"):
            name = element.get("type").split("/")[-1]
            assert name in embedded, name
            for terminal in element.findall("terminals/terminal"):
                terminals[(element.get("uuid"), terminal.get("uuid"))] = (
                    int(float(element.get("x"))) + int(float(terminal.get("x"))),
                    int(float(element.get("y"))) + int(float(terminal.get("y"))),
                )
        for conductor in diagram.findall("conductors/conductor"):
            start = terminals[(conductor.get("element1"), conductor.get("terminal1"))]
            end = terminals[(conductor.get("element2"), conductor.get("terminal2"))]
            assert start[0] == end[0] or start[1] == end[1], conductor.get("num")


def test_text_is_readable_and_the_old_relay_is_absent():
    text = QET.read_text(encoding="utf-8")
    for token in text.split('font="')[1:]:
        face = token.split('"', 1)[0]
        size = int(face.split(",")[1])
        # 9 pt is the pin letter inside an IEC symbol. At the folio scale that is about 2.6 mm.
        assert size >= 9, face
    assert "ATV320" in text
    assert "100378" in text
    assert "100197" in text
    assert "750104" in text
    assert "750-8212" not in text
    assert "PNOZ s7" not in text


def test_motor_feed_section_matches_the_cable():
    sections = {
        conductor.get("num"): conductor.get("conductor_section")
        for conductor in _project().findall(".//conductor")
        if conductor.get("num") in {"600_U", "600_V", "600_W"}
    }
    assert set(sections) == {"600_U", "600_V", "600_W"}
    assert set(sections.values()) == {"1.5 mm2"}


def test_geometry_gate_reports_no_hit():
    import sys

    path = str(ROOT / "cad" / "electrical" / "VC-SCH-5000")
    if path not in sys.path:
        sys.path.insert(0, path)
    import generate_qet

    generate_qet.load_symbols()
    import sheets_qet

    generate_qet.check(sheets_qet.build())


def test_articles_strips_and_wires_match_revision_0c():
    root = _project()
    articles = {
        item.text
        for item in root.findall(".//elementInformation[@name='manufacturer_reference']")
        if item.text
    }
    missing = [article for article in ARTICLES if article not in articles]
    assert not missing, missing
    labels = {
        item.text
        for item in root.findall(".//elementInformation[@name='label']")
        if item.text
    }
    for strip in STRIPS:
        assert any(label == strip or label.startswith(strip + ":") for label in labels), strip
    nets = {conductor.get("num") for conductor in root.findall(".//conductor")}
    for wire in WIRES:
        assert wire in nets, wire
