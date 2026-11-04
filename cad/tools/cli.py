"""Command line for the Vibrocore CAD/BOM toolchain.

    python -m cad.tools.cli validate
    python -m cad.tools.cli export
    python -m cad.tools.cli check
    python -m cad.tools.cli plm-sync
    python -m cad.tools.cli plm-sync --apply
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


def _plm_sync_command(args) -> int:
    from cad.tools.bom import BomError
    from cad.tools.plm_client import PlmClient, PlmConfig, PlmError
    from cad.tools.plm_sync import sync_bom

    if args.apply and args.dry_run:
        print("Use either --apply or --dry-run.", file=sys.stderr)
        return 2
    try:
        bom = load_bom(Path(args.bom) if args.bom else None)
    except BomError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    dry_run = not args.apply
    config = PlmConfig.from_env()
    step = Path(args.step) if args.step else None
    pdf = Path(args.pdf) if args.pdf else None
    if dry_run and config is None:
        try:
            report = sync_bom(
                bom,
                client=None,
                dry_run=True,
                part_number=args.part,
                step_path=step,
                pdf_path=pdf,
            )
        except (PlmError, BomError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(report.text(), end="")
        return 0
    if config is None:
        print(
            "plm-sync --apply needs ODOO_URL, ODOO_DB, ODOO_USER and "
            "ODOO_API_KEY or ODOO_PASSWORD in the environment. Nothing was written.",
            file=sys.stderr,
        )
        return 1
    client = PlmClient(config)
    try:
        client.isalive()
        client.authenticate()
        if not dry_run:
            client.login_upload()
        report = sync_bom(
            bom,
            client=client,
            dry_run=dry_run,
            part_number=args.part,
            step_path=step,
            pdf_path=pdf,
        )
    except (PlmError, BomError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        f"Connected to {config.url} database {config.database} as {config.user}.",
    )
    print(report.text(), end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vibrocore CAD/BOM tools")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("export")
    sub.add_parser("check")
    plm = sub.add_parser(
        "plm-sync",
        help="Create or update draft OdooPLM products, documents and the engineering BOM",
    )
    plm.add_argument(
        "--apply",
        action="store_true",
        help="Write to Odoo. Without this flag the command only prints the plan.",
    )
    plm.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan and do not write. This is the default.",
    )
    plm.add_argument("--part", help="Sync one part number. An assembly also ensures its direct components.")
    plm.add_argument("--step", help="STEP file for --part. Defaults to cad/export/step.")
    plm.add_argument("--pdf", help="PDF printout for --part. Defaults to cad/export/pdf.")
    plm.add_argument("--bom", help="BOM YAML. Defaults to cad/bom/vibrocore.bom.yaml.")
    args = parser.parse_args(argv)
    if args.command == "validate":
        bom = load_bom()
        print(f"Valid BOM: {len(bom.parts)} parts, {len(bom.assemblies)} BOMs.")
        return 0
    if args.command == "export":
        export_all()
        print("Exported Odoo CSV, STEP, PDF, SVG and OPEN_POINTS.md.")
        return 0
    if args.command == "check":
        return check()
    return _plm_sync_command(args)


if __name__ == "__main__":
    sys.exit(main())
