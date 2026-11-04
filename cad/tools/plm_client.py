"""Open client for the OdooPLM server API.

Verified against OmniaGit/odooplm 19.0 commit
b9db89248c206fd61bd38191d7a5289c58ce8a54 (plm/controllers/main.py,
class UploadDocument) and against Odoo 19.0 commit
a81f10aaedb8eed773c32a6e0a1bd6d975f9ee72 (odoo/service/common.py,
odoo/http.py, odoo/addons/base/models/res_users.py).

The CAD client's file routes do not create products or documents. They write
bytes onto an ir.attachment that already has is_plm set:

- GET  /plm_document_upload/isalive
    auth="none". Body "True".
- POST /plm_document_upload/login
    form fields login, password, and optional db.
    auth="none", csrf=False.
    Calls request.session.authenticate(request.env, {"type": "password",
    "login": login, "password": password}). Session.authenticate passes
    interactive=True, and res.users._check_credentials accepts an API key
    only when interactive is false. A password works here. An API key does
    not. Success is HTTP 200 with an empty body, a session cookie and
    X-CSRF-TOKEN. The upload routes set csrf=False, so the token is recorded
    and not sent back. A database that is not request.db raises, and the
    route's webservice wrapper turns that into HTTP 500.
- POST /plm_document_upload/upload
    auth="user". Multipart fields mod_file (the bytes), filename, and
    doc_id. doc_id is json.loads'd, so the text "123" becomes the integer
    123. Writes ir.attachment.datas and name. 400 when the id is missing or
    is not a PLM document. hostname and hostpws are left empty on purpose:
    setupCadOpen records a CAD session only when both are set.
- POST /plm_document_upload/upload_pdf
    auth="user". Multipart fields file_stream and doc_id (same JSON rule).
    Writes ir.attachment.printout.

Products, the document row, the component link and the engineering BOM are
not on those routes. They go through JSON-RPC /jsonrpc, service "object",
method execute_kw. common.authenticate(db, login, password, {}) is
exp_authenticate, which calls res.users.authenticate with interactive=False,
so either the account password or an RPC API key is accepted there.
"""

from __future__ import annotations

import json
import uuid
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.cookiejar import CookieJar

ODOOPLM_COMMIT = "b9db89248c206fd61bd38191d7a5289c58ce8a54"
ODOO_COMMIT = "a81f10aaedb8eed773c32a6e0a1bd6d975f9ee72"

# Never call a workflow method. Draft stays draft.
ALLOWED_METHODS = frozenset({"fields_get", "search", "search_read", "read", "create", "write", "unlink"})
REFUSED_METHODS = frozenset(
    {
        "action_confirm",
        "action_release",
        "new_version",
        "action_create_normalBom_WF",
        "_create_normalBom",
        "button_confirm",
    }
)


class PlmError(RuntimeError):
    pass


@dataclass(frozen=True)
class PlmConfig:
    url: str
    database: str
    user: str
    rpc_secret: str
    rest_secret: str
    rpc_secret_kind: str
    rest_secret_kind: str

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "PlmConfig | None":
        """Read connection settings. None when the variables are not all set.

        ODOO_API_KEY is preferred for JSON-RPC. ODOO_PASSWORD is preferred for
        /plm_document_upload/login, because that route is an interactive
        session and does not accept an API key. One secret may fill both
        roles when the other variable is empty; the upload then fails with
        an explanation if that secret is an API key.
        """
        import os

        source = env if env is not None else os.environ
        url = (source.get("ODOO_URL") or "").strip().rstrip("/")
        database = (source.get("ODOO_DB") or "").strip()
        user = (source.get("ODOO_USER") or "").strip()
        api_key = (source.get("ODOO_API_KEY") or "").strip()
        password = (source.get("ODOO_PASSWORD") or "").strip()
        if not (url and database and user and (api_key or password)):
            return None
        if api_key:
            rpc_secret, rpc_kind = api_key, "ODOO_API_KEY"
        else:
            rpc_secret, rpc_kind = password, "ODOO_PASSWORD"
        if password:
            rest_secret, rest_kind = password, "ODOO_PASSWORD"
        else:
            rest_secret, rest_kind = api_key, "ODOO_API_KEY"
        return cls(url, database, user, rpc_secret, rest_secret, rpc_kind, rest_kind)

    def missing_message(self) -> str:
        return (
            "plm-sync --apply needs ODOO_URL, ODOO_DB, ODOO_USER and "
            "ODOO_API_KEY or ODOO_PASSWORD in the environment. "
            "Nothing was written."
        )


