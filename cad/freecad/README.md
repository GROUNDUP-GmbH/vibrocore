# FreeCAD

FreeCAD 1.0 or newer is the interactive CAD tool: Part, Assembly, TechDraw.
CI does not install it.

`make_plate.py` rebuilds the vibrating-plate blank from `cad/export/geometry.json`
with `freecadcmd`. It writes `cad/export/freecad/`, which is gitignored.

```bash
freecadcmd cad/freecad/make_plate.py
```

TechDraw can place that solid on an A3 sheet with an ISO 7200 title block once
the holes exist. The SVG/PDF in `cad/drawings` and `cad/export/pdf` are the
headless sheets until then.

`make_plate.py` does not connect to Odoo.

`plm_upload_macro.py` exports the active solid and calls
`python -m cad.tools.cli plm-sync --part …`. It runs in FreeCAD 1.x on macOS.
The default is a dry run. How to point it at a test database is in
`docs/cad/ODOOPLM.md`.
