"""Create and update Vibrocore records in OdooPLM. Draft only.

The YAML file stays the source. A second run updates the same engineering
code and revision instead of inserting another one. A file is uploaded only
when the attachment record is missing, the stored field has no bytes, or the
stored checksum or bytes differ. Float fields use the decimal precision from
fields_get. engineering_state is written only as "draft" on create.
action_confirm, action_release and new_version are not called, and a record
that is no longer draft is left alone, including its file bytes and its
engineering BOM.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from cad.tools.adr import AdrDocument, load_adrs
from cad.tools.bom import ROOT, BillOfMaterials, BomError, Part, load_bom
from cad.tools.odoo_export import _description, document_rows
from cad.tools.plm_client import PlmClient, PlmError

DRAFT = "draft"
ADR_REVISION = 0
# OdooPLM 19.0 leaves checksum False and file_size 0 while the bytes still
# sit in datas (store_fname / db_datas) or in the printout Binary. Those
# files are a few MB. Do not download a larger one just to compare it.
CONTENT_LIMIT = 16 * 1024 * 1024
# One read() stays inside this many raw bytes and this many records.
READ_BUDGET = 16 * 1024 * 1024
READ_BATCH_COUNT = 4
PROBE_BATCH = 40
_EMPTY_SHA1 = hashlib.sha1(b"").hexdigest()
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


def _is_real_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _decimal_places(digits) -> int | None:
    if isinstance(digits, bool) or digits is None:
        return None
    if isinstance(digits, int):
        return digits
    if isinstance(digits, (list, tuple)) and digits:
        places = digits[-1]
        if isinstance(places, int) and not isinstance(places, bool):
            return int(places)
    return None


def _quantize(value, places: int) -> Decimal:
    number = Decimal(str(float(value or 0)))
    quantum = Decimal(1).scaleb(-int(places))
    return number.quantize(quantum, rounding=ROUND_HALF_UP)


def _same(current: dict, desired: dict, precision: dict[str, int] | None = None) -> bool:
    precision = precision or {}
    for key, wanted in desired.items():
        have = current.get(key)
        have = m2o_id(have) if key in M2O_FIELDS or isinstance(have, (list, tuple)) else have
        places = precision.get(key)
        if places is not None and (_is_real_number(wanted) or _is_real_number(have) or wanted in (False, None)):
            if _quantize(have, places) != _quantize(wanted, places):
                return False
            continue
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


def _sha1(content: bytes) -> str:
    return hashlib.sha1(content).hexdigest()


def _file_digest(path: Path) -> tuple[str, int]:
    """SHA1 and length of a local file. The file is not kept in memory."""
    digest = hashlib.sha1()
    size = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _int_size(value) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _normalize_checksum(value) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if len(text) == 40 and all(char in "0123456789abcdef" for char in text):
        return text
    return None


def _checksum_decision(local_sha1: str, local_size: int, checksum, file_size) -> str | None:
    """Return new, changed, unchanged, or None when the bytes must be read.

    `checksum` is the SHA1 of the stored bytes. `file_size` is their length.
    None means the checksum is missing. OdooPLM 19.0 leaves it False and
    leaves file_size at 0 while `datas` or `printout` still holds the file.
    A checksum of the empty file means there is no stored content.
    A file_size of 0 does not, when a real checksum is present.
    """
    stored = _normalize_checksum(checksum)
    size = _int_size(file_size)
    if stored is None:
        return None
    if stored == _EMPTY_SHA1:
        return "new" if local_size else "unchanged"
    if size == 0:
        return "unchanged" if stored == local_sha1 else "changed"
    if stored == local_sha1 and (size is None or size == local_size):
        return "unchanged"
    return "changed"


def _chunks(items: list, count: int):
    step = max(1, int(count))
    for start in range(0, len(items), step):
        yield items[start : start + step]


def _groups_by_budget(items: list[tuple[int, int]], budget: int, count: int):
    """Group (id, size) pairs so one read stays within budget and count."""
    group: list[int] = []
    total = 0
    for record_id, size in items:
        size = max(0, int(size))
        if group and (len(group) >= count or total + size > budget):
            yield group
            group = []
            total = 0
        group.append(record_id)
        total += size
    if group:
        yield group


def _bytes_reason(remote_sha1: str | None, local_sha1: str, local_size: int) -> str:
    if not remote_sha1:
        return "new" if local_size else "unchanged"
    return "unchanged" if remote_sha1 == local_sha1 else "changed"


def _oversized_reason(datas_reason: str) -> str:
    if datas_reason == "unchanged":
        return "unchanged"
    if datas_reason == "changed":
        return "changed"
    return "new"


def _decode_binary(value) -> bytes:
    if not value:
        return b""
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        try:
            return base64.b64decode(value, validate=False)
        except (binascii.Error, ValueError):
            return b""
    return b""


def _parse_human_size(value) -> int | None:
    """Parse an Odoo bin_size string such as '1.50 Kb'. None when it is not one."""
    if not isinstance(value, str):
        return None
    parts = value.strip().split()
    if len(parts) != 2:
        return None
    try:
        number = float(parts[0])
    except ValueError:
        return None
    scale = {"bytes": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4}.get(parts[1].lower())
    if scale is None:
        return None
    return int(number * scale)


def _upload_detail(filename: str, reason: str, document_id: int = 0) -> str:
    detail = f"{filename} reason={reason}"
    if document_id:
        return f"doc_id={document_id} {detail}"
    return detail


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
        self._adrs: list[AdrDocument] = []
        self._field_info: dict[str, dict] = {}
        self._attachments_ready = False
        self._attachment_index: dict[tuple, list[dict]] = {}
        self._printout_rows: dict[int, list[dict]] = {}
        # SHA1 of a remote field, or None when the field has no bytes.
        # The base64 payload is hashed and dropped.
        self._remote_sha1: dict[tuple[int, str], str | None] = {}
        self._too_big: set[tuple[int, str]] = set()

    def run(self) -> SyncReport:
        self._adrs = self._selected_adrs()
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
        self._prefetch_attachment_binaries()
        for part, payload in self._document_payloads():
            self._sync_document(part, payload)
        for adr in self._adrs:
            self._sync_adr(adr)
        for number in self._assembly_numbers():
            self._sync_bom(number)
        return self.report

    def _selected_adrs(self) -> list[AdrDocument]:
        try:
            docs = load_adrs()
        except ValueError as exc:
            raise PlmError(str(exc)) from exc
        if not self.part_number:
            return docs
        return [doc for doc in docs if self.part_number in doc.parts]

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
        for adr in self._adrs:
            if not adr.attachment_path.is_file():
                missing.append(str(adr.attachment_path))
            for part_number in adr.parts:
                if part_number not in self.bom.parts:
                    raise PlmError(
                        f"{adr.code} lists unknown part {part_number}. "
                        "Fix the ADR front matter or add the part to the YAML."
                    )
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
        for adr in self._adrs:
            self.report.add(
                "plan",
                "ir.attachment",
                adr.code,
                f"datas={adr.attachment_filename} rendered_as={adr.rendered_as}",
            )
            for part_number in adr.parts:
                self.report.add(
                    "plan",
                    "plm.component.document.rel",
                    f"{adr.code}->{part_number}",
                    "linkeddocuments",
                )
        for number in self._assembly_numbers():
            count = len(self.bom.children(number))
            self.report.add("plan", "mrp.bom", number, f"type=ebom lines={count}")

    def _execute(self, model: str, method: str, args: list, kwargs: dict | None = None):
        assert self.client is not None
        return self.client.execute(model, method, args, kwargs)

    def _model_fields(self, model: str) -> dict:
        if model not in self._field_info:
            result = self._execute(
                model,
                "fields_get",
                [],
                {"attributes": ["string", "type", "digits"]},
            )
            self._field_info[model] = result or {}
        return self._field_info[model]

    def _fields(self, model: str) -> set[str]:
        return set(self._model_fields(model))

    def _precision(self, model: str) -> dict[str, int]:
        found: dict[str, int] = {}
        for name, spec in self._model_fields(model).items():
            if not isinstance(spec, dict):
                continue
            places = _decimal_places(spec.get("digits"))
            if places is not None:
                found[name] = places
        return found

    def _quantize_vals(self, model: str, vals: dict) -> dict:
        precision = self._precision(model)
        if not precision:
            return vals
        out = dict(vals)
        for name, places in precision.items():
            value = out.get(name)
            if _is_real_number(value):
                out[name] = float(_quantize(value, places))
        return out

    def _document_read_fields(self) -> list[str]:
        fields = ["id", "name", "engineering_state", "is_plm", "description"]
        known = self._model_fields("ir.attachment")
        for name in ("checksum", "file_size"):
            if not known or name in known:
                fields.append(name)
        return fields

    def _use_field(self, name: str) -> bool:
        known = self._model_fields("ir.attachment")
        return (not known) or (name in known)

    def _column_checksum(self, row: dict):
        if not self._use_field("checksum"):
            return None
        return row.get("checksum")

    def _column_size(self, row: dict) -> int | None:
        if not self._use_field("file_size"):
            return None
        return _int_size(row.get("file_size"))

    def _metadata_decision(self, row: dict, local_sha1: str, local_size: int) -> str | None:
        return _checksum_decision(
            local_sha1,
            local_size,
            self._column_checksum(row),
            self._column_size(row),
        )

    def _datas_reason(self, current: dict | None, local_sha1: str, local_size: int) -> str:
        if not current or not current.get("id"):
            return "new"
        decision = self._metadata_decision(current, local_sha1, local_size)
        if decision:
            return decision
        size = self._column_size(current)
        if size is not None and size > CONTENT_LIMIT:
            return "changed"
        return self._content_reason(int(current["id"]), "datas", local_sha1, local_size, "changed")

    def _attachment_jobs(self) -> list[tuple[str, int, bool]]:
        jobs = []
        for part, payload in self._document_payloads():
            if not payload.get("odoo_datas_file"):
                continue
            jobs.append(
                (part.engineering_code, part.revision_index, bool(payload.get("odoo_printout_file")))
            )
        for adr in self._adrs:
            jobs.append((adr.code, ADR_REVISION, False))
        return jobs

    def _prefetch_attachment_binaries(self) -> None:
        """Read datas and printout for documents whose checksum cannot decide.

        OdooPLM stores the document bytes on ir.attachment.datas (computed from
        store_fname or db_datas) and the PDF on ir.attachment.printout. Both
        are base64 on XML-RPC read(), as the logged-in user. The printout HTTP
        route renders a report, so this path does not call it.
        """
        jobs = self._attachment_jobs()
        self._attachment_index = {}
        self._printout_rows = {}
        self._attachments_ready = True
        if not jobs:
            return
        codes = sorted({code for code, _revision, _has_pdf in jobs})
        fields = list(
            dict.fromkeys(self._document_read_fields() + ["engineering_code", "engineering_revision"])
        )
        rows = self._execute(
            "ir.attachment",
            "search_read",
            [[("engineering_code", "in", codes)]],
            {"fields": fields},
        ) or []
        for row in rows:
            key = (row.get("engineering_code"), row.get("engineering_revision"))
            self._attachment_index.setdefault(key, []).append(row)
        datas_ids = []
        printout_ids = []
        doc_ids = []
        for code, revision, has_pdf in jobs:
            found = self._attachment_index.get((code, revision), [])
            if len(found) != 1:
                continue
            row = found[0]
            record_id = int(row["id"])
            if (row.get("engineering_state") or DRAFT) != DRAFT:
                continue
            if _normalize_checksum(self._column_checksum(row)) is None:
                size = self._column_size(row)
                if size is not None and size > CONTENT_LIMIT:
                    self._too_big.add((record_id, "datas"))
                else:
                    datas_ids.append(record_id)
            if not has_pdf:
                continue
            doc_ids.append(record_id)
        self._prefetch_field(datas_ids, "datas")
        if not doc_ids:
            return
        storage_fields = ["id", "res_id"]
        for name in ("checksum", "file_size"):
            if self._use_field(name):
                storage_fields.append(name)
        storage = self._execute(
            "ir.attachment",
            "search_read",
            [[
                ("res_model", "=", "ir.attachment"),
                ("res_field", "=", "printout"),
                ("res_id", "in", doc_ids),
            ]],
            {"fields": storage_fields},
        ) or []
        for row in storage:
            self._printout_rows.setdefault(int(row["res_id"]), []).append(row)
        for doc_id in doc_ids:
            stored = self._printout_rows.get(doc_id, [])
            if any(_normalize_checksum(self._column_checksum(row)) for row in stored):
                continue
            sizes = [self._column_size(row) for row in stored]
            sizes = [size for size in sizes if size is not None]
            if sizes and max(sizes) > CONTENT_LIMIT:
                self._too_big.add((doc_id, "printout"))
                continue
            printout_ids.append(doc_id)
        self._prefetch_field(printout_ids, "printout")

    def _prefetch_field(self, ids: list[int], field_name: str) -> None:
        pending = []
        seen = set()
        for record_id in ids:
            record_id = int(record_id)
            key = (record_id, field_name)
            if record_id in seen or key in self._remote_sha1 or key in self._too_big:
                continue
            seen.add(record_id)
            pending.append(record_id)
        small: list[tuple[int, int]] = []
        for chunk in _chunks(pending, PROBE_BATCH):
            rows = self._execute(
                "ir.attachment",
                "read",
                [chunk],
                {"fields": ["id", field_name], "context": {"bin_size": True}},
            ) or []
            got = set()
            for row in rows:
                record_id = int(row["id"])
                got.add(record_id)
                sized = self._note_probe(record_id, field_name, row.get(field_name, False))
                if sized is not None:
                    small.append(sized)
            for record_id in chunk:
                if record_id not in got:
                    self._remote_sha1[(record_id, field_name)] = None
        for chunk in _groups_by_budget(small, READ_BUDGET, READ_BATCH_COUNT):
            rows = self._execute(
                "ir.attachment",
                "read",
                [chunk],
                {"fields": ["id", field_name]},
            ) or []
            got = set()
            for row in rows:
                record_id = int(row["id"])
                got.add(record_id)
                self._note_bytes(record_id, field_name, _decode_binary(row.get(field_name)))
            for record_id in chunk:
                if record_id not in got:
                    self._remote_sha1[(record_id, field_name)] = None

    def _note_probe(self, record_id: int, field_name: str, value) -> tuple[int, int] | None:
        """Remember a bin_size probe. Return (id, size) when the bytes are still needed."""
        key = (int(record_id), field_name)
        if value in (False, None, ""):
            self._remote_sha1[key] = None
            return None
        if isinstance(value, (bytes, bytearray)):
            self._note_bytes(record_id, field_name, bytes(value))
            return None
        if isinstance(value, str):
            size = _parse_human_size(value)
            if size is None:
                self._note_bytes(record_id, field_name, _decode_binary(value))
                return None
            if size == 0:
                self._remote_sha1[key] = None
                return None
            if size > CONTENT_LIMIT:
                self._too_big.add(key)
                return None
            return (int(record_id), size)
        self._too_big.add(key)
        return None

    def _note_bytes(self, record_id: int, field_name: str, raw: bytes) -> None:
        """Hash bytes already in memory, then drop them."""
        key = (int(record_id), field_name)
        self._too_big.discard(key)
        self._remote_sha1[key] = _sha1(raw) if raw else None

    def _content_reason(
        self,
        record_id: int,
        field_name: str,
        local_sha1: str,
        local_size: int,
        fallback: str,
    ) -> str:
        key = (int(record_id), field_name)
        if key in self._remote_sha1:
            return _bytes_reason(self._remote_sha1[key], local_sha1, local_size)
        if key in self._too_big:
            return fallback
        value = self._probe_binary(record_id, field_name)
        sized = self._note_probe(record_id, field_name, value)
        if sized is not None:
            self._note_bytes(record_id, field_name, self._read_binary(record_id, field_name))
        if key in self._remote_sha1:
            return _bytes_reason(self._remote_sha1[key], local_sha1, local_size)
        return fallback

    def _printout_storage(self, document_id: int) -> list[dict]:
        if not document_id:
            return []
        if self._attachments_ready:
            return list(self._printout_rows.get(int(document_id), []))
        fields = ["id", "res_id"]
        for name in ("checksum", "file_size"):
            if self._use_field(name):
                fields.append(name)
        found = self._execute(
            "ir.attachment",
            "search_read",
            [[
                ("res_model", "=", "ir.attachment"),
                ("res_field", "=", "printout"),
                ("res_id", "=", document_id),
            ]],
            {"fields": fields, "limit": 5},
        )
        return list(found or [])

    def _printout_reason(self, document_id: int, local_sha1: str, local_size: int, datas_reason: str) -> str:
        if not document_id:
            return "new"
        rows = self._printout_storage(document_id)
        if rows:
            return self._reason_from_storage(rows, local_sha1, local_size, datas_reason, document_id)
        return self._content_reason(
            document_id, "printout", local_sha1, local_size, _oversized_reason(datas_reason)
        )

    def _reason_from_storage(
        self,
        rows: list[dict],
        local_sha1: str,
        local_size: int,
        datas_reason: str,
        document_id: int,
    ) -> str:
        decisions = []
        for row in rows:
            decision = _checksum_decision(
                local_sha1,
                local_size,
                self._column_checksum(row),
                self._column_size(row),
            )
            if decision == "unchanged":
                return "unchanged"
            if decision:
                decisions.append(decision)
        if "changed" in decisions:
            return "changed"
        if "new" in decisions:
            return "new"
        sizes = [self._column_size(row) for row in rows]
        sizes = [size for size in sizes if size is not None]
        fallback = _oversized_reason(datas_reason)
        if sizes and max(sizes) > CONTENT_LIMIT:
            return fallback
        # file_size 0 is not an empty PDF. Read ir.attachment.printout.
        return self._content_reason(document_id, "printout", local_sha1, local_size, fallback)

    def _probe_binary(self, record_id: int, field_name: str):
        rows = self._execute(
            "ir.attachment",
            "read",
            [[int(record_id)]],
            {"fields": ["id", field_name], "context": {"bin_size": True}},
        )
        if not rows:
            return False
        return rows[0].get(field_name, False)

    def _read_binary(self, record_id: int, field_name: str) -> bytes:
        rows = self._execute(
            "ir.attachment",
            "read",
            [[int(record_id)]],
            {"fields": ["id", field_name]},
        )
        if not rows:
            return b""
        return _decode_binary(rows[0].get(field_name))

    def _send_upload(self, route: str, document_id: int, key: str, filename: str, content: bytes, reason: str) -> None:
        if reason == "unchanged":
            return
        if reason not in {"new", "changed"}:
            raise PlmError(f"Unknown upload reason {reason!r}.")
        if self.dry_run or not document_id:
            self.report.add("upload", route, key, _upload_detail(filename, reason))
            return
        assert self.client is not None
        if route.endswith("/upload_pdf"):
            self.client.upload_printout(document_id, filename, content)
        else:
            self.client.upload_datas(document_id, filename, content)
        self.report.add("upload", route, key, _upload_detail(filename, reason, document_id))

    def _upload_datas(self, current: dict | None, document_id: int, key: str, filename: str, path: Path, state: str) -> str:
        """Plan or send datas. Return the reason, including 'unchanged'."""
        if state != DRAFT:
            return "unchanged"
        if current is None or not document_id:
            reason = "new"
        else:
            local_sha1, local_size = _file_digest(path)
            reason = self._datas_reason(current, local_sha1, local_size)
        content = b""
        if reason in {"new", "changed"} and not self.dry_run and document_id:
            content = path.read_bytes()
        self._send_upload("/plm_document_upload/upload", document_id, key, filename, content, reason)
        return reason

    def _upload_printout(
        self,
        document_id: int,
        key: str,
        filename: str,
        path: Path,
        state: str,
        datas_reason: str,
    ) -> None:
        if state != DRAFT:
            return
        if not document_id:
            self._send_upload("/plm_document_upload/upload_pdf", 0, key, filename, b"", "new")
            return
        local_sha1, local_size = _file_digest(path)
        reason = self._printout_reason(document_id, local_sha1, local_size, datas_reason)
        content = b""
        if reason in {"new", "changed"} and not self.dry_run:
            content = path.read_bytes()
        self._send_upload("/plm_document_upload/upload_pdf", document_id, key, filename, content, reason)

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
        if model == "ir.attachment" and self._attachments_ready:
            found = self._attachment_index.get((part.engineering_code, part.revision_index), [])
            if len(found) > 1:
                raise PlmError(
                    f"{model} {part.part_number} rev {part.revision_index} exists more than once."
                )
            return found[0] if found else None
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
        vals = self._quantize_vals("product.product", self._product_vals(part))
        precision = self._precision("product.product")
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
        if _same(current, comparable, precision):
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
        vals = self._quantize_vals("product.supplierinfo", vals)
        supplier_precision = self._precision("product.supplierinfo")
        if not found:
            if self.dry_run or not product["id"] or not partner_id:
                self.report.add("create", "product.supplierinfo", part.part_number, "")
                return
            created = self._execute("product.supplierinfo", "create", [vals])
            self.report.add("create", "product.supplierinfo", part.part_number, f"id={_one_id(created)}")
            return
        current = found[0]
        supplier_compare = {"price": vals["price"], "min_qty": vals["min_qty"], "product_code": vals["product_code"]}
        if _same(current, supplier_compare, supplier_precision):
            self.report.add("unchanged", "product.supplierinfo", part.part_number, f"id={current['id']}")
            return
        if self.dry_run:
            self.report.add("update", "product.supplierinfo", part.part_number, f"id={current['id']}")
            return
        self._execute(
            "product.supplierinfo",
            "write",
            [[current["id"]], supplier_compare],
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
            self._document_read_fields(),
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
        datas_reason = self._upload_datas(current, document_id, key, filename, datas_path, state)
        if printout_path:
            self._upload_printout(document_id, key, printout_name, printout_path, state, datas_reason)

    def _sync_link(
        self,
        part: Part,
        product_id: int,
        document_id: int,
        product_state: str,
        document_state: str,
        key: str | None = None,
    ) -> None:
        key = key or part.part_number
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

    def _find_adr_record(self, adr: AdrDocument, fields: list[str]) -> dict | None:
        if self._attachments_ready:
            found = self._attachment_index.get((adr.code, ADR_REVISION), [])
            if len(found) > 1:
                raise PlmError(f"ir.attachment {adr.code} rev {ADR_REVISION} exists more than once.")
            return found[0] if found else None
        found = self._execute(
            "ir.attachment",
            "search_read",
            [[
                ("engineering_code", "=", adr.code),
                ("engineering_revision", "=", ADR_REVISION),
            ]],
            {"fields": fields, "limit": 2},
        )
        if len(found) > 1:
            raise PlmError(f"ir.attachment {adr.code} rev {ADR_REVISION} exists more than once.")
        return found[0] if found else None

    def _sync_adr(self, adr: AdrDocument) -> None:
        """Upload an ADR and link it to every named part. Draft only, idempotent."""
        key = f"{adr.code} rev {ADR_REVISION}"
        datas_path = adr.attachment_path
        filename = adr.attachment_filename
        description = (
            f"ADR {adr.code}: {adr.title}. Status {adr.status}. "
            f"Rendered as {adr.rendered_as} by plm-sync. "
            f"Source {adr.source_path.relative_to(ROOT)}. "
            f"Parts: {', '.join(adr.parts)}."
        )
        current = self._find_adr_record(adr, self._document_read_fields())
        if current is not None and not current.get("is_plm", True):
            raise PlmError(
                f"ir.attachment {adr.code} rev {ADR_REVISION} exists but is_plm is false. "
                "The upload routes refuse it."
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
                                "engineering_code": adr.code,
                                "engineering_revision": ADR_REVISION,
                                "engineering_revision_letter": "A",
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

        # Ensure every named part exists in _products (may be outside --part selection).
        for part_number in adr.parts:
            if part_number not in self._products:
                self._sync_product(self.bom.part(part_number))

        for part_number in adr.parts:
            product = self._products[part_number]
            part = self.bom.part(part_number)
            self._sync_link(
                part,
                product["id"],
                document_id,
                product["engineering_state"],
                state,
                key=f"{adr.code}->{part_number}",
            )

        self._upload_datas(current, document_id, key, filename, datas_path, state)

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
            comparable = self._quantize_vals("mrp.bom.line", comparable)
            if _same(current, comparable, self._precision("mrp.bom.line")):
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
