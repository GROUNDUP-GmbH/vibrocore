"""plm-sync against a fake OdooPLM. No real Odoo process."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from cad.tools.bom import load_bom
from cad.tools.cli import main
from cad.tools.plm_client import PlmClient, PlmConfig, PlmError
from cad.tools.plm_sync import PlmSync, sync_bom
from tests.fake_odooplm import FakeOdoo

SECRET = "secret-token-should-not-leak"


@pytest.fixture()
def server():
    fake = FakeOdoo()
    url = fake.start()
    yield fake, url
    fake.stop()


def _env(url):
    return {
        "ODOO_URL": url,
        "ODOO_DB": "odooplm",
        "ODOO_USER": "admin",
        "ODOO_PASSWORD": SECRET,
        "ODOO_API_KEY": "",
    }


def _apply(url, part=None, env=None):
    source = _env(url)
    if env:
        source.update(env)
    config = PlmConfig.from_env(source)
    client = PlmClient(config)
    client.isalive()
    client.authenticate()
    client.login_upload()
    return sync_bom(client=client, dry_run=False, part_number=part)


def _codes(fake, model="product.product"):
    return {row.get("engineering_code") for row in fake.records(model)}


def test_client_refuses_workflow_methods():
    config = PlmConfig("http://127.0.0.1", "db", "user", "pw", "pw", "ODOO_PASSWORD", "ODOO_PASSWORD")
    client = PlmClient(config)
    client.uid = 1
    with pytest.raises(PlmError, match="does not confirm"):
        client.execute("product.product", "action_confirm", [[1]])
    with pytest.raises(PlmError):
        client.execute("product.product", "action_release", [[1]])
    with pytest.raises(PlmError):
        client.execute("ir.attachment", "new_version", [[1]])


def test_dry_run_sends_nothing(monkeypatch, capsys):
    for name in ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY", "ODOO_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    assert main(["plm-sync"]) == 0
    out = capsys.readouterr().out
    assert "dry-run" in out
    assert "no request sent" in out
    assert "VC-ASM-0000" in out
    assert "type=ebom" in out
    assert SECRET not in out


def test_apply_without_env_writes_nothing(monkeypatch, capsys):
    for name in ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY", "ODOO_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    assert main(["plm-sync", "--apply"]) == 1
    err = capsys.readouterr().err
    assert "Nothing was written" in err
    assert SECRET not in err


def test_unreachable_server_is_a_plm_error():
    config = PlmConfig(
        "http://127.0.0.1:1", "db", "user", "pw", "pw", "ODOO_PASSWORD", "ODOO_PASSWORD"
    )
    client = PlmClient(config, timeout=2)
    with pytest.raises(PlmError, match="Could not reach http://127.0.0.1:1"):
        client.isalive()


def test_upload_speaks_the_odooplm_routes(server):
    fake, url = server
    report = _apply(url, part="VC-SH-1301")
    text = report.text()
    assert SECRET not in text
    assert fake.login_form == {"login": "admin", "password": SECRET, "db": "odooplm"}
    assert "/plm_document_upload/isalive" in fake.http
    assert "/plm_document_upload/login" in fake.http
    products = fake.records("product.product")
    assert len(products) == 1
    product = products[0]
    assert product["engineering_code"] == "VC-SH-1301"
    assert product["engineering_revision"] == 0
    assert product["engineering_revision_letter"] == "A"
    assert product["engineering_state"] == "draft"
    assert product["default_code"] == "VC-SH-1301"
    assert product["type"] == "consu"
    documents = fake.records("ir.attachment")
    assert len(documents) == 1
    document = documents[0]
    assert document["is_plm"] is True
    assert document["engineering_state"] == "draft"
    assert document["name"] == "VC-SH-1301.step"
    assert document["datas"].startswith(b"ISO-10303-21")
    assert document["printout"].startswith(b"%PDF")
    step_upload = next(item for item in fake.uploads if item["field"] == "mod_file")
    pdf_upload = next(item for item in fake.uploads if item["field"] == "file_stream")
    assert step_upload["path"] == "/plm_document_upload/upload"
    assert json.loads(step_upload["doc_id_raw"]) == document["id"]
    assert isinstance(json.loads(step_upload["doc_id_raw"]), int)
    assert step_upload["filename"] == "VC-SH-1301.step"
    assert pdf_upload["path"] == "/plm_document_upload/upload_pdf"
    assert json.loads(pdf_upload["doc_id_raw"]) == document["id"]
    links = fake.records("plm.component.document.rel")
    assert links == [
        {
            "id": links[0]["id"],
            "component_id": product["id"],
            "document_id": document["id"],
        }
    ]
    assert not fake.records("mrp.bom")
    assert all(method not in {"action_confirm", "action_release", "new_version"} for _model, method in fake.calls)


def test_full_sync_is_idempotent_and_stays_draft(server):
    fake, url = server
    bom = load_bom()
    first = _apply(url)
    creates = [call for call in fake.calls if call[1] == "create"]
    assert creates
    assert {row["engineering_state"] for row in fake.records("product.product")} == {"draft"}
    assert {row["engineering_state"] for row in fake.records("ir.attachment")} == {"draft"}
    assert _codes(fake) == set(bom.parts)
    assert {row["type"] for row in fake.records("mrp.bom")} == {"ebom"}
    assert {row["code"] for row in fake.records("mrp.bom")} == set(bom.assemblies)
    machine = next(row for row in fake.records("product.product") if row["engineering_code"] == "VC-ASM-0000")
    bom_row = next(row for row in fake.records("mrp.bom") if row["product_id"] == machine["id"])
    child = next(row for row in fake.records("product.product") if row["engineering_code"] == "VC-ASM-1000")
    extra = fake._create(
        "mrp.bom.line",
        {"bom_id": bom_row["id"], "product_id": child["id"] + 9, "product_qty": 4.0, "itemnum": 99, "itemlbl": "99"},
    )
    calls_after_first = len(creates)
    uploads_after_first = len(fake.uploads)
    second = _apply(url)
    creates_second = [call for call in fake.calls if call[1] == "create"]
    assert len(creates_second) == calls_after_first
    assert len(fake.records("product.product")) == len(bom.parts)
    assert len(fake.records("ir.attachment")) == len({row["engineering_code"] for row in fake.records("ir.attachment")})
    assert all(row["id"] != extra for row in fake.records("mrp.bom.line"))
    assert len(fake.uploads) == uploads_after_first
    assert "upload" not in {action.op for action in second.actions}
    assert "create" not in {action.op for action in second.actions}
    assert "skip-locked" not in {action.op for action in first.actions}
    assert all(method not in {"action_confirm", "action_release", "new_version"} for _model, method in fake.calls)


def test_a_released_part_is_not_rewritten(server):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    product = fake.records("product.product")[0]
    document = fake.records("ir.attachment")[0]
    product["engineering_state"] = "released"
    product["name"] = "FROZEN"
    document["engineering_state"] = "released"
    frozen_datas = document["datas"]
    uploads = len(fake.uploads)
    report = _apply(url, part="VC-SH-1301")
    assert product["name"] == "FROZEN"
    assert document["datas"] == frozen_datas
    assert len(fake.uploads) == uploads
    assert any(action.op == "skip-locked" and action.model == "product.product" for action in report.actions)
    assert len(fake.records("product.product")) == 1


def test_assembly_sync_creates_one_ebom_and_its_components(server):
    fake, url = server
    bom = load_bom()
    children = {line.part_number for line in bom.children("VC-ASM-1000")}
    _apply(url, part="VC-ASM-1000")
    assert _codes(fake) == children | {"VC-ASM-1000"}
    assert "VC-ASM-0000" not in _codes(fake)
    eboms = fake.records("mrp.bom")
    assert len(eboms) == 1 and eboms[0]["type"] == "ebom" and eboms[0]["code"] == "VC-ASM-1000"
    lines = fake.records("mrp.bom.line")
    assert len(lines) == len(children)
    assert [line["itemnum"] for line in sorted(lines, key=lambda item: item["itemnum"])] == list(range(1, len(children) + 1))
    assert {line["itemlbl"] for line in lines} == {str(number) for number in range(1, len(children) + 1)}


def test_auto_internalref_is_turned_off_when_the_field_exists(server):
    fake, url = server
    fake.auto_default_code = True
    _apply(url, part="VC-CT-6610")
    product = fake.records("product.product")[0]
    assert product["default_code"] == "VC-CT-6610"
    assert product["auto_default_code"] is False
    assert product["type"] == "service"
    assert product["is_storable"] is False


def test_api_key_is_used_for_rpc_and_password_for_the_upload_route(server, monkeypatch):
    fake, url = server
    monkeypatch.setenv("ODOO_URL", url)
    monkeypatch.setenv("ODOO_DB", "odooplm")
    monkeypatch.setenv("ODOO_USER", "admin")
    monkeypatch.setenv("ODOO_API_KEY", "rpc-key-not-for-login")
    monkeypatch.setenv("ODOO_PASSWORD", SECRET)
    assert main(["plm-sync", "--part", "VC-SH-1400", "--apply"]) == 0
    assert fake.login_form["password"] == SECRET
    assert fake.rpc_secrets[0] == "rpc-key-not-for-login"


def test_step_override_is_the_uploaded_datas(server, tmp_path: Path):
    fake, url = server
    step = tmp_path / "VC-SH-1301.step"
    step.write_bytes(b"ISO-10303-21;\nfrom-freecad;\n")
    pdf = tmp_path / "plate.pdf"
    pdf.write_bytes(b"%PDF-1.4\nfreedcad\n")
    config = PlmConfig.from_env(_env(url))
    client = PlmClient(config)
    client.isalive()
    client.authenticate()
    client.login_upload()
    sync_bom(client=client, dry_run=False, part_number="VC-SH-1301", step_path=step, pdf_path=pdf)
    document = fake.records("ir.attachment")[0]
    assert document["datas"] == step.read_bytes()
    assert document["printout"] == pdf.read_bytes()
    assert document["name"] == "VC-SH-1301.step"


def test_freecad_macro_builds_a_dry_run_command():
    path = Path(__file__).resolve().parents[1] / "cad" / "freecad" / "plm_upload_macro.py"
    spec = importlib.util.spec_from_file_location("plm_upload_macro", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    command = module.build_sync_command(
        "python3",
        "VC-SH-1301",
        Path("/tmp/VC-SH-1301.step"),
        Path("/tmp/VC-SH-1301.pdf"),
        False,
    )
    assert command[:4] == ["python3", "-m", "cad.tools.cli", "plm-sync"]
    assert "--apply" not in command
    assert command[command.index("--part") + 1] == "VC-SH-1301"
    assert module.part_number_from_text("plate VC-SH-1301 blank") == "VC-SH-1301"
    applied = module.build_sync_command("python3", "VC-SH-1301", Path("a.step"), None, True)
    assert applied[-1] == "--apply"
    assert "--pdf" not in applied


def test_online_dry_run_does_not_create(server):
    fake, url = server
    config = PlmConfig.from_env(_env(url))
    client = PlmClient(config)
    client.authenticate()
    report = sync_bom(client=client, dry_run=True, part_number="VC-SH-1301")
    assert not fake.records("product.product")
    assert not fake.uploads
    assert "/plm_document_upload/login" not in fake.http
    assert any(action.op == "create" and action.model == "product.product" for action in report.actions)
    text = report.text()
    assert "dry-run" in text
    assert "upload=2" in text
    uploads = [action for action in report.actions if action.op == "upload"]
    assert len(uploads) == 2
    assert all("reason=new" in action.detail for action in uploads)
    assert any(action.model == "/plm_document_upload/upload" for action in uploads)
    assert any(action.model == "/plm_document_upload/upload_pdf" for action in uploads)
    assert SECRET not in text


def _connect(url, login=False):
    config = PlmConfig.from_env(_env(url))
    client = PlmClient(config)
    client.authenticate()
    if login:
        client.isalive()
        client.login_upload()
    return client


def test_unchanged_file_is_not_uploaded(server):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    document = fake.records("ir.attachment")[0]
    assert document["checksum"] == hashlib.sha1(document["datas"]).hexdigest()
    uploads = len(fake.uploads)
    http = len(fake.http)
    calls = len(fake.calls)
    # The stored checksum is enough. Empty datas must not cause another upload.
    document["datas"] = b""
    dry = sync_bom(client=_connect(url), dry_run=True, part_number="VC-SH-1301")
    assert document["datas"] == b""
    assert not fake.uploads[uploads:]
    assert not any(action.op == "upload" for action in dry.actions)
    assert "upload=" not in dry.text()
    assert {method for _model, method in fake.calls[calls:]} <= {"fields_get", "search_read", "read", "search"}
    assert all(
        path not in {"/plm_document_upload/upload", "/plm_document_upload/upload_pdf"}
        for path in fake.http[http:]
    )
    document["datas"] = (Path(__file__).resolve().parents[1] / "cad/export/step/VC-SH-1301.step").read_bytes()
    second = _apply(url, part="VC-SH-1301")
    assert len(fake.uploads) == uploads
    assert not any(action.op == "upload" for action in second.actions)
    assert "upload=" not in second.text()


def test_changed_file_is_uploaded(server, tmp_path: Path):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    uploads = len(fake.uploads)
    step = tmp_path / "VC-SH-1301.step"
    step.write_bytes(b"ISO-10303-21;\nchanged-step;\n")
    dry = sync_bom(
        client=_connect(url),
        dry_run=True,
        part_number="VC-SH-1301",
        step_path=step,
    )
    assert len(fake.uploads) == uploads
    planned = [action for action in dry.actions if action.op == "upload"]
    assert len(planned) == 1
    assert planned[0].model == "/plm_document_upload/upload"
    assert "VC-SH-1301.step" in planned[0].detail
    assert "reason=changed" in planned[0].detail
    assert "upload=1" in dry.text()
    assert "reason=new" not in dry.text()
    applied = sync_bom(
        client=_connect(url, login=True),
        dry_run=False,
        part_number="VC-SH-1301",
        step_path=step,
    )
    new_uploads = fake.uploads[uploads:]
    assert len(new_uploads) == 1
    assert new_uploads[0]["field"] == "mod_file"
    assert new_uploads[0]["content"] == step.read_bytes()
    sent = [action for action in applied.actions if action.op == "upload"]
    assert len(sent) == 1
    assert "reason=changed" in sent[0].detail
    assert sent[0].model == "/plm_document_upload/upload"


def test_printout_checksum_skips_unchanged_pdf(server, tmp_path: Path):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    document = next(row for row in fake.records("ir.attachment") if row.get("is_plm"))
    pdf = document["printout"]
    fake._store_printout(document, pdf)
    document["printout"] = b""
    uploads = len(fake.uploads)
    reads = len(fake.binary_reads)
    report = _apply(url, part="VC-SH-1301")
    assert len(fake.uploads) == uploads
    assert not any(action.op == "upload" for action in report.actions)
    assert document["printout"] == b""
    assert not [item for item in fake.binary_reads[reads:] if item[0] == "printout" and not item[1]]
    changed = tmp_path / "plate.pdf"
    changed.write_bytes(b"%PDF-1.4\nchanged-printout\n")
    dry = sync_bom(
        client=_connect(url),
        dry_run=True,
        part_number="VC-SH-1301",
        pdf_path=changed,
    )
    planned = [action for action in dry.actions if action.op == "upload"]
    assert len(planned) == 1
    assert planned[0].model == "/plm_document_upload/upload_pdf"
    assert "reason=changed" in planned[0].detail
    assert "upload=1" in dry.text()


def _wipe_checksum(fake, document, datas=None, printout=None):
    """OdooPLM 19.0 shape: checksum False, file_size 0, bytes still stored."""
    if datas is not None:
        document["datas"] = datas
    if printout is not None:
        document["printout"] = printout
    document["checksum"] = False
    document["file_size"] = 0
    fake._create(
        "ir.attachment",
        {
            "name": "printout",
            "res_model": "ir.attachment",
            "res_field": "printout",
            "res_id": document["id"],
            "checksum": False,
            "file_size": 0,
            "datas": document.get("printout") or b"",
            "type": "binary",
        },
    )


def test_empty_checksum_same_bytes_is_not_uploaded(server):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    document = next(row for row in fake.records("ir.attachment") if row.get("is_plm"))
    _wipe_checksum(fake, document)
    uploads = len(fake.uploads)
    calls = len(fake.calls)
    before_reads = len(fake.read_calls)
    dry = sync_bom(client=_connect(url), dry_run=True, part_number="VC-SH-1301")
    assert len(fake.uploads) == uploads
    assert not any(action.op == "upload" for action in dry.actions)
    assert "upload=" not in dry.text()
    assert {method for _model, method in fake.calls[calls:]} <= {"fields_get", "search_read", "read", "search"}
    fresh = fake.read_calls[before_reads:]
    assert any("datas" in call["fields"] and not call["bin_size"] for call in fresh)
    assert any("printout" in call["fields"] and not call["bin_size"] for call in fresh)
    applied = _apply(url, part="VC-SH-1301")
    assert len(fake.uploads) == uploads
    assert not any(action.op == "upload" for action in applied.actions)
    assert "upload=" not in applied.text()


def test_empty_checksum_different_bytes_is_uploaded(server, tmp_path: Path):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    document = next(row for row in fake.records("ir.attachment") if row.get("is_plm"))
    _wipe_checksum(fake, document)
    uploads = len(fake.uploads)
    step = tmp_path / "VC-SH-1301.step"
    step.write_bytes(b"ISO-10303-21;\nchanged-step;\n")
    pdf = tmp_path / "plate.pdf"
    pdf.write_bytes(b"%PDF-1.4\nchanged-printout\n")
    dry = sync_bom(
        client=_connect(url),
        dry_run=True,
        part_number="VC-SH-1301",
        step_path=step,
        pdf_path=pdf,
    )
    assert len(fake.uploads) == uploads
    planned = [action for action in dry.actions if action.op == "upload"]
    assert len(planned) == 2
    assert {action.model for action in planned} == {
        "/plm_document_upload/upload",
        "/plm_document_upload/upload_pdf",
    }
    assert all("reason=changed" in action.detail for action in planned)
    assert "reason=new" not in dry.text()
    assert "upload=2" in dry.text()
    applied = sync_bom(
        client=_connect(url, login=True),
        dry_run=False,
        part_number="VC-SH-1301",
        step_path=step,
        pdf_path=pdf,
    )
    sent = fake.uploads[uploads:]
    assert len(sent) == 2
    assert {item["field"] for item in sent} == {"mod_file", "file_stream"}
    assert next(item["content"] for item in sent if item["field"] == "mod_file") == step.read_bytes()
    assert next(item["content"] for item in sent if item["field"] == "file_stream") == pdf.read_bytes()
    assert all("reason=changed" in action.detail for action in applied.actions if action.op == "upload")
    assert "upload=2" in applied.text()


def test_missing_attachment_is_reason_new(server):
    fake, url = server
    calls = len(fake.calls)
    report = sync_bom(client=_connect(url), dry_run=True, part_number="VC-SH-1301")
    uploads = [action for action in report.actions if action.op == "upload"]
    assert len(uploads) == 2
    assert all("reason=new" in action.detail for action in uploads)
    assert "upload=2" in report.text()
    assert "reason=changed" not in report.text()
    assert not fake.records("ir.attachment")
    assert not fake.uploads
    assert {method for _model, method in fake.calls[calls:]} <= {"fields_get", "search_read", "read", "search"}
    assert all(
        method not in {"action_confirm", "action_release", "new_version", "create", "write", "unlink"}
        for _model, method in fake.calls
    )


def test_empty_stored_content_is_reason_new(server):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    document = next(row for row in fake.records("ir.attachment") if row.get("is_plm"))
    _wipe_checksum(fake, document, datas=b"", printout=b"")
    uploads = len(fake.uploads)
    calls = len(fake.calls)
    dry = sync_bom(client=_connect(url), dry_run=True, part_number="VC-SH-1301")
    planned = [action for action in dry.actions if action.op == "upload"]
    assert len(planned) == 2
    assert all("reason=new" in action.detail for action in planned)
    assert "upload=2" in dry.text()
    assert "reason=changed" not in dry.text()
    assert len(fake.uploads) == uploads
    assert {method for _model, method in fake.calls[calls:]} <= {"fields_get", "search_read", "read", "search"}


def test_content_reads_are_batched(server):
    fake, url = server
    payload = b"ISO-10303-21;\nbatch;\n"
    ids = []
    for index in range(3):
        ids.append(
            fake._create(
                "ir.attachment",
                {
                    "name": f"batch-{index}.step",
                    "datas": payload,
                    "checksum": False,
                    "file_size": 0,
                    "is_plm": True,
                    "engineering_code": f"BATCH-{index}",
                    "engineering_revision": 0,
                    "engineering_state": "draft",
                    "type": "binary",
                },
            )
        )
    sync = PlmSync(load_bom(), _connect(url), dry_run=True)
    before = len(fake.read_calls)
    sync._prefetch_field(ids, "datas")
    fresh = fake.read_calls[before:]
    probes = [call for call in fresh if call["bin_size"] and "datas" in call["fields"]]
    full = [call for call in fresh if not call["bin_size"] and "datas" in call["fields"]]
    assert len(probes) == 1 and set(probes[0]["ids"]) == set(ids)
    assert len(full) == 1 and set(full[0]["ids"]) == set(ids)
    digest = hashlib.sha1(payload).hexdigest()
    assert all(sync._remote_sha1[(item, "datas")] == digest for item in ids)


def test_large_printout_without_checksum_is_not_reread_when_datas_matches(server):
    fake, url = server
    _apply(url, part="VC-SH-1301")
    document = next(row for row in fake.records("ir.attachment") if row.get("is_plm"))
    storage_id = fake._create(
        "ir.attachment",
        {
            "name": "printout",
            "res_model": "ir.attachment",
            "res_field": "printout",
            "res_id": document["id"],
            "file_size": 50 * 1024 * 1024,
            "checksum": False,
            "type": "binary",
        },
    )
    assert storage_id
    uploads = len(fake.uploads)
    reads = len(fake.binary_reads)
    report = sync_bom(client=_connect(url), dry_run=True, part_number="VC-SH-1301")
    assert len(fake.uploads) == uploads
    assert not any(action.op == "upload" for action in report.actions)
    assert not [item for item in fake.binary_reads[reads:] if item[0] == "printout"]


def test_weight_within_field_digits_is_unchanged(server):
    fake, url = server
    fake.field_meta["product.product"] = {
        "weight": {"string": "Weight", "type": "float", "digits": [16, 2]},
    }
    _apply(url, part="VC-SH-1301")
    product = fake.records("product.product")[0]
    # Odoo stores Stock Weight with 2 decimals. The YAML value is 19.782 kg.
    product["weight"] = 19.78
    report = _apply(url, part="VC-SH-1301")
    assert product["weight"] == 19.78
    assert any(action.op == "unchanged" and action.model == "product.product" for action in report.actions)
    assert not any(action.op == "update" and action.model == "product.product" for action in report.actions)
    product["weight"] = 19.70
    changed = _apply(url, part="VC-SH-1301")
    assert any(action.op == "update" and action.model == "product.product" for action in changed.actions)
    assert product["weight"] == 19.78


def test_dry_run_plans_adr_links(monkeypatch, capsys):
    for name in ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY", "ODOO_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    assert main(["plm-sync"]) == 0
    out = capsys.readouterr().out
    assert "ADR-0001" in out
    assert "ADR-0001->VC-CT-6100" in out
    assert "linkeddocuments" in out
    assert SECRET not in out


def test_adr_upload_links_listed_parts(server):
    fake, url = server
    report = _apply(url, part="VC-CT-6100")
    text = report.text()
    assert SECRET not in text
    adr_docs = [
        row for row in fake.records("ir.attachment") if row.get("engineering_code") == "ADR-0001"
    ]
    assert len(adr_docs) == 1
    document = adr_docs[0]
    assert document["engineering_state"] == "draft"
    assert document["is_plm"] is True
    assert document["name"] == "ADR-0001.pdf"
    assert document["datas"].startswith(b"%PDF")
    products = {
        row["engineering_code"]: row
        for row in fake.records("product.product")
        if row["engineering_code"] in {"VC-CT-6100", "VC-CT-6110", "VC-CT-6120", "VC-ASM-5000"}
    }
    assert set(products) == {"VC-CT-6100", "VC-CT-6110", "VC-CT-6120", "VC-ASM-5000"}
    links = fake.records("plm.component.document.rel")
    linked_components = {link["component_id"] for link in links if link["document_id"] == document["id"]}
    assert linked_components == {products[code]["id"] for code in products}
    assert all(method not in {"action_confirm", "action_release", "new_version"} for _model, method in fake.calls)
    # Idempotent: second apply does not create a second ADR document.
    _apply(url, part="VC-CT-6100")
    assert len([row for row in fake.records("ir.attachment") if row.get("engineering_code") == "ADR-0001"]) == 1


def _draft_document(client, name="VC-SH-1400.step"):
    return client.execute(
        "ir.attachment",
        "create",
        [
            {
                "name": name,
                "is_plm": True,
                "engineering_code": name.split(".", 1)[0],
                "engineering_revision": 0,
                "engineering_state": "draft",
            }
        ],
    )


def test_route_success_without_bytes_is_repaired_by_read_back(server):
    """HTTP 200 and the text 'Upload succeeded' with empty datas is not success."""
    fake, url = server
    fake.upload_response = "empty"
    client = _connect(url, login=True)
    document_id = _draft_document(client)
    payload = b"ISO-10303-21;\nHEADER;\nEND-ISO-10303-21;"
    client.upload_datas(document_id, "VC-SH-1400.step", payload)
    document = fake.rows["ir.attachment"][document_id]
    assert document["datas"] == payload
    assert document["checksum"] == hashlib.sha1(payload).hexdigest()
    assert document["file_size"] == len(payload)
    assert fake.uploads[-1]["response"] == "empty"
    assert fake.uploads[-1]["content"] == payload
    pdf = b"%PDF-1.4\nrepair\n"
    client.upload_printout(document_id, "VC-SH-1400.pdf", pdf)
    assert document["printout"] == pdf


def test_route_login_page_and_redirect_do_not_count_as_stored(server):
    fake, url = server
    client = _connect(url, login=True)
    document_id = _draft_document(client, "VC-ASM-0000_vibrocore-v1.pdf")
    payload = b"%PDF-1.4\nlogin-was-not-the-file\n"
    fake.upload_response = "html"
    client.upload_printout(document_id, "VC-ASM-0000_vibrocore-v1.pdf", payload)
    assert fake.rows["ir.attachment"][document_id]["printout"] == payload
    assert "/web/login" not in fake.http

    fake.upload_response = "redirect"
    step = b"ISO-10303-21;\nredirect;\n"
    client.upload_datas(document_id, "VC-ASM-0000.step", step)
    assert fake.rows["ir.attachment"][document_id]["datas"] == step
    assert "/web/login" not in fake.http
    assert any(item.get("response") == "redirect" for item in fake.uploads)


def test_apply_exits_when_read_back_is_still_empty(server, monkeypatch, capsys):
    fake, url = server
    fake.upload_response = "empty"
    fake.block_binary_write = True
    for key, value in _env(url).items():
        monkeypatch.setenv(key, value)
    assert main(["plm-sync", "--apply", "--part", "VC-SH-1301"]) == 1
    captured = capsys.readouterr()
    assert "VC-SH-1301.step" in captured.err
    assert "datas" in captured.err
    assert "ir.attachment" in captured.err
    assert "not counted" in captured.err
    assert "upload=" not in captured.out
    document = fake.records("ir.attachment")[0]
    assert not document.get("datas")


def test_released_adr_is_not_rewritten(server):
    fake, url = server
    _apply(url, part="VC-CT-6100")
    document = next(row for row in fake.records("ir.attachment") if row.get("engineering_code") == "ADR-0001")
    document["engineering_state"] = "released"
    frozen = document["datas"]
    uploads = len(fake.uploads)
    report = _apply(url, part="VC-CT-6100")
    assert document["datas"] == frozen
    assert len(fake.uploads) == uploads
    assert any(
        action.op == "skip-locked" and action.model == "ir.attachment" and "ADR-0001" in action.key
        for action in report.actions
    )
