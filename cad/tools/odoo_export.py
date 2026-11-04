"""Write Odoo 19 import files for OdooPLM and for plain Manufacturing.

Field names were taken from OmniaGit/odooplm 19.0 commit b9db892
(plm 19.0.1.0.50) and from Odoo 19 product.template / mrp.bom:

- engineering_code, engineering_revision (Integer), engineering_revision_letter,
  engineering_state live on product.template via revision.plm.mixin.
- product.product reaches them through _inherits.
- plm_engineering adds mrp.bom.type 'ebom' and mrp.bom.ebom_source_id (Integer,
  a raw database id — left empty because it does not exist before import).
- mrp.bom.line.itemnum / itemlbl are the CAD position fields on the PLM line.
- ir.attachment is the engineering document. (engineering_code, engineering_revision)
  is unique, so a part has one document. The PDF is the printout file on disk;
  it is not a second attachment with the same code.
- plm.component.document.rel links product.product to ir.attachment.
- kit_bom exists on both product.template and product.product; this export sets
  the product.product field.
- plm_auto_internalref is intentionally not fed. Its default rewrites
  default_code to "{engineering_code}_{engineering_revision}". We keep
  default_code equal to engineering_code so the manufacturing fallback matches.
"""

from __future__ import annotations

import csv
from pathlib import Path

from cad.tools.bom import ROOT, BillOfMaterials, Part
from cad.tools.drawings import drawing_parts, drawing_stem

PLM_DIR = ROOT / "cad" / "odoo" / "plm"
MRP_DIR = ROOT / "cad" / "odoo" / "mrp"

UOM_UNIT = "uom.product_uom_unit"
ENGINEERING_STATE = "draft"


def external_id(kind: str, part_number: str) -> str:
    return f"vibrocore.{kind}_{part_number.lower().replace('-', '_')}"


def _category_id(name: str) -> str:
    slug = name.lower().replace(" ", "_").replace("&", "and")
    return f"vibrocore.categ_{slug}"


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if row.get(key) is None else row[key] for key in fieldnames})


def _money(value: float | None) -> str:
    if value is None:
        return "0.00"
    return f"{value:.2f}"


def _flag(value: bool) -> str:
    return "1" if value else "0"


def _description(part: Part) -> str:
    chunks = [part.spec, f"Legacy ref docs/engineering/BOM.md {part.legacy_ref}."]
    if part.estimate_eur_low is not None:
        chunks.append(
            "Preliminary unit estimate "
            f"EUR {part.estimate_eur_low:.2f}–{part.estimate_eur_high:.2f}. Not a supplier quote."
        )
    elif part.cost_included_in:
        chunks.append(f"No own price. Cost is included in {part.cost_included_in}.")
    elif part.has_bom:
        chunks.append("No own price. Use the rolled-up component estimates.")
    else:
        chunks.append("No estimate in the source BOM.")
    if part.manufacturer_pn:
        chunks.append(f"Manufacturer PN: {part.manufacturer_pn}.")
    if part.material:
        chunks.append(f"Material: {part.material}.")
    if part.unknowns:
        chunks.append("TODO: " + "; ".join(part.unknowns))
    if part.notes:
        chunks.append(part.notes)
    return " ".join(chunks)


def _sorted_parts(bom: BillOfMaterials) -> list[Part]:
    return sorted(bom.parts.values(), key=lambda part: part.part_number)


def category_rows(bom: BillOfMaterials) -> list[dict]:
    names = []
    for part in bom.parts.values():
        if part.category not in names:
            names.append(part.category)
    rows = [
        {
            "id": "vibrocore.categ_root",
            "name": "Vibrocore",
            "parent_id/id": "product.product_category_all",
        }
    ]
    for name in sorted(names):
        rows.append(
            {
                "id": _category_id(name),
                "name": name,
                "parent_id/id": "vibrocore.categ_root",
            }
        )
    return rows


def product_rows(bom: BillOfMaterials, plm: bool) -> list[dict]:
    rows = []
    for part in _sorted_parts(bom):
        row = {
            "id": external_id("product", part.part_number),
            "name": part.name,
            "default_code": part.part_number,
            "type": "service" if part.is_service else "consu",
            "is_storable": _flag(not part.is_service),
            "sale_ok": _flag(part.sale_ok),
            "purchase_ok": _flag(part.supply in {"purchase", "subcontract", "service"}),
            "uom_id/id": UOM_UNIT,
            "categ_id/id": _category_id(part.category),
            "standard_price": _money(part.estimate_eur_low),
            "description_purchase": _description(part),
            "weight": "" if part.mass_kg is None else f"{part.mass_kg:.3f}",
        }
        if plm:
            row.update(
                {
                    "engineering_code": part.engineering_code,
                    "engineering_revision": str(part.revision_index),
                    "engineering_revision_letter": part.revision_letter,
                    "engineering_state": ENGINEERING_STATE,
                    "engineering_material": part.material or "",
                    "kit_bom": _flag(part.supply == "kit"),
                    "tmp_material/id": (
                        f"vibrocore.material_{part.plm_material}" if part.plm_material else ""
                    ),
                }
            )
        rows.append(row)
    return rows


