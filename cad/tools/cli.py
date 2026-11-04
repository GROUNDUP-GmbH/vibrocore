"""Command line for the Vibrocore CAD/BOM toolchain.

    python -m cad.tools.cli validate
    python -m cad.tools.cli export
    python -m cad.tools.cli check
"""

from __future__ import annotations

import argparse
import filecmp
import sys
import tempfile
from pathlib import Path

from cad.tools.bom import ROOT, load_bom, modelled_parts
from cad.tools.drawings import export_drawings
from cad.tools.geometry import export_step_files
from cad.tools.odoo_export import export_odoo

EXPORT_ROOTS = [
    ROOT / "cad" / "odoo" / "plm",
    ROOT / "cad" / "odoo" / "mrp",
    ROOT / "cad" / "export" / "step",
    ROOT / "cad" / "export" / "pdf",
    ROOT / "cad" / "drawings",
    ROOT / "cad" / "export" / "geometry.json",
    ROOT / "cad" / "OPEN_POINTS.md",
]


def open_points_text(bom) -> str:
    lines = [
        "# Open points on the Vibrocore CAD model",
        "",
        "Generated from `cad/bom/vibrocore.bom.yaml`. Do not edit by hand.",
        "The Odoo-side work is in `docs/cad/ODOOPLM.md`.",
        "",
        "## Known conflicts in the source BOM",
        "",
    ]
    for issue in bom.issues:
        lines.append(f"- `{issue['id']}`: {issue['summary']}")
    lines.extend(["", "## Parts with undocumented geometry or procurement data", ""])
    for part in sorted(bom.parts.values(), key=lambda item: item.part_number):
        if not part.unknowns and not part.geometry:
            lines.append(
                f"- `{part.part_number}` {part.name}: no solid. Dimensions were not complete enough to model."
            )
        for item in part.unknowns:
            lines.append(f"- `{part.part_number}` {part.name}: {item}")
    lines.extend(
        [
            "",
            "## Modelled in this revision",
            "",
        ]
    )
    for part in modelled_parts(bom):
        lines.append(
            f"- `{part.part_number}` {part.name}: {part.geometry['kind']}, "
            f"fidelity `{part.geometry['fidelity']}` ({part.geometry['source']})."
        )
    return "\n".join(lines) + "\n"


def write_open_points(bom, path: Path | None = None) -> Path:
    path = path or (ROOT / "cad" / "OPEN_POINTS.md")
    path.write_text(open_points_text(bom), encoding="utf-8")
    return path


def export_all(bom=None) -> None:
    bom = bom or load_bom()
    export_odoo(bom)
    export_drawings(bom)
    export_step_files(bom)
    write_open_points(bom)


def _files_under(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(item for item in path.rglob("*") if item.is_file())


def check() -> int:
    bom = load_bom()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # Re-export into a copy of the tree by monkeypatching module paths.
        from cad.tools import drawings, geometry, odoo_export

        originals = {
            "plm": odoo_export.PLM_DIR,
            "mrp": odoo_export.MRP_DIR,
            "svg": drawings.SVG_DIR,
            "pdf": drawings.PDF_DIR,
            "step": geometry.STEP_DIR,
            "json": geometry.GEOMETRY_JSON,
        }
        odoo_export.PLM_DIR = root / "plm"
        odoo_export.MRP_DIR = root / "mrp"
        drawings.SVG_DIR = root / "drawings"
        drawings.PDF_DIR = root / "pdf"
        geometry.STEP_DIR = root / "step"
        geometry.GEOMETRY_JSON = root / "geometry.json"
        try:
            export_odoo(bom)
            export_drawings(bom)
            export_step_files(bom)
            write_open_points(bom, root / "OPEN_POINTS.md")
        finally:
            odoo_export.PLM_DIR = originals["plm"]
            odoo_export.MRP_DIR = originals["mrp"]
            drawings.SVG_DIR = originals["svg"]
            drawings.PDF_DIR = originals["pdf"]
            geometry.STEP_DIR = originals["step"]
            geometry.GEOMETRY_JSON = originals["json"]

        pairs = [
            (root / "plm", originals["plm"]),
            (root / "mrp", originals["mrp"]),
            (root / "drawings", originals["svg"]),
            (root / "pdf", originals["pdf"]),
            (root / "step", originals["step"]),
            (root / "geometry.json", originals["json"]),
            (root / "OPEN_POINTS.md", ROOT / "cad" / "OPEN_POINTS.md"),
        ]
        mismatches: list[str] = []
        for generated, committed in pairs:
            gen_files = {path.relative_to(generated) for path in _files_under(generated)}
            com_files = {path.relative_to(committed) for path in _files_under(committed)}
            missing = com_files - gen_files
            extra = gen_files - com_files
            if missing or extra:
                mismatches.append(f"{committed}: missing={sorted(map(str, missing))} extra={sorted(map(str, extra))}")
            for relative in sorted(gen_files & com_files):
                if not filecmp.cmp(generated / relative, committed / relative, shallow=False):
                    mismatches.append(f"differs: {committed / relative}")
    if mismatches:
        print("Export is out of date:\n" + "\n".join(mismatches), file=sys.stderr)
        return 1
    print(f"BOM valid ({len(bom.parts)} parts, {len(bom.assemblies)} BOMs). Exports match.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vibrocore CAD/BOM tools")
    parser.add_argument("command", choices=("validate", "export", "check"))
    args = parser.parse_args(argv)
    if args.command == "validate":
        bom = load_bom()
        print(f"Valid BOM: {len(bom.parts)} parts, {len(bom.assemblies)} BOMs.")
        return 0
    if args.command == "export":
        export_all()
        print("Exported Odoo CSV, STEP, PDF, SVG and OPEN_POINTS.md.")
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