class PlmClient:
    def __init__(self, config: PlmConfig, timeout: float = 120.0):
        self.config = config
        self.timeout = timeout
        self.uid: int | None = None
        self.csrf_token: str | None = None
        self._jar = CookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._jar))
        self._rpc_id = 0

    def isalive(self) -> None:
        status, body, _headers = self._request("GET", "/plm_document_upload/isalive")
        if status != 200 or body.strip() != b"True":
            raise PlmError(
                f"GET /plm_document_upload/isalive returned {status}: {body[:200]!r}"
            )

    def authenticate(self) -> int:
        """JSON-RPC common.authenticate. Does not log the secret."""
        result = self._jsonrpc(
            "common",
            "authenticate",
            [self.config.database, self.config.user, self.config.rpc_secret, {}],
        )
        if not result:
            raise PlmError(
                "JSON-RPC common.authenticate was refused for "
                f"{self.config.user} on database {self.config.database}."
            )
        self.uid = int(result)
        return self.uid

    def login_upload(self) -> None:
        """POST /plm_document_upload/login. Call this before any create."""
        form = urllib.parse.urlencode(
            {
                "login": self.config.user,
                "password": self.config.rest_secret,
                "db": self.config.database,
            }
        ).encode("utf-8")
        status, body, headers = self._request(
            "POST",
            "/plm_document_upload/login",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if status == 401 or status >= 400:
            hint = ""
            if self.config.rest_secret_kind == "ODOO_API_KEY":
                hint = (
                    " /plm_document_upload/login calls Session.authenticate with "
                    "interactive=True (Odoo odoo/http.py). An API key is accepted "
                    "only for non-interactive RPC (res.users._check_credentials). "
                    "Set ODOO_PASSWORD for the file upload. JSON-RPC can keep "
                    "using ODOO_API_KEY."
                )
            raise PlmError(
                f"POST /plm_document_upload/login returned {status}: {body[:300]!r}.{hint}"
            )
        if not _has_session_cookie(self._jar):
            raise PlmError(
                "POST /plm_document_upload/login returned 200 without a session_id cookie."
            )
        self.csrf_token = headers.get("X-CSRF-TOKEN") or headers.get("X-Csrf-Token")

    def execute(self, model: str, method: str, args: list, kwargs: dict | None = None):
        if method in REFUSED_METHODS or method not in ALLOWED_METHODS:
            raise PlmError(
                f"Refusing {model}.{method}. plm-sync does not confirm, release or revise."
            )
        if self.uid is None:
            raise PlmError("authenticate() before execute().")
        payload_args = [
            self.config.database,
            self.uid,
            self.config.rpc_secret,
            model,
            method,
            args,
            kwargs or {},
        ]
        return self._jsonrpc("object", "execute_kw", payload_args)

    def upload_datas(self, document_id: int, filename: str, content: bytes) -> None:
        """POST /plm_document_upload/upload. doc_id is a JSON integer."""
        self._upload(
            "/plm_document_upload/upload",
            fields={"doc_id": str(int(document_id)), "filename": filename},
            files={"mod_file": (filename, content, "application/octet-stream")},
        )

    def upload_printout(self, document_id: int, filename: str, content: bytes) -> None:
        """POST /plm_document_upload/upload_pdf. Writes ir.attachment.printout."""
        self._upload(
            "/plm_document_upload/upload_pdf",
            fields={"doc_id": str(int(document_id))},
            files={"file_stream": (filename, content, "application/pdf")},
        )

    def _upload(self, path: str, fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> None:
        if not _has_session_cookie(self._jar):
            raise PlmError(f"{path} needs the session from /plm_document_upload/login.")
        body, content_type = _encode_multipart(fields, files)
        status, response, _headers = self._request(
            "POST",
            path,
            data=body,
            headers={"Content-Type": content_type},
        )
        if status != 200:
            raise PlmError(f"POST {path} returned {status}: {response[:300]!r}")

    def _jsonrpc(self, service: str, method: str, args: list):
        self._rpc_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"service": service, "method": method, "args": args},
            "id": self._rpc_id,
        }
        status, body, _headers = self._request(
            "POST",
            "/jsonrpc",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        if status != 200:
            raise PlmError(f"JSON-RPC {service}.{method} returned HTTP {status}: {body[:300]!r}")
        try:
            decoded = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise PlmError(f"JSON-RPC {service}.{method} did not return JSON.") from exc
        if decoded.get("error"):
            error = decoded["error"]
            message = error.get("data", {}).get("message") or error.get("message") or error
            raise PlmError(f"JSON-RPC {service}.{method}: {message}")
        return decoded.get("result")

    def _request(self, method: str, path: str, data: bytes | None = None, headers: dict | None = None):
        request = urllib.request.Request(
            self.config.url + path,
            data=data,
            headers=headers or {},
            method=method,
        )
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                return response.status, response.read(), dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), dict(exc.headers.items())


def _has_session_cookie(jar: CookieJar) -> bool:
    return any(cookie.name == "session_id" and cookie.value for cookie in jar)


def _encode_multipart(fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    boundary = "----vibrocore" + uuid.uuid4().hex
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                f"{value}\r\n"
            ).encode("utf-8")
        )
    for name, (filename, content, content_type) in files.items():
        chunks.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode("utf-8")
        )
        chunks.append(content)
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"