def bom_rows(bom: BillOfMaterials, plm: bool) -> list[dict]:
    rows = []
    for number in sorted(bom.assemblies):
        assembly = bom.assemblies[number]
        part = bom.part(number)
        rows.append(
            {
                "id": external_id("bom_ebom" if plm else "bom_mrp", number),
                "product_tmpl_id/default_code": part.part_number,
                "product_id/id": external_id("product", part.part_number),
                "product_qty": "1.0",
                "product_uom_id/id": UOM_UNIT,
                "type": "ebom" if plm else assembly.mrp_type,
                "code": part.part_number,
            }
        )
    return rows


def bom_line_rows(bom: BillOfMaterials, plm: bool) -> list[dict]:
    rows = []
    for number in sorted(bom.assemblies):
        for index, line in enumerate(bom.children(number), start=1):
            qty = f"{line.qty:.3f}".rstrip("0").rstrip(".")
            row = {
                "id": external_id("bomline_ebom" if plm else "bomline_mrp", f"{number}_{index:03d}"),
                "bom_id/id": external_id("bom_ebom" if plm else "bom_mrp", number),
                "product_id/default_code": line.part_number,
                "product_qty": qty if "." in f"{line.qty}" else f"{line.qty:.1f}",
                "product_uom_id/id": UOM_UNIT,
            }
            # Keep a stable one-decimal quantity for whole numbers (Odoo accepts both).
            if float(line.qty).is_integer():
                row["product_qty"] = f"{line.qty:.1f}"
            if plm:
                row["itemnum"] = str(index)
                row["itemlbl"] = str(index)
            rows.append(row)
    return rows


def material_rows(bom: BillOfMaterials) -> list[dict]:
    return [
        {
            "id": f"vibrocore.material_{item['id']}",
            "name": item["name"],
            "description": item.get("description") or "",
        }
        for item in sorted(bom.materials, key=lambda item: item["id"])
    ]


def partner_rows(bom: BillOfMaterials) -> list[dict]:
    rows = []
    for supplier in sorted(bom.suppliers, key=lambda item: item["id"]):
        row = {
            "id": f"vibrocore.partner_{supplier['id']}",
            "name": supplier["name"],
            "is_company": "1",
            "supplier_rank": "1",
            "website": supplier.get("website") or "",
            "comment": supplier.get("comment") or "",
        }
        if supplier.get("country_xml"):
            row["country_id/id"] = supplier["country_xml"]
        else:
            row["country_id/id"] = ""
        rows.append(row)
    return rows


def supplierinfo_rows(bom: BillOfMaterials) -> list[dict]:
    rows = []
    for part in _sorted_parts(bom):
        if not part.supplier_id or part.estimate_eur_low is None:
            continue
        rows.append(
            {
                "id": external_id("seller", part.part_number),
                "product_id/id": external_id("product", part.part_number),
                "partner_id/id": f"vibrocore.partner_{part.supplier_id}",
                "min_qty": "1.0",
                "price": _money(part.estimate_eur_low),
                "currency_id/id": "base.EUR",
                "product_code": part.manufacturer_pn or "",
            }
        )
    return rows


