"""BOM, drawing, STEP and OdooPLM export checks. No Odoo server required."""

import csv
from pathlib import Path

from cad.tools.bom import ROOT, load_bom
from cad.tools.cli import check
from cad.tools.geometry import expected_bbox_mm, read_step_bbox_mm, step_path
from cad.tools.odoo_export import external_id

DENSITY = 7850.0


def _rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_bom_rollups_match_published_lines():
    bom = load_bom()
    expected = {
        "VC-ASM-1000": (1185, 1900),
        # The ROTEX coupling is placed. The obsolete brake is not.
        "VC-ASM-2000": (1435, 2310),
        # Gussets are obsolete. The mk slot hardware is in this rollup.
        "VC-ASM-3000": (460, 754),
        # SDR-480-48 has no verified EUR price, so the old 80-140 band is not in the rollup.
        "VC-ASM-4000": (2655, 2780),
        # V1.1 control has qty 2 of 750-430 and 750-530.
        # The second SE050 line, the 9 V converter and the old enclosure price are out.
        "VC-ASM-5000": (1565, 2460),
        "VC-ASM-8000": (1259, 2300),
        "VC-KIT-7000": (2020, 2040),
    }
    for number, (low, high) in expected.items():
        assert bom.rollup(number, "low") == low
        assert bom.rollup(number, "high") == high
    # Two rods, four shoes and one O-ring pack from offer 26100096.
    assert bom.rollup("VC-KIT-6000", "low") == bom.rollup("VC-KIT-6000", "high")
    assert abs(bom.rollup("VC-KIT-6000", "low") - (2 * 389.99 + 4 * 300.78 + 24.75)) < 1e-6
    assert bom.rollup("VC-ASM-0000", "low") == 1185 + 1435 + 460 + 2655 + 1565 + 1259
    assert bom.rollup("VC-ASM-0000", "high") == 1900 + 2310 + 754 + 2780 + 2460 + 2300


def test_revision_letters_follow_odooplm_index():
    bom = load_bom()
    for part in bom.parts.values():
        assert part.revision_index == 0
        assert part.revision_letter == "A"
        assert part.engineering_code == part.part_number


def test_positioning_kit_does_not_repeat_the_gps():
    bom = load_bom()
    children = {line.part_number for line in bom.children("VC-KIT-7000")}
    assert children == {"VC-PS-8100", "VC-PS-8200"}
    control = {line.part_number for line in bom.children("VC-ASM-5000")}
    assert "VC-CT-6500" in control and "VC-CT-6510" in control
    assert any(issue["id"] == "positioning-gps-duplicate" for issue in bom.issues)


def test_plate_mass_uses_the_documented_density():
    bom = load_bom()
    plate = bom.part("VC-SH-1301")
    geometry = plate.geometry
    volume_m3 = (
        geometry["length_mm"] * geometry["width_mm"] * geometry["height_mm"]
    ) / 1e9
    assert abs(plate.mass_kg - DENSITY * volume_m3) < 1e-9
    column = bom.part("VC-SH-1400")
    shaft_volume = 3.141592653589793 * (0.025 ** 2) * 0.200
    assert DENSITY * shaft_volume < column.mass_kg


def test_odooplm_and_mrp_share_part_numbers():
    plm_products = _rows(ROOT / "cad/odoo/plm/product.product.csv")
    mrp_products = _rows(ROOT / "cad/odoo/mrp/product.product.csv")
    assert [row["default_code"] for row in plm_products] == [
        row["default_code"] for row in mrp_products
    ]
    assert "engineering_code" not in mrp_products[0]
    for row in plm_products:
        assert row["engineering_code"] == row["default_code"]
        assert row["engineering_revision"] == "0"
        assert row["engineering_revision_letter"] == "A"
        assert row["engineering_state"] == "draft"
        assert row["id"] == external_id("product", row["default_code"])
    sim = next(row for row in plm_products if row["default_code"] == "VC-CT-6610")
    assert sim["type"] == "service" and sim["is_storable"] == "0"
    machine = next(row for row in plm_products if row["default_code"] == "VC-ASM-0000")
    assert machine["sale_ok"] == "1" and machine["type"] == "consu"


def test_ebom_and_normal_bom_have_the_same_components():
    ebom = _rows(ROOT / "cad/odoo/plm/mrp.bom.csv")
    normal = _rows(ROOT / "cad/odoo/mrp/mrp.bom.csv")
    assert {row["code"] for row in ebom} == {row["code"] for row in normal}
    assert {row["type"] for row in ebom} == {"ebom"}
    assert {row["type"] for row in normal} <= {"normal", "phantom"}
    kits = {row["code"] for row in normal if row["type"] == "phantom"}
    assert kits == {"VC-KIT-6000", "VC-KIT-7000"}
    ebom_lines = _rows(ROOT / "cad/odoo/plm/mrp.bom.line.csv")
    mrp_lines = _rows(ROOT / "cad/odoo/mrp/mrp.bom.line.csv")
    assert [(row["bom_id/id"], row["product_id/default_code"], row["product_qty"]) for row in ebom_lines] == [
        (
            row["bom_id/id"].replace("bom_mrp", "bom_ebom"),
            row["product_id/default_code"],
            row["product_qty"],
        )
        for row in mrp_lines
    ]
    assert "itemnum" not in mrp_lines[0]
    numbers = [int(row["itemnum"]) for row in ebom_lines if row["bom_id/id"].endswith("vc_asm_1000")]
    assert numbers == list(range(1, len(numbers) + 1))


def test_documents_are_one_per_code_and_files_exist():
    docs = _rows(ROOT / "cad/odoo/plm/ir.attachment.csv")
    codes = [row["engineering_code"] for row in docs]
    assert len(codes) == len(set(codes))
    assert all(row["engineering_state"] == "draft" and row["is_plm"] == "1" for row in docs)
    relations = _rows(ROOT / "cad/odoo/plm/plm.component.document.rel.csv")
    assert {row["document_id/id"] for row in relations} == {row["id"] for row in docs}
    for payload in _rows(ROOT / "cad/odoo/plm/document_payloads.csv"):
        assert (ROOT / payload["odoo_datas_file"]).is_file()
        assert (ROOT / payload["odoo_printout_file"]).is_file()
        assert (ROOT / payload["svg_file"]).is_file()


def test_plate_drawing_and_step_use_documented_size():
    bom = load_bom()
    plate = bom.part("VC-SH-1301")
    svg = (ROOT / "cad/drawings/VC-SH-1301_vibrating-plate-blank.svg").read_text(encoding="utf-8")
    assert "ISO 7200" in svg
    assert "420" in svg and "300" in svg and "20" in svg
    assert "TODO" in svg
    assert "first angle" in svg
    pdf = (ROOT / "cad/export/pdf/VC-SH-1301_vibrating-plate-blank.pdf").read_bytes()
    assert pdf.startswith(b"%PDF-1.4")
    assert b"VC-SH-1301" in pdf
    size = read_step_bbox_mm(step_path(plate))
    assert size == expected_bbox_mm(plate) == (420.0, 300.0, 20.0)
    column = bom.part("VC-SH-1400")
    assert read_step_bbox_mm(step_path(column)) == (50.0, 50.0, 200.0)
    header = step_path(plate).read_text(encoding="utf-8")
    assert "FILE_NAME('VC-SH-1301','2026-11-19T00:00:00'" in header


def test_exports_are_regenerable():
    assert check() == 0
