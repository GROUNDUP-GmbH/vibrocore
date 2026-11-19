"""Study layout of the mast stack. Not a manufacturing model.

All lengths live in this module. A value marked TBD is a placeholder so the
layout can be drawn. It is not a measurement. Do not manufacture from the STEP
file. Do not change the 1500 mm profile from this study.

The height chain is:

    required = ground clearance + shoe + casing + adapter + head + carriage + top margin

The available mast stroke is the 1300 mm value already stored as the physical
mast stroke. The margin is that stroke minus the required height. A negative
margin is a deficit.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cad.tools.bom import ROOT

LAYOUT_DIR = ROOT / "cad" / "export" / "layout"
DOCUMENT_ID = "MAST-LAYOUT"

# --- Documented lengths. Sources are named. Do not replace a documented value.

# VC-FR-4100. The profile length stays 1500 mm.
MAST_PROFILE_LENGTH_MM = 1500.0
MAST_PROFILE_WIDTH_MM = 50.0
MAST_PROFILE_DEPTH_MM = 100.0
MAST_PROFILE_COUNT = 2

# VC-FR-4300 and VC-FR-4400.
BOTTOM_PLATE_LENGTH_MM = 400.0
BOTTOM_PLATE_WIDTH_MM = 300.0
BOTTOM_PLATE_THICKNESS_MM = 15.0
TOP_PLATE_LENGTH_MM = 300.0
TOP_PLATE_WIDTH_MM = 200.0
TOP_PLATE_THICKNESS_MM = 12.0

# VC-GP-7100. 48 in x 25.4 mm = 1219.2 mm. 3.25 in and 2.625 in.
CASING_LENGTH_MM = round(48 * 25.4, 1)
CASING_OD_MM = round(3.25 * 25.4, 2)
CASING_ID_MM = round(2.625 * 25.4, 3)

# VC-GP-7200, Geoprobe 205449. The outside diameter is documented. The length is not.
SHOE_OD_MM = round(3.45 * 25.4, 2)

# VC-SH-1100 envelope. SONIC_HEAD.md section 2.2 calls 175 mm the height.
MOTOR_LENGTH_MM = 255.0
MOTOR_WIDTH_MM = 154.0
MOTOR_HEIGHT_MM = 175.0

# VC-SH-1301 and VC-SH-1400. The shaft length does not include the flange.
VIBRATING_PLATE_LENGTH_MM = 420.0
VIBRATING_PLATE_WIDTH_MM = 300.0
VIBRATING_PLATE_THICKNESS_MM = 20.0
COLUMN_DIAMETER_MM = 50.0
COLUMN_SHAFT_LENGTH_MM = 200.0
COLUMN_FLANGE_DIAMETER_MM = 80.0

# VC-HB-3200. Thickness only. It is not the carriage height in the chain.
CARRIAGE_PLATE_THICKNESS_MM = 10.0

# VC-HB-3100 rail length, and rMAX_STROKE_MM in firmware/codesys/GVL_PARAMS.st.
RAIL_LENGTH_MM = 1300.0
FIRMWARE_STROKE_MM = 1300.0

# Assumption from SONIC_HEAD.md: the shaft is perpendicular to the rod, so the
# published 175 mm height is axial. Set this false to drop that height from the head.
MOTOR_HEIGHT_IN_AXIAL_STACK = True

# --- TBD placeholders. Not measurements. Change these only when a length is known.

# Length of cutting shoe 205449. Ask Geoprobe. TBD.
SHOE_LENGTH_MM = 80.0
# Axial length of VC-SH-1500. The thread is not confirmed. TBD.
ADAPTER_LENGTH_MM = 60.0
# Axial height of the carriage block. The 10 mm plate thickness is not this height. TBD.
CARRIAGE_HEIGHT_MM = 80.0
# Gap from the ground line to the shoe tip at the start of the stroke. TBD.
GROUND_CLEARANCE_MM = 50.0
# Gap from the top of the carriage to the end of the required height. TBD.
TOP_MARGIN_MM = 40.0
# VC-SH-1400 flange thickness. The 80 mm diameter is documented. The thickness is not. TBD.
COLUMN_FLANGE_THICKNESS_MM = 12.0

# Visual stand-ins. They are not terms in the height chain.
# Centre distance of the two profiles. TBD. Do not read a clearance from this pitch.
PROFILE_SPACING_MM = 300.0
# Envelope diameter of VC-SH-1500. TBD. The solid is not the thread.
ADAPTER_OD_MM = 50.0
# Plan size of the carriage block. TBD. Only the height is in the chain.
CARRIAGE_WIDTH_MM = 160.0
CARRIAGE_DEPTH_MM = 120.0
# Ground datum in the STEP file. Not a part. Not in the height chain.
GROUND_DATUM_THICKNESS_MM = 0.5
GROUND_DATUM_LENGTH_MM = 420.0
GROUND_DATUM_WIDTH_MM = 8.0

PLACEHOLDERS: dict[str, tuple[float, str]] = {
    "shoe_length_mm": (
        SHOE_LENGTH_MM,
        "TBD. Length of cutting shoe 205449 is not in the offer. Ask Geoprobe.",
    ),
    "adapter_length_mm": (
        ADAPTER_LENGTH_MM,
        "TBD. Axial length of VC-SH-1500 is unknown. The thread is not confirmed.",
    ),
    "carriage_height_mm": (
        CARRIAGE_HEIGHT_MM,
        "TBD. Axial height of the carriage block. VC-HB-3200 gives only the 10 mm plate thickness.",
    ),
    "ground_clearance_mm": (
        GROUND_CLEARANCE_MM,
        "TBD. Required gap from the ground line to the shoe tip at the start of the stroke.",
    ),
    "top_margin_mm": (
        TOP_MARGIN_MM,
        "TBD. Gap above the carriage for the sprocket, the chain and the upper limit switch.",
    ),
    "column_flange_thickness_mm": (
        COLUMN_FLANGE_THICKNESS_MM,
        "TBD. Flange thickness on VC-SH-1400. The 80 mm flange diameter is documented.",
    ),
    "profile_spacing_mm": (
        PROFILE_SPACING_MM,
        "TBD. Centre distance of the two profiles. Not a height. Do not claim a shoe clearance from it.",
    ),
    "adapter_od_mm": (
        ADAPTER_OD_MM,
        "TBD. Outside diameter of VC-SH-1500. The layout cylinder is an envelope, not a thread.",
    ),
}


@dataclass(frozen=True)
class ChainTerm:
    name: str
    length_mm: float
    tbd: bool
    detail: str


def _mm(value: float) -> float:
    return round(float(value) + 0.0, 1)


def head_length_mm(*, include_motor: bool | None = None, zero_placeholders: bool = False) -> float:
    """Axial head from the bottom of the column shaft to the top of the motor envelope."""
    use_motor = MOTOR_HEIGHT_IN_AXIAL_STACK if include_motor is None else include_motor
    flange = 0.0 if zero_placeholders else COLUMN_FLANGE_THICKNESS_MM
    motor = MOTOR_HEIGHT_MM if use_motor else 0.0
    return _mm(COLUMN_SHAFT_LENGTH_MM + flange + VIBRATING_PLATE_THICKNESS_MM + motor)


def chain_terms(*, include_motor: bool | None = None, zero_placeholders: bool = False) -> tuple[ChainTerm, ...]:
    """Seven terms of the required height, from the ground upward."""
    ground = 0.0 if zero_placeholders else GROUND_CLEARANCE_MM
    shoe = 0.0 if zero_placeholders else SHOE_LENGTH_MM
    adapter = 0.0 if zero_placeholders else ADAPTER_LENGTH_MM
    carriage = 0.0 if zero_placeholders else CARRIAGE_HEIGHT_MM
    margin = 0.0 if zero_placeholders else TOP_MARGIN_MM
    head = head_length_mm(include_motor=include_motor, zero_placeholders=zero_placeholders)
    flange = 0.0 if zero_placeholders else COLUMN_FLANGE_THICKNESS_MM
    motor_note = "motor height in the stack" if (
        MOTOR_HEIGHT_IN_AXIAL_STACK if include_motor is None else include_motor
    ) else "motor height not in the stack"
    return (
        ChainTerm("ground_clearance", _mm(ground), True, "TBD placeholder"),
        ChainTerm("shoe", _mm(shoe), True, "TBD placeholder. Outside diameter is documented."),
        ChainTerm("casing", _mm(CASING_LENGTH_MM), False, "48 in casing, VC-GP-7100"),
        ChainTerm("adapter", _mm(adapter), True, "TBD placeholder, VC-SH-1500"),
        ChainTerm(
            "head",
            head,
            False,
            f"shaft {_mm(COLUMN_SHAFT_LENGTH_MM):.1f} + flange {_mm(flange):.1f} TBD "
            f"+ plate {_mm(VIBRATING_PLATE_THICKNESS_MM):.1f} + {motor_note}",
        ),
        ChainTerm("carriage", _mm(carriage), True, "TBD placeholder. Plate thickness is 10 mm and is not this term."),
        ChainTerm("top_margin", _mm(margin), True, "TBD placeholder"),
    )


def required_total_mm(**kwargs) -> float:
    return _mm(sum(term.length_mm for term in chain_terms(**kwargs)))


def available_mast_stroke_mm() -> float:
    """Carriage travel the repository already calls the physical mast stroke.

    GVL_PARAMS.st stores rMAX_STROKE_MM = 1300. VC-HB-3100 rails are 1300 mm.
    This function does not read the 1500 mm profile as the stroke.
    """
    if FIRMWARE_STROKE_MM != RAIL_LENGTH_MM:
        raise ValueError("firmware stroke and rail length disagree; name both on the drawing")
    return _mm(FIRMWARE_STROKE_MM)


def margin_vs_stroke_mm(**kwargs) -> float:
    """Stroke minus required height. Negative means the stack is longer than the stroke."""
    return _mm(available_mast_stroke_mm() - required_total_mm(**kwargs))


def deficit_vs_stroke_mm(**kwargs) -> float:
    """Required height minus the stroke. Positive means a deficit."""
    return _mm(required_total_mm(**kwargs) - available_mast_stroke_mm())


def deficit_vs_profile_mm(**kwargs) -> float:
    """Required height minus the 1500 mm profile. Positive means a deficit."""
    return _mm(required_total_mm(**kwargs) - MAST_PROFILE_LENGTH_MM)


def documented_axial_mm(*, include_motor: bool | None = None) -> float:
    """Casing plus the documented head pieces. Every TBD length is zero."""
    return required_total_mm(include_motor=include_motor, zero_placeholders=True)


def plate_opening_mm() -> float:
    """Clear gap if the plates sit on the profile ends. SAMPLING.md uses this assumption."""
    return _mm(MAST_PROFILE_LENGTH_MM - BOTTOM_PLATE_THICKNESS_MM - TOP_PLATE_THICKNESS_MM)


def sampling_remainder_mm() -> float:
    """1473 mm opening minus column shaft, plate and casing. Same 33.8 mm as SAMPLING.md.

    That remainder does not include the motor height, the carriage, the shoe,
    the adapter or the margins. It is not the result of this layout.
    """
    known = COLUMN_SHAFT_LENGTH_MM + VIBRATING_PLATE_THICKNESS_MM + CASING_LENGTH_MM
    return _mm(plate_opening_mm() - known)


def carrier_study_length_mm(bom=None) -> float:
    """Axial length of the VC-SP-7620 study solid. Tube length is TBD. Not a chain term."""
    from cad.models.split_carrier import stack_length_mm

    if bom is None:
        from cad.tools.bom import load_bom

        bom = load_bom()
    return float(stack_length_mm(bom.part("VC-SP-7620").geometry))


def stations(**kwargs) -> list[tuple[ChainTerm, float]]:
    """Each term and the station at its top, measured from the ground line."""
    z = 0.0
    rows = []
    for term in chain_terms(**kwargs):
        z = _mm(z + term.length_mm)
        rows.append((term, z))
    return rows


def layout_shape(bom=None):
    """Positioned study solids. Z is up. The string is on the machine axis.

    The ground box is a datum. Its thickness is not part of the height chain.
    Profile spacing, adapter diameter and carriage plan size are TBD.
    """
    from build123d import Box, Compound, Cylinder, Pos

    from cad.models.split_carrier import shape_for_geometry, stack_length_mm

    if bom is None:
        from cad.tools.bom import load_bom

        bom = load_bom()

    bottoms = {term.name: _mm(top - term.length_mm) for term, top in stations()}
    solids = []

    def add(name: str, shape):
        shape.label = name
        solids.append(shape)

    add(
        "GROUND-DATUM",
        Pos(0, 0, -GROUND_DATUM_THICKNESS_MM / 2.0)
        * Box(GROUND_DATUM_LENGTH_MM, GROUND_DATUM_WIDTH_MM, GROUND_DATUM_THICKNESS_MM),
    )
    half_pitch = PROFILE_SPACING_MM / 2.0
    for index, sign in enumerate((-1.0, 1.0)[:MAST_PROFILE_COUNT], start=1):
        add(
            f"VC-FR-4100-{index}",
            Pos(0, sign * half_pitch, MAST_PROFILE_LENGTH_MM / 2.0)
            * Box(MAST_PROFILE_WIDTH_MM, MAST_PROFILE_DEPTH_MM, MAST_PROFILE_LENGTH_MM),
        )
    add(
        "VC-FR-4300",
        Pos(0, 0, BOTTOM_PLATE_THICKNESS_MM / 2.0)
        * Box(BOTTOM_PLATE_LENGTH_MM, BOTTOM_PLATE_WIDTH_MM, BOTTOM_PLATE_THICKNESS_MM),
    )
    add(
        "VC-FR-4400",
        Pos(0, 0, MAST_PROFILE_LENGTH_MM - TOP_PLATE_THICKNESS_MM / 2.0)
        * Box(TOP_PLATE_LENGTH_MM, TOP_PLATE_WIDTH_MM, TOP_PLATE_THICKNESS_MM),
    )

    def vertical_cylinder(name: str, diameter: float, length: float, z_bottom: float):
        if length <= 0:
            return
        add(
            name,
            Pos(0, 0, z_bottom + length / 2.0) * Cylinder(diameter / 2.0, length),
        )

    vertical_cylinder("VC-GP-7200", SHOE_OD_MM, SHOE_LENGTH_MM, bottoms["shoe"])
    casing_bottom = bottoms["casing"]
    casing = Cylinder(CASING_OD_MM / 2.0, CASING_LENGTH_MM) - Cylinder(CASING_ID_MM / 2.0, CASING_LENGTH_MM + 1.0)
    add("VC-GP-7100", Pos(0, 0, casing_bottom + CASING_LENGTH_MM / 2.0) * casing)

    carrier_geom = bom.part("VC-SP-7620").geometry
    carrier_length = stack_length_mm(carrier_geom)
    # Tube length is TBD. The carrier is inside the casing and is not a chain term.
    if carrier_length > CASING_LENGTH_MM:
        raise ValueError("study carrier is longer than one casing; show that before export")
    carrier = shape_for_geometry(carrier_geom)
    add(
        "VC-SP-7620",
        Pos(0, 0, casing_bottom + CASING_LENGTH_MM / 2.0) * carrier,
    )

    vertical_cylinder("VC-SH-1500", ADAPTER_OD_MM, ADAPTER_LENGTH_MM, bottoms["adapter"])
    head_bottom = bottoms["head"]
    cursor = head_bottom
    vertical_cylinder("VC-SH-1400", COLUMN_DIAMETER_MM, COLUMN_SHAFT_LENGTH_MM, cursor)
    cursor = _mm(cursor + COLUMN_SHAFT_LENGTH_MM)
    vertical_cylinder("VC-SH-1400-FLANGE", COLUMN_FLANGE_DIAMETER_MM, COLUMN_FLANGE_THICKNESS_MM, cursor)
    cursor = _mm(cursor + COLUMN_FLANGE_THICKNESS_MM)
    add(
        "VC-SH-1301",
        Pos(0, 0, cursor + VIBRATING_PLATE_THICKNESS_MM / 2.0)
        * Box(VIBRATING_PLATE_LENGTH_MM, VIBRATING_PLATE_WIDTH_MM, VIBRATING_PLATE_THICKNESS_MM),
    )
    cursor = _mm(cursor + VIBRATING_PLATE_THICKNESS_MM)
    if MOTOR_HEIGHT_IN_AXIAL_STACK:
        # One motor envelope shows the axial height. The second motor is not placed.
        # The centre distance is only a minimum of 170 mm.
        add(
            "VC-SH-1100",
            Pos(0, 0, cursor + MOTOR_HEIGHT_MM / 2.0)
            * Box(MOTOR_LENGTH_MM, MOTOR_WIDTH_MM, MOTOR_HEIGHT_MM),
        )
        cursor = _mm(cursor + MOTOR_HEIGHT_MM)
    if _mm(cursor - head_bottom) != head_length_mm():
        raise ValueError("head solids do not sum to the head chain term")

    add(
        "VC-HB-3200",
        Pos(0, 0, bottoms["carriage"] + CARRIAGE_HEIGHT_MM / 2.0)
        * Box(CARRIAGE_WIDTH_MM, CARRIAGE_DEPTH_MM, CARRIAGE_HEIGHT_MM),
    )
    compound = Compound(children=solids)
    compound.label = DOCUMENT_ID
    return compound


def export_mast_layout(bom, destination: Path | None = None) -> list[Path]:
    """Write the study SVG, PDF and STEP. The caller passes the BOM for the title block."""
    from build123d import export_step

    from cad.tools.geometry import _freeze_step_header
    from cad.tools.mast_drawing import pdf_bytes, svg_text

    directory = destination or LAYOUT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    owner = bom.meta["owner"]
    created = bom.meta["cad_baseline_date"]
    svg_path = directory / "mast-stack.svg"
    pdf_path = directory / "mast-stack.pdf"
    step_path = directory / "mast-stack.step"
    svg_path.write_text(svg_text(owner, created), encoding="utf-8")
    pdf_path.write_bytes(pdf_bytes(owner, created))
    export_step(layout_shape(bom), step_path)
    _freeze_step_header(step_path, DOCUMENT_ID, created)
    return [svg_path, pdf_path, step_path]