def document_rows(bom: BillOfMaterials) -> tuple[list[dict], list[dict], list[dict]]:
    attachments = []
    relations = []
    payloads = []
    for part in drawing_parts(bom):
        stem = drawing_stem(part)
        has_step = part.geometry is not None
        name = f"{part.part_number}.step" if has_step else f"{stem}.pdf"
        mimetype = "model/step" if has_step else "application/pdf"
        description = (
            f"Git export for {part.part_number} rev {part.revision_letter}. "
            f"Fidelity: {(part.geometry or {}).get('fidelity', 'schematic')}. "
            "PDF printout and SVG sheet are in the repository; upload the PDF into "
            "ir.attachment.printout after import. document_type stays 'other' until "
            ".step/.stp are added to ir.config_parameter file_exte_type_rel_3D "
            "and .pdf to file_exte_type_rel_2D (plm/views/ir_config_parameter.xml, noupdate)."
        )
        attachments.append(
            {
                "id": external_id("doc", part.part_number),
                "name": name,
                "engineering_code": part.engineering_code,
                "engineering_revision": str(part.revision_index),
                "engineering_revision_letter": part.revision_letter,
                "engineering_state": ENGINEERING_STATE,
                "is_plm": "1",
                "type": "binary",
                "mimetype": mimetype,
                "description": description,
            }
        )
        relations.append(
            {
                "id": external_id("rel", part.part_number),
                "component_id/id": external_id("product", part.part_number),
                "document_id/id": external_id("doc", part.part_number),
            }
        )
        payloads.append(
            {
                "engineering_code": part.part_number,
                "engineering_revision": str(part.revision_index),
                "attachment_external_id": external_id("doc", part.part_number),
                "odoo_datas_file": (
                    f"cad/export/step/{part.part_number}.step"
                    if has_step
                    else f"cad/export/pdf/{stem}.pdf"
                ),
                "odoo_printout_file": f"cad/export/pdf/{stem}.pdf",
                "svg_file": f"cad/drawings/{stem}.svg",
                "fidelity": (part.geometry or {}).get("fidelity", "schematic"),
            }
        )
    return attachments, relations, payloads


PRODUCT_FIELDS = [
    "id",
    "name",
    "default_code",
    "type",
    "is_storable",
    "sale_ok",
    "purchase_ok",
    "uom_id/id",
    "categ_id/id",
    "standard_price",
    "weight",
    "description_purchase",
]
PLM_PRODUCT_FIELDS = PRODUCT_FIELDS + [
    "engineering_code",
    "engineering_revision",
    "engineering_revision_letter",
    "engineering_state",
    "engineering_material",
    "kit_bom",
    "tmp_material/id",
]
BOM_FIELDS = [
    "id",
    "product_tmpl_id/default_code",
    "product_id/id",
    "product_qty",
    "product_uom_id/id",
    "type",
    "code",
]
LINE_FIELDS = ["id", "bom_id/id", "product_id/default_code", "product_qty", "product_uom_id/id"]
PLM_LINE_FIELDS = LINE_FIELDS + ["itemnum", "itemlbl"]


def export_odoo(bom: BillOfMaterials, plm_dir: Path | None = None, mrp_dir: Path | None = None) -> list[Path]:
    plm_dir = plm_dir or PLM_DIR
    mrp_dir = mrp_dir or MRP_DIR
    written: list[Path] = []

    def dump(directory: Path, name: str, fields: list[str], rows: list[dict]) -> None:
        path = directory / name
        _write_csv(path, fields, rows)
        written.append(path)

    categories = category_rows(bom)
    dump(plm_dir, "product.category.csv", ["id", "name", "parent_id/id"], categories)
    dump(mrp_dir, "product.category.csv", ["id", "name", "parent_id/id"], categories)
    dump(
        plm_dir,
        "plm.material.csv",
        ["id", "name", "description"],
        material_rows(bom),
    )
    dump(
        plm_dir,
        "res.partner.csv",
        ["id", "name", "is_company", "supplier_rank", "website", "country_id/id", "comment"],
        partner_rows(bom),
    )
    dump(plm_dir, "product.product.csv", PLM_PRODUCT_FIELDS, product_rows(bom, plm=True))
    dump(mrp_dir, "product.product.csv", PRODUCT_FIELDS, product_rows(bom, plm=False))
    dump(plm_dir, "product.supplierinfo.csv", [
        "id", "product_id/id", "partner_id/id", "min_qty", "price", "currency_id/id", "product_code",
    ], supplierinfo_rows(bom))
    dump(plm_dir, "mrp.bom.csv", BOM_FIELDS, bom_rows(bom, plm=True))
    dump(mrp_dir, "mrp.bom.csv", BOM_FIELDS, bom_rows(bom, plm=False))
    dump(plm_dir, "mrp.bom.line.csv", PLM_LINE_FIELDS, bom_line_rows(bom, plm=True))
    dump(mrp_dir, "mrp.bom.line.csv", LINE_FIELDS, bom_line_rows(bom, plm=False))
    attachments, relations, payloads = document_rows(bom)
    dump(plm_dir, "ir.attachment.csv", [
        "id", "name", "engineering_code", "engineering_revision", "engineering_revision_letter",
        "engineering_state", "is_plm", "type", "mimetype", "description",
    ], attachments)
    dump(plm_dir, "plm.component.document.rel.csv", [
        "id", "component_id/id", "document_id/id",
    ], relations)
    dump(plm_dir, "document_payloads.csv", [
        "engineering_code", "engineering_revision", "attachment_external_id",
        "odoo_datas_file", "odoo_printout_file", "svg_file", "fidelity",
    ], payloads)
    return written
