"""In-process stand-in for the OdooPLM routes plm-sync talks to.

The shapes match plm/controllers/main.py at OmniaGit/odooplm b9db892:
login form fields, upload multipart names, doc_id passed through json.loads,
and a JSON-RPC execute_kw object service.
"""

from __future__ import annotations

import json
import threading
import urllib.parse
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

M2O = {
    "product_tmpl_id",
    "categ_id",
    "uom_id",
    "tmp_material",
    "partner_id",
    "product_id",
    "currency_id",
    "country_id",
    "bom_id",
    "parent_id",
    "product_uom_id",
}


class FakeOdoo:
    def __init__(self):
        self.rows: dict[str, dict[int, dict]] = defaultdict(dict)
        self.seq: dict[str, int] = defaultdict(lambda: 100)
        self.calls: list[tuple[str, str]] = []
        self.http: list[str] = []
        self.uploads: list[dict] = []
        self.login_form: dict[str, str] | None = None
        self.rpc_secrets: list[str] = []
        self.auto_default_code = False
        self.fail_login = False
        self._seed()
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def _seed(self) -> None:
        self.rows["uom.uom"][1] = {"id": 1, "name": "Units"}
        self.rows["product.category"][1] = {"id": 1, "name": "All", "parent_id": False}
        self.rows["res.currency"][1] = {"id": 1, "name": "EUR"}
        seeds = [
            (1, "uom", "product_uom_unit", 1),
            (2, "product", "product_category_all", 1),
            (3, "base", "EUR", 1),
        ]
        for xml_id, module, name, res_id in seeds:
            self.rows["ir.model.data"][xml_id] = {
                "id": xml_id,
                "module": module,
                "name": name,
                "res_id": res_id,
            }

    def start(self) -> str:
        store = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                return

            def do_GET(self):
                store.http.append(self.path.split("?", 1)[0])
                if self.path.split("?", 1)[0] == "/plm_document_upload/isalive":
                    self._body(200, b"True", "text/plain")
                    return
                self._body(404, b"missing", "text/plain")

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                path = self.path.split("?", 1)[0]
                store.http.append(path)
                if path == "/plm_document_upload/login":
                    self._login(body)
                    return
                if path == "/jsonrpc":
                    self._jsonrpc(body)
                    return
                if path in ("/plm_document_upload/upload", "/plm_document_upload/upload_pdf"):
                    self._upload(path, body)
                    return
                self._body(404, b"missing", "text/plain")

            def _login(self, body: bytes):
                form = {key: values[-1] for key, values in urllib.parse.parse_qs(body.decode()).items()}
                store.login_form = form
                if store.fail_login or not form.get("password"):
                    self._body(401, b"Wrong login/password", "text/plain")
                    return
                self.send_response(200)
                self.send_header("X-CSRF-TOKEN", "test-csrf")
                self.send_header("Set-Cookie", "session_id=test-session; Path=/; HttpOnly")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def _upload(self, path: str, body: bytes):
                cookie = self.headers.get("Cookie", "")
                if "session_id=test-session" not in cookie:
                    self._body(401, b"session", "text/plain")
                    return
                fields, files = _parse_multipart(body, self.headers.get("Content-Type", ""))
                try:
                    doc_id = json.loads(fields.get("doc_id", "null"))
                except json.JSONDecodeError:
                    self._body(400, b"Failed upload", "text/plain")
                    return
                document = store.rows["ir.attachment"].get(doc_id)
                if not document or not document.get("is_plm"):
                    self._body(400, b"Failed upload", "text/plain")
                    return
                if document.get("engineering_state") not in (None, "draft"):
                    self._body(400, b"Failed upload", "text/plain")
                    return
                if path.endswith("/upload"):
                    content = files["mod_file"][1]
                    document["datas"] = content
                    document["name"] = fields.get("filename") or files["mod_file"][0]
                    store.uploads.append(
                        {
                            "path": path,
                            "doc_id": doc_id,
                            "doc_id_raw": fields.get("doc_id"),
                            "filename": fields.get("filename"),
                            "field": "mod_file",
                            "content": content,
                        }
                    )
                else:
                    content = files["file_stream"][1]
                    document["printout"] = content
                    store.uploads.append(
                        {
                            "path": path,
                            "doc_id": doc_id,
                            "doc_id_raw": fields.get("doc_id"),
                            "filename": files["file_stream"][0],
                            "field": "file_stream",
                            "content": content,
                        }
                    )
                self._body(200, b"Upload succeeded", "text/plain")

            def _jsonrpc(self, body: bytes):
                payload = json.loads(body.decode())
                params = payload["params"]
                try:
                    if params["service"] == "common" and params["method"] == "authenticate":
                        _db, _login, password, _env = params["args"]
                        store.rpc_secrets.append(password)
                        result = 2 if password else False
                    elif params["service"] == "object" and params["method"] == "execute_kw":
                        result = store.execute(*params["args"])
                    else:
                        raise RuntimeError(f"unexpected rpc {params['service']}.{params['method']}")
                    response = {"jsonrpc": "2.0", "id": payload["id"], "result": result}
                except Exception as exc:
                    response = {
                        "jsonrpc": "2.0",
                        "id": payload.get("id"),
                        "error": {"message": str(exc), "data": {"message": str(exc)}},
                    }
                raw = json.dumps(response).encode()
                self._body(200, raw, "application/json")

            def _body(self, status: int, payload: bytes, content_type: str):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        host, port = self._httpd.server_address
        return f"http://{host}:{port}"

    def stop(self) -> None:
        if self._httpd:
            self._httpd.shutdown()

    def execute(self, _db, _uid, _password, model, method, args, kwargs=None):
        kwargs = kwargs or {}
        self.calls.append((model, method))
        if method == "fields_get":
            fields = {"name": {"string": "Name"}, "engineering_code": {"string": "Code"}}
            if self.auto_default_code:
                fields["auto_default_code"] = {"string": "Automatic Internal Reference"}
            return fields
        if method == "search_read":
            return self._search_read(model, args[0], kwargs.get("fields") or [], kwargs.get("limit"))
        if method == "read":
            return [self._public(self.rows[model][int(item)], kwargs.get("fields") or []) for item in args[0]]
        if method == "create":
            return self._create(model, args[0])
        if method == "write":
            return self._write(model, args[0], args[1])
        if method == "unlink":
            for item in args[0]:
                del self.rows[model][int(item)]
            return True
        if method == "search":
            return [row["id"] for row in self._matching(model, args[0])]
        raise RuntimeError(f"refused or unknown {model}.{method}")

    def _matching(self, model, domain):
        found = []
        for row in self.rows[model].values():
            if _domain_ok(row, domain):
                found.append(row)
        return found

    def _search_read(self, model, domain, fields, limit):
        rows = self._matching(model, domain)
        if limit:
            rows = rows[: int(limit)]
        return [self._public(row, fields) for row in rows]

    def _public(self, row, fields):
        keys = fields or list(row)
        out = {}
        for key in keys:
            value = row.get(key, False)
            if key in M2O and value:
                out[key] = [value, "named"]
            else:
                out[key] = False if value is None else value
        return out

    def _create(self, model, vals):
        if vals.get("engineering_state") not in (None, "draft"):
            raise RuntimeError("create refused a non-draft engineering_state")
        self.seq[model] += 1
        record_id = self.seq[model]
        row = {"id": record_id}
        row.update(vals)
        if model == "product.product":
            row.setdefault("engineering_state", "draft")
            row["product_tmpl_id"] = record_id + 1000
        if model == "ir.attachment":
            row.setdefault("engineering_state", "draft")
        self.rows[model][record_id] = row
        return record_id

    def _write(self, model, ids, vals):
        if "engineering_state" in vals:
            raise RuntimeError("write of engineering_state is refused")
        for item in ids:
            row = self.rows[model][int(item)]
            if row.get("engineering_state") not in (None, "draft"):
                raise RuntimeError(f"write refused on {model} {item} in state {row.get('engineering_state')}")
            row.update(vals)
        return True

    def records(self, model):
        return list(self.rows[model].values())


