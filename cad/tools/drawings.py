"""ISO drawing sheets as SVG and a small PDF, generated from the BOM.

Sheets follow ISO 7200 (title block), ISO 5457 (A3 landscape frame, simplified)
and ISO 128 (first-angle projection). Only dimensions present in the BOM are
drawn. Everything else is written as TODO, not as a fake dimension.
"""

from __future__ import annotations

from pathlib import Path

from cad.tools.bom import ROOT, BillOfMaterials, Part

SVG_DIR = ROOT / "cad" / "drawings"
PDF_DIR = ROOT / "cad" / "export" / "pdf"

SHEET_W = 420.0
SHEET_H = 297.0


def _slug(name: str) -> str:
    cleaned = []
    for char in name.lower():
        cleaned.append(char if char.isalnum() else "-")
    slug = "".join(cleaned).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug


def drawing_stem(part: Part) -> str:
    return f"{part.part_number}_{_slug(part.name)}"


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _title_block(part: Part, bom: BillOfMaterials, document_type: str) -> str:
    meta = bom.meta
    rows = [
        ("Legal owner", meta["owner"]),
        ("Document title", part.name),
        ("Document type", document_type),
        ("Document status", "preliminary"),
        ("Identification number", part.part_number),
        ("Revision index / letter", f"{part.revision_index} / {part.revision_letter}"),
        ("Creator", "vibrocore cad export"),
        ("Created", meta["cad_baseline_date"]),
        ("Units", "mm"),
        ("Projection", "first angle (ISO 128)"),
        ("Sheet", "1 / 1"),
    ]
    lines = []
    y = 274
    for label, value in rows:
        lines.append(
            f'<text x="268" y="{y}" font-size="2.4" font-family="sans-serif">{_esc(label)}</text>'
        )
        lines.append(
            f'<text x="332" y="{y}" font-size="2.6" font-family="sans-serif" font-weight="700">{_esc(str(value))}</text>'
        )
        y += 4.2
    return "\n".join(lines)


def _frame() -> str:
    return """
<rect x="10" y="10" width="400" height="277" fill="none" stroke="#111" stroke-width="0.6"/>
<rect x="14" y="14" width="392" height="269" fill="none" stroke="#111" stroke-width="0.25"/>
<rect x="262" y="248" width="144" height="35" fill="none" stroke="#111" stroke-width="0.4"/>
<text x="18" y="22" font-size="3.2" font-family="sans-serif">ISO 7200 title block · ISO 5457 A3 · not released for manufacture</text>
""".strip()


def _notes(part: Part) -> str:
    items = []
    if part.geometry:
        items.append(f"Fidelity: {part.geometry['fidelity']}. Source: {part.geometry['source']}.")
    if part.material:
        items.append(f"Material (engineering_material): {part.material}.")
    if part.mass_kg is not None:
        items.append(f"Mass: {part.mass_kg} kg. {part.mass_note or ''}".strip())
    items.extend(f"TODO: {item}" for item in part.unknowns)
    if part.notes:
        items.append(part.notes)
    items.append("General tolerances: TODO. No tolerance class is specified in the design documents.")
    lines = []
    y = 40
    for item in items:
        lines.append(
            f'<text x="20" y="{y}" font-size="3" font-family="sans-serif">{_esc(item[:140])}</text>'
        )
        y += 4.5
        if y > 230:
            break
    return "\n".join(lines)


def _box_views(part: Part) -> str:
    geometry = part.geometry
    length = float(geometry["length_mm"])
    width = float(geometry["width_mm"])
    height = float(geometry["height_mm"])
    scale = min(90 / length, 70 / width, 70 / height)
    top_w, top_h = length * scale, width * scale
    front_w, front_h = length * scale, height * scale
    return f"""
<text x="20" y="118" font-size="3.2" font-family="sans-serif">Top view (X–Y), scale fitted</text>
<rect x="30" y="{130}" width="{top_w:.2f}" height="{top_h:.2f}" fill="none" stroke="#111" stroke-width="0.5"/>
<text x="30" y="{128 + top_h + 6:.1f}" font-size="3.4" font-family="sans-serif">{length:g} mm</text>
<text x="{34 + top_w:.1f}" y="{130 + top_h / 2:.1f}" font-size="3.4" font-family="sans-serif">{width:g} mm</text>
<text x="200" y="118" font-size="3.2" font-family="sans-serif">Front view (X–Z), first angle</text>
<rect x="210" y="140" width="{front_w:.2f}" height="{front_h:.2f}" fill="none" stroke="#111" stroke-width="0.5"/>
<text x="210" y="{146 + front_h:.1f}" font-size="3.4" font-family="sans-serif">{height:g} mm thick</text>
""".strip()


def _cylinder_views(part: Part) -> str:
    geometry = part.geometry
    diameter = float(geometry["diameter_mm"])
    length = float(geometry["length_mm"])
    scale = min(80 / length, 50 / diameter)
    front_w, front_h = length * scale, diameter * scale
    radius = diameter * scale / 2
    return f"""
<text x="20" y="120" font-size="3.2" font-family="sans-serif">Front view, shaft axis horizontal</text>
<rect x="30" y="140" width="{front_w:.2f}" height="{front_h:.2f}" fill="none" stroke="#111" stroke-width="0.5"/>
<text x="30" y="{148 + front_h:.1f}" font-size="3.4" font-family="sans-serif">{length:g} mm</text>
<text x="{36 + front_w:.1f}" y="{140 + front_h / 2:.1f}" font-size="3.4" font-family="sans-serif">Ø {diameter:g} mm</text>
<text x="200" y="120" font-size="3.2" font-family="sans-serif">End view</text>
<circle cx="250" cy="{155 + radius:.1f}" r="{radius:.2f}" fill="none" stroke="#111" stroke-width="0.5"/>
""".strip()


