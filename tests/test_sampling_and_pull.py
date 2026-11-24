"""Decisions from the 2026-11-19 BOM review."""

from cad.models.split_carrier import bbox_mm, validate_split_carrier
from cad.tools.bom import load_bom
from cad.tools.geometry import shape_for
from cad.tools.pull_force import (
    allowable_pull_n,
    chain_force_n,
    gearbox_emergency_force_n,
    gearbox_nominal_force_n,
    gearbox_output_from_motor_nm,
    load_cell_needs_bypass,
)


def test_sampling_string_is_the_outer_casing_only():
    bom = load_bom()
    children = {line.part_number for line in bom.children("VC-KIT-6000")}
    assert children == {
        "VC-GP-7100",
        "VC-GP-7150",
        "VC-GP-7200",
        "VC-SP-7620",
        "VC-SP-7621",
        "VC-SP-7630",
    }
    rings = bom.part("VC-GP-7150")
    assert rings.manufacturer_pn == "201325"
    assert rings.lifecycle == "active"
    drive_head = bom.part("VC-GP-7310")
    retainer = bom.part("VC-GP-7410")
    assert drive_head.manufacturer_pn == "201385"
    assert retainer.manufacturer_pn == "208472"
    for part in (bom.part("VC-GP-7300"), bom.part("VC-GP-7400"), drive_head, retainer):
        assert part.lifecycle == "obsolete"
        assert part.part_number not in children
        for assembly in bom.assemblies.values():
            assert part.part_number not in {line.part_number for line in assembly.lines}


def test_casing_rod_is_one_rod_and_the_gh60_cap_is_off_the_kit():
    bom = load_bom()
    rod = bom.part("VC-GP-7100")
    assert rod.mass_kg == 17.7
    assert rod.estimate_eur_low == 389.99
    assert rod.manufacturer_pn == "201446"
    shoe = bom.part("VC-GP-7200")
    assert shoe.estimate_eur_low == 300.78
    cap = bom.part("VC-GP-7300")
    liner = bom.part("VC-GP-7400")
    assert cap.lifecycle == "obsolete"
    assert liner.lifecycle == "obsolete"
    children = {line.part_number for line in bom.children("VC-KIT-6000")}
    assert "VC-GP-7300" not in children
    assert "VC-GP-7400" not in children
    assert children == {
        "VC-GP-7100",
        "VC-GP-7150",
        "VC-GP-7200",
        "VC-SP-7620",
        "VC-SP-7621",
        "VC-SP-7630",
    }


def test_lab_tubes_and_caps_are_not_bom_lines():
    bom = load_bom()
    for part in bom.parts.values():
        assert part.supplier_id != "radiclelab"
        name = part.name.lower()
        assert "push-on" not in name
        assert "steckdeckel" not in name
        assert not name.startswith("sample tube")


def test_split_carrier_is_a_placeholder_without_cap_clearance():
    bom = load_bom()
    half_a = bom.part("VC-SP-7620")
    half_b = bom.part("VC-SP-7621")
    assert half_a.geometry["side"] == "A"
    assert half_b.geometry["side"] == "B"
    assert "tube_od_mm" in half_a.geometry["placeholders"]
    assert "tube_length_mm" in half_a.geometry["placeholders"]
    validate_split_carrier(half_a.geometry)
    length = half_a.geometry["tube_count"] * half_a.geometry["tube_length_mm"]
    size = bbox_mm(half_a.geometry)
    assert size[2] == length
    solid = shape_for(half_a)
    got = solid.bounding_box().size
    assert abs(got.Z - length) < 1e-6
    # The pocket is the tube stack. There is no extra cap length on the solid.
    assert abs(got.Z - size[2]) < 1e-6


def test_bushing_opens_for_the_cutting_shoe():
    bom = load_bom()
    spec = bom.part("VC-FR-4500").spec
    assert "83 mm" in spec
    assert "87.63" in spec


def test_safety_and_power_lines_follow_the_review():
    bom = load_bom()
    assert bom.part("VC-PW-5200").manufacturer_pn == "SDR-480-48"
    assert bom.part("VC-PW-5200").lifecycle == "obsolete"
    assert bom.part("VC-PW-5200").estimate_eur_low is None
    assert bom.part("VC-PW-5400").lifecycle == "obsolete"
    power = {line.part_number for line in bom.children("VC-ASM-4000")}
    assert "VC-PW-5200" not in power
    assert "VC-PW-5400" not in power
    assert {"VC-PW-5310", "VC-PW-5320"} <= power
    assert bom.part("VC-CT-6300").estimate_eur_low is None
    assert "200 x 150 x 80 mm is withdrawn" in bom.part("VC-CT-6300").spec
    assert bom.part("VC-CT-6410").lifecycle == "obsolete"
    assert bom.part("VC-CT-6620").lifecycle == "obsolete"
    control = {line.part_number for line in bom.children("VC-ASM-5000")}
    assert "VC-CT-6410" not in control
    assert "VC-CT-6620" not in control
    assert "VC-CT-6230" in control
    assert "VC-CT-6240" in control
    power = {line.part_number for line in bom.children("VC-ASM-4000")}
    assert {"VC-PW-5700", "VC-PW-5710", "VC-PW-5720"} <= power


def test_allowable_pull_is_the_chain_working_load():
    assert allowable_pull_n() == 4500
    assert round(gearbox_nominal_force_n()) == 5005
    assert round(gearbox_emergency_force_n()) == 9369
    assert round(chain_force_n(gearbox_output_from_motor_nm(6.7))) == 5826
    assert load_cell_needs_bypass()
    bom = load_bom()
    assert "9.37 kN" in bom.part("VC-PN-9340").spec
    assert "VC-PN-9340" in {line.part_number for line in bom.children("VC-ASM-8300")}
