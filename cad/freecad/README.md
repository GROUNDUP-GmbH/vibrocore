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

This script does not connect to Odoo. The OdooPLM FreeCAD connector is a
proprietary Windows client and is not part of this workflow. The test plan for
it is in `docs/cad/ODOOPLM.md`.