def _bom_table(part: Part, bom: BillOfMaterials) -> str:
    lines = [
        '<text x="20" y="36" font-size="4" font-family="sans-serif" font-weight="700">Parts list (same item numbers as the OdooPLM EBOM itemnum)</text>'
    ]
    header_y = 42
    lines.append(
        f'<text x="20" y="{header_y}" font-size="2.8" font-family="sans-serif">Item  Part number   Rev  Qty  Name</text>'
    )
    y = header_y + 5
    for index, line in enumerate(bom.children(part.part_number), start=1):
        child = bom.part(line.part_number)
        qty = int(line.qty) if line.qty == int(line.qty) else line.qty
        text = f"{index:<5}  {child.part_number:<14} {child.revision_letter:<3}  {qty:<4} {child.name}"
        lines.append(
            f'<text x="20" y="{y}" font-size="2.8" font-family="sans-serif">{_esc(text[:110])}</text>'
        )
        y += 4.2
        if y > 240:
            lines.append(
                f'<text x="20" y="{y}" font-size="2.8" font-family="sans-serif">… truncated on the sheet; the CSV BOM is complete.</text>'
            )
            break
    lines.append(
        '<text x="20" y="244" font-size="3" font-family="sans-serif">Schematic only. Component positions that are not dimensioned in the design documents are not drawn.</text>'
    )
    return "\n".join(lines)


def svg_for(part: Part, bom: BillOfMaterials) -> str:
    if part.part_number in bom.assemblies:
        body = _bom_table(part, bom)
        document_type = "assembly drawing"
    elif part.geometry and part.geometry["kind"] == "box":
        body = _box_views(part) + "\n" + _notes(part)
        document_type = "part drawing"
    elif part.geometry and part.geometry["kind"] == "cylinder":
        body = _cylinder_views(part) + "\n" + _notes(part)
        document_type = "part drawing"
    else:
        raise ValueError(f"{part.part_number} has neither a BOM nor geometry")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 {SHEET_W} {SHEET_H}">
<title>{_esc(part.part_number)} {_esc(part.name)}</title>
<rect width="100%" height="100%" fill="#fff"/>
{_frame()}
{body}
{_title_block(part, bom, document_type)}
</svg>
"""


def _pdf_escape(text: str) -> str:
    encoded = text.encode("latin-1", errors="replace").decode("latin-1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_for(part: Part, bom: BillOfMaterials) -> bytes:
    """Single-page A3 PDF with the same identification block as the SVG."""
    if part.part_number in bom.assemblies:
        rows = [f"{part.part_number} {part.name}  assembly, preliminary"]
        for index, line in enumerate(bom.children(part.part_number), start=1):
            child = bom.part(line.part_number)
            rows.append(f"{index}  {child.part_number}  rev {child.revision_letter}  qty {line.qty:g}  {child.name}")
    else:
        geometry = part.geometry or {}
        rows = [
            f"{part.part_number} {part.name}",
            f"Fidelity: {geometry.get('fidelity', 'n/a')}",
            f"Source: {geometry.get('source', '')}",
        ]
        if geometry.get("kind") == "box":
            rows.append(
                f"Box {geometry['length_mm']:g} x {geometry['width_mm']:g} x {geometry['height_mm']:g} mm"
            )
        elif geometry.get("kind") == "cylinder":
            rows.append(f"Cylinder diameter {geometry['diameter_mm']:g} mm, length {geometry['length_mm']:g} mm")
        rows.extend(f"TODO: {item}" for item in part.unknowns)
    rows.extend(
        [
            f"Owner: {bom.meta['owner']}",
            "Document status: preliminary",
            f"Identification: {part.part_number}",
            f"Revision index/letter: {part.revision_index} / {part.revision_letter}",
            f"Date: {bom.meta['cad_baseline_date']}",
            "Units: mm. Projection: first angle (ISO 128).",
            "General tolerances: TODO.",
            "ISO 7200 title-block fields. Not released for manufacture.",
        ]
    )
    commands = ["BT", "/F1 11 Tf", "36 800 Td", "16 TL"]
    for row in rows:
        commands.append(f"({_pdf_escape(row[:140])}) Tj")
        commands.append("T*")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 1190.55 841.89] "
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
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def drawing_parts(bom: BillOfMaterials) -> list[Part]:
    selected = []
    for part in bom.parts.values():
        if part.geometry or part.part_number in bom.assemblies:
            selected.append(part)
    return sorted(selected, key=lambda item: item.part_number)


def export_drawings(bom: BillOfMaterials, svg_dir: Path | None = None, pdf_dir: Path | None = None) -> list[Path]:
    svg_dir = svg_dir or SVG_DIR
    pdf_dir = pdf_dir or PDF_DIR
    svg_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for part in drawing_parts(bom):
        stem = drawing_stem(part)
        svg_path = svg_dir / f"{stem}.svg"
        pdf_path = pdf_dir / f"{stem}.pdf"
        svg_path.write_text(svg_for(part, bom), encoding="utf-8")
        pdf_path.write_bytes(pdf_for(part, bom))
        written.extend((svg_path, pdf_path))
    return written
