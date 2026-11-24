# FreeCAD

FreeCAD 1.0 or newer is the CAD tool for interaction.
The tool has Part and Assembly and TechDraw.
CI does not install it.
`make_plate.py` rebuilds the plate blank from `cad/export/geometry.json`.
The plate is the one that vibrates.
The script uses `freecadcmd`.

- The script writes `cad/export/freecad/`.
- Git ignores that folder.

```bash
freecadcmd cad/freecad/make_plate.py
```

TechDraw can place that solid on an A3 sheet.
The sheet has an ISO 7200 title block.
You can do this after the holes exist.
The SVG and PDF files in `cad/drawings` and `cad/export/pdf` are the headless sheets until the holes exist.

- `make_plate.py` does not connect to Odoo.
- `plm_upload_macro.py` exports the active solid.
- The macro calls `python -m cad.tools.cli plm-sync --part …`.
- It runs in FreeCAD 1.x on macOS.
- The default is a dry run.
- `docs/cad/ODOOPLM.md` tells you how to aim it at a test database.
