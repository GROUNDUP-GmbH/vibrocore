# Odoo import files

Generated from `cad/bom/vibrocore.bom.yaml`. Do not edit the CSVs by hand.

- `plm/` — Odoo 19 plus OdooPLM (`plm`, `plm_engineering`). Engineering BOM
  type `ebom`, engineering code, document rows.
- `mrp/` — the same products and the same components as ordinary
  manufacturing BOMs (`normal`, kits as `phantom`). No PLM columns, so it
  imports on Odoo 19 without OdooPLM.

`plm/document_payloads.csv` is not an Odoo model. It maps each document
external id to the STEP and PDF in this repository.

Import order, field names and the revision workflow: `docs/cad/ODOOPLM.md`.
`python -m cad.tools.cli plm-sync` writes the same engineering records through
the OdooPLM HTTP API instead of the CSV importer.
