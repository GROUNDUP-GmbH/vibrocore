# STE100 audit

This report lists the STE100 deviation of each file before the rewrite.

- The checker is `tools/ste100_check.py` from farmlink-core.
- The checker reads Markdown.
- The checker tests the length of a sentence.
- The checker tests the verb form.
- The checker tests the structure.
- The checker does not test the controlled dictionary.
- The dictionary has a licence.

## Levels

- The level is high if the error count is 5 or more.
- The level is high if the warning count is 50 or more.
- The level is medium if the error count is 1 to 4.
- The level is medium if there are 15 to 49 warnings and no errors.
- The level is low if there are 1 to 14 warnings and no errors.
- The level is none if the checker reports no issue.

## Scan

- The scan date is 2026-11-24.
- The Markdown scan uses the PR 19 branch.
- If PR 19 skips a file, it matches `main`.
- The scan covers 39 files.
- The files are Markdown.
- The checker reports 43 errors and 1238 warnings.

## Markdown files

| File | Level | Errors | Warnings |
| --- | --- | --- | --- |
| README.md | high | 3 | 90 |
| cad/CONVENTIONS.md | low | 0 | 3 |
| cad/OPEN_POINTS.md | high | 5 | 208 |
| cad/export/kicad/cable-list.md | none | 0 | 0 |
| cad/export/kicad/terminal-list.md | low | 0 | 1 |
| cad/freecad/README.md | low | 0 | 5 |
| cad/odoo/README.md | low | 0 | 9 |
| cad/vendor/VC-HB-2100/SOURCE.md | low | 0 | 6 |
| cad/vendor/VC-HB-2200/SOURCE.md | low | 0 | 13 |
| cad/vendor/VC-HB-2400/SOURCE.md | medium | 0 | 15 |
| cad/vendor/VC-HB-2800/SOURCE.md | low | 0 | 9 |
| cad/vendor/VC-HB-2810/SOURCE.md | low | 0 | 6 |
| cad/vendor/VC-HB-3000/SOURCE.md | low | 0 | 7 |
| cad/vendor/VC-HB-3100/SOURCE.md | low | 0 | 8 |
| cad/vendor/VC-HB-3110/SOURCE.md | low | 0 | 11 |
| cad/vendor/VC-PW-5310/SOURCE.md | low | 0 | 3 |
| cad/vendor/VC-PW-5320/SOURCE.md | low | 0 | 3 |
| docs/adr/ADR-0001-HMI-PLC-INTERFACE.md | medium | 0 | 15 |
| docs/adr/ADR-0002-CONTROL-SOFTWARE-ARCHITECTURE.md | medium | 0 | 17 |
| docs/cad/CAD_SETUP.md | medium | 1 | 16 |
| docs/cad/ODOOPLM.md | high | 1 | 83 |
| docs/design/ARCHITECTURE.md | medium | 0 | 19 |
| docs/design/CONTROL_SYSTEM.md | high | 11 | 99 |
| docs/design/HUB_SYSTEM.md | medium | 2 | 34 |
| docs/design/SONIC_HEAD.md | high | 4 | 81 |
| docs/engineering/BOM.md | high | 10 | 114 |
| docs/engineering/CABINET-ADDITIONS.md | medium | 0 | 26 |
| docs/engineering/CARRIAGE-BRACKET.md | medium | 0 | 16 |
| docs/engineering/DIMENSIONING.md | medium | 0 | 15 |
| docs/engineering/ENCLOSURE.md | medium | 0 | 17 |
| docs/engineering/IO-LIST.md | medium | 0 | 23 |
| docs/engineering/LIFT-DRIVE-SIZING.md | medium | 0 | 19 |
| docs/engineering/MAST-LAYOUT.md | high | 1 | 96 |
| docs/engineering/PULL_FORCE.md | medium | 0 | 23 |
| docs/engineering/SAMPLING.md | medium | 1 | 24 |
| docs/engineering/SCHEMATIC.md | medium | 0 | 35 |
| docs/references/REFERENCES.md | medium | 1 | 40 |
| firmware/docker/README.md | medium | 3 | 14 |
| firmware/revpi/README.md | medium | 0 | 15 |

## File names

Look at the names below.
Each one uses an underscore.
Use uppercase words in a new name.
Put a hyphen between the words.
This pass does not rename a file.

- `docs/cad/CAD_SETUP.md`
- `docs/design/CONTROL_SYSTEM.md`
- `docs/design/HUB_SYSTEM.md`
- `docs/design/SONIC_HEAD.md`
- `docs/engineering/PULL_FORCE.md`

## Files this pass does not rewrite

- PR 13 stays open.
- This pass does not merge PR 13.
- This pass does not edit a file that only PR 13 changes.
- `cad/CONVENTIONS.md`
- `cad/OPEN_POINTS.md`
- `docs/cad/CAD_SETUP.md`
- `docs/engineering/SAMPLING.md`
- `cad/vendor/VC-HB-2100/SOURCE.md`
- `cad/vendor/VC-HB-2200/SOURCE.md`
- `cad/vendor/VC-HB-2400/SOURCE.md`
- `cad/vendor/VC-HB-2800/SOURCE.md`
- `cad/models/machine_assembly.py`
- `cad/models/mast_layout.py`
- `cad/models/vendor_parts.py`
- `cad/tools/bom.py`
- `cad/tools/cli.py`
- `cad/tools/drawings.py`
- `cad/tools/geometry.py`

PR 13 also changes `cad/bom/vibrocore.bom.yaml`.
PR 13 also changes that Odoo export.
PR 19 changes those documents too.
The rewrite of those documents starts from PR 19.

- `docs/design/HUB_SYSTEM.md`
- `docs/engineering/BOM.md`
- `docs/engineering/DIMENSIONING.md`
- `docs/engineering/LIFT-DRIVE-SIZING.md`
- `docs/engineering/MAST-LAYOUT.md`
- `docs/engineering/PULL_FORCE.md`

- PR 20 changes `.github/workflows/kicad-erc.yml` only.
- This pass does not edit that file.

## German text

- `docs/references/REFERENCES.md` has one sentence in German.
- That sentence stays as it is.
- The English prose around it is in scope.

## YAML and comments

- The Markdown checker does not read YAML.
- The Markdown checker does not read a source comment.
- This audit uses the same sentence rules on four YAML keys.
- The keys are `spec`, `notes`, `comment`, and `description`.
- That pass reports 2 errors and 206 warnings.
- The warnings sit on 170 lines.
- The level for `cad/bom/vibrocore.bom.yaml` is high.
- There are 17 errors in the comments.
- There are 353 warnings in the comments.
- The comments sit in 53 files.
- The level for the comment set is high.
- The PR 13 comments stay.
