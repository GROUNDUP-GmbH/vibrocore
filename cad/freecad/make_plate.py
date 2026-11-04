"""Build the vibrating-plate blank in FreeCAD. Optional. Not used by CI.

The OdooPLM desktop connector is not used. This script only checks that a
designer can rebuild VC-SH-1301 from the dimensions already in geometry.json.

    freecadcmd cad/freecad/make_plate.py

Output goes to cad/export/freecad/, which is gitignored.
"""

import json
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / "cad" / "export" / "geometry.json").read_text(encoding="utf-8"))
PLATE = next(item for item in MANIFEST if item["part_number"] == "VC-SH-1301")
BOX = PLATE["bbox_mm"]

document = App.newDocument("VC-SH-1301")
feature = document.addObject("Part::Feature", "VC_SH_1301")
feature.Shape = Part.makeBox(BOX["x"], BOX["y"], BOX["z"])
document.recompute()

out = ROOT / "cad" / "export" / "freecad"
out.mkdir(parents=True, exist_ok=True)
document.saveAs(str(out / "VC-SH-1301.FCStd"))
feature.Shape.exportStep(str(out / "VC-SH-1301-freecad.step"))
print(f"Wrote {out / 'VC-SH-1301.FCStd'}")
