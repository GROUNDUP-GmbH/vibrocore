# Odoo import files

The files come from `cad/bom/vibrocore.bom.yaml`.
Do not edit the CSVs by hand.

- `plm/` is for Odoo 19 plus OdooPLM (`plm`, `plm_engineering`).
- The BOM type is `ebom`.
- The file has the design code and the document rows.
- `mrp/` has the same products and the same components.
- Those rows are shop BOMs of type `normal`.
- Kits are `phantom`.
- There are no PLM columns, so the file imports on Odoo 19 with no OdooPLM.

`plm/document_payloads.csv` is not an Odoo model.
It maps each document id to the STEP and the PDF in this repository.

- The import order and the field names and the revision workflow are in `docs/cad/ODOOPLM.md`.
- `python -m cad.tools.cli plm-sync` writes the same design records.
- The command uses the OdooPLM HTTP API.
- The command does not use the CSV importer.
