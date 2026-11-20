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
from cad.models.carriage_bracket import (
    design_pull_n,
    gusset_bending_mpa,
    proof_load_n,
    upper_bolt_tension_n,
    working_pull_n,
)
from cad.models.mast_layout import (
    ADAPTER_LENGTH_MM,
    CARRIAGE_HEIGHT_MM,
    CASING_LENGTH_MM,
    GROUND_CLEARANCE_MM,
    GUIDED_TRAVEL_MM,
    MAST_PROFILE_LENGTH_MM,
    MOTOR_CENTRE_DISTANCE_MIN_MM,
    MOTOR_HEIGHT_MM,
    PLACEHOLDERS,
    PROFILE_SPACING_MM,
    SHOE_LENGTH_MM,
    TOP_MARGIN_MM,
    head_length_mm,
    required_total_mm,
)
from cad.tools.bom import ROOT, load_bom
from cad.tools.geometry import STEP_DIR, read_step_bbox_mm

PART_NUMBERS = (
    "VC-FR-4100",
    "VC-FR-4150",
    "VC-FR-4160",
    "VC-FR-4170",
    "VC-FR-4180",
    "VC-FR-4182",
    "VC-FR-4185",
    "VC-FR-4186",
    "VC-FR-4190",
    "VC-FR-4195",
    "VC-FR-4300",
    "VC-HB-2100",
    "VC-HB-2110",
    "VC-HB-2200",
    "VC-HB-2400",
    "VC-HB-2500",
    "VC-HB-2600",
    "VC-HB-2700",
    "VC-HB-2800",
    "VC-HB-2810",
    "VC-HB-2820",
    "VC-HB-2830",
    "VC-HB-2900",
    "VC-HB-3100",
    "VC-HB-3110",
    "VC-HB-3200",
    "VC-SH-1100",
    "VC-SH-1301",
    "VC-SH-1302",
    "VC-SH-1350",
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
    assert overlap_pairs(assembly_parts(bom, stroke_mm=0.0)) == []
    assert overlap_pairs(assembly_parts(bom, stroke_mm=round(GUIDED_TRAVEL_MM / 2.0, 1))) == []
    report = clearance_report(parts)
    assert report["shoe_to_profile_mm"] == 419.1
    assert report["casing_to_profile_mm"] == 175.8
    assert report["casing_to_bottom_plate_mm"] == 0.225
    assert report["guide_radial_clearance_mm"] == 0.225
    assert report["guide_bore_diameter_mm"] == 83.0
    assert report["rod_axis_x_mm"] == 227.5
    assert report["rod_overhang_from_rail_mm"] == 160.0
    assert report["motor_to_carriage_mm"] == 10.0
    assert report["motor_to_profile_mm"] == 50.0
    assert report["motor_to_rail_mm"] == 32.5
    assert report["plate_bottom_vs_lower_block_mm"] == 0.0
    assert report["carriage_to_chain_mm"] == 0.0
    assert report["shoe_tip_z_mm"] == -446.6
    assert report["profile_overhang_past_bottom_plate_mm"] == 25.0
    assert report["chain_min_x_mm"] == -45.9
    assert report["rear_face_x_mm"] == -50.0
    assert report["rear_stiffener_min_x_mm"] == -54.0
    assert report["lift_motor_min_x_mm"] == -33.0
    lift = next(item for item in parts if item.name == "VC-HB-2100")
    assert float(lift.shape.bounding_box().min.Z) > 15.0
    short = next(item for item in parts if item.name == "VC-FR-4100-1")
    long = next(item for item in parts if item.name == "VC-FR-4100-2")
    assert float(short.shape.bounding_box().size.Z) < MAST_PROFILE_LENGTH_MM - 1.0
    assert abs(float(long.shape.bounding_box().size.Z) - MAST_PROFILE_LENGTH_MM) < 0.05
    assert abs(float(short.shape.bounding_box().max.Z) - float(long.shape.bounding_box().max.Z)) < 0.05
    flange = next(item for item in parts if item.name == "VC-FR-4182")
    gearbox = next(item for item in parts if item.name == "VC-HB-2200")
    assert float(flange.shape.bounding_box().max.Y) < 0.0
    assert abs(float(flange.shape.bounding_box().max.Z) - float(gearbox.shape.bounding_box().min.Z)) < 0.05
    assert abs(float(gearbox.shape.bounding_box().size.Y) - 204.0) < 0.05
    assert abs(float(gearbox.shape.bounding_box().min.X) + 50.0) < 0.05
    assert abs(float(gearbox.shape.bounding_box().min.Y) - float(lift.shape.bounding_box().max.Y)) < 0.05
    hub = next(item for item in parts if item.name == "VC-HB-2400")
    shaft_root = float(gearbox.shape.bounding_box().max.Y) - 55.0
    assert shaft_root < float(hub.shape.bounding_box().min.Y) < float(gearbox.shape.bounding_box().max.Y)
    assert float(hub.shape.bounding_box().max.Y) < -210.0
    assert bom.part("VC-HB-2200").mass_kg == 7.65
    assert report["guided_travel_mm"] == 1009.6
    assert report["stroke_position_mm"] == 1009.6
    assert report["profile_size_x_mm"] == 100.0
    assert report["profile_size_y_mm"] == 50.0
    assert report["profile_size_z_mm"] == 1500.0
    assert report["required_mm"] == 1761.2
    names = [item.name for item in parts]
    assert names.count("VC-SH-1100-1") == 1
    assert names.count("VC-SH-1100-2") == 1
    assert names.count("VC-HB-3110-1") == 1
    assert sum(name.startswith("VC-HB-3110-") for name in names) == 4
    assert PLACEHOLDERS["motor_centre_distance_mm"][0] >= MOTOR_CENTRE_DISTANCE_MIN_MM
    assert OVERLAP_TOLERANCE_MM3 == 1.0


def test_bbox_matches_the_placed_solids():
    size = assembly_bbox_mm()
    assert abs(size[0] - 454.0) < 0.05
    assert abs(size[1] - 902.10) < 0.05
    # Shoe tip at Z=-446.6. Idler tooth tip at about Z=1592.1. The mast axis is Z.
    assert abs(size[2] - 2038.74) < 0.05
    assert size[2] > size[0]
    assert size[2] > size[1]
    bom = load_bom()
    assert ASSEMBLY_ID not in bom.parts
    step = read_step_bbox_mm(STEP_DIR / STEP_NAME)
    assert abs(step[0] - size[0]) < 0.05
    assert abs(step[1] - size[1]) < 0.05
    assert abs(step[2] - size[2]) < 0.05


def test_step_names_each_part_and_pngs_are_distinct():
    text = (STEP_DIR / STEP_NAME).read_text(encoding="utf-8")
    assert "FILE_NAME('VC-ASM-0000-layout','2026-11-19T00:00:00'" in text
    assert "DIRECTION('',(0.,0.,1.))" in text
    assert "DIRECTION('',(1.,0.,-0.))" not in text
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
    assert "0.225 mm" in doc
    assert "VC-FR-4180" in doc
    bar = next(item for item in assembly_parts(load_bom()) if item.name == "VC-FR-4180")
    box = bar.shape.bounding_box()
    assert abs(float(box.max.Y - box.min.Y) - (PROFILE_SPACING_MM - 50.0)) < 0.05
    assert abs(float(box.max.Z - box.min.Z) - MAST_PROFILE_LENGTH_MM) > 1.0


def test_pull_out_bracket_stays_below_yield():
    assert working_pull_n() == 4500.0
    assert design_pull_n() == 5000.0
    assert round(upper_bolt_tension_n(5000.0), 1) == 2226.6
    assert upper_bolt_tension_n(5000.0) < proof_load_n()
    assert round(gusset_bending_mpa(5000.0), 1) == 41.7
    assert gusset_bending_mpa(5000.0) * 3.0 < 355.0
    text = (ROOT / "docs/engineering/CARRIAGE-BRACKET.md").read_text(encoding="utf-8")
    assert "2227 N" in text
    assert "41.7 MPa" in text


def test_compound_intersection_uses_leaf_solids():
    from build123d import Box, Compound, Pos

    from cad.models.machine_assembly import intersection_volume_mm3

    left = Compound(children=[Box(10, 10, 10), Pos(0, 0, 40) * Box(10, 10, 10)])
    far = Pos(0, 0, 200) * Box(10, 10, 10)
    assert intersection_volume_mm3(left, far) == 0.0
    assert intersection_volume_mm3(left, Box(10, 10, 10)) > 1.0


def test_vendor_step_replaces_the_envelope(tmp_path, monkeypatch):
    from build123d import Box, export_step

    from cad.tools import geometry

    folder = tmp_path / "VC-FR-4100"
    folder.mkdir()
    export_step(Box(10, 20, 30), folder / "profile.step")
    monkeypatch.setattr(geometry, "VENDOR_DIR", tmp_path)
    solid = geometry.load_vendor_shape("VC-FR-4100")
    center = solid.bounding_box().center()
    assert abs(float(center.X)) < 0.05
    assert abs(float(center.Y)) < 0.05
    assert abs(float(center.Z)) < 0.05
    assert geometry.load_vendor_shape("VC-NO-SUCH") is None
    parts = assembly_parts(load_bom())
    profile = next(item for item in parts if item.name == "VC-FR-4100-1")
    size = profile.shape.bounding_box().size
    assert abs(float(size.Z) - 30.0) < 0.05
