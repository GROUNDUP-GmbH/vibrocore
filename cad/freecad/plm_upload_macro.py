"""Upload the active FreeCAD part through the open OdooPLM API.

Works in FreeCAD 1.0 or newer on macOS (and anywhere else FreeCAD 1.x runs).
It does not use the proprietary Windows connector.

The macro exports the selected solid to STEP, and a TechDraw page to PDF when
the document has one. It then runs the same command as:

    python -m cad.tools.cli plm-sync --part VC-SH-1301 --step <file> --pdf <file>

That command is a dry run unless APPLY is turned on below, or the environment
variable VIBROCORE_PLM_APPLY=1 is set. Connection settings stay in ODOO_URL,
ODOO_DB, ODOO_USER and ODOO_API_KEY or ODOO_PASSWORD. They are not arguments
of this macro.

The part number is read from the document name, its label, or the selected
object's label. It has to look like VC-SH-1301.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PART_NUMBER_RE = re.compile(r"VC-(?:ASM|KIT|SH|HB|FR|PW|CT|GP|PS)-\d{4}")
ROOT = Path(__file__).resolve().parents[2]
# Dry run unless this is set, matching `plm-sync` itself.
APPLY = False


def part_number_from_text(*values: str) -> str | None:
    for value in values:
        match = PART_NUMBER_RE.search(value or "")
        if match:
            return match.group(0)
    return None


def build_sync_command(python: str, part_number: str, step_path: Path, pdf_path: Path | None, apply: bool) -> list[str]:
    command = [
        python,
        "-m",
        "cad.tools.cli",
        "plm-sync",
        "--part",
        part_number,
        "--step",
        str(step_path),
    ]
    if pdf_path:
        command.extend(["--pdf", str(pdf_path)])
    if apply:
        command.append("--apply")
    return command


def _texts(document, selected) -> list[str]:
    texts = [getattr(document, "Name", ""), getattr(document, "Label", ""), getattr(document, "Comment", "")]
    for obj in selected:
        texts.append(getattr(obj, "Label", ""))
        texts.append(getattr(obj, "Name", ""))
    return texts


def _selected_shape(document):
    selected = []
    try:
        import FreeCADGui as Gui

        selected = list(Gui.Selection.getSelection())
    except Exception:
        selected = []
    objects = selected or list(getattr(document, "Objects", []))
    for obj in objects:
        shape = getattr(obj, "Shape", None)
        if shape and not shape.isNull():
            return obj, shape, selected
    return None, None, selected


def export_active(destination: Path | None = None) -> tuple[str, Path, Path | None]:
    import FreeCAD as App

    document = App.ActiveDocument
    if document is None:
        raise RuntimeError("Open a FreeCAD document first.")
    obj, shape, selected = _selected_shape(document)
    if shape is None:
        raise RuntimeError("The document has no solid to export.")
    part_number = part_number_from_text(*_texts(document, selected or [obj]))
    if not part_number:
        raise RuntimeError(
            "Name the document or the solid with its part number, for example VC-SH-1301."
        )
    out = destination or (ROOT / "cad" / "export" / "freecad")
    out.mkdir(parents=True, exist_ok=True)
    step_path = out / f"{part_number}.step"
    shape.exportStep(str(step_path))
    pdf_path = _export_techdraw(document, out / f"{part_number}.pdf")
    return part_number, step_path, pdf_path


def _export_techdraw(document, pdf_path: Path) -> Path | None:
    pages = [
        obj
        for obj in document.Objects
        if getattr(obj, "TypeId", "").startswith("TechDraw::DrawPage")
    ]
    if not pages:
        return None
    import TechDrawGui

    TechDrawGui.exportPageAsPdf(pages[0], str(pdf_path))
    return pdf_path


def main() -> None:
    part_number, step_path, pdf_path = export_active()
    python = os.environ.get("VIBROCORE_PYTHON") or shutil.which("python3") or sys.executable
    apply = APPLY or os.environ.get("VIBROCORE_PLM_APPLY") == "1"
    command = build_sync_command(python, part_number, step_path, pdf_path, apply)
    print(" ".join(command))
    subprocess.check_call(command, cwd=str(ROOT))


if __name__ == "__main__":
    main()
