# CAD conventions

Hardware design sources in `cad/` are under CERN-OHL-S-2.0, same as the rest of
the hardware. The Python under `cad/tools/` is MIT, same as the firmware. The
narrative docs are CC BY-SA 4.0.

## Numbers

| Item | Rule |
|---|---|
| Unit of length | Millimetre. STEP files are millimetres, solids centred on the origin |
| Unit of mass | Kilogram. Steel blanks use 7850 kg/m³, the density already used in `docs/engineering/DIMENSIONING.md` |
| Money | Euro. `estimate_eur_low` / `estimate_eur_high` are **unit** costs. BOM.md prints line totals; unit = line total / quantity |
| Projection | First angle, ISO 128 |
| Sheet | A3 landscape, simplified ISO 5457 frame |
| Title block | ISO 7200 fields: legal owner, title, document type, document status, identification number, revision, creator, date, sheet |
| Status | `preliminary` until a human releases the revision in OdooPLM. No general tolerance class is stated; drawings say TODO rather than ISO 2768 |

## Identity

```text
VC-ASM-0000   saleable machine
VC-ASM-1nnn   sonic head
VC-ASM-2nnn   hub
VC-ASM-3nnn   frame
VC-ASM-4nnn   power
VC-ASM-5nnn   control
VC-KIT-6000   DT325 kit (not a machine BOM line)
VC-KIT-7000   positioning kit
VC-SH-        sonic-head parts
VC-HB-        hub parts
VC-FR-        frame parts
VC-PW-        power parts
VC-CT-        control parts
VC-GP-        Geoprobe parts
VC-PS-        positioning parts
```

`legacy_ref` is `section.row` from `docs/engineering/BOM.md`. Those row numbers
are not unique and are not the part number.

OdooPLM, from `plm/models/plm_mixin.py` in the 19.0 commit recorded in the YAML:

- `engineering_code` = part number
- `engineering_revision` = integer index, `0` for this baseline
- `engineering_revision_letter` = `A` for index 0 (`UPPERCASE_LETTERS[0]`)
- `engineering_state` = `draft` until the workflow in `docs/cad/ODOOPLM.md`
- `default_code` = the same part number

A document (`ir.attachment`) uses the same code and revision as its component.
The pair is unique, so the PDF is the printout of that document, not a second
code.

## Files

```text
cad/bom/vibrocore.bom.yaml          source of truth
cad/odoo/plm/                       OdooPLM CSV import
cad/odoo/mrp/                       product + mrp.bom fallback, no PLM fields
cad/export/step/VC-….step           one solid per modelled part
cad/export/pdf/VC-…_.pdf            drawing printout
cad/drawings/VC-…_.svg              same sheet, easier to diff
cad/export/geometry.json            dimensions the FreeCAD script reads
cad/kicad/vibrocore-control/        wiring skeleton
cad/freecad/make_plate.py           optional freecadcmd check
```

`geometry.fidelity` is `solid` (the blank is the part), `partial` (a defined
subset only; the rest is in `unknowns`) or `envelope` (outer box of a purchased
or slotted part, not for manufacture).

## Supply

| `supply` | OdooPLM BOM | Manufacturing fallback | `purchase_ok` |
|---|---|---|---|
| `purchase` | component, no BOM | no BOM | yes |
| `subcontract` | component, no BOM | no BOM | yes |
| `assemble` | `mrp.bom.type = ebom` | `type = normal` | no |
| `kit` | `ebom`, `kit_bom` set | `type = phantom` | no |
| `service` | `type = service` | same | yes |
