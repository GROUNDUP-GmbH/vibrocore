"""A3 study sheet for the mast stack. Schematic, not a released drawing.

Vertical distances use one scale. Horizontal sizes on the sheet are schematic.
The PDF carries the same chain as the SVG, as text, in the repo PDF style.
"""

from __future__ import annotations

from cad.models.mast_layout import (
    CASING_ID_MM,
    CASING_OD_MM,
    COLUMN_SHAFT_LENGTH_MM,
    DOCUMENT_ID,
    MAST_PROFILE_LENGTH_MM,
    MOTOR_HEIGHT_MM,
    SHOE_OD_MM,
    VIBRATING_PLATE_THICKNESS_MM,
    available_mast_stroke_mm,
    chain_terms,
    deficit_vs_profile_mm,
    deficit_vs_stroke_mm,
    documented_axial_mm,
    plate_opening_mm,
    required_total_mm,
    sampling_remainder_mm,
    stations,
)

SHEET_W = 420.0
SHEET_H = 297.0
SCALE = 0.07
GROUND_Y = 248.0


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _pdf_escape(text: str) -> str:
    encoded = text.encode("latin-1", errors="replace").decode("latin-1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _y(z_mm: float) -> float:
    return GROUND_Y - z_mm * SCALE


def chain_lines() -> list[str]:
    """Text form of the dimension chain. The SVG and the PDF both use this list."""
    lines = [
        "Required height = ground clearance + shoe + casing + adapter + head + carriage + top margin.",
    ]
    for term, top in stations():
        mark = " TBD" if term.tbd else ""
        lines.append(f"{term.name}: {term.length_mm:.1f} mm{mark}. Station {top:.1f} mm. {term.detail}")
    lines.extend(
        [
            f"Required total: {required_total_mm():.1f} mm.",
            f"Available mast stroke: {available_mast_stroke_mm():.1f} mm.",
            f"Deficit against stroke: {deficit_vs_stroke_mm():.1f} mm.",
            f"Mast profile: {MAST_PROFILE_LENGTH_MM:.1f} mm. Length unchanged.",
            f"Deficit against profile: {deficit_vs_profile_mm():.1f} mm.",
            f"Documented lengths alone, TBD set to 0: {documented_axial_mm():.1f} mm.",
            f"Deficit of documented lengths against the profile: {documented_axial_mm() - MAST_PROFILE_LENGTH_MM:.1f} mm.",
            f"Plate opening assumption: {plate_opening_mm():.1f} mm. SAMPLING remainder: {sampling_remainder_mm():.1f} mm.",
            "The SAMPLING remainder is not this chain. It omits motor height, carriage, shoe, adapter and margins.",
            f"Head uses column shaft {COLUMN_SHAFT_LENGTH_MM:.0f} mm, plate {VIBRATING_PLATE_THICKNESS_MM:.0f} mm, "
            f"motor height {MOTOR_HEIGHT_MM:.0f} mm, plus the flange placeholder.",
            f"Casing OD {CASING_OD_MM:.2f} mm. Casing ID {CASING_ID_MM:.3f} mm. Shoe OD {SHOE_OD_MM:.2f} mm.",
            "Dashed segments are TBD. Do not manufacture from this sheet.",
        ]
    )
    return lines


def svg_text(owner: str, created: str) -> str:
    deficit = deficit_vs_stroke_mm()
    graphic = _graphic()
    table = _table()
    title = _title(owner, created)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 {SHEET_W} {SHEET_H}">
<title>{DOCUMENT_ID} mast stack layout</title>
<rect width="100%" height="100%" fill="#fff"/>
<rect x="10" y="10" width="400" height="277" fill="none" stroke="#111" stroke-width="0.6"/>
<rect x="14" y="14" width="392" height="269" fill="none" stroke="#111" stroke-width="0.25"/>
<text x="18" y="22" font-size="3.2" font-family="sans-serif">Study layout. Not released. Vertical scale {SCALE:g}. Horizontal sizes are schematic.</text>
<text x="18" y="32" font-size="6.5" font-family="sans-serif" font-weight="700">Deficit against stroke: {deficit:.1f} mm</text>
<text x="200" y="32" font-size="3.4" font-family="sans-serif">Required {required_total_mm():.1f} mm. Stroke {available_mast_stroke_mm():.1f} mm. Profile {MAST_PROFILE_LENGTH_MM:.0f} mm stays.</text>
{graphic}
{table}
{title}
<text x="18" y="258" font-size="2.6" font-family="sans-serif">Ground line is the baseline. The stroke bar is the 1300 mm travel, not a located zone on the profile.</text>
<text x="18" y="263" font-size="2.6" font-family="sans-serif">Split carrier is inside the casing. Its length is a tube placeholder and is not in the sum.</text>
</svg>
"""


def _segment(x: float, width: float, z0: float, z1: float, fill: str, dashed: bool, label: str) -> str:
    y = _y(z1)
    height = max((z1 - z0) * SCALE, 0.4)
    dash = ' stroke-dasharray="1.1 0.7"' if dashed else ""
    text = ""
    if label and height >= 7:
        text_y = y + height / 2 + 1.1
        text = (
            f'<text x="{x + width + 1.5:.2f}" y="{text_y:.2f}" font-size="2.5" '
            f'font-family="sans-serif">{_esc(label)}</text>'
        )
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" '
        f'fill="{fill}" stroke="#111" stroke-width="0.25"{dash}/>'
        f"{text}"
    )


def _graphic() -> str:
    parts = []
    parts.append(
        f'<line x1="18" y1="{GROUND_Y:.2f}" x2="150" y2="{GROUND_Y:.2f}" stroke="#111" stroke-width="0.6"/>'
    )
    parts.append(
        f'<text x="18" y="{GROUND_Y + 4:.2f}" font-size="2.4" font-family="sans-serif">ground line</text>'
    )
    mast_top = _y(MAST_PROFILE_LENGTH_MM)
    mast_h = MAST_PROFILE_LENGTH_MM * SCALE
    parts.append(
        f'<rect x="22" y="{mast_top:.2f}" width="12" height="{mast_h:.2f}" fill="#cbd5e1" stroke="#111" stroke-width="0.3"/>'
    )
    parts.append(
        f'<text x="22" y="{mast_top - 1.5:.2f}" font-size="2.3" font-family="sans-serif">profile {MAST_PROFILE_LENGTH_MM:.0f}</text>'
    )
    stroke = available_mast_stroke_mm()
    parts.append(
        f'<rect x="38" y="{_y(stroke):.2f}" width="8" height="{stroke * SCALE:.2f}" '
        f'fill="none" stroke="#0f766e" stroke-width="0.6" stroke-dasharray="1.4 0.8"/>'
    )
    parts.append(
        f'<text x="36" y="{_y(stroke) - 1.5:.2f}" font-size="2.3" font-family="sans-serif" fill="#0f766e">stroke {stroke:.0f}</text>'
    )
    colors = {
        "ground_clearance": "#e2e8f0",
        "shoe": "#c2410c",
        "casing": "#78716c",
        "adapter": "#7c3aed",
        "head": "#ea580c",
        "carriage": "#0369a1",
        "top_margin": "#f8fafc",
    }
    z0 = 0.0
    for term in chain_terms():
        z1 = round(z0 + term.length_mm, 1)
        label = f"{term.name} {term.length_mm:.1f}"
        if term.tbd:
            label += " TBD"
        parts.append(_segment(56, 26, z0, z1, colors[term.name], term.tbd, label))
        z0 = z1
    from cad.models.mast_layout import carrier_study_length_mm

    casing = next(term for term in chain_terms() if term.name == "casing")
    before = sum(term.length_mm for term in chain_terms() if term.name in {"ground_clearance", "shoe"})
    carrier = carrier_study_length_mm()
    inset = (casing.length_mm - carrier) / 2.0
    parts.append(_segment(62, 14, before + inset, before + inset + carrier, "#bfdbfe", True, ""))
    return "\n".join(parts)


def _wrap(text: str, width: int = 68) -> list[str]:
    rows: list[str] = []
    current = ""
    for word in text.split():
        trial = word if not current else f"{current} {word}"
        if len(trial) > width and current:
            rows.append(current)
            current = word
        else:
            current = trial
    if current:
        rows.append(current)
    return rows


def _table() -> str:
    lines = ['<text x="168" y="42" font-size="3.2" font-family="sans-serif" font-weight="700">Dimension chain</text>']
    y = 48.0
    for line in chain_lines():
        for row in _wrap(line):
            lines.append(
                f'<text x="168" y="{y:.1f}" font-size="2.35" font-family="sans-serif">{_esc(row)}</text>'
            )
            y += 3.5
            if y > 220:
                break
        if y > 220:
            break
    return "\n".join(lines)


def _title(owner: str, created: str) -> str:
    rows = [
        ("Legal owner", owner),
        ("Document title", "Mast stack layout"),
        ("Document type", "study layout"),
        ("Document status", "preliminary"),
        ("Identification", DOCUMENT_ID),
        ("Revision", "study"),
        ("Creator", "vibrocore cad export"),
        ("Created", created),
        ("Units", "mm"),
        ("Sheet", "1 / 1"),
    ]
    body = [
        '<rect x="248" y="230" width="152" height="52" fill="#fff" stroke="#111" stroke-width="0.4"/>'
    ]
    y = 236.0
    for label, value in rows:
        body.append(
            f'<text x="251" y="{y:.1f}" font-size="2.2" font-family="sans-serif">{_esc(label)}</text>'
        )
        body.append(
            f'<text x="292" y="{y:.1f}" font-size="2.3" font-family="sans-serif" font-weight="700">{_esc(str(value)[:34])}</text>'
        )
        y += 4.4
    return "\n".join(body)


def pdf_bytes(owner: str, created: str) -> bytes:
    rows = [
        f"{DOCUMENT_ID} Mast stack layout. Study. Preliminary. Not for manufacture.",
        *chain_lines(),
        f"Owner: {owner}",
        f"Date: {created}",
        "Units: mm. Schematic stack. Not a first-angle view of the assembled machine.",
        "ISO 7200 fields are on the SVG sheet. General tolerances: TODO.",
        "The 1500 mm profile length is unchanged.",
    ]
    commands = ["BT", "/F1 10 Tf", "36 800 Td", "14 TL"]
    for row in rows:
        commands.append(f"({_pdf_escape(row[:150])}) Tj")
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
