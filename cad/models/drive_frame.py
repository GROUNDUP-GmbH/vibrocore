"""Welded lower drive frame. One inverted U under the two profiles.

The cross beam carries both SYJ 30 TF bearings. The sprocket sits
between them. A flange plate on the drive end takes the gearbox
output flange. The drive-side upright stands in front of the gearbox,
because the 115 mm gearbox is wider than the 100 mm profile.
Fillet welds are a separate solid. Size a5 (5 mm leg).
Each bead sits 0.2 mm clear of the parent faces.
"""

from __future__ import annotations

import math

from build123d import Box, Cylinder, Pos, Rot

from cad.models.mast_layout import GEARBOX_FLANGE_MM

BEAM_HALF_X_MM = 75.0
BEAM_Y0_MM = -116.0
BEAM_Y1_MM = 116.0
BEAM_Z0_MM = 15.2
BEAM_Z1_MM = 39.2
WELD_LEG_MM = 5.0
FLANGE_THICKNESS_MM = 8.0
GUARD_THICKNESS_MM = 2.0
# The Neugart STEP holes are empty on a Ø100 mm circle, on the diagonals.
FLANGE_PCD_MM = 100.0
# Side-sheet screws, X and Y relative to the chain axis. They go down into the beam.
# The rear screw stays in front of the rear face. A 10 mm head at X = -44.5 ends at X = -49.5.
# Y = ±17 keeps the head between the chain plates and the bearing, which starts at |Y| = 24.75.
SIDE_SCREW_OFFSETS_MM = ((-44.5, -17.0), (-44.5, 17.0), (55.0, -17.0), (55.0, 17.0))
# Cover screws enter the flange from outside X. Z is relative to the shaft.
COVER_SCREW_Z_MM = (-24.0, 24.0)


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
    return Pos((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
    )


def _fuse(pieces):
    solid = pieces[0]
    for piece in pieces[1:]:
        solid = solid + piece
    return solid


def lower_frame(
    axis_x: float,
    face_y: float,
    z_shaft: float,
    bearing_ys: tuple[float, float],
    drive_inner_y: float,
):
    """Steel frame and the a5 weld solid. face_y is the gearbox output face."""
    x0 = axis_x - BEAM_HALF_X_MM
    x1 = axis_x + BEAM_HALF_X_MM
    pieces = [
        _box(x0, x1, BEAM_Y0_MM, BEAM_Y1_MM, BEAM_Z0_MM, BEAM_Z1_MM),
    ]
    # Idle upright. It stands on the plate and meets the beam.
    pieces.append(_box(axis_x - 40.0, axis_x + 40.0, 116.8, 124.8, BEAM_Z0_MM, 140.0))
    # Drive cheek above the gearbox, on the inner face.
    pieces.append(
        _box(axis_x - 40.0, axis_x + 50.0, drive_inner_y + 0.2, drive_inner_y + 8.2, 155.0, 250.0)
    )
    # Front ear of that cheek. The gearbox body ends at X = ±57.5 mm.
    pieces.append(
        _box(axis_x + 50.0, axis_x + 78.0, drive_inner_y + 0.2, drive_inner_y + 8.2, 155.0, 200.0)
    )
    # Foot on the plate. It stops at Z = 100 mm, under the carriage at stroke 0.
    # The runner then occupies Y = -172 mm to -128 mm from Z = 115 mm up.
    pieces.append(_box(axis_x + 70.5, axis_x + 84.0, -180.0, -132.0, BEAM_Z0_MM, 100.0))
    pieces.append(_box(axis_x + 70.5, axis_x + 78.0, -132.0, BEAM_Y0_MM, BEAM_Z0_MM, 100.0))
    pieces.append(_box(axis_x + 70.5, axis_x + 78.0, -126.0, drive_inner_y + 8.0, 40.0, 158.0))
    flange = _box(
        axis_x - GEARBOX_FLANGE_MM / 2.0,
        axis_x + GEARBOX_FLANGE_MM / 2.0,
        face_y,
        face_y + FLANGE_THICKNESS_MM,
        30.0,
        140.0,
    )
    # The output spigot is Ø80 mm and stands 4 mm proud of the face.
    bore = Pos(axis_x, face_y + FLANGE_THICKNESS_MM / 2.0, z_shaft) * (
        Rot(90, 0, 0) * Cylinder(43.0, FLANGE_THICKNESS_MM + 4.0)
    )
    flange = flange - bore
    # Ø100 mm circle, on the diagonals. That is where the STEP holes are empty.
    half = FLANGE_PCD_MM / 2.0 / math.sqrt(2.0)
    for sign_x in (-1.0, 1.0):
        for sign_z in (-1.0, 1.0):
            hole = Pos(
                axis_x + sign_x * half,
                face_y + FLANGE_THICKNESS_MM / 2.0,
                z_shaft + sign_z * half,
            ) * (Rot(90, 0, 0) * Cylinder(3.3, FLANGE_THICKNESS_MM + 2.0))
            flange = flange - hole
    # M5 clearance for the removable cover. The screws come in from outside X.
    for sign_x in (-1.0, 1.0):
        edge = axis_x + sign_x * (GEARBOX_FLANGE_MM / 2.0 - 6.0)
        for dz in COVER_SCREW_Z_MM:
            hole = Pos(edge, face_y + FLANGE_THICKNESS_MM / 2.0, z_shaft + dz) * (
                Rot(0, 90, 0) * Cylinder(2.7, 16.0)
            )
            flange = flange - hole
    pieces.append(flange)
    # Arm from the flange to the beam, on the front side of the gearbox and the rail.
    pieces.append(
        _box(axis_x + 70.5, axis_x + 84.0, face_y, BEAM_Y0_MM, BEAM_Z0_MM, BEAM_Z1_MM)
    )
    # Brace stays under Z = 100 mm. The carriage and the runner fill the space above that at stroke 0.
    pieces.append(_box(axis_x + 72.0, axis_x + 80.0, face_y + 12.0, -116.0, 48.0, 100.0))
    frame = _fuse(pieces)
    # The closed chain passes under the sprocket. Open the beam for the plates.
    chain_notch = _box(axis_x - 22.0, axis_x + 22.0, -22.0, 22.0, 36.0, 42.0)
    frame = frame - chain_notch
    for dx, sy in SIDE_SCREW_OFFSETS_MM:
        hole = Pos(axis_x + dx, sy, (BEAM_Z0_MM + BEAM_Z1_MM) / 2.0) * Cylinder(3.3, 30.0)
        frame = frame - hole
    # Open the draft-drop slot. The slot in the plate is 40 x 44 mm at Y = 75 mm.
    slot = Pos(axis_x, 75.0, (BEAM_Z0_MM + BEAM_Z1_MM) / 2.0) * Box(44.0, 48.0, 30.0)
    frame = frame - slot
    for centre_y in bearing_ys:
        for dx in (-59.0, 59.0):
            hole = Pos(axis_x + dx, centre_y, (BEAM_Z0_MM + BEAM_Z1_MM) / 2.0) * Cylinder(6.6, 40.0)
            frame = frame - hole
    # M8 clearance holes in the uprights. Four screws per side.
    for slot_x in (-25.0, 25.0):
        for slot_z in (180.0, 230.0):
            hole = Pos(slot_x, drive_inner_y + 4.0, slot_z) * (Rot(90, 0, 0) * Cylinder(4.5, 20.0))
            frame = frame - hole
        for slot_z in (50.0, 110.0):
            hole = Pos(slot_x, 120.0, slot_z) * (Rot(90, 0, 0) * Cylinder(4.5, 20.0))
            frame = frame - hole
    welds = _welds(axis_x, face_y, drive_inner_y)
    return frame, welds


def _welds(axis_x: float, face_y: float, drive_inner_y: float):
    leg = WELD_LEG_MM
    # Each bead is 0.2 mm clear of the parent faces. Size a5.
    beads = [
        _box(axis_x - 30.0, axis_x + 30.0, 110.0, 115.0, BEAM_Z1_MM + 0.2, BEAM_Z1_MM + 0.2 + leg),
        _box(axis_x + 72.0, axis_x + 82.0, -115.6, -110.0, BEAM_Z1_MM + 0.2, BEAM_Z1_MM + 0.2 + leg),
        _box(axis_x + 50.4, axis_x + 56.0, drive_inner_y + 8.6, drive_inner_y + 14.0, 165.0, 190.0),
    ]
    return _fuse(beads)


def guard_sheets(axis_x: float, face_y: float, motor_y0: float, bearing_min_y: float, z_shaft: float):
    """Side sheets around the sprocket, and a cover over the motor and the coupling.

    The cover comes off to reach the coupling and the motor-flange screws.
    Four M6 screws hold the side sheets to the beam. Four M5 screws hold the
    cover to the flange edge. Sheet is 2 mm steel. There is no sheet under
    the sprocket. The beam closes that side.
    """
    t = GUARD_THICKNESS_MM
    fixed = [
        _box(axis_x - 48.2, axis_x - 48.2 + t, -16.0, 16.0, 48.0, 136.0),
        _box(axis_x + 54.0, axis_x + 54.0 + t, -16.0, 16.0, 48.0, 136.0),
    ]
    for dx, sy in SIDE_SCREW_OFFSETS_MM:
        x = axis_x + dx
        # The rear foot stops at the rear face. The front foot is clear of that face.
        foot_x0 = max(x - 6.0, axis_x - 49.6)
        foot_x1 = x + 6.0
        fixed.append(_box(foot_x0, foot_x1, sy - 6.0, sy + 6.0, BEAM_Z1_MM, BEAM_Z1_MM + 2.0))
        if dx < 0.0:
            sheet_x0, sheet_x1 = axis_x - 48.2, axis_x - 48.2 + t
        else:
            sheet_x0, sheet_x1 = axis_x + 54.0, axis_x + 54.0 + t
        fixed.append(
            _box(
                min(sheet_x0, x - t / 2.0),
                max(sheet_x1, x + t / 2.0),
                min(sy, 16.0) - 2.0,
                max(sy, -16.0) + 2.0,
                41.2,
                50.0,
            )
        )
    fixed_solid = _fuse(fixed)
    for dx, sy in SIDE_SCREW_OFFSETS_MM:
        hole = Pos(axis_x + dx, sy, 40.0) * Cylinder(3.3, 12.0)
        # The head stands on the foot. The riser passes beside that head.
        head_clear = Pos(axis_x + dx, sy, 44.5) * Cylinder(5.2, 6.4)
        fixed_solid = fixed_solid - hole - head_clear
    y0 = motor_y0 + 4.0
    y_flange = face_y - 2.0
    cover = [
        _box(axis_x + 60.0, axis_x + 60.0 + t, y0, y_flange, 26.0, 145.0),
        _box(axis_x - 62.0, axis_x - 62.0 + t, y0, y_flange, 26.0, 145.0),
        _box(axis_x - 48.0, axis_x + 48.0, y0, y_flange, 22.2, 24.2),
        # The carriage reaches X = 90 mm. This sheet stands outside that face.
        _box(axis_x + 94.0, axis_x + 94.0 + t, face_y + 14.0, bearing_min_y - 2.0, 48.0, 140.0),
        _box(axis_x - 90.0, axis_x - 88.0, face_y + 14.0, bearing_min_y - 2.0, 48.0, 140.0),
    ]
    # Tabs wrap outside the gearbox and land 0.2 mm clear of the flange edge.
    for sign_x, outer_x in ((1.0, axis_x + 62.0), (-1.0, axis_x - 62.0)):
        edge = axis_x + sign_x * (GEARBOX_FLANGE_MM / 2.0)
        for dz in COVER_SCREW_Z_MM:
            z = z_shaft + dz
            cover.append(
                _box(outer_x - sign_x * t, outer_x, face_y - 2.0, face_y + FLANGE_THICKNESS_MM, z - 6.0, z + 6.0)
            )
            cover.append(
                _box(edge + sign_x * 0.2, outer_x, face_y, face_y + FLANGE_THICKNESS_MM, z - 6.0, z + 6.0)
            )
    cover_solid = _fuse(cover)
    for sign_x in (-1.0, 1.0):
        edge = axis_x + sign_x * (GEARBOX_FLANGE_MM / 2.0 - 6.0)
        for dz in COVER_SCREW_Z_MM:
            hole = Pos(edge, face_y + FLANGE_THICKNESS_MM / 2.0, z_shaft + dz) * (
                Rot(0, 90, 0) * Cylinder(2.7, 24.0)
            )
            cover_solid = cover_solid - hole
    return fixed_solid, cover_solid
