"""Study assembly of the machine in the start pose. Not a manufacturing model.

Every length comes from cad.models.mast_layout. A value marked TBD there is not
a measurement. The motors sit left and right of the rod, so their 175 mm height
is not in the axial chain.

The head is yawed 90 degrees about Z. The motor shafts point at the mast.
The vibrating plate shares the guide-block height. The rod sits close to the rails.
The bottom plate has an 83 mm bore on that axis. The bore guides the casing.
The drive sprocket sits on a Ø30 shaft between two SKF SYJ 30 TF bearings.
A ROTEX 28 coupling joins that shaft to the PLE120 output. The gearbox shaft
sees no chain radial load. The chain is centred between the uprights.
The volume behind the profile rear faces is reserved for the tilt mechanism.

The start pose puts the carriage at the top of the guided stroke. The four
HGH20 blocks stay on the rails. The shoe tip is then below the ground line.
That is the height deficit. The tip is not forced onto the ground.

A purchased part uses cad/vendor/<part-id>/*.step when that file exists.
load_vendor_shape recenters the bounding box and keeps the file axes.
The assembly then applies the rotation named in that part's SOURCE.md.
A missing file keeps the catalogue envelope.

Solids that already exist are built with cad.tools.geometry.shape_for.
This module only places them. It does not add a BOM line.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path

from cad.models.mast_layout import (
    ADAPTER_LENGTH_MM,
    ADAPTER_OD_MM,
    BOTTOM_PLATE_LENGTH_MM,
    BOTTOM_PLATE_REAR_OVERHANG_MM,
    BOTTOM_PLATE_THICKNESS_MM,
    BOTTOM_PLATE_WIDTH_MM,
    BRACKET_BOLT_PITCH_Z_MM,
    BRACKET_GUSSET_HEIGHT_MM,
    BRACKET_GUSSET_THICKNESS_MM,
    CARRIAGE_HEIGHT_MM,
    CARRIAGE_PLATE_THICKNESS_MM,
    CASING_GUIDE_BORE_DIAMETER_MM,
    CASING_ID_MM,
    CASING_LENGTH_MM,
    CASING_OD_MM,
    CHAIN_ROLLER_DIAMETER_MM,
    CHAIN_INNER_WIDTH_MM,
    CHAIN_TRANSVERSE_PITCH_MM,
    COLUMN_DIAMETER_MM,
    COLUMN_FLANGE_DIAMETER_MM,
    COLUMN_FLANGE_THICKNESS_MM,
    COLUMN_SHAFT_LENGTH_MM,
    COUPLING_DIAMETER_MM,
    COUPLING_LENGTH_MM,
    GEARBOX_FLANGE_MM,
    GEARBOX_LENGTH_MM,
    OUTPUT_SHAFT_LENGTH_MM,
    MOUNT_PLATE_THICKNESS_MM,
    GROUND_CLEARANCE_MM,
    GUSSET_HEIGHT_MM,
    GUSSET_SHEET_THICKNESS_MM,
    GROUND_DATUM_THICKNESS_MM,
    GUIDED_TRAVEL_MM,
    HEAD_FRONT_GAP_MM,
    ISOLATOR_COUNT,
    ISOLATOR_DIAMETER_MM,
    ISOLATOR_FREE_HEIGHT_MM,
    MAST_PROFILE_DEPTH_MM,
    MAST_PROFILE_LENGTH_MM,
    MAST_PROFILE_WIDTH_MM,
    MOTOR_CENTRE_DISTANCE_MIN_MM,
    MOTOR_CENTRE_DISTANCE_MM,
    MOTOR_HEIGHT_MM,
    MOTOR_LENGTH_MM,
    MOTOR_WIDTH_MM,
    SERVO_BODY_LENGTH_MM,
    SERVO_FLANGE_MM,
    SERVO_SHAFT_LENGTH_MM,
    PROFILE_SPACING_MM,
    PROFILE_YAW_DEG,
    RAIL_BOTTOM_OFFSET_MM,
    RAIL_LENGTH_MM,
    RAIL_SECTION_HEIGHT_MM,
    RAIL_SECTION_WIDTH_MM,
    RIB_CENTRE_X_MM,
    RUNNER_COUNT,
    RUNNER_HEIGHT_MM,
    RUNNER_LENGTH_MM,
    RUNNER_PITCH_MM,
    RUNNER_WIDTH_MM,
    PILLOW_BOLT_SPAN_MM,
    PILLOW_CENTER_HEIGHT_MM,
    PILLOW_HEIGHT_MM,
    PILLOW_LENGTH_MM,
    PILLOW_WIDTH_MM,
    SHAFT_DIAMETER_MM,
    SHOE_LENGTH_MM,
    SHOE_OD_MM,
    SPROCKET_PITCH_RADIUS_MM,
    SPROCKET_TIP_DIAMETER_MM,
    SPROCKET_WIDTH_MM,
    STRING_AXIS_Y_MM,
    STROKE_POSITION_MM,
    TOP_MARGIN_MM,
    TOP_PLATE_THICKNESS_MM,
    VIBRATING_PLATE_LENGTH_MM,
    VIBRATING_PLATE_THICKNESS_MM,
    VIBRATING_PLATE_WIDTH_MM,
    _mm,
    head_length_mm,
    required_total_mm,
)
from cad.tools.bom import ROOT

ASSEMBLY_ID = "VC-ASM-0000-layout"
RENDER_DIR = ROOT / "cad" / "export" / "renders"
STEP_NAME = f"{ASSEMBLY_ID}.step"
OVERLAP_TOLERANCE_MM3 = 1.0
# The Siemens oil seal extends 8 mm. This PLE120 recess is 4.4 mm deep.
# The key has no keyway in that bore. Flange faces still meet.
# Every other pair stays under the tolerance. See VC-HB-2200 in the BOM.
KNOWN_OVERLAP_PAIRS = frozenset({frozenset({"VC-HB-2100", "VC-HB-2200"})})
RENDER_VIEWS = ("iso", "side", "top")

# Datum plan for this pose. Not a part and not a chain term.
# It matches the bottom plate. It does not set the assembly bounding box.
_DATUM_LENGTH_MM = BOTTOM_PLATE_LENGTH_MM
_DATUM_WIDTH_MM = BOTTOM_PLATE_WIDTH_MM
_DATUM_CENTER_X_MM = 0.0
# Model air gap so a wrapped chain and a bored block do not share a volume.
_MODEL_GAP_MM = 0.4


@dataclass(frozen=True)
class Placed:
    name: str
    shape: object


def posed_stack_height_mm() -> float:
    """Parameter sum from the shoe tip to the top of the carriage term.

    Ground clearance and the top margin are not in this sum.
    The visual shoe tip is not on the ground. See shoe_tip_z_mm.
    """
    return _mm(
        SHOE_LENGTH_MM
        + CASING_LENGTH_MM
        + ADAPTER_LENGTH_MM
        + head_length_mm()
        + CARRIAGE_HEIGHT_MM
    )


def _stroke_mm(stroke_mm: float | None) -> float:
    stroke = STROKE_POSITION_MM if stroke_mm is None else float(stroke_mm)
    if stroke < -0.05 or stroke > GUIDED_TRAVEL_MM + 0.05:
        raise ValueError("stroke position is outside the guided travel")
    return stroke


def profile_front_x_mm() -> float:
    """+X face of a profile after the 90 degree yaw. This face points at the rod."""
    return MAST_PROFILE_DEPTH_MM / 2.0


def carriage_web_x_mm() -> tuple[float, float]:
    """Inner and outer X of the 10 mm carriage plate on the runner faces."""
    inner = profile_front_x_mm() + RUNNER_HEIGHT_MM
    return inner, inner + CARRIAGE_PLATE_THICKNESS_MM


def rod_axis_x_mm() -> float:
    """Rod axis. The motor rear face is flush with the vibrating-plate rear face."""
    rear = carriage_web_x_mm()[1] + HEAD_FRONT_GAP_MM
    return rear + MOTOR_LENGTH_MM / 2.0


def plate_rear_x_mm() -> float:
    """Rear face of the motors and of the vibrating plate."""
    return carriage_web_x_mm()[1] + HEAD_FRONT_GAP_MM


def bottom_plate_center_x_mm() -> float:
    """Centre of the 400 mm blank. The blank still covers the profiles and the bore."""
    rear = -profile_front_x_mm() - BOTTOM_PLATE_REAR_OVERHANG_MM
    return rear + BOTTOM_PLATE_LENGTH_MM / 2.0


def rear_face_x_mm() -> float:
    """Rear face of the yawed profiles. X below this is the tilt-mechanism volume."""
    return -profile_front_x_mm()


def _pillow_solid():
    """SKF SYJ 30 TF, or the measured envelope when the STEP is absent.

    Local bore is Y. Local Z = 0 is the shaft. The foot sole is at Z = -42.9 mm.
    """
    from build123d import Box, Pos

    from cad.models.vendor_parts import oriented_pillow

    solid = oriented_pillow()
    if solid is not None:
        return solid
    # The STEP box is not symmetric. These shifts match that box.
    # Sole at Z = -42.9 mm. Along-shaft span from Y = -22.2 mm to Y = 21.0 mm.
    center_y = (PILLOW_LENGTH_MM / 2.0) - 22.2
    center_z = -PILLOW_CENTER_HEIGHT_MM + PILLOW_HEIGHT_MM / 2.0
    return Pos(0.0, center_y, center_z) * Box(PILLOW_WIDTH_MM, PILLOW_LENGTH_MM, PILLOW_HEIGHT_MM)


def chain_axis_x_mm() -> float:
    """Sprocket, shaft, coupling and gearbox share this X.

    The SYJ foot is 165 mm along X. Its rear end stays on the rear face.
    """
    return rear_face_x_mm() + PILLOW_WIDTH_MM / 2.0


def lift_motor_axis_x_mm() -> float:
    """Axis of the lift train. Same line as the chain."""
    return chain_axis_x_mm()


def _drive_bay() -> dict:
    """Sprocket at the machine centre. Gearbox packed toward that centre.

    Order from the gearbox toward +Y: output shaft, ROTEX 28, drive-side
    bearing, sprocket, idle-side bearing. The two bearings sit close to the
    sprocket. The coupling has 5 mm of assembly gap beyond the drive bearing.
    The drive-side upright starts above the gearbox.
    """
    from cad.models.vendor_parts import oriented_coupling, oriented_gearbox, oriented_sprocket

    gear = oriented_gearbox()
    coupling = oriented_coupling()
    sprocket = oriented_sprocket()
    pillow = _pillow_solid()
    pillow_box = pillow.bounding_box()
    plate_top = BOTTOM_PLATE_THICKNESS_MM
    gap = 2.0
    half = GEARBOX_FLANGE_MM / 2.0
    motor_x = chain_axis_x_mm()
    # 25 mm flat bar under the bearings. The sole sits on that bar.
    z_lift = plate_top + 25.0 + PILLOW_CENTER_HEIGHT_MM
    if sprocket is None:
        sprocket_half = SPROCKET_WIDTH_MM / 2.0
    else:
        box = sprocket.bounding_box()
        sprocket_half = float(box.max.Y - box.min.Y) / 2.0
    # Drive bearing is on -Y. Its inboard face clears the sprocket by 2 mm.
    drive_y = -(sprocket_half + gap) - float(pillow_box.max.Y)
    idle_y = (sprocket_half + gap) - float(pillow_box.min.Y)
    drive_min_y = drive_y + float(pillow_box.min.Y)
    idle_max_y = idle_y + float(pillow_box.max.Y)
    if coupling is None:
        coupling_max = drive_min_y - 5.0
        coupling_y = coupling_max - COUPLING_LENGTH_MM / 2.0
        coupling_min = coupling_y - COUPLING_LENGTH_MM / 2.0
    else:
        couple_box = coupling.bounding_box()
        # Local Y = 0 is the jaw face. The chain-side end is max Y.
        coupling_y = drive_min_y - 5.0 - float(couple_box.max.Y)
        coupling_min = coupling_y + float(couple_box.min.Y)
        coupling_max = coupling_y + float(couple_box.max.Y)
    tip_local = GEARBOX_LENGTH_MM if gear is None else float(gear.bounding_box().max.Y)
    # The output tip stops 3 mm short of the jaw. The flange then misses the
    # carriage block, which reaches Y = -172 mm at stroke 0.
    tip_y = coupling_y - 3.0
    gear_y0 = tip_y - tip_local
    face_y = gear_y0 + tip_local - OUTPUT_SHAFT_LENGTH_MM
    motor_y1 = gear_y0
    motor_y0 = motor_y1 - SERVO_BODY_LENGTH_MM
    return {
        "gear": gear,
        "coupling": coupling,
        "motor_x": motor_x,
        "z_lift": z_lift,
        "sprocket_y": 0.0,
        "drive_bearing_y": drive_y,
        "idle_bearing_y": idle_y,
        "drive_bearing_min_y": drive_min_y,
        "idle_bearing_max_y": idle_max_y,
        "coupling_y": coupling_y,
        "coupling_min_y": coupling_min,
        "coupling_max_y": coupling_max,
        "gear_y0": gear_y0,
        "gear_y1": gear_y0 + GEARBOX_LENGTH_MM,
        "tip_y": tip_y,
        "face_y": face_y,
        "plate_outer_y": face_y + MOUNT_PLATE_THICKNESS_MM,
        "gear_bottom": z_lift - half,
        "gear_top": z_lift + half,
        "motor_y": (motor_y0 + motor_y1) / 2.0,
        "motor_y0": motor_y0,
        "motor_y1": motor_y1,
        # The short upright clears the gearbox. No end plate.
        "short_z0": z_lift + half + 2.0,
        "plate_top": plate_top,
        "shaft_y0": coupling_y + 8.0,
        "shaft_y1": idle_max_y + 2.0,
    }


def guide_radial_clearance_mm() -> float:
    """Radial gap of the 83 mm bore around the 82.55 mm casing."""
    return round((CASING_GUIDE_BORE_DIAMETER_MM - CASING_OD_MM) / 2.0, 3)


def visual_stations(stroke_mm: float | None = None) -> dict[str, float]:
    """World positions for the guided pose. Z is up.

    The carriage is on the rails. The string hangs below it.
    The shoe tip is not forced to Z = 0.
    """
    stroke = _stroke_mm(stroke_mm)
    profile_bottom = BOTTOM_PLATE_THICKNESS_MM
    profile_top = profile_bottom + MAST_PROFILE_LENGTH_MM
    rail_bottom = profile_bottom + RAIL_BOTTOM_OFFSET_MM
    rail_top = rail_bottom + RAIL_LENGTH_MM
    lower_bottom = rail_bottom + stroke
    upper_top = lower_bottom + RUNNER_PITCH_MM + RUNNER_LENGTH_MM
    if upper_top > rail_top + 0.05 or lower_bottom < rail_bottom - 0.05:
        raise ValueError("runners leave the rail")
    shelf_bottom = lower_bottom - CARRIAGE_PLATE_THICKNESS_MM
    # The vibrating plate shares the guide-block height. It does not hang below them.
    plate_bottom = lower_bottom
    plate_top = plate_bottom + VIBRATING_PLATE_THICKNESS_MM
    flange_bottom = plate_bottom - COLUMN_FLANGE_THICKNESS_MM
    shaft_bottom = flange_bottom - COLUMN_SHAFT_LENGTH_MM
    adapter_bottom = shaft_bottom - ADAPTER_LENGTH_MM
    casing_bottom = adapter_bottom - CASING_LENGTH_MM
    shoe_bottom = casing_bottom - SHOE_LENGTH_MM
    web_inner, web_outer = carriage_web_x_mm()
    return {
        "profile_bottom": profile_bottom,
        "profile_top": profile_top,
        "rail_bottom": rail_bottom,
        "rail_top": rail_top,
        "lower_bottom": lower_bottom,
        "upper_top": upper_top,
        "shelf_bottom": shelf_bottom,
        "plate_top": plate_top,
        "plate_bottom": plate_bottom,
        "flange_bottom": flange_bottom,
        "shaft_bottom": shaft_bottom,
        "adapter_bottom": adapter_bottom,
        "casing_bottom": casing_bottom,
        "shoe_bottom": shoe_bottom,
        "rod_x": rod_axis_x_mm(),
        "web_inner": web_inner,
        "web_outer": web_outer,
        "stroke": stroke,
    }


def shoe_tip_z_mm(stroke_mm: float | None = None) -> float:
    """Shoe tip in the guided pose. Negative means the tip is below the ground line."""
    return _mm(visual_stations(stroke_mm)["shoe_bottom"])


def assembly_parts(bom=None, stroke_mm: float | None = None) -> list[Placed]:
    """One named solid per instance. Labels are the part numbers FreeCAD shows."""
    from build123d import Box, Compound, Cylinder, Pos, Rot

    from cad.tools.geometry import load_vendor_shape, shape_for

    if bom is None:
        from cad.tools.bom import load_bom

        bom = load_bom()

    station = visual_stations(stroke_mm)
    rod_x = station["rod_x"]
    rod_y = STRING_AXIS_Y_MM
    parts: list[Placed] = []

    def add(name: str, shape, x: float, y: float, z: float, turn=None) -> None:
        # A shared blank would keep only the last STEP name. Copy first.
        base = copy.deepcopy(shape)
        moved = Pos(x, y, z) * (turn * base if turn else base)
        moved.label = name
        parts.append(Placed(name, moved))

    def bought(part_id: str, envelope):
        vendor = load_vendor_shape(part_id)
        return envelope if vendor is None else vendor

    def vertical_cylinder(name: str, radius: float, length: float, z_bottom: float, x: float, y: float) -> None:
        if length <= 0:
            return
        add(name, Cylinder(radius, length), x, y, z_bottom + length / 2.0)

    def along_y(radius: float, length: float):
        return Rot(90, 0, 0) * Cylinder(radius, length)

    def span(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        za, zb = sorted((z0, z1))
        return Pos((xa + xb) / 2.0, (ya + yb) / 2.0, (za + zb) / 2.0) * Box(
            xb - xa, yb - ya, zb - za
        )

    def fuse(pieces):
        solid = pieces[0]
        for piece in pieces[1:]:
            solid = solid + piece
        return solid

    plate_x = bottom_plate_center_x_mm()
    add(
        "GROUND-DATUM",
        Box(_DATUM_LENGTH_MM, _DATUM_WIDTH_MM, GROUND_DATUM_THICKNESS_MM),
        plate_x,
        0.0,
        -GROUND_DATUM_THICKNESS_MM / 2.0,
    )

    # Closed 83 mm bore on the rod axis. It guides the casing. The shoe cannot pass it.
    bay = _drive_bay()
    bottom = shape_for(bom.part("VC-FR-4300"))
    bore = Pos(rod_x - plate_x, rod_y, 0.0) * Cylinder(
        CASING_GUIDE_BORE_DIAMETER_MM / 2.0,
        BOTTOM_PLATE_THICKNESS_MM + 4.0,
    )
    # Slot between the uprights for the draft drop drive. The chain itself stays above the plate.
    drop_slot = Pos(chain_axis_x_mm() - plate_x, 75.0, 0.0) * Box(
        40.0, 44.0, BOTTOM_PLATE_THICKNESS_MM + 4.0
    )
    plate = bottom - bore - drop_slot
    # Gearbox-plate foot, stiffener angle, and the four SYJ M12 bolts.
    bolt_dx = PILLOW_BOLT_SPAN_MM / 2.0
    hole_xy = [
        (chain_axis_x_mm() - 40.0, -143.0),
        (chain_axis_x_mm() + 40.0, -143.0),
        (-10.0, 100.0),
        (10.0, 100.0),
    ]
    for center_y in (bay["drive_bearing_y"], bay["idle_bearing_y"]):
        for sign in (-1.0, 1.0):
            hole_xy.append((chain_axis_x_mm() + sign * bolt_dx, center_y))
    for hole_x, hole_y in hole_xy:
        radius = 6.5 if abs(hole_y) < 80.0 else 4.5
        plate = plate - Pos(hole_x - plate_x, hole_y, 0.0) * Cylinder(radius, BOTTOM_PLATE_THICKNESS_MM + 4.0)
    add(
        "VC-FR-4300",
        plate,
        plate_x,
        0.0,
        BOTTOM_PLATE_THICKNESS_MM / 2.0,
    )

    half_pitch = PROFILE_SPACING_MM / 2.0
    profile_center_z = station["profile_bottom"] + MAST_PROFILE_LENGTH_MM / 2.0
    profile_turn = Rot(0, 0, PROFILE_YAW_DEG)
    profile_inner_y = half_pitch - MAST_PROFILE_WIDTH_MM / 2.0
    profile_outer_y = half_pitch + MAST_PROFILE_WIDTH_MM / 2.0
    from cad.tools.geometry import vendor_step_path

    from cad.models.vendor_parts import oriented_mk2004

    mk_profile = oriented_mk2004()
    profile_vendor = vendor_step_path("VC-FR-4100") is not None
    for index, sign in enumerate((-1.0, 1.0), start=1):
        # The drive-side tube is cut short so the gearbox can sit above the plate.
        # The mk extrusion is scaled on its length axis. Any other vendor file
        # replaces both tubes at full length. The test hook depends on that.
        if mk_profile is not None:
            if sign < 0:
                length = station["profile_top"] - bay["short_z0"]
                blank = oriented_mk2004(length)
                center_z = bay["short_z0"] + length / 2.0
            else:
                blank = mk_profile
                center_z = profile_center_z
            add(
                f"VC-FR-4100-{index}",
                blank,
                0.0,
                sign * half_pitch,
                center_z,
                profile_turn,
            )
        elif sign < 0 and not profile_vendor:
            length = station["profile_top"] - bay["short_z0"]
            blank = Box(MAST_PROFILE_WIDTH_MM, MAST_PROFILE_DEPTH_MM, length)
            add(
                f"VC-FR-4100-{index}",
                blank,
                0.0,
                sign * half_pitch,
                bay["short_z0"] + length / 2.0,
                profile_turn,
            )
        else:
            add(
                f"VC-FR-4100-{index}",
                bought("VC-FR-4100", shape_for(bom.part("VC-FR-4100"))),
                0.0,
                sign * half_pitch,
                profile_center_z,
                profile_turn,
            )

    front = profile_front_x_mm()
    rail_center_z = station["rail_bottom"] + RAIL_LENGTH_MM / 2.0
    from cad.models.vendor_parts import oriented_block, oriented_rail

    rail_solid = oriented_rail()
    block_solid = oriented_block()
    # Envelope centres. A vendor solid keeps its mounting plane at local X = 0.
    rail_x = 0.0 if rail_solid is not None else front + RAIL_SECTION_HEIGHT_MM / 2.0
    rail_blank = Box(RAIL_SECTION_HEIGHT_MM, RAIL_SECTION_WIDTH_MM, RAIL_LENGTH_MM)
    for index, sign in enumerate((-1.0, 1.0), start=1):
        add(
            f"VC-HB-3100-{index}",
            rail_blank if rail_solid is None else rail_solid,
            front + rail_x,
            sign * half_pitch,
            rail_center_z,
        )

    def runner_blank():
        block = Box(RUNNER_HEIGHT_MM, RUNNER_WIDTH_MM, RUNNER_LENGTH_MM)
        channel = Box(
            RAIL_SECTION_HEIGHT_MM + _MODEL_GAP_MM,
            RAIL_SECTION_WIDTH_MM + _MODEL_GAP_MM,
            RUNNER_LENGTH_MM + 2.0,
        )
        shift = -RUNNER_HEIGHT_MM / 2.0 + (RAIL_SECTION_HEIGHT_MM + _MODEL_GAP_MM) / 2.0
        return block - Pos(shift, 0, 0) * channel

    runner_x = 0.0 if block_solid is not None else RUNNER_HEIGHT_MM / 2.0
    runner_zs = (
        station["lower_bottom"] + RUNNER_LENGTH_MM / 2.0,
        station["lower_bottom"] + RUNNER_PITCH_MM + RUNNER_LENGTH_MM / 2.0,
    )
    runner_index = 1
    for sign in (-1.0, 1.0):
        for center_z in runner_zs:
            add(
                f"VC-HB-3110-{runner_index}",
                runner_blank() if block_solid is None else block_solid,
                front + runner_x,
                sign * half_pitch,
                center_z,
            )
            runner_index += 1
    if runner_index - 1 != RUNNER_COUNT:
        raise ValueError("runner count does not match the BOM quantity")

    # The sprocket is centred on the chain line, between the uprights.
    from cad.models.vendor_parts import oriented_sprocket

    sprocket_solid = oriented_sprocket()
    drive_x = bay["motor_x"]
    z_drive = bay["z_lift"]
    chain_y = bay["sprocket_y"]
    sprocket_r = SPROCKET_TIP_DIAMETER_MM / 2.0
    # 8 mm is the upper cap. The idler sits on that cap, not on the raw profile end.
    z_idler = station["profile_top"] + 8.0 + 36.0
    front_strand_x = drive_x + SPROCKET_PITCH_RADIUS_MM

    web_z0 = station["shelf_bottom"]
    web_z1 = station["upper_top"]
    web_y = PROFILE_SPACING_MM + RUNNER_WIDTH_MM
    lug_z = station["lower_bottom"] + RUNNER_LENGTH_MM / 2.0
    strand_face_x = front_strand_x + CHAIN_ROLLER_DIAMETER_MM / 2.0
    # The arm stays in front of the profiles and above the mount plate.
    carriage = Compound(
        children=[
            span(
                station["web_inner"],
                station["web_outer"],
                -web_y / 2.0,
                web_y / 2.0,
                web_z0,
                web_z1,
            ),
            # Stay in front of the rail, then reach the strand outboard of the profile.
            span(
                station["web_inner"],
                station["web_outer"],
                chain_y + 16.0,
                -web_y / 2.0,
                lug_z - 8.0,
                lug_z + 8.0,
            ),
            span(
                strand_face_x,
                station["web_outer"],
                chain_y - 16.0,
                chain_y + 16.0,
                lug_z - 8.0,
                lug_z + 8.0,
            ),
        ]
    )
    carriage.label = "VC-HB-3200"
    parts.append(Placed("VC-HB-3200", carriage))

    # Head yaw: the 420 mm plate length lies along Y and the shafts lie along X.
    plate_rear = plate_rear_x_mm()
    plate_center_x = plate_rear + VIBRATING_PLATE_WIDTH_MM / 2.0
    head_turn = Rot(0, 0, 90)
    plate_bottom = station["plate_bottom"]
    add(
        "VC-SH-1301",
        shape_for(bom.part("VC-SH-1301")),
        plate_center_x,
        rod_y,
        plate_bottom + VIBRATING_PLATE_THICKNESS_MM / 2.0,
        head_turn,
    )
    rib_height = float(bom.part("VC-SH-1302").geometry["height_mm"])
    rib_z = plate_bottom - rib_height / 2.0
    for index, sign in enumerate((-1.0, 1.0), start=1):
        add(
            f"VC-SH-1302-{index}",
            shape_for(bom.part("VC-SH-1302")),
            plate_center_x,
            rod_y + sign * RIB_CENTRE_X_MM,
            rib_z,
        )

    add(
        "VC-SH-1400",
        shape_for(bom.part("VC-SH-1400")),
        rod_x,
        rod_y,
        station["shaft_bottom"] + COLUMN_SHAFT_LENGTH_MM / 2.0,
    )
    vertical_cylinder(
        "VC-SH-1400-FLANGE",
        COLUMN_FLANGE_DIAMETER_MM / 2.0,
        COLUMN_FLANGE_THICKNESS_MM,
        station["flange_bottom"],
        rod_x,
        rod_y,
    )

    # Shaft along X. The 154 mm width lies along Y. Both motors stay on the plate.
    motor_z = station["plate_top"] + MOTOR_HEIGHT_MM / 2.0
    half_centres = MOTOR_CENTRE_DISTANCE_MM / 2.0
    motor_blank = shape_for(bom.part("VC-SH-1100"))
    for index, sign in enumerate((-1.0, 1.0), start=1):
        add(
            f"VC-SH-1100-{index}",
            bought("VC-SH-1100", motor_blank),
            rod_x,
            rod_y + sign * half_centres,
            motor_z,
        )

    motor_inner_y = half_centres - MOTOR_WIDTH_MM / 2.0
    side_gap = 6.0
    gusset_outer_y = motor_inner_y - side_gap
    gusset_inner_y = gusset_outer_y - BRACKET_GUSSET_THICKNESS_MM
    iso_y = gusset_inner_y - side_gap - ISOLATOR_DIAMETER_MM / 2.0
    iso_x = 40.0
    corners = ((1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0))
    if len(corners) != ISOLATOR_COUNT:
        raise ValueError("isolator count and corner list disagree")
    for index, (sx, sy) in enumerate(corners, start=1):
        vertical_cylinder(
            f"VC-SH-1600-{index}",
            ISOLATOR_DIAMETER_MM / 2.0,
            ISOLATOR_FREE_HEIGHT_MM,
            station["plate_top"],
            rod_x + sx * iso_x,
            rod_y + sy * iso_y,
        )

    # Gussets take the pull. Isolators sit in the gap and do not carry that peel.
    plate_top = station["plate_top"]
    bracket_parts = []
    for sign in (-1.0, 1.0):
        bracket_parts.append(
            span(
                station["web_outer"],
                station["web_outer"] + BRACKET_GUSSET_THICKNESS_MM,
                sign * gusset_inner_y,
                sign * gusset_outer_y,
                plate_top,
                plate_top + BRACKET_GUSSET_HEIGHT_MM,
            )
        )
        bracket_parts.append(
            span(
                station["web_outer"],
                rod_x,
                sign * gusset_inner_y,
                sign * gusset_outer_y,
                plate_top,
                plate_top + BRACKET_GUSSET_THICKNESS_MM,
            )
        )
    bracket_parts.append(
        span(
            station["web_outer"],
            rod_x + 70.0,
            -gusset_outer_y,
            gusset_outer_y,
            plate_top + ISOLATOR_FREE_HEIGHT_MM,
            plate_top + ISOLATOR_FREE_HEIGHT_MM + BRACKET_GUSSET_THICKNESS_MM,
        )
    )
    bolt_y = motor_inner_y + 8.0
    bolt_zs = (
        station["shelf_bottom"] + 60.0,
        station["shelf_bottom"] + 60.0 + BRACKET_BOLT_PITCH_Z_MM,
    )
    bolt_pad = Rot(0, 90, 0) * Cylinder(8.0, 6.0)
    for sign in (-1.0, 1.0):
        for bolt_z in bolt_zs:
            bracket_parts.append(
                Pos(station["web_outer"] + 3.0, sign * bolt_y, bolt_z) * bolt_pad
            )
    add("VC-SH-1350", fuse(bracket_parts), 0.0, 0.0, 0.0)

    vertical_cylinder(
        "VC-SH-1500",
        ADAPTER_OD_MM / 2.0,
        ADAPTER_LENGTH_MM,
        station["adapter_bottom"],
        rod_x,
        rod_y,
    )
    casing = Cylinder(CASING_OD_MM / 2.0, CASING_LENGTH_MM) - Cylinder(
        CASING_ID_MM / 2.0, CASING_LENGTH_MM + 1.0
    )
    add(
        "VC-GP-7100",
        bought("VC-GP-7100", casing),
        rod_x,
        rod_y,
        station["casing_bottom"] + CASING_LENGTH_MM / 2.0,
    )
    add(
        "VC-GP-7200",
        bought("VC-GP-7200", Cylinder(SHOE_OD_MM / 2.0, SHOE_LENGTH_MM)),
        rod_x,
        rod_y,
        station["shoe_bottom"] + SHOE_LENGTH_MM / 2.0,
    )

    # shape_for recentres each half on its own box. Move the flat face back to the rod axis
    # so the two halves meet on the split and stay inside the casing bore.
    carrier_z = station["casing_bottom"] + CASING_LENGTH_MM / 2.0
    for number in ("VC-SP-7620", "VC-SP-7621"):
        part = bom.part(number)
        half = shape_for(part)
        box = half.bounding_box()
        if str(part.geometry["side"]) == "A":
            shift = -float(box.min.X)
        else:
            shift = -float(box.max.X)
        add(number, half, rod_x + shift, rod_y, carrier_z)

    def bored_sprocket():
        disk = along_y(sprocket_r, SPROCKET_WIDTH_MM)
        hole = along_y(SHAFT_DIAMETER_MM / 2.0 + _MODEL_GAP_MM, SPROCKET_WIDTH_MM + 2.0)
        return disk - hole

    add(
        "VC-HB-2800",
        bored_sprocket() if sprocket_solid is None else sprocket_solid,
        drive_x,
        chain_y,
        z_drive,
    )
    add(
        "VC-HB-2810",
        bored_sprocket() if sprocket_solid is None else sprocket_solid,
        drive_x,
        chain_y,
        z_idler,
    )

    strand_z0 = z_drive + sprocket_r + _MODEL_GAP_MM
    strand_z1 = z_idler - sprocket_r - _MODEL_GAP_MM
    chain_vendor = load_vendor_shape("VC-HB-2700")
    if chain_vendor is not None:
        add("VC-HB-2700", chain_vendor, drive_x, 0.0, (strand_z0 + strand_z1) / 2.0)
    else:
        from cad.models.roller_chain import duplex_chain

        tip_r = sprocket_r
        if sprocket_solid is not None:
            import math

            tip_r = max(
                math.hypot(float(vertex.X), float(vertex.Z)) for vertex in sprocket_solid.vertices()
            )
        add(
            "VC-HB-2700",
            duplex_chain(
                z_drive,
                z_idler,
                SPROCKET_PITCH_RADIUS_MM,
                tip_r,
                drive_x,
                _MODEL_GAP_MM,
                chain_y,
            ),
            0.0,
            0.0,
            0.0,
        )

    # Gearbox, then the coupling, then the shaft. The motor is last, on the input face.
    import math

    motor_x = bay["motor_x"]
    z_lift = bay["z_lift"]
    if bay["gear"] is not None:
        # Input face is local Y = 0, so the placement Y is the motor face.
        # The STEP access mouth is a shallow Ø8 dimple. Open it through to the
        # clamp pocket so the clamp screw can be seen. The vendor file is unchanged.
        access = Pos(-17.0, 12.5, -33.25) * Cylinder(3.6, 49.5)
        add("VC-HB-2200", bay["gear"] - access, motor_x, bay["gear_y0"], z_lift)
    else:
        add(
            "VC-HB-2200",
            Box(GEARBOX_FLANGE_MM, GEARBOX_LENGTH_MM, GEARBOX_FLANGE_MM),
            motor_x,
            (bay["gear_y0"] + bay["gear_y1"]) / 2.0,
            z_lift,
        )
    coupling = bay["coupling"]
    if coupling is None:
        coupling = along_y(COUPLING_DIAMETER_MM / 2.0, COUPLING_LENGTH_MM)
    else:
        # The chain-side hub in the STEP is unbored. Open it for the Ø30 shaft.
        cutter = Pos(0.0, 28.0, 0.0) * along_y(SHAFT_DIAMETER_MM / 2.0 + 0.4, 50.0)
        opened = [solid - cutter for solid in coupling.solids()]
        coupling = Compound(children=opened)
    add("VC-HB-2400", coupling, motor_x, bay["coupling_y"], z_lift)

    # One laser-cut 10 mm plate, one bend. No weld, no notch, no inspection window.
    # The upright stops under the carriage. A narrow ear reaches the upper M6
    # behind the rail. The foot lies under the gearbox, in the 10 mm gap.
    face_y = bay["face_y"]
    plate_top = bay["plate_top"]
    short_z0 = bay["short_z0"]
    bend_z = 25.0
    mount = span(motor_x - 55.0, motor_x + 54.0, face_y, face_y + 10.0, bend_z, 100.0)
    ear = span(motor_x - 16.0, motor_x + 15.0, face_y, face_y + 10.0, 100.0, z_lift + 52.0)
    mount = fuse([mount, ear])
    mount = mount - Pos(drive_x, face_y + 5.0, z_lift) * along_y(42.0, 30.0)
    for deg in (0.0, 90.0, 180.0, 270.0):
        angle = math.radians(deg)
        mount = mount - Pos(
            drive_x + 45.0 * math.cos(angle),
            face_y + 5.0,
            z_lift + 45.0 * math.sin(angle),
        ) * along_y(3.3, 30.0)
    foot_plate = span(motor_x - 50.0, motor_x + 50.0, face_y, -136.0, plate_top + 0.2, bend_z)
    for hole_x in (motor_x - 40.0, motor_x + 40.0):
        foot_plate = foot_plate - Pos(hole_x, -143.0, plate_top + 6.0) * Cylinder(4.5, 16.0)
    add("VC-FR-4182", fuse([mount, foot_plate]), 0.0, 0.0, 0.0)

    pillow = _pillow_solid()
    pillow_box = pillow.bounding_box()
    sole_z = z_lift + float(pillow_box.min.Z)
    bolt_dx = PILLOW_BOLT_SPAN_MM / 2.0
    seats = []
    for center_y in (bay["drive_bearing_y"], bay["idle_bearing_y"]):
        seat = span(
            rear_face_x_mm() + 2.0,
            motor_x + 68.0,
            center_y - 18.0,
            center_y + 18.0,
            bay["plate_top"],
            sole_z,
        )
        for sign in (-1.0, 1.0):
            seat = seat - Pos(motor_x + sign * bolt_dx, center_y, (bay["plate_top"] + sole_z) / 2.0) * Cylinder(
                6.5, sole_z - bay["plate_top"] + 4.0
            )
        seats.append(seat)
    for index, seat in enumerate(seats, start=1):
        add(f"VC-FR-4183-{index}", seat, 0.0, 0.0, 0.0)

    # One 40 x 40 x 6 angle. Inner side slots of the idle profile, and two
    # M8 through the bottom plate. No weld. The measured throat is 10.10 mm.
    idle_inner = profile_inner_y
    # Sawn 40 x 40 x 6 angle, 80 mm long. Both legs share that width.
    upright = span(-40.0, 40.0, idle_inner - 6.0, idle_inner - 0.2, 21.2, 61.2)
    sole = span(-40.0, 40.0, idle_inner - 40.0, idle_inner - 0.2, plate_top + 0.2, 21.2)
    for slot_x in (25.0, -25.0):
        upright = upright - Pos(slot_x, idle_inner - 3.0, 48.0) * along_y(4.5, 20.0)
    for hole_x in (-10.0, 10.0):
        sole = sole - Pos(hole_x, 100.0, plate_top + 4.0) * Cylinder(4.5, 16.0)
    add("VC-FR-4184", upright + sole, 0.0, 0.0, 0.0)

    add("VC-HB-2600-1", pillow, motor_x, bay["drive_bearing_y"], z_lift)
    add("VC-HB-2600-2", pillow, motor_x, bay["idle_bearing_y"], z_lift)
    shaft_y0 = bay["shaft_y0"]
    shaft_y1 = bay["shaft_y1"]
    shaft_mid = (shaft_y0 + shaft_y1) / 2.0
    shaft = along_y(SHAFT_DIAMETER_MM / 2.0 - 0.2, shaft_y1 - shaft_y0)
    # Key seat under the sprocket. DIN 6885, 8 mm key, 4 mm into a Ø30 shaft.
    key = Pos(0.0, -shaft_mid, SHAFT_DIAMETER_MM / 2.0 - 2.0) * Box(8.0, 28.0, 4.0)
    add("VC-HB-2500", shaft - key, motor_x, shaft_mid, z_lift)

    from cad.models.vendor_parts import oriented_motor

    motor = oriented_motor()
    if motor is None:
        add(
            "VC-HB-2100",
            Box(SERVO_FLANGE_MM, SERVO_BODY_LENGTH_MM, SERVO_FLANGE_MM),
            motor_x,
            bay["motor_y"],
            z_lift,
        )
    else:
        # Local Y = 0 is the flange face. The shaft enters the gearbox.
        add("VC-HB-2100", motor, motor_x, bay["gear_y0"], z_lift)
        # Flange back is at local Y = -6.4 mm. Thread depth on the adapter is 15 mm.
        # Length 16 mm gives 9.6 mm of thread. 1.5 x 6 mm is 9 mm, so M6x16 is enough.
        # Heads sit 0.2 mm off the flange. Shanks sit in the Ø6.6 holes, on PCD 90 mm.
        pcd = 45.0 / math.sqrt(2.0)
        screw_index = 0
        for sign_x in (-1.0, 1.0):
            for sign_z in (-1.0, 1.0):
                screw_index += 1
                shank = along_y(2.4, 15.6)
                head = Pos(0.0, -11.2, 0.0) * along_y(5.0, 6.0)
                add(
                    f"VC-HB-2120-{screw_index}",
                    shank + head,
                    motor_x + sign_x * pcd,
                    bay["gear_y0"] + 1.6,
                    z_lift + sign_z * pcd,
                )
        # Clamp screw near the mouth of the access hole so it can be seen.
        # Size, torque and the true seat at the hub are not in the vendor folder.
        # The plug is pulled 4.5 mm clear of the mouth.
        clamp_shank = Cylinder(2.0, 12.0)
        clamp_head = Pos(0.0, 0.0, -8.0) * Cylinder(3.0, 4.0)
        add(
            "VC-HB-2122",
            clamp_shank + clamp_head,
            motor_x - 17.0,
            bay["gear_y0"] + 12.5,
            z_lift - 40.0,
        )
        add(
            "VC-HB-2124",
            Cylinder(3.4, 4.0),
            motor_x - 17.0,
            bay["gear_y0"] + 12.5,
            z_lift - 64.0,
        )

    profile_top = station["profile_top"]
    cap = 8.0
    # Upper mount. Two caps, a rear bridge, and one lip on each inner side slot.
    # Slot bolts replace the end threads. No weld.
    caps = []
    for sign in (-1.0, 1.0):
        inner = sign * profile_inner_y
        cap_solid = span(
            rear_face_x_mm(),
            front,
            sign * profile_inner_y,
            sign * profile_outer_y,
            profile_top + 0.2,
            profile_top + cap,
        )
        hanger = span(10.0, 40.0, inner - sign * 6.0, inner - sign * 0.2, profile_top - 28.0, profile_top + 0.2)
        tab = span(10.0, 40.0, inner - sign * 6.0, inner + sign * 5.0, profile_top + 0.2, profile_top + cap - 0.2)
        hanger = hanger - Pos(25.0, inner - sign * 3.0, profile_top - 16.0) * along_y(4.5, 20.0)
        caps.append(fuse([cap_solid, hanger, tab]))
    caps.append(
        span(
            rear_face_x_mm() + 2.0,
            -16.0,
            -profile_inner_y - 2.0,
            profile_inner_y + 2.0,
            profile_top + 0.2,
            profile_top + cap,
        )
    )
    add("VC-FR-4198", fuse(caps), 0.0, 0.0, 0.0)

    # Idler on the cap. The cheek sits beside the sprocket, toward the mast.
    add(
        "VC-HB-2820",
        along_y(SHAFT_DIAMETER_MM / 2.0, 70.0),
        drive_x,
        chain_y + 8.0,
        z_idler,
    )
    foot = span(-30.0, drive_x + 62.0, -profile_outer_y, -profile_inner_y, profile_top + cap, profile_top + cap + 8.0)
    arm = span(
        drive_x + 46.0,
        drive_x + 62.0,
        -profile_outer_y,
        chain_y + 32.0,
        profile_top + cap,
        profile_top + cap + 14.0,
    )
    cheek = span(drive_x - 22.0, drive_x + 62.0, chain_y + 18.0, chain_y + 32.0, z_idler - 24.0, z_idler + 24.0)
    hole = Pos(drive_x, chain_y + 25.0, z_idler) * along_y(
        SHAFT_DIAMETER_MM / 2.0 + _MODEL_GAP_MM, 80.0
    )
    add("VC-HB-2830-1", foot + arm + cheek - hole, 0.0, 0.0, 0.0)
    # One box. The old disc was the grey wire frame in FreeCAD.
    add("VC-HB-2900", Box(40.0, 30.0, 57.0), drive_x + 90.0, chain_y, profile_top + cap + 70.0)

    # Slot nuts in the 10.10 mm throats. Screws stop short of the nuts.
    # Through-bolt nuts sit under the plate, clear of the 0.5 mm datum skin.
    nut_i = 0
    screw_i = 0
    hex_i = 0
    m6_i = 0

    def add_screw(x0, y0, z0, x1, y1, z1, radius=3.9, prefix="VC-FR-4121"):
        nonlocal screw_i
        screw_i += 1
        length = math.dist((x0, y0, z0), (x1, y1, z1))
        mx, my, mz = (x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0
        dx, dy, dz = abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
        if dz >= dx and dz >= dy:
            blank = Cylinder(radius, length)
        elif dx >= dy:
            blank = Rot(0, 90, 0) * Cylinder(radius, length)
        else:
            blank = along_y(radius, length)
        add(f"{prefix}-{screw_i}", blank, mx, my, mz)

    def add_slot_nut(x, y, z):
        nonlocal nut_i
        nut_i += 1
        # 8 mm across the 10.10 mm throat, 6 mm into the slot, 5 mm along Z.
        add(f"VC-FR-4120-{nut_i}", Box(8.0, 6.0, 5.0), x, y, z)

    def add_hex_nut(x, y):
        nonlocal hex_i
        hex_i += 1
        add(f"VC-FR-4124-{hex_i}", Box(13.0, 13.0, 6.8), x, y, -4.4)

    for sign in (-1.0, 1.0):
        inner = sign * profile_inner_y
        z_nut = profile_top - 16.0
        add_slot_nut(25.0, inner + sign * 4.0, z_nut)
        add_screw(25.0, inner - sign * 12.0, z_nut, 25.0, inner + sign * 1.0, z_nut)
    for slot_x in (25.0, -25.0):
        add_slot_nut(slot_x, idle_inner + 4.0, 48.0)
        add_screw(slot_x, idle_inner - 12.0, 48.0, slot_x, idle_inner + 1.0, 48.0)
    for hole_x in (motor_x - 40.0, motor_x + 40.0):
        add_screw(hole_x, -143.0, 2.0, hole_x, -143.0, 24.5)
        add_hex_nut(hole_x, -143.0)
    for hole_x in (-10.0, 10.0):
        add_screw(hole_x, 100.0, 2.0, hole_x, 100.0, 20.5)
        add_hex_nut(hole_x, 100.0)
    # Plate is 10 mm. Thread depth on the output flange is 15 mm.
    # M6x20 leaves 10 mm in the thread, more than 1.5 x 6 mm.
    # The shank stays inside the plate. The STEP output circle is Ø100 mm.
    for deg in (0.0, 90.0, 180.0, 270.0):
        angle = math.radians(deg)
        m6_i += 1
        add(
            f"VC-FR-4125-{m6_i}",
            along_y(2.5, 8.0),
            drive_x + 45.0 * math.cos(angle),
            face_y + 5.0,
            z_lift + 45.0 * math.sin(angle),
        )

    # Sheets above the rails. No bracket windows.
    stiffener_z0 = station["rail_top"] + 15.0
    add(
        "VC-FR-4190",
        span(front, front + GUSSET_SHEET_THICKNESS_MM, -profile_outer_y, profile_outer_y, stiffener_z0, profile_top),
        0.0,
        0.0,
        0.0,
    )
    add(
        "VC-FR-4195",
        span(
            rear_face_x_mm() - GUSSET_SHEET_THICKNESS_MM,
            rear_face_x_mm(),
            -profile_outer_y,
            profile_outer_y,
            stiffener_z0,
            profile_top,
        ),
        0.0,
        0.0,
        0.0,
    )
    front_top = station["rail_bottom"] - CARRIAGE_PLATE_THICKNESS_MM - 2.0
    # Idle front only. The drive front is the gearbox bay, under the short upright.
    add(
        "VC-FR-4185",
        span(front, front + GUSSET_SHEET_THICKNESS_MM, profile_inner_y, profile_outer_y, plate_top, front_top),
        0.0,
        0.0,
        0.0,
    )
    # Removable rear panel. Four slot bolts. No window in the mount plate.
    # The drive profile starts at the short upright, so that side has a tab.
    rear = rear_face_x_mm()
    panel = span(
        rear - GUSSET_SHEET_THICKNESS_MM,
        rear,
        -profile_outer_y,
        profile_outer_y,
        plate_top,
        short_z0 - 0.2,
    )
    panel = panel + span(
        rear - GUSSET_SHEET_THICKNESS_MM,
        rear,
        -profile_outer_y,
        -profile_inner_y,
        short_z0 - 0.2,
        210.0,
    )
    rear_bolts = (
        (half_pitch, 50.0),
        (half_pitch, 110.0),
        (-half_pitch, 160.0),
        (-half_pitch, 195.0),
    )
    hole_axis = Rot(0, 90, 0) * Cylinder(4.5, 8.0)
    for slot_y, slot_z in rear_bolts:
        panel = panel - Pos(rear - 2.0, slot_y, slot_z) * hole_axis
    add("VC-FR-4186", panel, 0.0, 0.0, 0.0)
    for slot_y, slot_z in rear_bolts:
        # Shank stays in the sheet hole, behind the rear face. The nut sits in the slot.
        add_screw(rear - 3.6, slot_y, slot_z, rear - 0.2, slot_y, slot_z)
        nut_i += 1
        add(f"VC-FR-4120-{nut_i}", Box(6.0, 8.0, 5.0), rear + 4.0, slot_y, slot_z)

    _check_pose(parts, station)
    return parts

def assembly_shape(bom=None, stroke_mm: float | None = None):
    from build123d import Compound

    parts = assembly_parts(bom, stroke_mm=stroke_mm)
    compound = Compound(children=[item.shape for item in parts])
    compound.label = ASSEMBLY_ID
    return compound


def _check_pose(parts: list[Placed], station: dict[str, float]) -> None:
    from cad.tools.geometry import vendor_step_path

    by_name = {item.name: item.shape for item in parts}
    long_profile = by_name["VC-FR-4100-2"].bounding_box()
    short_profile = by_name["VC-FR-4100-1"].bounding_box()
    profile = long_profile
    if vendor_step_path("VC-FR-4100") is None:
        for box in (long_profile, short_profile):
            size_x = float(box.max.X - box.min.X)
            size_y = float(box.max.Y - box.min.Y)
            if abs(size_x - MAST_PROFILE_DEPTH_MM) > 0.05:
                raise ValueError("profile is not yawed; the 100 mm side is not along X")
            if abs(size_y - MAST_PROFILE_WIDTH_MM) > 0.05:
                raise ValueError("profile is not yawed; the 50 mm side is not along Y")
            if abs(float(box.max.X) - profile_front_x_mm()) > 0.05:
                raise ValueError("profile front face is not the +X face")
        long_z = float(long_profile.max.Z - long_profile.min.Z)
        short_z = float(short_profile.max.Z - short_profile.min.Z)
        if abs(long_z - MAST_PROFILE_LENGTH_MM) > 0.05:
            raise ValueError("the idle-side profile is not the 1500 mm tube")
        if short_z > long_z - 1.0:
            raise ValueError("the drive-side profile was not cut short")
        if abs(float(long_profile.max.Z) - float(short_profile.max.Z)) > 0.05:
            raise ValueError("the short profile does not reach the same top")
    for obsolete in ("VC-FR-4150", "VC-FR-4160", "VC-FR-4170", "VC-FR-4180"):
        if obsolete in by_name:
            raise ValueError(f"{obsolete} is obsolete and must not be placed")
    cap = by_name["VC-FR-4198"].bounding_box()
    if float(cap.min.Y) > -PROFILE_SPACING_MM / 2.0 or float(cap.max.Y) < PROFILE_SPACING_MM / 2.0:
        raise ValueError("upper mount does not reach both profiles")
    rail = by_name["VC-HB-3100-1"].bounding_box()
    if float(rail.min.X) + 0.05 < float(profile.max.X):
        raise ValueError("rail is not on the profile front face")
    runners = [by_name[f"VC-HB-3110-{index}"] for index in range(1, RUNNER_COUNT + 1)]
    for runner in runners:
        box = runner.bounding_box()
        if float(box.min.Z) < station["rail_bottom"] - 0.05:
            raise ValueError("runner hangs below the rail")
        if float(box.max.Z) > station["rail_top"] + 0.05:
            raise ValueError("runner hangs above the rail")
        if float(box.min.X) > float(rail.max.X):
            raise ValueError("runner does not engage the rail")
    if abs(station["stroke"] - GUIDED_TRAVEL_MM) < 0.05:
        upper = max(float(runner.bounding_box().max.Z) for runner in runners)
        if abs(upper - station["rail_top"]) > 0.05:
            raise ValueError("start pose is not the top of the guided stroke")
    shoe = by_name["VC-GP-7200"].bounding_box()
    if abs(float(shoe.min.Z) - station["shoe_bottom"]) > 0.05:
        raise ValueError("shoe tip does not match the guided pose")
    plate = by_name["VC-SH-1301"].bounding_box()
    if abs(float(plate.max.X - plate.min.X) - VIBRATING_PLATE_WIDTH_MM) > 0.05:
        raise ValueError("vibrating plate is not yawed; the 300 mm side is not along X")
    if abs(float(plate.max.Y - plate.min.Y) - VIBRATING_PLATE_LENGTH_MM) > 0.05:
        raise ValueError("vibrating plate length is not along Y")
    if abs(float(plate.min.X) - plate_rear_x_mm()) > 0.05:
        raise ValueError("vibrating plate rear is not flush with the motor rear")
    bottom = by_name["VC-FR-4300"].bounding_box()
    if float(bottom.max.X) < station["rod_x"] + CASING_GUIDE_BORE_DIAMETER_MM / 2.0:
        raise ValueError("bottom plate does not reach past the guide bore")
    motors = [by_name["VC-SH-1100-1"], by_name["VC-SH-1100-2"]]
    centres = []
    for motor in motors:
        box = motor.bounding_box()
        if vendor_step_path("VC-SH-1100") is not None:
            centres.append(float(box.center().Y))
            continue
        if abs(float(box.max.Z - box.min.Z) - MOTOR_HEIGHT_MM) > 0.05:
            raise ValueError("motor height is not vertical")
        if abs(float(box.max.X - box.min.X) - MOTOR_LENGTH_MM) > 0.05:
            raise ValueError("motor shaft is not along X")
        if abs(float(box.max.Y - box.min.Y) - MOTOR_WIDTH_MM) > 0.05:
            raise ValueError("motor width is not along Y")
        if abs(float(box.min.X) - plate_rear_x_mm()) > 0.05:
            raise ValueError("motor rear is not on the plate rear")
        centres.append(float(box.center().Y))
    pitch = abs(centres[0] - centres[1])
    if pitch + 0.05 < MOTOR_CENTRE_DISTANCE_MIN_MM:
        raise ValueError("motor centre distance is below 170 mm")
    if vendor_step_path("VC-SH-1100") is None and abs(pitch - MOTOR_CENTRE_DISTANCE_MM) > 0.05:
        raise ValueError("motor centre distance does not match the shared parameter")
    if COLUMN_FLANGE_DIAMETER_MM > pitch - MOTOR_WIDTH_MM + 0.05:
        raise ValueError("column flange does not fit between the motors")
    lift = by_name["VC-HB-2100"].bounding_box()
    lift_span = float(lift.max.Y - lift.min.Y)
    shaft_span = SERVO_BODY_LENGTH_MM + SERVO_SHAFT_LENGTH_MM
    if abs(lift_span - shaft_span) <= 0.5:
        flange_y = float(lift.min.Y) + SERVO_BODY_LENGTH_MM
    else:
        if abs(lift_span - SERVO_BODY_LENGTH_MM) > 0.05:
            raise ValueError("lift motor axis is not parallel to the sprocket shaft")
        flange_y = float(lift.max.Y)
    if abs(float(lift.max.X - lift.min.X) - SERVO_FLANGE_MM) > 0.05:
        raise ValueError("lift motor flange is not the datasheet square")
    if float(lift.min.X) < rear_face_x_mm() - 0.05:
        raise ValueError("lift motor enters the reserved rear volume")
    gear = by_name["VC-HB-2200"].bounding_box()
    if vendor_step_path("VC-HB-2200") is not None:
        if abs(float(gear.max.Y - gear.min.Y) - GEARBOX_LENGTH_MM) > 0.05:
            raise ValueError("gearbox length is not 204 mm")
        if abs(float(gear.min.Y) - flange_y) > 0.05:
            raise ValueError("motor flange does not meet the gearbox input")
        if float(gear.min.X) < rear_face_x_mm() - 0.05:
            raise ValueError("gearbox enters the reserved rear volume")
        sprocket = by_name["VC-HB-2800"].bounding_box()
        if abs(float(sprocket.center().Y)) > 0.5:
            raise ValueError("drive sprocket is not on the machine centre")
        if abs(float(sprocket.center().X) - float(gear.center().X)) > 0.5:
            raise ValueError("drive sprocket is not on the gearbox axis")
        if abs(float(sprocket.center().Z) - float(gear.center().Z)) > 0.5:
            raise ValueError("drive sprocket is not on the gearbox axis")
        if float(sprocket.min.Y) < float(gear.max.Y):
            raise ValueError("drive sprocket still sits on the gearbox shaft")
        plate = by_name["VC-FR-4182"].bounding_box()
        shaft_root = float(gear.max.Y) - OUTPUT_SHAFT_LENGTH_MM
        if abs(float(plate.min.Y) - shaft_root) > 0.5:
            raise ValueError("mount plate does not meet the output flange")
        if float(plate.min.Z) > BOTTOM_PLATE_THICKNESS_MM + 0.5:
            raise ValueError("mount plate does not reach the bottom plate")
    if "VC-HB-3000" in by_name:
        raise ValueError("the separate brake is obsolete and must not be placed")
    if vendor_step_path("VC-HB-2800") is None:
        sprocket = by_name["VC-HB-2800"].bounding_box()
        if abs(float(sprocket.max.Y - sprocket.min.Y) - SPROCKET_WIDTH_MM) > 0.05:
            raise ValueError("drive sprocket axis is not along Y")
        if float(sprocket.min.X) < rear_face_x_mm() - 0.05:
            raise ValueError("drive sprocket enters the reserved rear volume")
        if abs(float(sprocket.center().X) - chain_axis_x_mm()) > 0.05:
            raise ValueError("drive sprocket is not on the gearbox axis")
    rear = rear_face_x_mm()
    for item in parts:
        if item.name == "GROUND-DATUM":
            continue
        box = item.shape.bounding_box()
        low_x = float(box.min.X)
        high_x = float(box.max.X)
        in_sheet = high_x <= rear + 0.05 and low_x >= rear - GUSSET_SHEET_THICKNESS_MM - 0.05
        if item.name.startswith("VC-FR-4195") or item.name.startswith("VC-FR-4186") or in_sheet:
            if low_x < rear - GUSSET_SHEET_THICKNESS_MM - 0.05:
                raise ValueError("rear stiffener is thicker than the draft sheet")
            continue
        if low_x < rear - 0.05:
            raise ValueError(f"{item.name} enters the reserved rear volume")
    shaft_box = by_name["VC-HB-2500"].bounding_box()
    gear_box = by_name["VC-HB-2200"].bounding_box()
    sprocket_box = by_name["VC-HB-2800"].bounding_box()
    bearing_centres = []
    for name in ("VC-HB-2600-1", "VC-HB-2600-2"):
        foot = by_name[name].bounding_box()
        if float(foot.min.Z) < BOTTOM_PLATE_THICKNESS_MM - 0.05:
            raise ValueError("bearing foot is below the bottom plate")
        if abs(float(foot.center().X) - float(shaft_box.center().X)) > 0.5:
            raise ValueError("bearing is not on the Ø30 shaft")
        if abs(float(shaft_box.center().Z) - (float(foot.min.Z) + PILLOW_CENTER_HEIGHT_MM)) > 0.2:
            raise ValueError("bearing shaft is not at the catalogue centre height")
        bearing_centres.append(float(foot.center().Y))
    if min(bearing_centres) >= float(sprocket_box.center().Y) or max(bearing_centres) <= float(sprocket_box.center().Y):
        raise ValueError("the sprocket is not between the two bearings")
    if abs(float(shaft_box.center().X) - float(gear_box.center().X)) > 0.5:
        raise ValueError("Ø30 shaft is not on the gearbox axis")
    if "VC-HB-2400" not in by_name:
        raise ValueError("the ROTEX coupling is not placed")


def _boxes_overlap(left, right, pad: float = 0.2) -> bool:
    a = left.bounding_box()
    b = right.bounding_box()
    return not (
        a.max.X < b.min.X - pad
        or a.min.X > b.max.X + pad
        or a.max.Y < b.min.Y - pad
        or a.min.Y > b.max.Y + pad
        or a.max.Z < b.min.Z - pad
        or a.min.Z > b.max.Z + pad
    )


def _leaf_solids(shape) -> list:
    """Solids inside a compound. A compound intersect can report a false volume."""
    solids = [item for item in shape.solids() if abs(item.volume) > 1.0] if hasattr(shape, "solids") else []
    return solids or [shape]


def intersection_volume_mm3(left, right) -> float:
    """Shared solid volume. Face contact and a missed pair both return 0."""
    if not _boxes_overlap(left, right):
        return 0.0
    total = 0.0
    for leaf in _leaf_solids(left):
        if not _boxes_overlap(leaf, right):
            continue
        for other in _leaf_solids(right):
            if not _boxes_overlap(leaf, other):
                continue
            common = leaf.intersect(other)
            if common is None:
                continue
            shapes = common.solids() if hasattr(common, "solids") else [common]
            for shape in shapes:
                total += abs(float(shape.volume))
    return total


def shape_distance_mm(left, right) -> float:
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape

    tool = BRepExtrema_DistShapeShape(left.wrapped, right.wrapped)
    tool.Perform()
    if not tool.IsDone():
        raise RuntimeError("shape distance failed")
    return float(tool.Value())


def overlap_pairs(parts: list[Placed] | None = None, bom=None) -> list[tuple[str, str, float]]:
    """Pairs whose shared volume is above the tolerance. Face contact is not an overlap."""
    items = parts if parts is not None else assembly_parts(bom)
    hits = []
    for index, left in enumerate(items):
        for right in items[index + 1 :]:
            if left.name == "GROUND-DATUM" or right.name == "GROUND-DATUM":
                continue
            volume = intersection_volume_mm3(left.shape, right.shape)
            if volume > OVERLAP_TOLERANCE_MM3:
                hits.append((left.name, right.name, volume))
    return hits


def split_overlaps(parts: list[Placed] | None = None, bom=None):
    """Unexpected overlaps, then the known motor-to-gearbox fit."""
    other = []
    known = []
    for left, right, volume in overlap_pairs(parts, bom):
        if frozenset((left, right)) in KNOWN_OVERLAP_PAIRS:
            known.append((left, right, volume))
        else:
            other.append((left, right, volume))
    return other, known


def _find(parts: list[Placed], name: str):
    for item in parts:
        if item.name == name:
            return item.shape
    raise KeyError(name)


def clearance_report(parts: list[Placed] | None = None, bom=None) -> dict[str, float]:
    """Clearances in millimetres. Profile pitch and several envelopes are TBD."""
    items = parts if parts is not None else assembly_parts(bom)
    station = visual_stations()
    profiles = [item.shape for item in items if item.name.startswith("VC-FR-4100-")]
    profile = max(profiles, key=lambda shape: float(shape.bounding_box().size.Z))
    bottom = _find(items, "VC-FR-4300")
    stiffener = _find(items, "VC-FR-4195")
    shoe = _find(items, "VC-GP-7200")
    casing = _find(items, "VC-GP-7100")
    motor = _find(items, "VC-SH-1100-1")
    rail = _find(items, "VC-HB-3100-1")
    carriage = _find(items, "VC-HB-3200")
    chains = [item.shape for item in items if item.name.startswith("VC-HB-2700")]
    chain = max(chains, key=lambda shape: float(shape.bounding_box().center().X))
    profile_box = profile.bounding_box()
    bottom_box = bottom.bounding_box()
    rail_box = rail.bounding_box()
    outer_y = max(abs(float(profile_box.min.Y)), abs(float(profile_box.max.Y)))
    chain_min_x = min(float(shape.bounding_box().min.X) for shape in chains)
    lift = _find(items, "VC-HB-2100")
    return {
        "shoe_to_profile_mm": _mm(shape_distance_mm(shoe, profile)),
        "casing_to_profile_mm": _mm(shape_distance_mm(casing, profile)),
        "casing_to_bottom_plate_mm": round(shape_distance_mm(casing, bottom), 3),
        "motor_to_profile_mm": _mm(min(shape_distance_mm(motor, item) for item in profiles)),
        "motor_to_rail_mm": _mm(shape_distance_mm(motor, rail)),
        "motor_to_carriage_mm": _mm(shape_distance_mm(motor, carriage)),
        "plate_bottom_vs_lower_block_mm": _mm(station["plate_bottom"] - station["lower_bottom"]),
        "carriage_to_chain_mm": _mm(shape_distance_mm(carriage, chain)),
        "shoe_tip_z_mm": _mm(float(shoe.bounding_box().min.Z)),
        "profile_overhang_past_bottom_plate_mm": _mm(outer_y - float(bottom_box.max.Y)),
        "chain_min_x_mm": _mm(chain_min_x),
        "rear_face_x_mm": rear_face_x_mm(),
        "rear_stiffener_min_x_mm": _mm(float(stiffener.bounding_box().min.X)),
        "lift_motor_min_x_mm": _mm(float(lift.bounding_box().min.X)),
        "guided_travel_mm": _mm(GUIDED_TRAVEL_MM),
        "stroke_position_mm": _mm(station["stroke"]),
        "rod_axis_x_mm": _mm(station["rod_x"]),
        "rod_overhang_from_rail_mm": _mm(station["rod_x"] - float(rail_box.max.X)),
        "guide_bore_diameter_mm": CASING_GUIDE_BORE_DIAMETER_MM,
        "guide_radial_clearance_mm": guide_radial_clearance_mm(),
        "posed_stack_mm": posed_stack_height_mm(),
        "required_mm": required_total_mm(),
        "rail_top_mm": _mm(station["rail_top"]),
        "profile_size_x_mm": _mm(float(profile_box.max.X - profile_box.min.X)),
        "profile_size_y_mm": _mm(float(profile_box.max.Y - profile_box.min.Y)),
        "profile_size_z_mm": _mm(float(profile_box.max.Z - profile_box.min.Z)),
    }


def assembly_bbox_mm(shape=None, bom=None) -> tuple[float, float, float]:
    solid = shape if shape is not None else assembly_shape(bom)
    size = solid.bounding_box().size
    return (float(size.X), float(size.Y), float(size.Z))


def export_machine_assembly(bom, step_dir: Path, render_dir: Path) -> list[Path]:
    """Write the assembly STEP, the three PNG views, two drive views and two joint close-ups."""
    from build123d import Compound, export_step

    from cad.tools.geometry import _freeze_step_header

    parts = assembly_parts(bom)
    step_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    shape = Compound(children=[item.shape for item in parts])
    shape.label = ASSEMBLY_ID
    step_path = step_dir / STEP_NAME
    export_step(shape, step_path)
    _freeze_step_header(step_path, ASSEMBLY_ID, bom.meta["cad_baseline_date"])
    _write_z_up_step(step_path)
    written = [step_path]
    for view in RENDER_VIEWS:
        path = render_dir / f"{ASSEMBLY_ID}-{view}.png"
        _render_png(parts, view, path)
        written.append(path)
    # Close-ups of the gearbox, the sprocket and the mount. X, Y, Z limits in mm.
    # Z starts above the datum so the ground plane does not fight the plate.
    # Z stops just above the sprocket so the chain strands do not hide the train.
    drive_clip = (-80.0, 180.0, -560.0, 120.0, 12.0, 145.0)
    for view in ("drive-iso", "drive-front"):
        path = render_dir / f"{ASSEMBLY_ID}-{view}.png"
        _render_png(parts, view, path, clip=drive_clip)
        written.append(path)
    gear = next(item.shape for item in parts if item.name == "VC-HB-2200")
    box = gear.bounding_box()
    # Motor flange, four screws, the open access hole and the pulled plug.
    joint_clip = (
        float(box.min.X) - 6.0,
        float(box.max.X) + 6.0,
        float(box.min.Y) - 30.0,
        float(box.min.Y) + 52.0,
        float(box.min.Z) - 16.0,
        float(box.max.Z) + 4.0,
    )
    for view in ("joint", "joint-access"):
        path = render_dir / f"{ASSEMBLY_ID}-{view}.png"
        _render_png(parts, view, path, clip=joint_clip)
        written.append(path)
    return written


def render_paths() -> list[Path]:
    return [RENDER_DIR / f"{ASSEMBLY_ID}-{view}.png" for view in RENDER_VIEWS]


def _write_z_up_step(path: Path) -> None:
    """Keep the mast on +Z. Drop negative zeros in direction triples.

    A negative zero in a reference direction is still +X geometrically.
    Some STEP readers rebuild the frame from that token and lay the mast over.
    The solids are not rotated.
    """
    import re

    text = path.read_text(encoding="utf-8")
    cleaned = re.sub(r"-0\.(?!\d)", "0.", text)
    if "DIRECTION('',(0.,0.,1.))" not in cleaned:
        raise ValueError(f"{path} has no +Z axis direction")
    if re.search(r"-0\.(?!\d)", cleaned):
        raise ValueError(f"{path} still has a negative zero")
    path.write_text(cleaned, encoding="utf-8")


def _render_png(parts: list[Placed], view: str, path: Path, clip: tuple[float, ...] | None = None) -> None:
    import numpy as np
    from PIL import Image

    eyes = {
        "iso": (np.array([1.0, -1.0, 0.72]), np.array([0.0, 0.0, 1.0])),
        "side": (np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])),
        "top": (np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0])),
        # Mostly along +X so the shaft axis (Y) reads left to right.
        "drive-iso": (np.array([0.90, 0.15, 0.35]), np.array([0.0, 0.0, 1.0])),
        "drive-front": (np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])),
        # Flange heads from the motor side.
        "joint": (np.array([0.35, -0.85, -0.40]), np.array([0.0, 0.0, 1.0])),
        # Underside of the adapter. The plug and the clamp screw sit on this face.
        "joint-access": (np.array([0.25, -0.55, -0.80]), np.array([0.0, 1.0, 0.0])),
    }
    eye, up = eyes[view]
    forward = -eye / np.linalg.norm(eye)
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    true_up = np.cross(right, forward)
    light = np.array([0.45, -0.35, 0.82])
    light = light / np.linalg.norm(light)

    triangles = []
    shades = []
    for item in parts:
        color = _color_for(item.name)
        # A compound mesh can come back empty. Mesh each solid on its own.
        leaves = [solid for solid in item.shape.solids() if abs(solid.volume) > 1.0]
        meshes = []
        for solid in leaves or [item.shape]:
            # Some vendor faces do not mesh at the default angular tolerance.
            try:
                meshes.append(solid.tessellate(1.8, 0.5))
            except Exception:
                meshes.append(solid.tessellate(1.8, 0.8))
        for vertices, faces in meshes:
            if not faces:
                continue
            points = np.array([(vertex.X, vertex.Y, vertex.Z) for vertex in vertices], dtype=np.float64)
            for face in faces:
                tri = points[list(face)]
                normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
                norm = np.linalg.norm(normal)
                longest = max(
                    float(np.linalg.norm(tri[1] - tri[0])),
                    float(np.linalg.norm(tri[2] - tri[1])),
                    float(np.linalg.norm(tri[0] - tri[2])),
                )
                # A sliver from a cone or a spline seam. Its area is ~0.
                # The painter then fills a long needle.
                if longest < 1e-9 or norm < 1e-3 * longest * longest:
                    continue
                shade = 0.38 + 0.62 * abs(float(np.dot(normal / norm, light)))
                pieces = [tri]
                if clip is not None:
                    # Keep the part of the triangle that sits in the window.
                    # A centre test draws the whole triangle, including the
                    # ground plane and any sliver whose centre happens to fall inside.
                    pieces = _clip_triangle(tri, clip)
                rgb = (color[0] * shade, color[1] * shade, color[2] * shade)
                for piece in pieces:
                    cam = np.column_stack(
                        (
                            piece @ right,
                            piece @ true_up,
                            piece @ -forward,
                        )
                    )
                    triangles.append(cam)
                    shades.append(rgb)

    width, height = 960, 720
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:, :] = (236, 236, 232)
    depth = np.full((height, width), -1e30, dtype=np.float64)
    if not triangles:
        raise ValueError("assembly render has no triangles")
    cloud = np.concatenate(triangles, axis=0)
    span_x = float(cloud[:, 0].max() - cloud[:, 0].min())
    span_y = float(cloud[:, 1].max() - cloud[:, 1].min())
    span_x = max(span_x, 1.0)
    span_y = max(span_y, 1.0)
    scale = min((width * 0.88) / span_x, (height * 0.88) / span_y)
    center_x = float(cloud[:, 0].min() + cloud[:, 0].max()) / 2.0
    center_y = float(cloud[:, 1].min() + cloud[:, 1].max()) / 2.0

    for tri, color in zip(triangles, shades):
        px = width / 2.0 + (tri[:, 0] - center_x) * scale
        py = height / 2.0 - (tri[:, 1] - center_y) * scale
        z = tri[:, 2]
        _paint_triangle(image, depth, px, py, z, color)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image, mode="RGB").save(path, format="PNG", compress_level=9, optimize=False)


def _clip_triangle(tri, clip):
    """Cut one triangle to an axis-aligned box. Return zero or more triangles."""
    import numpy as np

    poly = [tri[0], tri[1], tri[2]]
    planes = (
        (0, clip[0], True),
        (0, clip[1], False),
        (1, clip[2], True),
        (1, clip[3], False),
        (2, clip[4], True),
        (2, clip[5], False),
    )
    for axis, limit, keep_above in planes:
        if len(poly) < 3:
            return []
        nxt = []
        for index, curr in enumerate(poly):
            prev = poly[index - 1]
            if keep_above:
                curr_in = float(curr[axis]) >= limit - 1e-7
                prev_in = float(prev[axis]) >= limit - 1e-7
            else:
                curr_in = float(curr[axis]) <= limit + 1e-7
                prev_in = float(prev[axis]) <= limit + 1e-7
            if curr_in != prev_in:
                delta = float(curr[axis] - prev[axis])
                if abs(delta) > 1e-12:
                    t = (limit - float(prev[axis])) / delta
                    nxt.append(prev + (curr - prev) * t)
            if curr_in:
                nxt.append(curr)
        poly = nxt
    if len(poly) < 3:
        return []
    out = []
    for index in range(1, len(poly) - 1):
        piece = np.stack((poly[0], poly[index], poly[index + 1]))
        if np.linalg.norm(np.cross(piece[1] - piece[0], piece[2] - piece[0])) < 1e-6:
            continue
        out.append(piece)
    return out


def _paint_triangle(image, depth, px, py, z, color) -> None:
    import numpy as np

    height, width = depth.shape
    min_x = max(int(np.floor(px.min())), 0)
    max_x = min(int(np.ceil(px.max())), width - 1)
    min_y = max(int(np.floor(py.min())), 0)
    max_y = min(int(np.ceil(py.max())), height - 1)
    if min_x > max_x or min_y > max_y:
        return
    xs = np.arange(min_x, max_x + 1, dtype=np.float64) + 0.5
    ys = np.arange(min_y, max_y + 1, dtype=np.float64) + 0.5
    grid_x, grid_y = np.meshgrid(xs, ys)
    x0, x1, x2 = px
    y0, y1, y2 = py
    denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(float(denom)) < 1e-8:
        return
    w0 = ((y1 - y2) * (grid_x - x2) + (x2 - x1) * (grid_y - y2)) / denom
    w1 = ((y2 - y0) * (grid_x - x2) + (x0 - x2) * (grid_y - y2)) / denom
    w2 = 1.0 - w0 - w1
    inside = (w0 >= -0.001) & (w1 >= -0.001) & (w2 >= -0.001)
    if not inside.any():
        return
    zee = w0 * z[0] + w1 * z[1] + w2 * z[2]
    window = depth[min_y : max_y + 1, min_x : max_x + 1]
    update = inside & (zee > window)
    window[update] = zee[update]
    rgb = np.array(color, dtype=np.float64)
    patch = image[min_y : max_y + 1, min_x : max_x + 1]
    patch[update] = np.clip(rgb, 0, 255).astype(np.uint8)


def _color_for(name: str) -> tuple[int, int, int]:
    table = (
        ("GROUND-DATUM", (210, 206, 196)),
        ("VC-FR-4195", (100, 116, 139)),
        ("VC-FR-4190", (100, 116, 139)),
        ("VC-FR-4186", (100, 116, 139)),
        ("VC-FR-4185", (100, 116, 139)),
        ("VC-FR-4184", (30, 41, 59)),
        ("VC-FR-4183", (51, 65, 85)),
        ("VC-FR-4198", (71, 85, 105)),
        ("VC-FR-4125", (30, 41, 59)),
        ("VC-FR-4124", (203, 213, 225)),
        ("VC-FR-4121", (30, 41, 59)),
        ("VC-FR-4120", (203, 213, 225)),
        ("VC-FR-4182", (71, 85, 105)),
        ("VC-FR-4180", (148, 163, 184)),
        ("VC-FR-4150", (203, 213, 225)),
        ("VC-FR-4160", (203, 213, 225)),
        ("VC-FR-4170", (203, 213, 225)),
        ("VC-FR-4100", (148, 163, 184)),
        ("VC-FR-4300", (100, 116, 139)),
        ("VC-FR-4400", (71, 85, 105)),
        ("VC-HB-2110", (30, 58, 138)),
        ("VC-HB-2124", (226, 232, 240)),
        ("VC-HB-2122", (180, 120, 40)),
        ("VC-HB-2120", (203, 213, 225)),
        ("VC-HB-2100", (30, 64, 175)),
        ("VC-HB-2200", (51, 65, 85)),
        ("VC-HB-2400", (100, 116, 139)),
        ("VC-HB-2500", (148, 163, 184)),
        ("VC-HB-2600", (71, 85, 105)),
        ("VC-HB-2700", (180, 130, 40)),
        ("VC-HB-2800", (55, 65, 81)),
        ("VC-HB-2810", (71, 85, 105)),
        ("VC-HB-2820", (100, 116, 139)),
        ("VC-HB-2830", (51, 65, 85)),
        ("VC-HB-2900", (202, 138, 4)),
        ("VC-HB-3000", (127, 29, 29)),
        ("VC-HB-3100", (15, 118, 110)),
        ("VC-HB-3110", (13, 148, 136)),
        ("VC-HB-3200", (22, 163, 74)),
        ("VC-SH-1350", (180, 83, 9)),
        ("VC-SH-1301", (234, 88, 12)),
        ("VC-SH-1302", (194, 65, 12)),
        ("VC-SH-1400", (202, 138, 4)),
        ("VC-SH-1100", (185, 28, 28)),
        ("VC-SH-1600", (126, 34, 206)),
        ("VC-SH-1500", (120, 80, 40)),
        ("VC-GP-7100", (37, 99, 235)),
        ("VC-GP-7200", (30, 64, 175)),
        ("VC-SP-7620", (13, 148, 136)),
        ("VC-SP-7621", (15, 118, 110)),
    )
    for prefix, color in table:
        if name.startswith(prefix):
            return color
    return (120, 120, 120)


def chain_matches_pose() -> bool:
    """The pose height is the required height without ground clearance and the top margin."""
    expected = _mm(required_total_mm() - GROUND_CLEARANCE_MM - TOP_MARGIN_MM)
    return abs(posed_stack_height_mm() - expected) < 0.05
