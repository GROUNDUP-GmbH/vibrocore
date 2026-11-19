"""ADR discovery and PDF materialization."""

from pathlib import Path

from cad.tools.adr import load_adrs, parse_adr, render_adr_pdf


def test_adr_0001_lists_control_parts():
    docs = load_adrs()
    assert len(docs) >= 1
    adr = next(doc for doc in docs if doc.code == "ADR-0001")
    assert adr.parts == ("VC-CT-6100", "VC-CT-6110", "VC-CT-6120", "VC-ASM-5000")
    assert adr.rendered_as == "pdf"
    assert adr.attachment_path.is_file()
    assert adr.attachment_path.read_bytes().startswith(b"%PDF")


def test_render_adr_pdf_includes_title(tmp_path: Path):
    source = tmp_path / "ADR-9999-test.md"
    source.write_text(
        "---\ntitle: Test ADR\nstatus: Proposed\nparts:\n  - VC-CT-6100\n---\n\nBody line.\n",
        encoding="utf-8",
    )
    adr = parse_adr(source)
    pdf = render_adr_pdf(adr)
    assert pdf.startswith(b"%PDF")
    assert b"ADR-9999" in pdf
    assert b"Test ADR" in pdf
