"""Machine study assembly. Motors sit left and right. The profile length stays 1500 mm."""

from cad.models.machine_assembly import (
    ASSEMBLY_ID,
    OVERLAP_TOLERANCE_MM3,
    RENDER_DIR,
    STEP_NAME,
    assembly_bbox_mm,
    assembly_parts,
    chain_matches_pose,
    clearance_report,
    overlap_pairs,
    posed_stack_height_mm,
)
from cad.models.mast_layout import (
    ADAPTER_LENGTH_MM,
    CARRIAGE_HEIGHT_MM,
    CASING_LENGTH_MM,
    GROUND_CLEARANCE_MM,
    MOTOR_CENTRE_DISTANCE_MIN_MM,
    MOTOR_HEIGHT_MM,
    PLACEHOLDERS,
    SHOE_LENGTH_MM,
    TOP_MARGIN_MM,
    head_length_mm,
    required_total_mm,
)
from cad.tools.bom import ROOT, load_bom
from cad.tools.geometry import STEP_DIR, read_step_bbox_mm

PART_NUMBERS = (
    "VC-FR-4100",
    "VC-FR-4300",
    "VC-FR-4400",
    "VC-HB-3100",
    "VC-HB-3200",
    "VC-SH-1100",
    "VC-SH-1301",
    "VC-SH-1302",
    "VC-SH-1400",
    "VC-SH-1500",
    "VC-SH-1600",
    "VC-GP-7100",
    "VC-GP-7200",
    "VC-SP-7620",
    "VC-SP-7621",
)


def test_stack_height_is_the_sum_of_the_parameters():
    expected = round(
        SHOE_LENGTH_MM
        + CASING_LENGTH_MM
        + ADAPTER_LENGTH_MM
        + head_length_mm()
        + CARRIAGE_HEIGHT_MM,
        1,
    )
    assert posed_stack_height_mm() == expected == 1671.2
    assert chain_matches_pose()
    assert required_total_mm() - GROUND_CLEARANCE_MM - TOP_MARGIN_MM == expected
    assert MOTOR_HEIGHT_MM not in (
        SHOE_LENGTH_MM,
        CASING_LENGTH_MM,
        ADAPTER_LENGTH_MM,
        head_length_mm(),
        CARRIAGE_HEIGHT_MM,
    )
    assert head_length_mm() == 232.0


def test_assembly_has_no_overlaps_and_reports_clearances():
    bom = load_bom()
    parts = assembly_parts(bom)
    assert overlap_pairs(parts) == []
    report = clearance_report(parts)
    assert report["shoe_to_profile_mm"] == 56.2
    assert report["casing_to_profile_mm"] == 58.7
    assert report["motor_to_carriage_mm"] == 11.0
    assert report["motor_to_profile_mm"] == 82.3
    assert report["motor_to_rail_mm"] == 194.3
    assert report["vibrating_plate_to_top_plate_mm"] == 44.2
    assert report["carriage_above_rail_mm"] == 176.2
    assert report["profile_overhang_past_bottom_plate_mm"] == 50.0
    assert report["top_plate_cover_of_profile_mm"] == 0.0
    assert report["motor_to_profile_mm"] > 0
    assert report["motor_to_rail_mm"] > 0
    names = [item.name for item in parts]
    assert names.count("VC-SH-1100-1") == 1
    assert names.count("VC-SH-1100-2") == 1
    assert PLACEHOLDERS["motor_centre_distance_mm"][0] >= MOTOR_CENTRE_DISTANCE_MIN_MM
    assert OVERLAP_TOLERANCE_MM3 == 1.0


def test_bbox_matches_the_placed_solids():
    size = assembly_bbox_mm()
    assert abs(size[0] - 420.0) < 0.05
    assert abs(size[1] - 400.0) < 0.05
    # Shoe tip at Z=0, datum 0.5 mm below, motor tops at 1766.2 mm.
    assert abs(size[2] - 1766.7) < 0.05
    bom = load_bom()
    assert ASSEMBLY_ID not in bom.parts
    step = read_step_bbox_mm(STEP_DIR / STEP_NAME)
    assert abs(step[0] - size[0]) < 0.05
    assert abs(step[1] - size[1]) < 0.05
    assert abs(step[2] - size[2]) < 0.05


def test_step_names_each_part_and_pngs_are_distinct():
    text = (STEP_DIR / STEP_NAME).read_text(encoding="utf-8")
    assert "FILE_NAME('VC-ASM-0000-layout','2026-11-19T00:00:00'" in text
    for number in PART_NUMBERS:
        assert f"PRODUCT('{number}" in text
    pngs = [RENDER_DIR / f"{ASSEMBLY_ID}-{view}.png" for view in ("iso", "side", "top")]
    blobs = []
    for path in pngs:
        blob = path.read_bytes()
        assert blob.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(blob) > 1000
        blobs.append(blob)
    assert len(set(blobs)) == 3
    doc = (ROOT / "docs/engineering/MAST-LAYOUT.md").read_text(encoding="utf-8")
    for path in pngs:
        assert f"cad/export/renders/{path.name}" in doc
    assert "461.2 mm" in doc
    assert "No pair of part solids shares more than 1 mm" in doc