def _domain_ok(row, domain) -> bool:
    for term in domain:
        field, operator, expected = term
        have = row.get(field, False)
        if isinstance(have, list):
            have = have[0]
        if have is None:
            have = False
        if operator == "=":
            if have != expected and not (have is False and expected is False):
                return False
        elif operator == "!=":
            if have == expected:
                return False
        else:
            raise RuntimeError(f"domain operator {operator}")
    return True


def _parse_multipart(body: bytes, content_type: str):
    marker = ""
    for piece in content_type.split(";"):
        piece = piece.strip()
        if piece.startswith("boundary="):
            marker = piece.split("=", 1)[1].strip('"')
    if not marker:
        raise RuntimeError("missing multipart boundary")
    fields: dict[str, str] = {}
    files: dict[str, tuple[str, bytes]] = {}
    for chunk in body.split(("--" + marker).encode()):
        if chunk in (b"", b"--", b"--\r\n", b"\r\n"):
            continue
        if chunk.startswith(b"\r\n"):
            chunk = chunk[2:]
        if chunk.endswith(b"\r\n"):
            chunk = chunk[:-2]
        if chunk.endswith(b"--"):
            chunk = chunk[:-2]
        header_blob, _, content = chunk.partition(b"\r\n\r\n")
        header = header_blob.decode("utf-8", errors="replace")
        name = ""
        filename = ""
        for part in header.split(";"):
            part = part.strip()
            if part.startswith("name="):
                name = part.split("=", 1)[1].strip('"')
            elif part.startswith("filename="):
                filename = part.split("=", 1)[1].strip('"')
        if filename:
            files[name] = (filename, content)
        else:
            fields[name] = content.decode("utf-8")
    return fields, files
