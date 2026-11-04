"""Create and update Vibrocore records in OdooPLM. Draft only.

The YAML file stays the source. A second run updates the same engineering
code and revision instead of inserting another one. engineering_state is
written only as "draft" on create. action_confirm, action_release and
new_version are not called, and a record that is no longer draft is left
alone, including its file bytes and its engineering BOM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from cad.tools.bom import ROOT, BillOfMaterials, BomError, Part, load_bom
from cad.tools.odoo_export import _description, document_rows
from cad.tools.plm_client import PlmClient, PlmError

DRAFT = "draft"
M2O_FIELDS = {
    "product_tmpl_id",
    "categ_id",
    "uom_id",
    "tmp_material",
    "partner_id",
    "product_id",
    "currency_id",
    "country_id",
    "bom_id",
    "parent_id",
}


@dataclass
class Action:
    op: str
    model: str
    key: str
    detail: str = ""

    def line(self) -> str:
        extra = f" {self.detail}" if self.detail else ""
        return f"{self.op:12} {self.model} {self.key}{extra}"


@dataclass
class SyncReport:
    actions: list[Action] = field(default_factory=list)
    dry_run: bool = True
    offline: bool = True

    def add(self, op: str, model: str, key: str, detail: str = "") -> None:
        self.actions.append(Action(op, model, key, detail))

    def text(self) -> str:
        counts: dict[str, int] = {}
        for action in self.actions:
            counts[action.op] = counts.get(action.op, 0) + 1
        mode = "dry-run" if self.dry_run else "apply"
        where = "local plan, no request sent" if self.offline else "OdooPLM"
        summary = ", ".join(f"{name}={count}" for name, count in sorted(counts.items()))
        header = f"plm-sync {mode} ({where}): {summary or 'nothing to do'}"
        body = "\n".join(action.line() for action in self.actions)
        return header + ("\n" + body if body else "") + "\n"


def m2o_id(value):
    if isinstance(value, (list, tuple)):
        return value[0] if value else False
    return value or False


def _same(current: dict, desired: dict) -> bool:
    for key, wanted in desired.items():
        have = current.get(key)
        have = m2o_id(have) if key in M2O_FIELDS or isinstance(have, (list, tuple)) else have
        if isinstance(wanted, float) or isinstance(have, float):
            if abs(float(have or 0) - float(wanted or 0)) > 1e-6:
                return False
            continue
        if isinstance(wanted, bool) or isinstance(have, bool):
            if bool(have) != bool(wanted):
                return False
            continue
        if (have or False) != (wanted or False):
            return False
    return True


class PlmSync:
    def __init__(
        self,
        bom: BillOfMaterials,
        client: PlmClient | None,
        dry_run: bool,
        part_number: str | None = None,
        step_path: Path | None = None,
        pdf_path: Path | None = None,
    ):
        self.bom = bom
        self.client = client
        self.dry_run = dry_run
        self.offline = client is None
        self.part_number = part_number
        self.step_path = step_path
        self.pdf_path = pdf_path
        self.report = SyncReport(dry_run=dry_run, offline=self.offline)
        self._has_auto_default_code: bool | None = None
        self._root_category_id: int | None = None
        self._xml_ids: dict[str, int] = {}
        self._categories: dict[str, int] = {}
        self._materials: dict[str, int] = {}
        self._partners: dict[str, int] = {}
        self._products: dict[str, dict] = {}

    def run(self) -> SyncReport:
        self._check_files()
        if self.offline:
            self._plan_offline()
            return self.report
        assert self.client is not None
        self._uom_id = self._xml("uom.product_uom_unit")
        if not self._uom_id:
            raise PlmError(
                "uom.product_uom_unit was not found. The database has no Units of Measure record to attach."
            )
        self._currency_id = self._xml("base.EUR")
        self._all_category_id = self._xml("product.product_category_all")
        for part in self._product_parts():
            self._sync_product(part)
        for part in self._product_parts():
            self._sync_supplier(part)
        for part, payload in self._document_payloads():
            self._sync_document(part, payload)
        for number in self._assembly_numbers():
            self._sync_bom(number)
        return self.report

    def _product_parts(self) -> list[Part]:
        if not self.part_number:
            return sorted(self.bom.parts.values(), key=lambda item: item.part_number)
        selected = {self.part_number}
        if self.part_number in self.bom.assemblies:
            selected.update(line.part_number for line in self.bom.children(self.part_number))
        return [self.bom.part(number) for number in sorted(selected)]

    def _assembly_numbers(self) -> list[str]:
        if not self.part_number:
            return sorted(self.bom.assemblies)
        if self.part_number in self.bom.assemblies:
            return [self.part_number]
        return []

    def _document_payloads(self) -> list[tuple[Part, dict]]:
        by_code = {row["engineering_code"]: row for row in document_rows(self.bom)[2]}
        if self.part_number:
            codes = [self.part_number] if self.part_number in by_code or self.step_path or self.pdf_path else []
        else:
            codes = sorted(by_code)
        pairs = []
        for code in codes:
            part = self.bom.part(code)
            payload = dict(by_code.get(code) or {})
            if self.part_number == code:
                if self.step_path:
                    payload["odoo_datas_file"] = str(self.step_path)
                    payload["datas_filename"] = f"{code}.step"
                if self.pdf_path:
                    payload["odoo_printout_file"] = str(self.pdf_path)
            if not payload.get("odoo_datas_file") and not payload.get("odoo_printout_file"):
                continue
            pairs.append((part, payload))
        return pairs

    def _check_files(self) -> None:
        missing = []
        for _part, payload in self._document_payloads():
            for key in ("odoo_datas_file", "odoo_printout_file"):
                if payload.get(key) and not _resolve(payload[key]).is_file():
                    missing.append(payload[key])
        if missing:
            raise PlmError(
                "Generated files are missing. Run `python -m cad.tools.cli export` first:\n"
                + "\n".join(missing)
            )

    def _plan_offline(self) -> None:
        for part in self._product_parts():
            self.report.add("plan", "product.product", part.part_number, f"rev {part.revision_index} draft")
            if part.supplier_id and part.estimate_eur_low is not None:
                supplier = next(item for item in self.bom.suppliers if item["id"] == part.supplier_id)
                self.report.add("plan", "product.supplierinfo", part.part_number, supplier["name"])
        for part, payload in self._document_payloads():
            datas = Path(payload["odoo_datas_file"]).name
            self.report.add(
                "plan",
                "ir.attachment",
                part.part_number,
                f"datas={datas} printout={Path(payload['odoo_printout_file']).name}",
            )
            self.report.add("plan", "plm.component.document.rel", part.part_number, "")
        for number in self._assembly_numbers():
            count = len(self.bom.children(number))
            self.report.add("plan", "mrp.bom", number, f"type=ebom lines={count}")

    def _execute(self, model: str, method: str, args: list, kwargs: dict | None = None):
        assert self.client is not None
        return self.client.execute(model, method, args, kwargs)

    def _fields(self, model: str) -> set[str]:
        result = self._execute(model, "fields_get", [], {"attributes": ["string"]})
        return set(result or {})

    def _xml(self, xml_id: str) -> int | None:
        if xml_id in self._xml_ids:
            return self._xml_ids[xml_id]
        module, name = xml_id.split(".", 1)
        found = self._execute(
            "ir.model.data",
            "search_read",
            [[("module", "=", module), ("name", "=", name)]],
            {"fields": ["res_id"], "limit": 1},
        )
        if not found:
            return None
        self._xml_ids[xml_id] = int(found[0]["res_id"])
        return self._xml_ids[xml_id]

    def _auto_default_code(self) -> bool:
        if self._has_auto_default_code is None:
            names = self._fields("product.product")
            self._has_auto_default_code = "auto_default_code" in names
        return self._has_auto_default_code

    def _category(self, name: str) -> int:
        if name in self._categories:
            return self._categories[name]
        if self._root_category_id is None:
            self._root_category_id = self._ensure_category("Vibrocore", self._all_category_id)
        self._categories[name] = self._ensure_category(name, self._root_category_id)
        return self._categories[name]

    def _ensure_category(self, name: str, parent_id: int | None) -> int:
        domain = [("name", "=", name)]
        if parent_id:
            domain.append(("parent_id", "=", parent_id))
        found = self._execute(
            "product.category",
            "search_read",
            [domain],
            {"fields": ["id"], "limit": 1},
        )
        if found:
            return int(found[0]["id"])
        if self.dry_run:
            self.report.add("create", "product.category", name, "")
            return 0
        vals = {"name": name}
        if parent_id:
            vals["parent_id"] = parent_id
        created = self._execute("product.category", "create", [vals])
        self.report.add("create", "product.category", name, f"id={_one_id(created)}")
        return _one_id(created)

    def _material(self, material_id: str) -> int | None:
        if not material_id:
            return None
        if material_id in self._materials:
            return self._materials[material_id]
        spec = next(item for item in self.bom.materials if item["id"] == material_id)
        found = self._execute(
            "plm.material",
            "search_read",
            [[("name", "=", spec["name"])]],
            {"fields": ["id"], "limit": 1},
        )
        if found:
            self._materials[material_id] = int(found[0]["id"])
            self.report.add("unchanged", "plm.material", spec["name"], "")
            return self._materials[material_id]
        if self.dry_run:
            self.report.add("create", "plm.material", spec["name"], "")
            self._materials[material_id] = 0
            return 0
        created = self._execute(
            "plm.material",
            "create",
            [{"name": spec["name"], "description": spec.get("description") or ""}],
        )
        self._materials[material_id] = _one_id(created)
        self.report.add("create", "plm.material", spec["name"], f"id={self._materials[material_id]}")
        return self._materials[material_id]

    def _partner(self, supplier_id: str) -> int:
        if supplier_id in self._partners:
            return self._partners[supplier_id]
        spec = next(item for item in self.bom.suppliers if item["id"] == supplier_id)
        found = self._execute(
            "res.partner",
            "search_read",
            [[("name", "=", spec["name"]), ("is_company", "=", True)]],
            {"fields": ["id"], "limit": 1},
        )
        if found:
            self._partners[supplier_id] = int(found[0]["id"])
            self.report.add("unchanged", "res.partner", spec["name"], "")
            return self._partners[supplier_id]
        vals = {
            "name": spec["name"],
            "is_company": True,
            "supplier_rank": 1,
            "website": spec.get("website") or False,
            "comment": spec.get("comment") or False,
        }
        country = spec.get("country_xml")
        if country:
            country_id = self._xml(country)
            if country_id:
                vals["country_id"] = country_id
        if self.dry_run:
            self.report.add("create", "res.partner", spec["name"], "")
            self._partners[supplier_id] = 0
            return 0
        created = self._execute("res.partner", "create", [vals])
        self._partners[supplier_id] = _one_id(created)
        self.report.add("create", "res.partner", spec["name"], f"id={self._partners[supplier_id]}")
        return self._partners[supplier_id]

    def _product_vals(self, part: Part) -> dict:
        vals = {
            "name": part.name,
            "default_code": part.part_number,
            "type": "service" if part.is_service else "consu",
            "is_storable": not part.is_service,
            "sale_ok": part.sale_ok,
            "purchase_ok": part.supply in {"purchase", "subcontract", "service"},
            "uom_id": self._uom_id,
            "categ_id": self._category(part.category),
            "standard_price": float(part.estimate_eur_low or 0.0),
            "description_purchase": _description(part),
            "weight": float(part.mass_kg or 0.0),
            "engineering_code": part.engineering_code,
            "engineering_revision": part.revision_index,
            "engineering_revision_letter": part.revision_letter,
            "engineering_material": part.material or False,
            "kit_bom": part.supply == "kit",
        }
        material = self._material(part.plm_material) if part.plm_material else None
        if material:
            vals["tmp_material"] = material
        if self._auto_default_code():
            # plm_auto_internalref would otherwise rewrite default_code to
            # "{engineering_code}_{engineering_revision}" on create and write.
            vals["auto_default_code"] = False
        return vals

    def _find_part_record(self, model: str, part: Part, fields: list[str]) -> dict | None:
        found = self._execute(
            model,
            "search_read",
            [[
                ("engineering_code", "=", part.engineering_code),
                ("engineering_revision", "=", part.revision_index),
            ]],
            {"fields": fields, "limit": 2},
        )
        if len(found) > 1:
            raise PlmError(
                f"{model} {part.part_number} rev {part.revision_index} exists more than once."
            )
        return found[0] if found else None

    def _sync_product(self, part: Part) -> None:
        fields = [
            "id",
            "name",
            "default_code",
            "type",
            "is_storable",
            "sale_ok",
            "purchase_ok",
            "categ_id",
            "standard_price",
            "description_purchase",
            "weight",
            "engineering_state",
            "engineering_material",
            "engineering_revision_letter",
            "kit_bom",
            "product_tmpl_id",
            "tmp_material",
            "uom_id",
        ]
        current = self._find_part_record("product.product", part, fields)
        vals = self._product_vals(part)
        key = f"{part.part_number} rev {part.revision_index}"
        if current is None:
            if self.dry_run:
                self.report.add("create", "product.product", key, "engineering_state=draft")
                self._products[part.part_number] = {
                    "id": 0,
                    "product_tmpl_id": 0,
                    "engineering_state": DRAFT,
                }
                return
            vals["engineering_state"] = DRAFT
            created = _one_id(self._execute("product.product", "create", [vals]))
            read_back = self._execute(
                "product.product",
                "read",
                [[created]],
                {"fields": ["id", "product_tmpl_id", "engineering_state"]},
            )[0]
            state = read_back.get("engineering_state") or DRAFT
            if state != DRAFT:
                raise PlmError(f"{part.part_number} was created in state {state}, not draft.")
            self._products[part.part_number] = {
                "id": created,
                "product_tmpl_id": m2o_id(read_back["product_tmpl_id"]),
                "engineering_state": state,
            }
            self.report.add("create", "product.product", key, f"id={created} engineering_state=draft")
            return
        state = current.get("engineering_state") or DRAFT
        stored = {
            "id": int(current["id"]),
            "product_tmpl_id": m2o_id(current["product_tmpl_id"]),
            "engineering_state": state,
        }
        self._products[part.part_number] = stored
        if state != DRAFT:
            self.report.add("skip-locked", "product.product", key, f"engineering_state={state}")
            return
        comparable = {
            key: value
            for key, value in vals.items()
            if key not in {"engineering_code", "engineering_revision", "uom_id"}
        }
        if _same(current, comparable):
            self.report.add("unchanged", "product.product", key, f"id={stored['id']}")
            return
        if self.dry_run:
            self.report.add("update", "product.product", key, f"id={stored['id']}")
            return
        write_vals = dict(comparable)
        self._execute("product.product", "write", [[stored["id"]], write_vals])
        self.report.add("update", "product.product", key, f"id={stored['id']}")

    def _sync_supplier(self, part: Part) -> None:
        if not part.supplier_id or part.estimate_eur_low is None:
            return
        product = self._products[part.part_number]
        partner_id = self._partner(part.supplier_id)
        if product["engineering_state"] != DRAFT:
            self.report.add("skip-locked", "product.supplierinfo", part.part_number, "product is not draft")
            return
        domain = [("product_id", "=", product["id"]), ("partner_id", "=", partner_id)]
        if product["id"] and partner_id:
            found = self._execute(
                "product.supplierinfo",
                "search_read",
                [domain],
                {"fields": ["id", "price", "min_qty", "product_code"], "limit": 2},
            )
        else:
            found = []
        vals = {
            "partner_id": partner_id,
            "product_id": product["id"],
            "product_tmpl_id": product["product_tmpl_id"],
            "min_qty": 1.0,
            "price": float(part.estimate_eur_low),
            "product_code": part.manufacturer_pn or False,
        }
        if self._currency_id:
            vals["currency_id"] = self._currency_id
        if not found:
            if self.dry_run or not product["id"] or not partner_id:
                self.report.add("create", "product.supplierinfo", part.part_number, "")
                return
            created = self._execute("product.supplierinfo", "create", [vals])
            self.report.add("create", "product.supplierinfo", part.part_number, f"id={_one_id(created)}")
            return
        current = found[0]
        if _same(current, {"price": vals["price"], "min_qty": 1.0, "product_code": vals["product_code"]}):
            self.report.add("unchanged", "product.supplierinfo", part.part_number, f"id={current['id']}")
            return
        if self.dry_run:
            self.report.add("update", "product.supplierinfo", part.part_number, f"id={current['id']}")
            return
        self._execute(
            "product.supplierinfo",
            "write",
            [[current["id"]], {"price": vals["price"], "min_qty": 1.0, "product_code": vals["product_code"]}],
        )
        self.report.add("update", "product.supplierinfo", part.part_number, f"id={current['id']}")

    def _sync_document(self, part: Part, payload: dict) -> None:
        if not payload.get("odoo_datas_file"):
            raise PlmError(f"{part.part_number} has a printout and no datas file.")
        datas_path = _resolve(payload["odoo_datas_file"])
        printout_path = _resolve(payload["odoo_printout_file"]) if payload.get("odoo_printout_file") else None
        filename = payload.get("datas_filename") or datas_path.name
        key = f"{part.part_number} rev {part.revision_index}"
        current = self._find_part_record(
            "ir.attachment",
            part,
            ["id", "name", "engineering_state", "is_plm", "description"],
        )
        if current is not None and not current.get("is_plm", True):
            raise PlmError(
                f"ir.attachment {part.part_number} rev {part.revision_index} exists but is_plm is false. "
                "The upload routes refuse it."
            )
        printout_name = printout_path.name if printout_path else ""
        description = (
            f"Git export for {part.part_number} rev {part.revision_letter}. "
            f"Uploaded by plm-sync. datas={filename}."
            + (f" printout={printout_name}." if printout_name else "")
        )
        if current is None:
            if self.dry_run:
                self.report.add("create", "ir.attachment", key, f"datas={filename}")
                document_id = 0
                state = DRAFT
            else:
                created = _one_id(
                    self._execute(
                        "ir.attachment",
                        "create",
                        [
                            {
                                "name": filename,
                                "engineering_code": part.engineering_code,
                                "engineering_revision": part.revision_index,
                                "engineering_revision_letter": part.revision_letter,
                                "engineering_state": DRAFT,
                                "is_plm": True,
                                "type": "binary",
                                "description": description,
                            }
                        ],
                    )
                )
                document_id = created
                state = DRAFT
                self.report.add("create", "ir.attachment", key, f"id={created}")
        else:
            document_id = int(current["id"])
            state = current.get("engineering_state") or DRAFT
            if state != DRAFT:
                self.report.add("skip-locked", "ir.attachment", key, f"engineering_state={state}")
            elif current.get("name") != filename or current.get("description") != description:
                if self.dry_run:
                    self.report.add("update", "ir.attachment", key, f"id={document_id}")
                else:
                    self._execute(
                        "ir.attachment",
                        "write",
                        [[document_id], {"name": filename, "description": description, "is_plm": True}],
                    )
                    self.report.add("update", "ir.attachment", key, f"id={document_id}")
            else:
                self.report.add("unchanged", "ir.attachment", key, f"id={document_id}")
        product = self._products[part.part_number]
        self._sync_link(part, product["id"], document_id, product["engineering_state"], state)
        if state != DRAFT:
            return
        if self.dry_run or not document_id:
            self.report.add("upload", "/plm_document_upload/upload", key, filename)
            if printout_path:
                self.report.add("upload", "/plm_document_upload/upload_pdf", key, printout_name)
            return
        assert self.client is not None
        self.client.upload_datas(document_id, filename, datas_path.read_bytes())
        self.report.add("upload", "/plm_document_upload/upload", key, f"doc_id={document_id} {filename}")
        if printout_path:
            self.client.upload_printout(document_id, printout_name, printout_path.read_bytes())
            self.report.add(
                "upload",
                "/plm_document_upload/upload_pdf",
                key,
                f"doc_id={document_id} {printout_name}",
            )

    def _sync_link(self, part: Part, product_id: int, document_id: int, product_state: str, document_state: str) -> None:
        key = part.part_number
        if product_state != DRAFT or document_state != DRAFT:
            self.report.add("skip-locked", "plm.component.document.rel", key, "component or document is not draft")
            return
        if not product_id or not document_id:
            self.report.add("create", "plm.component.document.rel", key, "")
            return
        found = self._execute(
            "plm.component.document.rel",
            "search_read",
            [[("component_id", "=", product_id), ("document_id", "=", document_id)]],
            {"fields": ["id"], "limit": 1},
        )
        if found:
            self.report.add("unchanged", "plm.component.document.rel", key, f"id={found[0]['id']}")
            return
        if self.dry_run:
            self.report.add("create", "plm.component.document.rel", key, "")
            return
        # OdooPLM 19 overrides create() on this relation model in a way that
        # JSON-RPC cannot call. product.product.linkeddocuments is the supported
        # path and createFromIds() uses the same Many2many write.
        self._execute(
            "product.product",
            "write",
            [[product_id], {"linkeddocuments": [(4, document_id, False)]}],
        )
        self.report.add("create", "plm.component.document.rel", key, f"doc_id={document_id}")

    def _sync_bom(self, number: str) -> None:
        part = self.bom.part(number)
        product = self._products[number]
        key = number
        if product["engineering_state"] != DRAFT:
            self.report.add("skip-locked", "mrp.bom", key, "product is not draft")
            return
        if not product["id"]:
            self.report.add("create", "mrp.bom", key, f"type=ebom lines={len(self.bom.children(number))}")
            return
        found = self._execute(
            "mrp.bom",
            "search_read",
            [[("product_id", "=", product["id"]), ("type", "=", "ebom")]],
            {"fields": ["id", "code", "product_qty"], "limit": 5},
        )
        if len(found) > 1:
            named = [row for row in found if row.get("code") == number]
            chosen = named[0] if named else found[0]
            note = f"{len(found)} ebom rows already exist"
        elif found:
            chosen = found[0]
            note = ""
        else:
            chosen = None
            note = ""
        if chosen is None:
            if self.dry_run:
                self.report.add("create", "mrp.bom", key, "type=ebom")
                bom_id = 0
            else:
                vals = {
                    "product_id": product["id"],
                    "product_tmpl_id": product["product_tmpl_id"],
                    "product_qty": 1.0,
                    "product_uom_id": self._uom_id,
                    "type": "ebom",
                    "code": number,
                }
                bom_id = _one_id(self._execute("mrp.bom", "create", [vals]))
                self.report.add("create", "mrp.bom", key, f"id={bom_id} type=ebom")
        else:
            bom_id = int(chosen["id"])
            header = {}
            if abs(float(chosen.get("product_qty") or 0) - 1.0) > 1e-6:
                header["product_qty"] = 1.0
            if chosen.get("code") != number:
                header["code"] = number
            detail = f"id={bom_id} type=ebom" + (f" {note}" if note else "")
            if not header:
                self.report.add("unchanged", "mrp.bom", key, detail)
            elif self.dry_run:
                self.report.add("update", "mrp.bom", key, detail)
            else:
                self._execute("mrp.bom", "write", [[bom_id], header])
                self.report.add("update", "mrp.bom", key, detail)
        self._sync_bom_lines(number, bom_id)

    def _sync_bom_lines(self, number: str, bom_id: int) -> None:
        wanted = []
        for index, line in enumerate(self.bom.children(number), start=1):
            child = self._products[line.part_number]
            wanted.append(
                {
                    "product_id": child["id"],
                    "part_number": line.part_number,
                    "product_qty": float(line.qty),
                    "itemnum": index,
                    "itemlbl": str(index),
                }
            )
        if not bom_id:
            for line in wanted:
                self.report.add(
                    "create",
                    "mrp.bom.line",
                    f"{number}:{line['itemnum']}",
                    line["part_number"],
                )
            return
        existing = self._execute(
            "mrp.bom.line",
            "search_read",
            [[("bom_id", "=", bom_id)]],
            {"fields": ["id", "product_id", "product_qty", "itemnum", "itemlbl"]},
        )
        used = set()
        by_product: dict[int, dict] = {}
        for row in existing:
            product_id = m2o_id(row["product_id"])
            by_product.setdefault(product_id, row)
        for line in wanted:
            current = by_product.get(line["product_id"])
            label = f"{number}:{line['itemnum']} {line['part_number']}"
            if current is None:
                if self.dry_run or not line["product_id"]:
                    self.report.add("create", "mrp.bom.line", label, "")
                    continue
                created = self._execute(
                    "mrp.bom.line",
                    "create",
                    [
                        {
                            "bom_id": bom_id,
                            "product_id": line["product_id"],
                            "product_qty": line["product_qty"],
                            "product_uom_id": self._uom_id,
                            "itemnum": line["itemnum"],
                            "itemlbl": line["itemlbl"],
                        }
                    ],
                )
                self.report.add("create", "mrp.bom.line", label, f"id={_one_id(created)}")
                used.add(_one_id(created))
                continue
            used.add(int(current["id"]))
            comparable = {
                "product_qty": line["product_qty"],
                "itemnum": line["itemnum"],
                "itemlbl": line["itemlbl"],
            }
            if _same(current, comparable):
                self.report.add("unchanged", "mrp.bom.line", label, f"id={current['id']}")
                continue
            if self.dry_run:
                self.report.add("update", "mrp.bom.line", label, f"id={current['id']}")
                continue
            self._execute("mrp.bom.line", "write", [[current["id"]], comparable])
            self.report.add("update", "mrp.bom.line", label, f"id={current['id']}")
        extras = [int(row["id"]) for row in existing if int(row["id"]) not in used]
        if not extras:
            return
        if self.dry_run:
            self.report.add("unlink", "mrp.bom.line", number, f"extra={extras}")
            return
        self._execute("mrp.bom.line", "unlink", [extras])
        self.report.add("unlink", "mrp.bom.line", number, f"extra={extras}")


def _one_id(value) -> int:
    if isinstance(value, list):
        if len(value) != 1:
            raise PlmError(f"Expected one created id, got {value!r}.")
        return int(value[0])
    return int(value)


def _resolve(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def sync_bom(
    bom: BillOfMaterials | None = None,
    client: PlmClient | None = None,
    dry_run: bool = True,
    part_number: str | None = None,
    step_path: Path | None = None,
    pdf_path: Path | None = None,
) -> SyncReport:
    bom = bom or load_bom()
    if part_number and part_number not in bom.parts:
        raise BomError(f"Unknown part {part_number}.")
    if (step_path or pdf_path) and not part_number:
        raise PlmError("--step and --pdf need --part.")
    return PlmSync(
        bom,
        client,
        dry_run=dry_run,
        part_number=part_number,
        step_path=step_path,
        pdf_path=pdf_path,
    ).run()
