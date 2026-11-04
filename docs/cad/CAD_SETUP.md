# CAD and BOM setup

Vibrocore keeps one engineering bill of materials in git and generates the files
Odoo needs from it. The same part number is the OdooPLM engineering code and the
manufacturing internal reference.

## Stack

| Job | Tool | Why this one |
|---|---|---|
| Part numbers, revisions, quantities, estimates | `cad/bom/vibrocore.bom.yaml` | Diffable, reviewed in git, no CAD licence |
| Solids and STEP | [build123d](https://github.com/gumyr/build123d) 0.13 on OpenCascade | Headless, pinned, runs in CI. A part is modelled only when the design docs already give its dimensions |
| Drawings | SVG (A3) and a text PDF from `cad/tools/drawings.py` | ISO 7200 title block, ISO 5457 sheet, ISO 128 first-angle note. No GUI |
| Interactive mechanical CAD | FreeCAD 1.0 or newer, Part / Assembly / TechDraw | What a designer opens. `cad/freecad/make_plate.py` rebuilds the plate blank. `cad/freecad/plm_upload_macro.py` exports the active part and calls `plm-sync`. Not required for CI |
| Wiring notes | KiCad 8 schematic `cad/kicad/vibrocore-control/` | Text-native. There is no PCB yet |
| Product data | Odoo 19 with [OdooPLM](https://github.com/OmniaGit/odooplm) 19.0 | Engineering BOM, documents, revisions. Plain `mrp.bom` CSVs are the fallback |

FreeCAD's own Assembly and TechDraw workbenches are the right place for a released
drawing once the missing dimensions exist. They are not the CI path: a headless
TechDraw PDF still depends on a build with a GUI. The upload into OdooPLM is
`plm-sync` (see `docs/cad/ODOOPLM.md`), including the FreeCAD macro that calls it.

Code-CAD such as CadQuery would sit on the same OpenCascade kernel as build123d.
build123d 0.13 is the one pinned here because its STEP reader and writer are what
`plm_automated_convertion` also expects from a current OCP build.

## Conventions

Spelled out in `cad/CONVENTIONS.md`. Short version:

- Millimetres in CAD, kilograms on the product, euros for estimates.
- Part number `VC-<group>-<nnnn>` is both `engineering_code` and `default_code`.
- Revision index `0` is letter `A`, matching OdooPLM `get_revision_letter`.
- Do not invent a dimension. Leave it out of `geometry` and add an `unknowns` line.
- First-angle projection. Drawings are preliminary and say so in the title block.

## Everyday commands

```bash
pip install -r tests/requirements.txt -r requirements-cad.txt
python -m cad.tools.cli validate
python -m cad.tools.cli export
python -m cad.tools.cli check
python -m cad.tools.cli plm-sync
python -m pytest tests -q
```

`plm-sync` without `--apply` prints the OdooPLM plan and does not log in.
The write-up of that command is in `docs/cad/ODOOPLM.md`.

`export` rewrites the CSVs, STEP, PDF, SVG, `cad/export/geometry.json` and
`cad/OPEN_POINTS.md`. Commit those files with the YAML change. `check` fails if
they have drifted. STEP headers are pinned to the baseline date so two runs match.

Changing a length means editing the YAML, then `export`. The plate blank
`VC-SH-1301` is 420 × 300 × 20 mm because `docs/engineering/DIMENSIONING.md`
says so. The motor solid is only the 255 × 154 × 175 mm envelope.

## What is already modelled

| Part | What the file actually is |
|---|---|
| `VC-SH-1301` | Plate blank, 420 × 300 × 20 mm. No holes |
| `VC-SH-1302` | Rib blank, 300 × 10 × 60 mm. Not positioned on the plate |
| `VC-SH-1400` | Shaft only, Ø50 × 200 mm. Flange omitted |
| `VC-FR-4300`, `VC-FR-4400` | End-plate blanks. No hole patterns |
| `VC-FR-4100` | Outer envelope of the 50 × 100 × 1500 mm profile, not the mk 2004 slots |
| `VC-SH-1100` | Purchased-motor envelope, not an OLI model |

Assemblies have a parts list on the drawing sheet and an engineering BOM. They
do not have a positioned 3D assembly, because the pitches are not known.

## Odoo files

`cad/odoo/plm/` is the OdooPLM import. `cad/odoo/mrp/` is the same structure as
ordinary manufacturing BOMs (`normal`, or `phantom` for the two kits). Field
names and the import order are in `docs/cad/ODOOPLM.md`.

The authoritative description of what is still open is `cad/OPEN_POINTS.md`
plus the Odoo checklist in `docs/cad/ODOOPLM.md`.
