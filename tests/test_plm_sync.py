"""plm-sync against a fake OdooPLM. No real Odoo process."""

import importlib.util
import json
from pathlib import Path

import pytest

from cad.tools.bom import load_bom
from cad.tools.cli import main
from cad.tools.plm_client import PlmClient, PlmConfig, PlmError
from cad.tools.plm_sync import sync_bom
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
    assert len(fake.uploads) > uploads_after_first
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
    assert SECRET not in text
