# OdooPLM checklist for the Vibrocore database

This page is the work on the Odoo side.
Git stays the source of the BOM.
`plm-sync` pushes that source into a database.
The path is the open `plm` HTTP API.
The steps are in section 6.
From [OmniaGit/odooplm](https://github.com/OmniaGit/odooplm) we read the field names below.

- The branch is `19.0`.
- The commit is `b9db89248c206fd61bd38191d7a5289c58ce8a54`.
- That commit is the merge of PR 121 on 2026-11-02.
- Module versions in that tree are in the table.

| Module | Version in that commit | Licence in its manifest |
|---|---|---|
| `plm` | 19.0.1.0.50 | LGPL-3 |
| `plm_engineering` | 19.0.1.0.1 | AGPL-3 |
| `plm_automate_normal_bom` | 19.0.1.0.0 | AGPL-3 |
| `plm_web_3d` | (viewer; install from a recursive clone) | AGPL-3 |
| `plm_web_revision` | 19.0.1.0.1 | AGPL-3 |


- The Odoo website serves the AGPL-3 modules if you install them.
- Confirm that with the owner of the Ground UP licence.
- Do this before you enable the modules on the production database.
- `plm` itself is LGPL-3.
- A stock Odoo 19 with no such modules can still import `cad/odoo/mrp/`.
- Do not import the two packages into one database.

Import the two only if you want an engineering BOM and a manufacturing BOM from the start.
If both exist, `plm_automate_normal_bom` will not rebuild the normal BOM.
The cron creates the normal BOM only when the product has none.

## 1. Install

You can try this on an Odoo 19 instance.
The Docker image `ghcr.io/omniagit/odooplm:19.0` is the upstream way to try this.
The image is not a requirement.

```text
odoo -d <database> -i plm,plm_engineering,plm_automate_normal_bom,plm_web_3d,plm_web_revision
```

- `plm_web_3d` needs the git submodules (`git clone --recurse-submodules`).
- The PyPI wheel omits `plm_demo`.
- Do not install `plm_demo` on the real company database.
- Leave `plm_auto_internalref` uninstalled for this import.
- Its `create` sets `default_code` to `{engineering_code}_{engineering_revision}` (so `VC-ASM-0000_0`).
- The module does this when `auto_default_code` is true.
- True is the default.
- This repository keeps `default_code` equal to `engineering_code`.
- Then the shop fallback uses the same text.
- Company currency must be EUR.
- Estimates are preliminary unit costs, not quotes.
- `standard_price` is the low end of the range.
- The high end is in `description_purchase`.

## 2. Tell Odoo that STEP and PDF are engineering files

`plm/views/ir_config_parameter.xml` ships `noupdate="1"` lists that do not contain `.step`, `.stp`, `.pdf` or `.svg`.

- `file_exte_type_rel_2D`: `.dwg`, `.idw`, `.dxf`, `.iges`, `.e2`, `.slddrw`, `.dft`
- `file_exte_type_rel_3D`: `.e3`, `.iam`, `.ipt`, `.sldasm`, `.sldprt`, `.par`, `.asm`, `.psm`
- `file_exte_type_rel_PR`: `.ipn`

Until you add `.step` and `.stp` to `file_exte_type_rel_3D`, an attachment named `VC-SH-1301.step` gets `document_type = other`.
The browser viewer also keys off the file contents.
The PLM views filter on `document_type`.
Add `.pdf` to the 2D list.
Add `.svg` if you want the sheets classified.
Edit the parameters in Settings.

- Do not expect a module upgrade to refresh the parameters.
- The XML is `noupdate`.

## 3. Import order

Odoo imports the CSV with external ids.
The prefix is `vibrocore.`.
All design records are `engineering_state = draft`.
You can still write those records.

1. Import `cad/odoo/plm/product.category.csv` for the model `product.category`.
2. Import `cad/odoo/plm/plm.material.csv` for the model `plm.material`.
3. Import `cad/odoo/plm/res.partner.csv` for the model `res.partner`. `Custom fabrication (EU)` is a placeholder. Replace it before you buy.
4. Import `cad/odoo/plm/product.product.csv` for the model `product.product`.
- Design fields live on `product.template` (`revision.plm.mixin`).
- The import writes them with `_inherits`.
- `engineering_revision` is an integer.
- The default is 0.
- `engineering_revision_letter` is `A` for that index.
- The letter comes from `RevisionBaseMixin.get_revision_letter`.
- `type` is `consu` for Odoo 19 Goods or `service` for the SIM only.
- `is_storable` is the inventory flag.
- The import sets `kit_bom` on `product.product`.
- The same flag also exists on `product.template`.
- Check the template form after the import.
- If the view reads the template, set the flag there too.
5. Import `cad/odoo/plm/product.supplierinfo.csv` for the model `product.supplierinfo`.
- The price is the low unit estimate.
- The currency is `base.EUR`.
6. Import `cad/odoo/plm/mrp.bom.csv` for the model `mrp.bom`.
- The `type` is `ebom`.
- `plm_engineering` adds that selection.
- `ebom_source_id` is an Integer.
- The field holds the raw database id, not a many2one.
- Leave the field empty.
- In this commit `mrp.bom` does not inherit `revision.plm.mixin`.
- `mrp.bom.engineering_revision` is a related stored field of the product template.
- The product carries the revision.
- There is no separate row for a BOM revision.
7. Import `cad/odoo/plm/mrp.bom.line.csv` for the model `mrp.bom.line`.
- `itemnum` and `itemlbl` are the CAD position.
- They match the item column on the assembly sheet.
- `product_id/default_code` resolves the component.
8. Import `cad/odoo/plm/ir.attachment.csv` for the model `ir.attachment`.
- `is_plm` is true.
- Use one document for each pair `(engineering_code, engineering_revision)`.
- The unique index rejects the second file with the same pair.
- The STEP is `datas`.
- For an assembly, the PDF uses that same field.
- The sheet PDF is the printout, in the field `printout`.
- It is not a second attachment.
9. Upload the binaries from `cad/odoo/plm/document_payloads.csv`.
- `odoo_datas_file` goes to `datas`.
- `odoo_printout_file` goes to `printout`.
- The CSV has no base64 payload.
10. Import `cad/odoo/plm/plm.component.document.rel.csv` for the model `plm.component.document.rel`.
- That model is the link behind `linkeddocuments`.

The UoM external id in each row is `uom.product_uom_unit`.
Confirm that the id still resolves on this database before you import the BOMs.
You can create the same records with no CSV importer.
Section 6 is that path.
Use one of the two paths on a database.
Do not use both paths, or you will maintain the same design codes two times.

- `VC-ASM-0000` is the machine.
- `VC-KIT-6000` and `VC-KIT-7000` are not lines of that BOM.
- In the shop fallback they are `phantom` kits.

## 4. Revisions and change control

There is no `eco.order` model, or a similar model, in `plm` 19.0.1.0.50.
The flow is on `revision.plm.mixin`.
The product shows it with `product.product.action_confirm` and `action_release`.

```text
draft → confirmed → released ↔ undermodify → obsoleted
```

Records in `confirmed`, `released`, `undermodify` or `obsoleted` block writes (`PLM_NO_WRITE_STATE`).
That is why the import stays in `draft`.
Do this sequence after you trust the data.

1. Call `action_confirm` on the product. The state goes from draft to confirmed. The method on the product walks the children that are still draft (`recursive=True` in `commonWFAction`).
2. Call `action_release`. The state goes from confirmed to released. The flow obsoletes the previous released revision of that code.
3. Call `new_version()` only from a released record. The call copies the record with `engineering_revision + 1`. The letter comes from `get_revision_letter`. The state of the copy is `draft`. The call moves the previous released revision to `undermodify`.
4. With `plm_automate_normal_bom` installed, the cron `generateAutomatedNBoms` runs.
- The cron looks for products in `released`.
- Those products have an `ebom` and no `normal` BOM.
- The cron then calls `action_create_normalBom_WF` and `_create_normalBom`.
- The call copies the EBOM.
- The call sets `type` to `normal`.
- The call sums the duplicate lines.
- That copy does not fill `ebom_source_id`.
- The path `product.product._create_bom_from_ebom` does fill it.
5. `plm_web_revision` adds the web wizards for a new product or a new document revision.
- It does not add the separate change object.
6. `activity_validation` is optional.
- This import does not use it.
- It is an approval by activity.
- `plm_mcp_ecr` talks of open changes in that sense.
- Install it only if you want gates on the activity.
- You do not need it to revise a part.

Do the first release on a copy of the database.
When you release, the products block writes.
The cron will then create normal BOMs.
Purchase and MRP will see those BOMs.

## 5. Browser STEP viewer

- Install `plm_web_3d`.
- Upstream describes a viewer in Three.js for 3MF and STEP and glTF.
- The viewer also opens STL and OBJ and DXF and SVG.
- The viewer has the section plane and measurement and markup.
- Do these checks after you put the STEP files from `cad/export/step/` on the attachment.
- Open the component. Then open the linked document. Then open the viewer.
- Confirm `VC-SH-1301` measures 420 × 300 × 20 mm.
- Confirm `VC-SH-1400` is the Ø50 × 200 mm shaft, not a flanged part.
- Confirm that you reject the profile `VC-FR-4100` as a shop model.
- The profile is the outer box only.

`plm_automated_convertion` can batch-convert STEP to 3MF and STL and a PNG preview.
It needs the CadQuery/OCP stack from `aaa_requirements.txt`.
The PyPI extra is not the same build.
This step is optional.
The git STEP files are already the artefacts to store.

## 6. Push the git BOM with plm-sync

- There is no Windows workstation in this flow.
- The flow does not use the proprietary desktop connector.
- The server module `plm` exposes the routes.
- The connector calls those routes.
- `python -m cad.tools.cli plm-sync` speaks those routes in a direct way.
- We read the behaviour below from `plm/controllers/main.py`.
- The commit is `b9db89248c206fd61bd38191d7a5289c58ce8a54`.
- We also read Odoo `odoo/service/common.py`, `odoo/http.py` and `res.users._check_credentials`.
- The Odoo commit is `a81f10aaedb8eed773c32a6e0a1bd6d975f9ee72`.

| Call | What it does |
|---|---|
| `GET /plm_document_upload/isalive` | Health check. Body is the text `True`. No session. |
| `POST /plm_document_upload/login` | Form fields `login`, `password`, `db`. `auth="none"`. Starts a session. HTTP 200 has an empty body, a `session_id` cookie and `X-CSRF-TOKEN`. The upload routes set `csrf=False`, so the token is not sent back. A `db` that is not the request's database becomes HTTP 500. |
| `POST /jsonrpc` `common.authenticate` | `db`, login, secret, `{}`. Returns the uid. This call is non-interactive, so an API key works. |
| `POST /jsonrpc` `object.execute_kw` | Creates and updates `product.product`, `ir.attachment` (`is_plm` true), `plm.component.document.rel`, `mrp.bom` (`type` `ebom`) and `mrp.bom.line` (`itemnum`, `itemlbl`). |
| `POST /plm_document_upload/upload` | Multipart `mod_file`, `filename`, `doc_id`. `doc_id` is JSON, so `123` is the ir.attachment id, not the engineering code. The route writes `datas` and `name`. The success body is the text `Upload succeeded`. |
| `POST /plm_document_upload/upload_pdf` | Multipart `file_stream` and `doc_id`. Writes `printout`. The success body is the text `Upload succeeded`. |


- The upload routes do not create the document.
- The command creates the `ir.attachment` first.
- `is_plm` is true, with the design code and the revision and the state `draft`.
- The command then posts the bytes.
- The command leaves `hostname` and `hostpws` empty.
- So `setupCadOpen` does not record a CAD session.
- The route answers `Upload succeeded` when `write` returns.
- The route does not read the field again.
- A file part that is empty still gets that answer.
- Odoo answers HTTP 303 to `/web/login` when the session has no user.
- The command does not follow redirects.
- After the POST, the command reads the field with JSON-RPC `read()`.
- `bin_size` is false.
- The stored bytes must be the local file.
- If they are not, the command writes that field over JSON-RPC.
- The value is base64 text.
- `datas` and `name` are the upload fields.
- `printout` is the PDF field.
- The command reads the field again.
- The command stops with an error when the field is still empty.
- The command does not count that upload.
- `plm-sync` exits with code 1.
- `/plm_document_upload/login` calls `Session.authenticate` with `interactive=True`.
- Odoo accepts an API key only when the check is not interactive.
- Set `ODOO_PASSWORD` for the file upload.
- The calls use `ODOO_API_KEY` for JSON-RPC when you set it.
- The command still sends the password to the login route.
- If you set only a password, the two calls use it.
- The command calls none of `action_confirm`, `action_release`, `new_version` or the normal-BOM copy.
- The command sets `engineering_state` to `draft` on create.
- The command does not write that field again.
- If a product or a document or a BOM is no longer draft, the command reports `skip-locked`.
- The command leaves the record as it is, with its files.
- If you run it again after the YAML change, the command updates the same code and the revision.
- The command does not insert a second record.
- If an engineering BOM line is no longer in the YAML, the command removes it.
- The command does not create the second engineering BOM for the same product.
- Before an upload, the command reads the attachment.
- It uses `fields_get` and `read` for `checksum` and `file_size`.
- `checksum` is the SHA1 value of the stored file.
- The command leaves the file in place when the checksum matches the local file.
- The command uploads the local file when the checksum differs.
- OdooPLM 19.0 can leave `checksum` empty and `file_size` at 0.
- The file can still be present.
- The document bytes are in `datas` (`store_fname` or `db_datas`).
- The PDF bytes are in the field `printout`.
- If the checksum is empty, the command reads that field with XML-RPC `read()`.
- The call runs as the logged-in user.
- The value is base64.
- The command compares its SHA1 value with the local file.
- The command does not download a file larger than 16 MB for this compare.
- The command reads the files in small batches.
- The command reports reason `new` when no attachment record exists.
- The command reports reason `new` when the stored field has no bytes.
- The command reports reason `changed` when the SHA1 values differ.
- A printout larger than 16 MB can have no checksum.
- If `datas` is the same, the command leaves that printout in place.
- A dry run reports `upload=N` for the files it will send.
- Each upload line gives the file name and the reason `new` or `changed`.
- Float fields use the decimal count from `fields_get`.
- `weight` is the example.
- The command reports the field as the same at that precision.
- It does this when the stored value and the YAML value are equal.
- The command rounds the YAML value to that precision before a write.
- The command does not install modules.
- The command does not edit `file_exte_type_rel_3D`.
- Until you do section 2, the stored `VC-SH-1301.step` keeps `document_type` `other`.
- Leave `plm_auto_internalref` uninstalled.
- Or accept that the command sets `auto_default_code` false when that field exists.
- Then `default_code` stays the part number.
- On the test database, you do section 1 first.
- Then do section 2.

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

With no `ODOO_URL`, `ODOO_DB`, `ODOO_USER` and no secret, the first two commands print the local plan.
Those commands do not open a connection.
If you set those variables, a command with no `--apply` logs in on JSON-RPC.
The command reads what is already there.
The command still does not write.
`--apply` writes.

- Copy `.env.example` to `.env` if you want the variables next to the tree.
- Git ignores `.env`.
- Do not put passwords in the command line.
- Do not put passwords in the workflow file.
- Do not put passwords in a commit.
- Check afterwards, still on the test database.

1. `VC-SH-1301` is one `product.product`. The design revision index is 0. The letter is A. The state is draft. A second `--apply` does not add another product.
2. There is one `ir.attachment` for that code and that revision. Confirm that `is_plm` is true. `datas` is the STEP file. The file starts as a STEP file. `printout` is the PDF of the sheet. A second `--apply` does not upload a file when the checksum matches. A second `--apply` does not upload a file when the checksum is empty and the stored bytes match.
3. `plm.component.document.rel` links that product to that document.
4. `VC-ASM-1000` has one `mrp.bom` with `type` `ebom`. The line `itemnum` matches the balloons on the sheet. There is no `normal` BOM yet. The team did not release a record, so the cron has nothing to copy.
5. Open the linked document in the viewer `plm_web_3d`. See section 5 for the viewer. The plate is 420 × 300 × 20 mm. If the viewer lists the plate as `other`, you skipped section 2.
6. Each ADR in `docs/adr/` that lists `parts:` is one PLM document. The document links to those parts. See the ADR subsection below.

### ADR documents (Architecture Decision Records)

`plm-sync` reads Markdown files in `docs/adr/`.
Each file must have front matter in YAML.
The matter has a `parts` list of Vibrocore part numbers (`VC-…`).

Example:

```yaml
---
title: ADR-0001 HMI–PLC Interface
status: Accepted
date: 2026-11-19
parts:
  - VC-CT-6100
  - VC-CT-6110
  - VC-CT-6120
  - VC-ASM-5000
---
```

Procedure:

1. The command finds each `ADR-*.md` file.
2. The command makes a PDF from the ADR text. The writer of the PDF is the small Helvetica writer. The CAD sheets use that writer. The repository does not add weasyprint or pandoc. If the PDF creation fails, the command stores the Markdown file as the attachment. The command reports `rendered_as=markdown`.
3. The command writes the file under `cad/export/adr/`. An example file is `ADR-0001.pdf`.
4. The command creates or updates one `ir.attachment`. The command sets `engineering_code = ADR-0001`. The command sets `engineering_revision = 0`. The command sets `engineering_state = draft`. The command sets `is_plm = true`.
5. The command uploads the file bytes with `/plm_document_upload/upload` when the record is new. The command also uploads when the stored field has no bytes. The command also uploads when the checksum differs. The command also uploads when the stored bytes differ. The command reads `datas` after the upload. The command stops when `datas` is still empty.
6. The command links the document to each listed part through `product.product.linkeddocuments`. The write is Many2many `(4, doc_id)`. This is the same path as the CAD document links. The command does not call `plm.component.document.rel.create` in a direct way.

Rules (same as CAD document upload):

- The default mode is a dry run.
- No write occurs without `--apply`.
- A second run with the same ADR code and revision updates the same record.
- The command does not create a second document.
- If the document or a target part is not in `draft`, the command reports `skip-locked`.
- The command does not change that record.
- The command never calls `action_confirm`, `action_release` or `new_version`.
- Do not put credentials in the repository.

The text of an ADR uses SI with a space (example: `12 mm`, `100 Hz`, `24 V`).

- `cad/freecad/plm_upload_macro.py` is the same command from FreeCAD 1.x.
- The command also runs on macOS.
- The macro exports the active solid to STEP.
- The macro exports the TechDraw page to PDF when the document has one.
- The macro calls `plm-sync --part`.
- The macro stays in a dry run until `APPLY` in the macro or `VIBROCORE_PLM_APPLY=1`.
- The part number must be in the document name or in the label of the solid (`VC-SH-1301`).
- The macro uses `VIBROCORE_PYTHON` or `python3` on `PATH`.
- FreeCAD has an interpreter that does not have the dependencies of this repository.
- `cad/freecad/make_plate.py` is still the local script for the plate.
- The script does not log in.
- The workflow `.github/workflows/cad-plm-sync.yml` is a GitHub Actions workflow.
- A person must start it by hand (`workflow_dispatch`).
- The apply input is false by default.
- The workflow reads `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_API_KEY` and `ODOO_PASSWORD` from repository secrets.
- A normal push does not call Odoo.
- CI does not start `tests/test_plm_sync_integration.py` unless `ODOO_PLM_INTEGRATION=1`.
- Point the test at a disposable database if you want the real server in the loop.
- CI runs the mocked tests in `tests/test_plm_sync.py`.

## 7. Decisions still owed by engineering

These items change the BOM.
Put them in the YAML before the next import.
Do not edit them in silence in Odoo.

- There is no 48 V rail.
- Do not order SDR-480-48 or SDR-75-48.
- VC-PW-5310 is the dedicated SDR-120-24 for the control supply of the S200 and for the brake.
- VC-PW-5320 is an open 24 V slot.
- The slot is the size of SDR-480-24.
- Freeze the catalogue numbers for the VFD and the stepper driver.
- Also freeze the numbers for the coupler and the brake and the isolator.
- The YAML lists the candidates and does not pick one where the source document does not.
- Motor pitch is only "at least 170 mm".
- The isolator coordinates are unknown.
- The flange thickness is unknown.
- The PCD is unknown.
- The carriage size is unknown.
- The shaft length is unknown.
- The DT325 thread is unknown.
- The model has no holes.
- `VC-CT-6300` no longer uses 200 x 150 x 80 mm.
- The order code is still unknown.
- The VFD size is unknown.
- `VC-CT-6410` is obsolete.
- The SE050 breakout stays in `VC-CT-6400`.
- Decide if the WLAN bridge and the ESP32-C3 wallet are one board.
- The choice is Instagrid rental or the EUR 2500 purchase line.
- Map `purchase_ok` and the shop routes onto the real warehouse.
- The routes are not in the CSV.
- The id `mrp.route_warehouse0_manufacture` depends on the warehouse xml id of that database.
- Fastener kits stay as kits.
- Buy the kits as kits or replace the lines.
- We removed the duplicate GPS rows from BOM.md section 7.
- The subtotals for the scanner now follow the YAML rollups.
- The subtotals for the control now follow the YAML rollups.
- Option A or Option B (RevPi) stays the commercial choice.
- RevPi parts stay `lifecycle: alternative`.
- Those parts are not on the control BOM for Option A.

`cad/OPEN_POINTS.md` is the list that the tool generates for each `unknowns` entry.
