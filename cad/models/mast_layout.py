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
# The plate projects 25 mm past each profile outer face.
# Outer face is at ±175 mm. Half width is 175 + 25 = 200 mm.
BOTTOM_PLATE_SIDE_OVERHANG_MM = 25.0
BOTTOM_PLATE_WIDTH_MM = 400.0
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

# The shafts stay perpendicular to the rod. The motors sit left and right of
# the rod, so the 175 mm envelope height is not a term in the axial head.
# Set this true only to compare the older stacked-motor chain.
MOTOR_HEIGHT_IN_AXIAL_STACK = False

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
# Documented minimum. SONIC_HEAD.md. The layout pitch below is not this minimum.
MOTOR_CENTRE_DISTANCE_MIN_MM = 170.0
# TBD pitch. Both 154 mm motor widths stay on the 420 mm plate. Not a measurement.
MOTOR_CENTRE_DISTANCE_MM = max(
    MOTOR_CENTRE_DISTANCE_MIN_MM,
    VIBRATING_PLATE_LENGTH_MM - MOTOR_WIDTH_MM,
)
# TBD. Lateral gap from each motor envelope to the carriage block.
MOTOR_TO_CARRIAGE_GAP_MM = 11.0
# Plan size of the carriage block. TBD. Only the height is in the chain.
# The width is the gap between the motor envelopes minus the two lateral gaps.
CARRIAGE_WIDTH_MM = (
    MOTOR_CENTRE_DISTANCE_MM - MOTOR_WIDTH_MM - 2.0 * MOTOR_TO_CARRIAGE_GAP_MM
)
CARRIAGE_DEPTH_MM = 120.0
# VC-SH-1600. Free height and diameter are unknown. TBD.
# The diameter placeholder fits in the strip beside the 255 mm motor on the 300 mm plate.
ISOLATOR_FREE_HEIGHT_MM = 40.0
ISOLATOR_DIAMETER_MM = 16.0
ISOLATOR_COUNT = 4
# VC-HB-3100. Hiwin HGR20R published section. WR is the width. HR is the height.
# The STEP mounting face is the profile front face. See cad/vendor/VC-HB-3100/SOURCE.md.
RAIL_SECTION_WIDTH_MM = 20.0
RAIL_SECTION_HEIGHT_MM = 17.5
# VC-HB-3110. Hiwin HGH20CAZ0H. H is the height from the rail mounting face.
# W is the width. The length is the STEP solid, including the end seals.
# The mounting-hole centre is 5.3 mm from that solid centre. See SOURCE.md.
RUNNER_HEIGHT_MM = 30.0
RUNNER_WIDTH_MM = 44.0
RUNNER_LENGTH_MM = 90.4
RUNNER_COUNT = 4
# TBD. Centre distance of the two blocks on one rail. Not in the BOM.
RUNNER_PITCH_MM = 200.0
# Travel of the lower block. The upper block stays on the 1300 mm rail.
GUIDED_TRAVEL_MM = round(RAIL_LENGTH_MM - RUNNER_PITCH_MM - RUNNER_LENGTH_MM, 1)
# Start pose. Zero is the lower end of travel. The start value is the top of travel.
STROKE_POSITION_MM = GUIDED_TRAVEL_MM
# Draft. Gap from the carriage plate to the rear face of the motors.
# The vibrating plate rear is flush with that face, so the rod sits close to the rails.
HEAD_FRONT_GAP_MM = 10.0
# The 400 mm bottom-plate blank stays. Its rear face is flush with the profile rear faces.
# The volume behind those faces is reserved for the machine tilt mechanism.
BOTTOM_PLATE_REAR_OVERHANG_MM = 0.0
# VC-FR-4500 closed bore. It guides the 82.55 mm casing VC-GP-7100, not the column.
CASING_GUIDE_BORE_DIAMETER_MM = 83.0
# Old chain mid-plane. The drive sprocket now shares the gearbox axis.
CHAIN_AXIS_X_MM = 0.0
# Draft sheet for the frame gussets. Not a shop measurement.
GUSSET_SHEET_THICKNESS_MM = 4.0
GUSSET_HEIGHT_MM = 80.0
# Draft sizes for the vibration-motor bracket VC-SH-1350. See CARRIAGE-BRACKET.md.
BRACKET_GUSSET_THICKNESS_MM = 8.0
BRACKET_GUSSET_HEIGHT_MM = 80.0
BRACKET_BOLT_PITCH_Z_MM = 160.0
# Yaw of each profile about its own vertical axis. The 100 mm side then lies along X.
PROFILE_YAW_DEG = 90.0
# Distance from the bottom of the profile to the bottom of the rail. TBD.
RAIL_BOTTOM_OFFSET_MM = 100.0
# Drive envelopes. A catalogue number is named. An unknown length stays TBD.
# Pitch radius already used for the hub force calculation.
SPROCKET_PITCH_RADIUS_MM = 37.9
# iwis 10B-2, 15 teeth. Tip diameter and overall length from the published product page.
SPROCKET_TIP_DIAMETER_MM = 83.0
SPROCKET_WIDTH_MM = 40.0
# Neugart PLE120-040, article 100460948. The vendor solid matches these sizes.
# 204 mm is the input adapter 47.5 mm, the housing 101.5 mm and the output shaft 55 mm.
GEARBOX_FLANGE_MM = 115.0
GEARBOX_LENGTH_MM = 204.0
# Output shaft, from the output flange face to the tip. It is inside the 204 mm.
OUTPUT_SHAFT_LENGTH_MM = 55.0
# VC-FR-4187. The output flange bolts to this frame. The sprocket sits outside it.
MOUNT_PLATE_THICKNESS_MM = 12.0
# Siemens 1FL2104-4AG11-1MC0. Flange AB is 81 mm.
# 186.6 mm is the body behind the flange face. The STEP shaft adds 40 mm.
# Overall length including that shaft is 226.6 mm.
SERVO_FLANGE_MM = 81.0
SERVO_BODY_LENGTH_MM = 186.6
SERVO_SHAFT_LENGTH_MM = 40.0
# Throat opening measured on the mk 2004 STEP. The T-slot undercut is wider.
PROFILE_SLOT_WIDTH_MM = 10.10
# Fallback coupling envelope. The placed solid is the ROTEX 28 STEP set. TBD when those files are absent.
COUPLING_DIAMETER_MM = 65.0
COUPLING_LENGTH_MM = 50.0
# Shaft diameter at the top of the 25-30 mm range. It matches the SYJ 30 TF bore.
# The gearbox output is Ø25 h7. The ROTEX hub is 32H7. Neither fits this bore.
SHAFT_DIAMETER_MM = 30.0
# SKF SYJ 30 TF. Measured on the 3Dfindit STEP. Catalogue values are in SOURCE.md.
# Length is along the shaft. Width is the foot. Height is the overall housing.
PILLOW_CENTER_HEIGHT_MM = 42.9
PILLOW_LENGTH_MM = 43.2
PILLOW_WIDTH_MM = 165.0
PILLOW_HEIGHT_MM = 82.5
PILLOW_BOLT_SPAN_MM = 118.0
# Old strand envelope. The placed chain uses the ISO 606 section below.
CHAIN_SECTION_X_MM = 16.0
CHAIN_SECTION_Y_MM = 32.0
# ISO 606 size 10B-2. G&G publishes no chain CAD, so the section is these sizes.
CHAIN_PITCH_MM = 15.875
CHAIN_ROLLER_DIAMETER_MM = 10.16
CHAIN_INNER_WIDTH_MM = 9.65
CHAIN_TRANSVERSE_PITCH_MM = 16.59
# VC-SH-1302 weld position along the plate length. TBD.
# The ribs hang under the plate and must stay outside the top plate.
RIB_CENTRE_X_MM = 170.0
# Guide bores are not located. The layout cuts a centred hole. TBD radial clearance.
SHOE_PASSAGE_RADIAL_CLEARANCE_MM = 1.0
COLUMN_PASSAGE_RADIAL_CLEARANCE_MM = 5.0
# Rod axis on the plates. TBD. Zero is the plate centre. The bore is not located.
STRING_AXIS_X_MM = 0.0
STRING_AXIS_Y_MM = 0.0
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
    "motor_centre_distance_mm": (
        MOTOR_CENTRE_DISTANCE_MM,
        "TBD. Layout pitch of the two motors. The documented minimum is 170 mm. "
        "This pitch keeps both envelopes on the 420 mm plate.",
    ),
    "motor_to_carriage_gap_mm": (
        MOTOR_TO_CARRIAGE_GAP_MM,
        "TBD. Lateral gap from each motor envelope to the carriage block.",
    ),
    "carriage_width_mm": (
        CARRIAGE_WIDTH_MM,
        "TBD. Carriage width. It is the motor gap minus the two lateral gaps. Not a measured plate.",
    ),
    "carriage_depth_mm": (
        CARRIAGE_DEPTH_MM,
        "TBD. Carriage depth. Plan size only. Not a measured plate.",
    ),
    "isolator_free_height_mm": (
        ISOLATOR_FREE_HEIGHT_MM,
        "TBD. Free height of VC-SH-1600. Not in the height chain. Not a catalogue height.",
    ),
    "isolator_diameter_mm": (
        ISOLATOR_DIAMETER_MM,
        "TBD. Diameter of VC-SH-1600. Placeholder sized to the strip beside the motor envelope.",
    ),
    "rail_section_width_mm": (
        RAIL_SECTION_WIDTH_MM,
        "Hiwin HGR20R published rail width WR. The STEP mounting face sits on the profile.",
    ),
    "rail_section_height_mm": (
        RAIL_SECTION_HEIGHT_MM,
        "Hiwin HGR20R published rail height HR. The STEP mounting face sits on the profile.",
    ),
    "runner_pitch_mm": (
        RUNNER_PITCH_MM,
        "TBD. Centre distance of the two HGH20CA blocks on one rail. Not in the BOM.",
    ),
    "head_front_gap_mm": (
        HEAD_FRONT_GAP_MM,
        "TBD. Draft gap from the carriage plate to the rear face of the motors. "
        "The plate rear is flush with that face.",
    ),
    "bottom_plate_rear_overhang_mm": (
        BOTTOM_PLATE_REAR_OVERHANG_MM,
        "TBD. Draft rear overhang of the 400 mm bottom plate. Zero keeps the rear face flush with the profiles.",
    ),
    "gusset_sheet_thickness_mm": (
        GUSSET_SHEET_THICKNESS_MM,
        "TBD. Draft thickness of the bent frame gussets. Not a shop measurement.",
    ),
    "bracket_gusset_thickness_mm": (
        BRACKET_GUSSET_THICKNESS_MM,
        "TBD. Draft thickness of the vibration-motor bracket gussets. See CARRIAGE-BRACKET.md.",
    ),
    "bracket_gusset_height_mm": (
        BRACKET_GUSSET_HEIGHT_MM,
        "TBD. Draft height of the vibration-motor bracket gussets. See CARRIAGE-BRACKET.md.",
    ),
    "servo_body_length_mm": (
        SERVO_BODY_LENGTH_MM,
        "Body length of Siemens 1FL2104 behind the flange face. The STEP shaft adds 40 mm.",
    ),
    "coupling_diameter_mm": (
        COUPLING_DIAMETER_MM,
        "TBD. Fallback envelope diameter of VC-HB-2400 when no STEP is present.",
    ),
    "coupling_length_mm": (
        COUPLING_LENGTH_MM,
        "TBD. Fallback envelope length of VC-HB-2400 when no STEP is present.",
    ),
    "pillow_length_mm": (
        PILLOW_LENGTH_MM,
        "SYJ 30 TF along the shaft. Catalogue base width A is 42 mm. The STEP bounding box is 43.2 mm.",
    ),
    "pillow_width_mm": (
        PILLOW_WIDTH_MM,
        "SYJ 30 TF foot length L. Bolt spacing J is 118 mm.",
    ),
    "pillow_height_mm": (
        PILLOW_HEIGHT_MM,
        "SYJ 30 TF overall height. Catalogue H is 82 mm. Centre height H1 is 42.9 mm.",
    ),
    "chain_section_x_mm": (
        CHAIN_SECTION_X_MM,
        "Old envelope thickness. The placed chain uses the ISO 606 roller diameter 10.16 mm.",
    ),
    "chain_section_y_mm": (
        CHAIN_SECTION_Y_MM,
        "Old envelope width. The placed duplex rows use inner width 9.65 mm and transverse pitch 16.59 mm.",
    ),
    "rail_bottom_offset_mm": (
        RAIL_BOTTOM_OFFSET_MM,
        "TBD. Distance from the bottom of the profile to the bottom of the 1300 mm rail.",
    ),
    "rib_centre_x_mm": (
        RIB_CENTRE_X_MM,
        "TBD. Weld position of VC-SH-1302 along the plate length, from the rod axis.",
    ),
    "shoe_passage_radial_clearance_mm": (
        SHOE_PASSAGE_RADIAL_CLEARANCE_MM,
        "TBD. Radial clearance of the layout bore in VC-FR-4300 around the shoe.",
    ),
    "column_passage_radial_clearance_mm": (
        COLUMN_PASSAGE_RADIAL_CLEARANCE_MM,
        "TBD. Radial clearance of the layout bore in VC-FR-4400 around the column.",
    ),
    "string_axis_x_mm": (
        STRING_AXIS_X_MM,
        "TBD. Rod axis X on the plates. The guide bore is not located. Zero is the plate centre.",
    ),
    "string_axis_y_mm": (
        STRING_AXIS_Y_MM,
        "TBD. Rod axis Y on the plates. The guide bore is not located. Zero is the plate centre.",
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
    """Axial head from the bottom of the column shaft to the top of the vibrating plate.

    The motor height is included only when include_motor is true, or when the
    module flag MOTOR_HEIGHT_IN_AXIAL_STACK is true. The assembly leaves that
    flag false and places the motors left and right of the rod.
    """
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
        # Comparison only. The machine assembly places both motors left and right.
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
