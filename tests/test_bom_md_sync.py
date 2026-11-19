"""Fail CI when docs/engineering/BOM.md and the YAML single source diverge."""

from cad.tools.bom import load_bom
from cad.tools.bom_md import compare_bom_md_and_yaml, parse_bom_md, yaml_position_map


def test_bom_md_parses_v11_positions():
    rows = {row.position: row for row in parse_bom_md()}
    assert "47b" in rows and "RevPi" in rows["47b"].component
    assert "48b" in rows
    assert "70" in rows and rows["70"].qty == 2
    assert "80" in rows and "Raspberry Pi 4" in rows["80"].component
    assert "38" in rows and rows["38"].qty == 0


def test_yaml_maps_required_v11_parts():
    bom = load_bom()
    mapping = yaml_position_map(bom)
    assert mapping["47b"] == ["VC-CT-6800"]
    assert mapping["48b"] == ["VC-CT-6810"]
    assert "VC-LT-9100" in mapping["70"]
    assert "VC-CS-9400" in mapping["80"]
    assert bom.part("VC-FR-4700").lifecycle == "obsolete"
    assert bom.part("VC-PW-5300").lifecycle == "superseded"
    assert bom.part("VC-PW-5310").manufacturer_pn == "SDR-120-24"


def test_bom_md_and_yaml_are_aligned():
    errors = compare_bom_md_and_yaml()
    assert errors == [], "\n".join(errors)
