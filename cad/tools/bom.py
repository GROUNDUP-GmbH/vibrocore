"""Load and validate the Vibrocore bill of materials.

The YAML file is the only place part numbers, revisions, quantities and
estimates are authored. OdooPLM field names used here were read from
OmniaGit/odooplm branch 19.0 (commit recorded in the YAML meta block),
not from a later guess.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
BOM_PATH = ROOT / "cad" / "bom" / "vibrocore.bom.yaml"

PART_NUMBER_RE = re.compile(r"^VC-(ASM|KIT|SH|HB|FR|PW|CT|GP|PS)-\d{4}$")
SUPPLIES = {"purchase", "subcontract", "assemble", "kit", "service"}
FIDELITY = {"solid", "partial", "envelope"}
# RevisionBaseMixin.get_revision_letter uses UPPERCASE_LETTERS[index] for
# index 0..25. Index 0 is the module default and maps to "A".
REVISION_LETTERS = [chr(i) for i in range(ord("A"), ord("Z") + 1)]


class BomError(ValueError):
    pass


@dataclass
class Part:
    raw: dict
    part_number: str
    name: str
    revision_index: int
    revision_letter: str
    supply: str
    subsystem: str
    category: str
    spec: str
    legacy_ref: str
    manufacturer_pn: str | None
    supplier_id: str | None
    estimate_eur_low: float | None
    estimate_eur_high: float | None
    cost_included_in: str | None
    material: str | None
    plm_material: str | None
    mass_kg: float | None
    mass_note: str | None
    geometry: dict | None
    unknowns: list[str]
    notes: str
    sale_ok: bool

    @property
    def engineering_code(self) -> str:
        """product.template.engineering_code. Same text as the internal reference."""
        return self.part_number

    @property
    def is_service(self) -> bool:
        return self.supply == "service"

    @property
    def has_bom(self) -> bool:
        return self.supply in {"assemble", "kit"}


@dataclass
class BomLine:
    part_number: str
    qty: float


@dataclass
class Assembly:
    part_number: str
    mrp_type: str
    lines: list[BomLine]


@dataclass
class BillOfMaterials:
    meta: dict
    materials: list[dict]
    suppliers: list[dict]
    parts: dict[str, Part]
    assemblies: dict[str, Assembly]
    issues: list[dict]
    path: Path = field(default=BOM_PATH)

    def part(self, part_number: str) -> Part:
        return self.parts[part_number]

    def children(self, part_number: str) -> list[BomLine]:
        assembly = self.assemblies.get(part_number)
        return assembly.lines if assembly else []

    def unit_cost(self, part: Part, bound: str) -> float | None:
        value = part.estimate_eur_low if bound == "low" else part.estimate_eur_high
        return None if value is None else float(value)

    def line_cost(self, line: BomLine, bound: str) -> float:
        """Cost of one BOM line.

        A part estimate is the unit cost. An assembly without its own estimate
        contributes the rolled-up cost of one assembly, multiplied by qty.
        Parts whose cost is included in a parent contribute nothing.
        """
        part = self.part(line.part_number)
        if part.cost_included_in:
            return 0.0
        own = self.unit_cost(part, bound)
        if own is not None:
            return own * line.qty
        if part.part_number in self.assemblies:
            return self.rollup(part.part_number, bound) * line.qty
        return 0.0

    def rollup(self, part_number: str, bound: str) -> float:
        part = self.part(part_number)
        own = self.unit_cost(part, bound)
        if own is not None and part_number not in self.assemblies:
            return own
        total = 0.0
        for line in self.children(part_number):
            total += self.line_cost(line, bound)
        return total


def revision_letter_for_index(index: int) -> str:
    if index < 0:
        raise BomError(f"revision index must be >= 0, got {index}")
    if index >= len(REVISION_LETTERS):
        raise BomError(
            f"revision index {index} exceeds the A–Z mapping verified against "
            "OdooPLM RevisionBaseMixin.get_revision_letter"
        )
    return REVISION_LETTERS[index]


def _require(raw: dict, key: str, where: str):
    if key not in raw or raw[key] in (None, ""):
        raise BomError(f"{where}: missing {key}")
    return raw[key]


def load_bom(path: Path | None = None) -> BillOfMaterials:
    path = path or BOM_PATH
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    errors: list[str] = []

    def fail(message: str) -> None:
        errors.append(message)

    meta = data.get("meta") or {}
    for key in (
        "owner",
        "currency",
        "length_unit",
        "odooplm_commit",
        "odooplm_module_version",
        "cad_baseline_date",
    ):
        if not meta.get(key):
            fail(f"meta.{key} is required")
    if meta.get("length_unit") != "mm":
        fail("length unit must be mm")
    if meta.get("currency") != "EUR":
        fail("currency must be EUR")

    materials = data.get("materials") or []
    material_ids = {item["id"] for item in materials}
    suppliers = data.get("suppliers") or []
    supplier_ids = {item["id"] for item in suppliers}
    for supplier in suppliers:
        if not supplier.get("name"):
            fail(f"supplier {supplier.get('id')} has no name")

    parts: dict[str, Part] = {}
    for raw in data.get("parts") or []:
        try:
            number = _require(raw, "part_number", "part")
        except BomError as exc:
            fail(str(exc))
            continue
        if number in parts:
            fail(f"duplicate part number {number}")
            continue
        if not PART_NUMBER_RE.match(str(number)):
            fail(f"{number}: part number does not match VC-<group>-<nnnn>")
        try:
            revision_index = int(raw["revision_index"])
            letter = str(raw["revision_letter"])
            supply = str(raw["supply"])
        except (KeyError, TypeError, ValueError) as exc:
            fail(f"{number}: {exc}")
            continue
        expected = None
        try:
            expected = revision_letter_for_index(revision_index)
        except BomError as exc:
            fail(f"{number}: {exc}")
        if expected is not None and letter != expected:
            fail(
                f"{number}: revision_letter {letter} != {expected} for "
                f"engineering_revision {revision_index}"
            )
        if supply not in SUPPLIES:
            fail(f"{number}: supply {supply} is not one of {sorted(SUPPLIES)}")
        low = raw.get("estimate_eur_low")
        high = raw.get("estimate_eur_high")
        if (low is None) ^ (high is None):
            fail(f"{number}: estimate low and high must both be set or both empty")
        if low is not None and high is not None and float(low) > float(high):
            fail(f"{number}: estimate low {low} exceeds high {high}")
        if low is not None and float(low) < 0:
            fail(f"{number}: negative estimate")
        geometry = raw.get("geometry")
        if geometry:
            kind = geometry.get("kind")
            fidelity = geometry.get("fidelity")
            if kind not in {"box", "cylinder"}:
                fail(f"{number}: geometry.kind {kind} is not box or cylinder")
            if fidelity not in FIDELITY:
                fail(f"{number}: geometry.fidelity {fidelity} is invalid")
            if not geometry.get("source"):
                fail(f"{number}: geometry.source must cite a document")
            if kind == "box":
                for axis in ("length_mm", "width_mm", "height_mm"):
                    if not geometry.get(axis) or float(geometry[axis]) <= 0:
                        fail(f"{number}: geometry.{axis} must be a positive documented value")
            if kind == "cylinder":
                for axis in ("diameter_mm", "length_mm"):
                    if not geometry.get(axis) or float(geometry[axis]) <= 0:
                        fail(f"{number}: geometry.{axis} must be a positive documented value")
        plm_material = raw.get("plm_material")
        if plm_material and plm_material not in material_ids:
            fail(f"{number}: unknown plm_material {plm_material}")
        supplier_id = raw.get("supplier_id")
        if supplier_id and supplier_id not in supplier_ids:
            fail(f"{number}: unknown supplier_id {supplier_id}")
        included = raw.get("cost_included_in")
        if included and (low is not None or high is not None):
            fail(f"{number}: cost_included_in cannot carry its own estimate")
        try:
            parts[number] = Part(
                raw=raw,
                part_number=number,
                name=str(_require(raw, "name", number)),
                revision_index=revision_index,
                revision_letter=letter,
                supply=supply,
                subsystem=str(_require(raw, "subsystem", number)),
                category=str(_require(raw, "category", number)),
                spec=str(_require(raw, "spec", number)),
                legacy_ref=str(_require(raw, "legacy_ref", number)),
                manufacturer_pn=raw.get("manufacturer_pn"),
                supplier_id=supplier_id,
                estimate_eur_low=None if low is None else float(low),
                estimate_eur_high=None if high is None else float(high),
                cost_included_in=included,
                material=raw.get("material"),
                plm_material=plm_material,
                mass_kg=None if raw.get("mass_kg") is None else float(raw["mass_kg"]),
                mass_note=raw.get("mass_note"),
                geometry=geometry,
                unknowns=list(raw.get("unknowns") or []),
                notes=str(raw.get("notes") or ""),
                sale_ok=bool(raw.get("sale_ok", False)),
            )
        except BomError as exc:
            fail(str(exc))

    assemblies: dict[str, Assembly] = {}
    for raw in data.get("boms") or []:
        number = raw.get("part_number")
        if number not in parts:
            fail(f"BOM {number}: parent part does not exist")
            continue
        if number in assemblies:
            fail(f"duplicate BOM for {number}")
            continue
        mrp_type = raw.get("mrp_type")
        if mrp_type not in {"normal", "phantom"}:
            fail(f"{number}: mrp_type must be normal or phantom")
        lines: list[BomLine] = []
        seen: set[str] = set()
        for entry in raw.get("lines") or []:
            child = entry.get("part_number")
            qty = entry.get("qty")
            if child not in parts:
                fail(f"{number}: BOM line {child} is not a part")
                continue
            if child in seen:
                fail(f"{number}: duplicate BOM line {child}")
            seen.add(child)
            if qty is None or float(qty) <= 0:
                fail(f"{number}: qty for {child} must be > 0")
                continue
            lines.append(BomLine(part_number=child, qty=float(qty)))
        if not lines:
            fail(f"{number}: BOM has no lines")
        assemblies[number] = Assembly(part_number=number, mrp_type=mrp_type or "", lines=lines)

    for number, part in parts.items():
        has = number in assemblies
        if part.has_bom and not has:
            fail(f"{number}: supply {part.supply} requires a BOM")
        if not part.has_bom and has:
            fail(f"{number}: supply {part.supply} must not have a BOM")
        if part.supply == "kit" and assemblies.get(number) and assemblies[number].mrp_type != "phantom":
            fail(f"{number}: kits use mrp_type phantom in the standard manufacturing fallback")
        if part.supply == "assemble" and assemblies.get(number) and assemblies[number].mrp_type != "normal":
            fail(f"{number}: assemblies use mrp_type normal in the standard manufacturing fallback")
        if part.cost_included_in and part.cost_included_in not in parts:
            fail(f"{number}: cost_included_in {part.cost_included_in} does not exist")

    # Cycle check.
    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(number: str) -> None:
        if number in visiting:
            fail(f"BOM cycle at {number}")
            return
        if number in visited:
            return
        visiting.add(number)
        for line in assemblies.get(number, Assembly(number, "", [])).lines:
            walk(line.part_number)
        visiting.remove(number)
        visited.add(number)

    for number in assemblies:
        walk(number)

    issues = list(data.get("data_issues") or [])
    if not issues:
        fail("data_issues must record the known conflicts with BOM.md")

    if errors:
        raise BomError("BOM validation failed:\n- " + "\n- ".join(errors))

    return BillOfMaterials(
        meta=meta,
        materials=materials,
        suppliers=suppliers,
        parts=parts,
        assemblies=assemblies,
        issues=issues,
        path=path,
    )


def modelled_parts(bom: BillOfMaterials) -> list[Part]:
    return [part for part in bom.parts.values() if part.geometry]
