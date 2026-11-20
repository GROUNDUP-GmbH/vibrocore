"""Mast stack study. The profile length stays 1500 mm. Placeholders stay marked TBD."""

import json

from cad.models.mast_layout import (
    CASING_ID_MM,
    CASING_LENGTH_MM,
    CASING_OD_MM,
    DOCUMENT_ID,
    LAYOUT_DIR,
    MAST_PROFILE_LENGTH_MM,
    PLACEHOLDERS,
    SHOE_OD_MM,
    available_mast_stroke_mm,
    chain_terms,
    deficit_vs_profile_mm,
    deficit_vs_stroke_mm,
    documented_axial_mm,
    head_length_mm,
    required_total_mm,
    sampling_remainder_mm,
)
from cad.tools.bom import ROOT, load_bom
from cad.tools.geometry import read_step_bbox_mm
from cad.tools.mast_drawing import chain_lines


CHAIN_NAMES = (
    "ground_clearance",
    "shoe",
    "casing",
    "adapter",
    "head",
    "carriage",
    "top_margin",
)


def test_profile_length_stays_1500_mm():
    bom = load_bom()
    profile = bom.part("VC-FR-4100")
    assert profile.geometry["height_mm"] == 1500
    assert MAST_PROFILE_LENGTH_MM == 1500.0
    issue = next(item for item in bom.issues if item["id"] == "mast-height-deficit")
    assert "docs/engineering/MAST-LAYOUT.md" in issue["summary"]
    assert "1500 mm profile is unchanged" in issue["summary"]
    assert "TBD" in issue["summary"]


def test_chain_uses_documented_casing_and_shoe_diameter():
    assert CASING_LENGTH_MM == 1219.2
    assert CASING_OD_MM == 82.55
    assert CASING_ID_MM == 66.675
    assert SHOE_OD_MM == 87.63
    names = [term.name for term in chain_terms()]
    assert names == list(CHAIN_NAMES)
    assert required_total_mm() == round(sum(term.length_mm for term in chain_terms()), 1)


def test_placeholders_are_named_and_marked_tbd():
    for name in (
        "shoe_length_mm",
        "adapter_length_mm",
        "carriage_height_mm",
        "ground_clearance_mm",
        "top_margin_mm",
        "column_flange_thickness_mm",
    ):
        value, note = PLACEHOLDERS[name]
        assert value > 0
        assert note.startswith("TBD")
    shoe = next(term for term in chain_terms() if term.name == "shoe")
    assert shoe.tbd is True
    casing = next(term for term in chain_terms() if term.name == "casing")
    assert casing.tbd is False


def test_deficit_is_computed_from_the_parameters():
    assert available_mast_stroke_mm() == 1300.0
    # Motors sit left and right, so the 175 mm height is not in the head.
    assert head_length_mm() == 232.0
    assert required_total_mm() == 1761.2
    assert deficit_vs_stroke_mm() == 461.2
    assert deficit_vs_profile_mm() == 261.2
    assert documented_axial_mm() == 1439.2
    assert round(documented_axial_mm() - MAST_PROFILE_LENGTH_MM, 1) == -60.8
    assert head_length_mm(include_motor=True) == 407.0
    assert required_total_mm(include_motor=True) == 1936.2
    assert documented_axial_mm(include_motor=True) == 1614.2
    assert sampling_remainder_mm() == 33.8


def test_sheet_prints_the_same_deficit():
    text = "\n".join(chain_lines())
    assert "Deficit against stroke: 461.2 mm." in text
    assert "Deficit against profile: 261.2 mm." in text
    assert "Motor height 175 mm is not in the head." in text
    svg = (LAYOUT_DIR / "mast-stack.svg").read_text(encoding="utf-8")
    pdf = (LAYOUT_DIR / "mast-stack.pdf").read_bytes()
    assert "Deficit against stroke: 461.2 mm" in svg
    assert "+ top margin." in svg
    assert "TBD" in svg
    assert "ground line" in svg
    assert pdf.startswith(b"%PDF-1.4")
    assert b"461.2" in pdf
    assert b"MAST-LAYOUT" in pdf
    doc = (ROOT / "docs/engineering/MAST-LAYOUT.md").read_text(encoding="utf-8")
    assert "461.2 mm" in doc
    assert "Longer profile" in doc
    assert "Telescopic mast" in doc
    assert "Two-stage push" in doc
    assert "VC-FR-4100 stays 1500 mm" in doc


def test_layout_step_is_not_a_part_and_matches_the_stack():
    bom = load_bom()
    assert DOCUMENT_ID not in bom.parts
    manifest = json.loads((ROOT / "cad/export/geometry.json").read_text(encoding="utf-8"))
    assert all(row["part_number"] != DOCUMENT_ID for row in manifest)
    size = read_step_bbox_mm(LAYOUT_DIR / "mast-stack.step")
    # Ground datum is 0.5 mm below Z=0. Carriage top is required height minus the top margin.
    carriage = next(term.length_mm for term in chain_terms() if term.name == "carriage")
    top_margin = next(term.length_mm for term in chain_terms() if term.name == "top_margin")
    stack_top = required_total_mm() - top_margin
    assert stack_top == 1721.2
    assert carriage == 80.0
    assert abs(size[0] - 420.0) < 0.05
    assert abs(size[1] - 466.6) < 0.05
    assert abs(size[2] - (stack_top + 0.5)) < 0.05
    header = (LAYOUT_DIR / "mast-stack.step").read_text(encoding="utf-8")
    assert "FILE_NAME('MAST-LAYOUT','2026-11-19T00:00:00'" in header
