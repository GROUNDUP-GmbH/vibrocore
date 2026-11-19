"""Parse docs/engineering/BOM.md and compare it to the YAML single source.

The Markdown tables are the human-readable BOM. The YAML owns part numbers.
This module checks that every numbered position, its part mapping and the
live quantities stay aligned.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from cad.tools.bom import ROOT, BillOfMaterials, load_bom

BOM_MD_PATH = ROOT / "docs" / "engineering" / "BOM.md"

ROW_RE = re.compile(
    r"^\|\s*(?P<pos>\d+[a-z]?)\s*\|\s*(?P<component>[^|]+?)\s*\|"
    r"(?P<spec>[^|]*)\|"
    r"\s*(?P<qty>[^|]*?)\s*\|"
)

# Item rows that must map to a YAML part for the V1.1 baseline.
REQUIRED_ITEM_POSITIONS = (
    [str(n) for n in list(range(1, 9)) + list(range(17, 65))]
    + ["47b", "48b"]
    + [str(n) for n in range(70, 96)]
    + [str(n) for n in range(96, 110)]
)

# Fixed part anchors used by firmware / V1.1 docs.
ANCHORS = {
    "38": "VC-FR-4700",
    "47": "VC-CT-6100",
    "47b": "VC-CT-6800",
    "48": "VC-CT-6110",
    "48b": "VC-CT-6810",
    "49": "VC-CT-6120",
    "70": "VC-LT-9100",
    "73": "VC-LT-9200",
    "76": "VC-PN-9300",
    "80": "VC-CS-9400",
    "95": "VC-CS-9550",
}

# BOM.md reuses 56-63 across Control, Geoprobe and Positioning. The Markdown
# parser keeps the first table occurrence (Control). YAML keeps all three via
# section.row legacy_ref; only the Control-side part is qty-checked here.
PREFERRED_SECTION_FOR_REUSED = {
    "56": "5",
    "57": "5",
    "58": "5",
    "59": "5",
    "60": "5",
    "61": "5",
    "62": "5",
    "63": "5",
}


@dataclass(frozen=True)
class MdRow:
    position: str
    component: str
    qty: float | None
    raw_qty: str


@dataclass(frozen=True)
class YamlRef:
    part_number: str
    section: str | None
    position: str


def parse_bom_md(path: Path | None = None) -> list[MdRow]:
    path = path or BOM_MD_PATH
    rows: list[MdRow] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        pos = match.group("pos").strip()
        component = match.group("component").strip()
        raw_qty = match.group("qty").strip()
        if component.lower() in {"component", "---"}:
            continue
        if not re.fullmatch(r"\d+[a-z]?", pos):
            continue
        # First occurrence wins for reused numbers (Control vs Geoprobe).
        if pos in seen:
            continue
        seen.add(pos)
        rows.append(
            MdRow(
                position=pos,
                component=component,
                qty=_parse_qty(raw_qty),
                raw_qty=raw_qty,
            )
        )
    return rows


def _parse_qty(text: str) -> float | None:
    text = text.strip()
    if not text or text in {"—", "-", "–"}:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    return float(match.group(1))


def parse_legacy_ref(legacy_ref: str) -> YamlRef | None:
    """Parse section.row legacy_ref into a BOM.md position token.

    Bare section refs (\"1\", \"8a\") are assemblies, not item rows.
    """
    text = str(legacy_ref).strip()
    match = re.fullmatch(r"(?P<section>\d+[a-z]?)\.(?P<row>\d+[a-z]?|psu)", text)
    if match:
        return YamlRef(
            part_number="",  # filled by caller
            section=match.group("section"),
            position=match.group("row"),
        )
    return None


def yaml_item_refs(bom: BillOfMaterials) -> dict[str, list[tuple[str, str | None]]]:
    """Map BOM.md item position -> list of (part_number, section)."""
    mapping: dict[str, list[tuple[str, str | None]]] = {}
    for part in bom.parts.values():
        parsed = parse_legacy_ref(part.legacy_ref)
        if not parsed:
            continue
        mapping.setdefault(parsed.position, []).append((part.part_number, parsed.section))
    return mapping


def yaml_position_map(bom: BillOfMaterials) -> dict[str, list[str]]:
    """Backward-compatible map: position -> part numbers (item refs only)."""
    return {
        pos: [part_number for part_number, _section in refs]
        for pos, refs in yaml_item_refs(bom).items()
    }


def live_qty(bom: BillOfMaterials, part_number: str) -> float:
    total = 0.0
    for assembly in bom.assemblies.values():
        for line in assembly.lines:
            if line.part_number == part_number:
                total += line.qty
    return total


def _pick_part(pos: str, refs: list[tuple[str, str | None]], bom: BillOfMaterials) -> str | None:
    """Pick the YAML part that the first BOM.md row for this number describes.

    Reused numbers (56-63) prefer section 5. An inactive preferred part stays
    selected so a later section cannot take over the quantity check.
    """
    preferred_section = PREFERRED_SECTION_FOR_REUSED.get(pos)
    if preferred_section is not None:
        preferred = [pn for pn, section in refs if section == preferred_section]
        if len(preferred) == 1:
            return preferred[0]
    active = [pn for pn, _section in refs if bom.part(pn).is_active]
    if len(active) == 1:
        return active[0]
    if pos in ANCHORS:
        for pn, _section in refs:
            if pn == ANCHORS[pos]:
                return pn
    return None


def compare_bom_md_and_yaml(
    bom: BillOfMaterials | None = None,
    md_path: Path | None = None,
) -> list[str]:
    """Return human-readable mismatch lines. Empty means aligned."""
    bom = bom or load_bom()
    md_path = md_path or BOM_MD_PATH
    md_rows = {row.position: row for row in parse_bom_md(md_path)}
    yaml_refs = yaml_item_refs(bom)
    errors: list[str] = []

    for pos in REQUIRED_ITEM_POSITIONS:
        if pos not in md_rows:
            errors.append(f"position {pos}: missing from BOM.md tables")
        if pos not in yaml_refs:
            errors.append(f"position {pos}: missing from YAML legacy_ref map")

    for pos, expected_pn in ANCHORS.items():
        found = [pn for pn, _section in yaml_refs.get(pos, [])]
        if expected_pn not in found:
            errors.append(f"position {pos}: expected part {expected_pn}, found {found}")

    for pos in REQUIRED_ITEM_POSITIONS:
        if pos not in md_rows or pos not in yaml_refs:
            continue
        md = md_rows[pos]
        refs = yaml_refs[pos]

        if pos == "38":
            if "VC-FR-4700" not in [pn for pn, _s in refs]:
                errors.append("position 38: expected VC-FR-4700")
            elif bom.part("VC-FR-4700").lifecycle != "obsolete":
                errors.append("position 38: VC-FR-4700 must be obsolete")
            if live_qty(bom, "VC-FR-4700") != 0:
                errors.append("position 38: obsolete tilt must have live qty 0")
            continue

        pn = _pick_part(pos, refs, bom)
        if pn is None:
            active = [p for p, _s in refs if bom.part(p).is_active]
            if not active:
                continue
            errors.append(f"position {pos}: could not pick a single active YAML part from {active}")
            continue

        part = bom.part(pn)
        if not part.is_active:
            # Option B lines stay in BOM.md with a quantity, but they are not on the live BOM.
            if part.lifecycle == "alternative":
                if live_qty(bom, pn) != 0:
                    errors.append(f"position {pos} ({pn}): alternative part must have live qty 0")
                continue
            if live_qty(bom, pn) != 0:
                errors.append(f"position {pos} ({pn}): inactive part must have live qty 0")
            if md.qty not in (None, 0.0):
                errors.append(
                    f"position {pos} ({pn}): inactive part must have BOM.md qty 0, got {md.raw_qty}"
                )
            continue
        yaml_qty = live_qty(bom, pn)
        if md.qty is None:
            continue
        expected = md.qty
        # Second WAGO DI/DO modules for V1.1 lift/tilt share the same part number.
        if pos in {"48", "49"} and pn in {"VC-CT-6110", "VC-CT-6120"}:
            expected = 2.0
        if abs(yaml_qty - expected) > 1e-6:
            errors.append(
                f"position {pos} ({pn}): BOM.md qty {expected:g} != YAML live qty {yaml_qty:g}"
            )

    sdr = bom.part("VC-PW-5310")
    if sdr.manufacturer_pn != "SDR-120-24":
        errors.append("VC-PW-5310 must be manufacturer_pn SDR-120-24")
    if live_qty(bom, "VC-PW-5310") != 1:
        errors.append("VC-PW-5310 must appear once on a live BOM")
    if bom.part("VC-PW-5300").lifecycle != "superseded":
        errors.append("VC-PW-5300 must be lifecycle superseded (DDR-60D-24 history)")
    if live_qty(bom, "VC-PW-5300") != 0:
        errors.append("superseded VC-PW-5300 must have live qty 0")

    md_text = md_path.read_text(encoding="utf-8")
    if re.search(r"Zero\s*2W", md_text, re.IGNORECASE):
        errors.append("BOM.md still mentions Raspberry Pi Zero 2W")
    if "EUR 530" not in md_text or "EUR 680" not in md_text:
        errors.append("BOM.md must document both EUR 530 (V1) and EUR 680 (V1.1) Option B savings")

    return errors
