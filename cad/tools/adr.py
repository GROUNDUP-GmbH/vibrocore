"""Discover Architecture Decision Records and build PLM document payloads.

ADRs live in docs/adr/*.md with YAML front matter. The `parts` list names the
VC-… engineering codes that must receive the ADR as a linked document.

PDF rendering uses the same minimal PDF writer as cad/tools/drawings.py
(Helvetica text on an A4 page). No weasyprint/pandoc dependency is added.
If that writer cannot run, the Markdown file is attached as-is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from cad.tools.bom import ROOT

ADR_DIR = ROOT / "docs" / "adr"
ADR_EXPORT_DIR = ROOT / "cad" / "export" / "adr"
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)
ADR_CODE_RE = re.compile(r"^ADR-\d{4}$")


@dataclass(frozen=True)
class AdrDocument:
    code: str
    title: str
    status: str
    parts: tuple[str, ...]
    source_path: Path
    body: str
    attachment_path: Path
    attachment_filename: str
    rendered_as: str  # "pdf" or "markdown"


def list_adr_paths(directory: Path | None = None) -> list[Path]:
    directory = directory or ADR_DIR
    if not directory.is_dir():
        return []
    return sorted(directory.glob("ADR-*.md"))


def parse_adr(path: Path) -> AdrDocument:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: missing YAML front matter")
    meta = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    code = str(meta.get("id") or path.stem.split("-")[0] + "-" + path.stem.split("-")[1])
    # Prefer filename ADR-0001-... → ADR-0001
    stem_match = re.match(r"(ADR-\d{4})", path.stem)
    if stem_match:
        code = stem_match.group(1)
    if not ADR_CODE_RE.match(code):
        raise ValueError(f"{path}: invalid ADR code {code!r}")
    title = str(meta.get("title") or path.stem)
    status = str(meta.get("status") or "Proposed")
    parts = meta.get("parts") or []
    if not isinstance(parts, list) or not parts:
        raise ValueError(f"{path}: front matter must list parts: [VC-…]")
    part_tuple = tuple(str(item) for item in parts)
    pdf_name = f"{code}.pdf"
    pdf_path = ADR_EXPORT_DIR / pdf_name
    return AdrDocument(
        code=code,
        title=title,
        status=status,
        parts=part_tuple,
        source_path=path,
        body=body,
        attachment_path=pdf_path,
        attachment_filename=pdf_name,
        rendered_as="pdf",
    )


def _pdf_escape(text: str) -> str:
    encoded = text.encode("latin-1", errors="replace").decode("latin-1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def render_adr_pdf(adr: AdrDocument) -> bytes:
    """Minimal multi-page-capable single-page A4 PDF of the ADR text."""
    lines = [
        adr.code,
        adr.title,
        f"Status: {adr.status}",
        "Parts: " + ", ".join(adr.parts),
        "",
    ]
    for raw in adr.body.splitlines():
        row = raw.rstrip()
        if len(row) <= 95:
            lines.append(row)
        else:
            while row:
                lines.append(row[:95])
                row = row[95:]
        if len(lines) > 90:
            lines.append("… truncated for PLM text PDF; full Markdown is in git.")
            break
    commands = ["BT", "/F1 10 Tf", "40 800 Td", "12 TL"]
    for row in lines:
        commands.append(f"({_pdf_escape(row)}) Tj")
        commands.append("T*")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(output)


def materialize_adr(adr: AdrDocument) -> AdrDocument:
    """Write the ADR attachment bytes under cad/export/adr/."""
    ADR_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        pdf = render_adr_pdf(adr)
        adr.attachment_path.write_bytes(pdf)
        return adr
    except Exception:
        # Fallback documented in ODOOPLM.md: attach Markdown as-is.
        md_path = ADR_EXPORT_DIR / f"{adr.code}.md"
        md_path.write_text(
            adr.source_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        return AdrDocument(
            code=adr.code,
            title=adr.title,
            status=adr.status,
            parts=adr.parts,
            source_path=adr.source_path,
            body=adr.body,
            attachment_path=md_path,
            attachment_filename=md_path.name,
            rendered_as="markdown",
        )


def load_adrs(directory: Path | None = None) -> list[AdrDocument]:
    docs = []
    for path in list_adr_paths(directory):
        docs.append(materialize_adr(parse_adr(path)))
    return docs
