# OdooPLM checklist for the Vibrocore database

This is the Odoo-side work. Git stays the source of the BOM. `plm-sync`
pushes that source into a database through the open `plm` HTTP API
(section 6). Field
names below were read from [OmniaGit/odooplm](https://github.com/OmniaGit/odooplm)
branch `19.0`, commit `b9db89248c206fd61bd38191d7a5289c58ce8a54`
(merge of PR 121, 2026-11-02). Module versions in that tree:

| Module | Version in that commit | Licence in its manifest |
|---|---|---|
| `plm` | 19.0.1.0.50 | LGPL-3 |
| `plm_engineering` | 19.0.1.0.1 | AGPL-3 |
| `plm_automate_normal_bom` | 19.0.1.0.0 | AGPL-3 |
| `plm_web_3d` | (viewer; install from a recursive clone) | AGPL-3 |
| `plm_web_revision` | 19.0.1.0.1 | AGPL-3 |

The AGPL-3 modules are served as part of the Odoo website if they are installed.
Confirm that with whoever owns the Ground UP Odoo licence before enabling them
on the production database. `plm` itself is LGPL-3.

A stock Odoo 19 without those modules can still import `cad/odoo/mrp/`.
Do not import both packages into the same database unless you mean to have an
engineering BOM and a manufacturing BOM side by side from day one. If both
exist, `plm_automate_normal_bom` will not rebuild the normal BOM: its cron
creates a normal BOM only when the product has none.

## 1. Install

On the Odoo 19 instance (the Docker image `ghcr.io/omniagit/odooplm:19.0` is
the upstream way to try this, not a requirement):

```text
odoo -d <database> -i plm,plm_engineering,plm_automate_normal_bom,plm_web_3d,plm_web_revision
```

`plm_web_3d` needs the git submodules (`git clone --recurse-submodules`).
The PyPI wheel omits `plm_demo`. Do not install `plm_demo` on the real company
database.

Leave `plm_auto_internalref` uninstalled for this import. Its `create` sets
`default_code` to `{engineering_code}_{engineering_revision}` (so `VC-ASM-0000_0`)
whenever `auto_default_code` is true, which is the default. This repository
keeps `default_code` equal to `engineering_code` so the manufacturing fallback
uses the same text.

Company currency should be EUR. Estimates are preliminary unit costs, not quotes.
`standard_price` is the low end of the range; the high end is in
`description_purchase`.

## 2. Tell Odoo that STEP and PDF are engineering files

`plm/views/ir_config_parameter.xml` ships `noupdate="1"` lists that do **not**
contain `.step`, `.stp`, `.pdf` or `.svg`:

- `file_exte_type_rel_2D`: `.dwg`, `.idw`, `.dxf`, `.iges`, `.e2`, `.slddrw`, `.dft`
- `file_exte_type_rel_3D`: `.e3`, `.iam`, `.ipt`, `.sldasm`, `.sldprt`, `.par`, `.asm`, `.psm`
- `file_exte_type_rel_PR`: `.ipn`

Until `.step` and `.stp` are added to `file_exte_type_rel_3D`, an attachment
named `VC-SH-1301.step` gets `document_type = other`. The browser viewer keys
off the file contents as well, but the PLM views filter on `document_type`.
Add `.pdf` (and `.svg` if you want the sheets classified) to the 2D list.
Edit the parameters in Settings. Do not expect a module upgrade to refresh
them, because the XML is `noupdate`.

## 3. Import order

Odoo CSV import, external ids prefixed `vibrocore.`. All engineering records
are `engineering_state = draft`, so they stay writable.

1. `cad/odoo/plm/product.category.csv` — model `product.category`
2. `cad/odoo/plm/plm.material.csv` — model `plm.material`
3. `cad/odoo/plm/res.partner.csv` — model `res.partner`
   `Custom fabrication (EU)` is a placeholder. Replace it before purchasing.
4. `cad/odoo/plm/product.product.csv` — model `product.product`
   Engineering fields live on `product.template` (`revision.plm.mixin`) and are
   written through `_inherits`. `engineering_revision` is an integer, default 0.
   `engineering_revision_letter` is `A` for that index
   (`RevisionBaseMixin.get_revision_letter`).
   `type` is `consu` (Odoo 19 "Goods") or `service` (the SIM only).
   `is_storable` is the inventory flag. `kit_bom` is set on `product.product`;
   the same flag also exists separately on `product.template`. Check the
   template form after import and set it there too if the view you use reads
   the template.
5. `cad/odoo/plm/product.supplierinfo.csv` — model `product.supplierinfo`
   Price is the low unit estimate, currency `base.EUR`.
6. `cad/odoo/plm/mrp.bom.csv` — model `mrp.bom`, `type` = `ebom`
   (`plm_engineering` adds that selection). `ebom_source_id` is an Integer
   holding a raw database id, not a many2one. Leave it empty.
   In this commit `mrp.bom` does **not** inherit `revision.plm.mixin`.
   `mrp.bom.engineering_revision` is a related stored field of the product
   template. The product carries the revision, not a separate BOM revision row.
7. `cad/odoo/plm/mrp.bom.line.csv` — model `mrp.bom.line`
   `itemnum` / `itemlbl` are the CAD position. They match the assembly-drawing
   item column. `product_id/default_code` resolves the component.
8. `cad/odoo/plm/ir.attachment.csv` — model `ir.attachment`, `is_plm` = true
   One document per `(engineering_code, engineering_revision)`. A second file
   with the same pair is rejected by the unique index. The STEP (or the PDF,
   for assemblies) is `datas`. The drawing PDF is the printout, field
   `printout`, not another attachment.
9. Upload binaries from `cad/odoo/plm/document_payloads.csv`
   (`odoo_datas_file` → `datas`, `odoo_printout_file` → `printout`).
   The CSV itself has no base64 payload.
10. `cad/odoo/plm/plm.component.document.rel.csv` — model
    `plm.component.document.rel`, the link behind `linkeddocuments`.

UoM external id used everywhere: `uom.product_uom_unit`. Confirm it still
resolves on this database before importing the BOMs.

The same records can be created without the CSV importer. Section 6 is that
path. Use one of the two on a given database, not both, or you will maintain
the same engineering codes twice.

`VC-ASM-0000` is the machine. `VC-KIT-6000` and `VC-KIT-7000` are not lines of
that BOM. In the manufacturing fallback they are `phantom` kits.

## 4. Revisions and change control

There is no `eco.order` (or similar) model in `plm` 19.0.1.0.50. The workflow
implemented on `revision.plm.mixin`, and exposed on the product by
`product.product.action_confirm` / `action_release`, is:

```text
draft → confirmed → released ↔ undermodify → obsoleted
```

Records in `confirmed`, `released`, `undermodify` or `obsoleted` are write
protected (`PLM_NO_WRITE_STATE`). That is why the import stays in `draft`.

Practical sequence, after you trust the data:

1. `action_confirm` on the product: draft → confirmed. The product method walks
   children that are still draft (`recursive=True` in `commonWFAction`).
2. `action_release`: confirmed → released. Previous released revisions of the
   same code are obsoleted.
3. `new_version()` only from a released record. It copies the record with
   `engineering_revision + 1`, letter from `get_revision_letter`, state `draft`.
   The previous released revision moves to `undermodify`.
4. With `plm_automate_normal_bom` installed, the cron
   `generateAutomatedNBoms` looks for products in `released` that have an `ebom`
   and no `normal` BOM, then `action_create_normalBom_WF` → `_create_normalBom`
   copies the EBOM, sets `type` to `normal`, and summarizes duplicate lines.
   That copy does not fill `ebom_source_id`. The wizard path
   `product.product._create_bom_from_ebom` does.
5. `plm_web_revision` adds the web wizards for a new product or document
   revision. It does not add a separate change object.
6. `activity_validation` (optional, not imported here) is an activity-based
   approval. `plm_mcp_ecr` talks about open changes in that sense. Install it
   only if you want activity gates; it is not required to revise a part.

Do the first release on a copy of the database. Releasing write-protects the
products, and the cron will then create normal BOMs that purchasing and MRP
will see.

## 5. Browser STEP viewer

Install `plm_web_3d`. Upstream describes a Three.js viewer for 3MF, STEP, glTF,
STL, OBJ, DXF and SVG (section plane, measurement, markup). After the STEP
files from `cad/export/step/` are on the attachment:

- Open the component, then the linked document, then the viewer.
- Confirm `VC-SH-1301` measures 420 × 300 × 20 mm.
- Confirm `VC-SH-1400` is the Ø50 × 200 mm shaft, not a flanged part.
- Confirm the profile `VC-FR-4100` is rejected as a manufacturing model: it is
  the outer box only.

`plm_automated_convertion` can batch-convert STEP to 3MF, STL and a PNG
preview. It needs the CadQuery/OCP stack from `aaa_requirements.txt` (the PyPI
extra is not the same build). Optional. The git STEP files are already the
artefacts to store.

## 6. Push the git BOM with plm-sync

There is no Windows workstation in this workflow, and the proprietary desktop
connector is not used. The server module `plm` already exposes the routes that
connector would call. `python -m cad.tools.cli plm-sync` speaks those routes
directly. The behaviour below was read from `plm/controllers/main.py` at
commit `b9db89248c206fd61bd38191d7a5289c58ce8a54`, and from Odoo
`odoo/service/common.py`, `odoo/http.py` and `res.users._check_credentials`
at `a81f10aaedb8eed773c32a6e0a1bd6d975f9ee72`.

| Call | What it does |
|---|---|
| `GET /plm_document_upload/isalive` | Health check. Body is the text `True`. No session. |
| `POST /plm_document_upload/login` | Form fields `login`, `password`, `db`. `auth="none"`. Starts a session. HTTP 200 has an empty body, a `session_id` cookie and `X-CSRF-TOKEN`. The upload routes set `csrf=False`, so the token is not sent back. A `db` that is not the request's database becomes HTTP 500. |
| `POST /jsonrpc` `common.authenticate` | `db`, login, secret, `{}`. Returns the uid. This call is non-interactive, so an API key works. |
| `POST /jsonrpc` `object.execute_kw` | Creates and updates `product.product`, `ir.attachment` (`is_plm` true), `plm.component.document.rel`, `mrp.bom` (`type` `ebom`) and `mrp.bom.line` (`itemnum`, `itemlbl`). |
| `POST /plm_document_upload/upload` | Multipart `mod_file`, `filename`, `doc_id`. `doc_id` is JSON, so `123` is the integer 123. Writes `datas` and `name` on that PLM document. 400 if the id is missing or `is_plm` is false. |
| `POST /plm_document_upload/upload_pdf` | Multipart `file_stream` and `doc_id`. Writes `printout`. |

The upload routes do not create the document. The command creates the
`ir.attachment` first (`is_plm` true, engineering code and revision, state
`draft`), then posts the bytes. `hostname` and `hostpws` are left empty, so
`setupCadOpen` does not record a CAD session.

`/plm_document_upload/login` calls `Session.authenticate` with
`interactive=True`. Odoo accepts an API key only when the check is not
interactive. Set `ODOO_PASSWORD` for the file upload. `ODOO_API_KEY` is used
for the JSON-RPC calls when it is set, and the password is still sent to the
login route. With only a password, both calls use it.

Nothing in the command calls `action_confirm`, `action_release`, `new_version`
or the normal-BOM copy. `engineering_state` is set to `draft` on create and is
not written again. A product, document or BOM whose state is no longer draft
is reported as `skip-locked` and left as it is, including its files. Run it
again after a YAML change: the same code and revision are updated, not
inserted a second time. An engineering BOM line that is no longer in the YAML
is removed. A second engineering BOM for the same product is not created.

The command does not install modules and it does not edit
`file_exte_type_rel_3D`. Until section 2 is done, a stored `VC-SH-1301.step`
keeps `document_type` `other`. Leave `plm_auto_internalref` uninstalled, or
accept that the command sets `auto_default_code` false when that field exists
so `default_code` stays the part number.

On a test database, after sections 1 and 2:

```bash
pip install -r requirements-cad.txt
export ODOO_URL=http://localhost:8069
export ODOO_DB=odooplm
export ODOO_USER=admin
export ODOO_PASSWORD=admin
# optional, used for JSON-RPC when set:
# export ODOO_API_KEY=

python -m cad.tools.cli plm-sync
python -m cad.tools.cli plm-sync --part VC-SH-1301
python -m cad.tools.cli plm-sync --apply
python -m cad.tools.cli plm-sync --apply --part VC-SH-1301
```

Without `ODOO_URL`, `ODOO_DB`, `ODOO_USER` and a secret, the first two
commands print a local plan and do not open a connection. With those variables
set, a command that has no `--apply` logs in over JSON-RPC, reads what is
already there, and still does not write. `--apply` writes. Copy
`.env.example` to `.env` if you want the variables next to the tree. `.env` is
gitignored. Do not put passwords in the command line, in the workflow file, or
in a commit.

Check afterwards, still on the test database:

1. `VC-SH-1301` is one `product.product`, engineering revision index 0, letter
   A, state draft. A second `--apply` does not add another.
2. One `ir.attachment` for that code and revision, `is_plm` set. `datas` is
   the STEP (it starts as a STEP file) and `printout` is the drawing PDF.
3. `plm.component.document.rel` links that product to that document.
4. `VC-ASM-1000` has one `mrp.bom` with `type` `ebom`. Line `itemnum` matches
   the drawing balloons. There is no `normal` BOM yet, because nothing was
   released and the cron has nothing to copy.
5. Open the linked document in the `plm_web_3d` viewer (section 5). The plate
   is 420 × 300 × 20 mm. If the viewer lists it as `other`, section 2 was
   skipped.

`cad/freecad/plm_upload_macro.py` is the same command from FreeCAD 1.x,
including macOS. It exports the active solid to STEP, a TechDraw page to PDF
when the document has one, and calls `plm-sync --part`. It stays a dry run
until `APPLY` in the macro or `VIBROCORE_PLM_APPLY=1`. The part number has to
be in the document name or the solid's label (`VC-SH-1301`). It uses
`VIBROCORE_PYTHON` or `python3` on `PATH`, because FreeCAD's own interpreter
does not have this repository's dependencies. `cad/freecad/make_plate.py` is
still the local plate script and does not log in.

A GitHub Actions workflow, `.github/workflows/cad-plm-sync.yml`, runs only
when someone starts it by hand (`workflow_dispatch`). The apply input defaults
to false. It reads `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_API_KEY` and
`ODOO_PASSWORD` from repository secrets. A normal push does not call Odoo.

`tests/test_plm_sync_integration.py` is skipped unless
`ODOO_PLM_INTEGRATION=1`. It is not started by CI. Point it at a disposable
database if you want the real server in the loop. The mocked tests in
`tests/test_plm_sync.py` are the ones CI runs.

## 7. Decisions still owed by engineering

These change the BOM, so they belong in the YAML before another import, not as
silent edits in Odoo:

- Close the 48 V supply conflict (BOM: 10 A, control diagram: Mean Well
  SDR-75-48 at 1.6 A) before anyone orders.
- Freeze the VFD, the stepper driver, the coupling, the brake and the
  isolator catalogue numbers. The YAML lists candidates and does not pick one
  where the source document doesn't.
- Motor pitch is only "at least 170 mm". Isolator coordinates, flange
  thickness, PCD, carriage size, shaft length and the DT325 thread are unknown.
  No holes were modelled.
- Confirm the 200 × 150 × 80 mm enclosure cannot hold the WAGO rack. The note
  is on `VC-CT-6300`.
- Decide whether `VC-CT-6410` (SE050 breakout) is already inside `VC-CT-6400`.
- Decide whether the WLAN bridge and the ESP32-C3 wallet are one board.
- Instagrid rental versus the EUR 2500 purchase line.
- Map `purchase_ok` / manufacturing routes onto the real warehouse. Routes are
  not in the CSV, because `mrp.route_warehouse0_manufacture` depends on the
  warehouse xml id of that database.
- Fastener kits are not exploded. Buy them as kits or replace the lines.
- The two GPS rows in BOM.md section 7 were not imported. See
  `positioning-gps-duplicate` in the YAML.

`cad/OPEN_POINTS.md` is the generated list of every `unknowns` entry.
