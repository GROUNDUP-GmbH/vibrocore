"""Welded lower drive frame. One 8 mm laser-cut part.

Approved 2026-11-20. Inverted U, 316.6 mm over the plates, 180 mm deep,
139 mm high. The left side is one flat plate from the foot to the tab.
The gearbox flange sits on the outer face of that plate. Four pads under
the beam carry the hanging SYJ 30 TF housings. The chain runs at Y = 0.

Concept Z = 0 is the top of the bottom plate. This module adds the 15 mm
plate and returns world coordinates.
"""

from __future__ import annotations

import math

from build123d import Box, Cylinder, Pos, Rot

from cad.models.mast_layout import (
    BOTTOM_PLATE_THICKNESS_MM,
    MAST_PROFILE_DEPTH_MM,
    MAST_PROFILE_WIDTH_MM,
    PROFILE_SPACING_MM,
)

PLATE_TOP_MM = BOTTOM_PLATE_THICKNESS_MM
SHEET_MM = 8.0
GUARD_MM = 3.0
DEPTH_MM = 180.0
# Inner face of each profile. 366.6 mm centres, 50 mm profile.
INNER_Y_MM = PROFILE_SPACING_MM / 2.0 - MAST_PROFILE_WIDTH_MM / 2.0
AXIS_Z_MM = PLATE_TOP_MM + 72.1
SOLE_Z_MM = AXIS_Z_MM + 42.9
PAD_MM = 16.0
BEAM_Z0_MM = SOLE_Z_MM + PAD_MM
BEAM_Z1_MM = BEAM_Z0_MM + SHEET_MM
TAB_TOP_MM = PLATE_TOP_MM + 300.0
FOOT_MM = 40.0
SHORT_PROFILE_Z_MM = PLATE_TOP_MM + 140.0
COUPLING_LENGTH_MM = 68.0
COUPLING_Y0_MM = -INNER_Y_MM + 25.0
SPROCKET_Y_MM = 0.0
DRIVE_BEARING_Y_MM = -41.1
IDLE_BEARING_Y_MM = 42.3
BEARING_YS_MM = (DRIVE_BEARING_Y_MM, IDLE_BEARING_Y_MM)
GEARBOX_FACE_Y_MM = -INNER_Y_MM
# oriented_gearbox: local Y = 0 is the motor face, local Y = 149 is the output face.
GEARBOX_Y_MM = GEARBOX_FACE_Y_MM - 149.0
SHAFT_Y0_MM = COUPLING_Y0_MM + COUPLING_LENGTH_MM - 30.0
SHAFT_Y1_MM = IDLE_BEARING_Y_MM + 25.0
# The PLE120 STEP holes are empty on a Ø100 mm circle, on the diagonals.
# The concept sketch uses Ø90 mm. The screws follow the STEP.
FLANGE_PCD_MM = 100.0
FLANGE_BORE_MM = 86.0


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
    return Pos((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
    )


def _fuse(pieces):
    solid = pieces[0]
    for piece in pieces[1:]:
        solid = solid + piece
    return solid


def _along_y(radius: float, length: float):
    return Rot(90, 0, 0) * Cylinder(radius, length)


def flange_offsets_mm() -> list[tuple[float, float]]:
    """X and Z offsets of the four flange screws, relative to the shaft."""
    half = FLANGE_PCD_MM / 2.0 / math.sqrt(2.0)
    return [(sign_x * half, sign_z * half) for sign_x in (-1.0, 1.0) for sign_z in (-1.0, 1.0)]


def foot_holes_mm() -> list[tuple[float, float]]:
    """M10 holes in the feet. X, Y. Six holes."""
    inset = INNER_Y_MM - SHEET_MM - FOOT_MM / 2.0
    return [(x, sign * inset) for x in (-60.0, 0.0, 60.0) for sign in (-1.0, 1.0)]


def profile_holes_mm() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """M8 holes. (x, world z) on the tab, then on the right cheek."""
    tab = [(x, PLATE_TOP_MM + z) for x in (-25.0, 25.0) for z in (175.0, 225.0, 275.0)]
    cheek = [(x, PLATE_TOP_MM + z) for x in (-25.0, 25.0) for z in (30.0, 65.0, 100.0)]
    return tab, cheek


def guard_holes_mm() -> list[tuple[float, float]]:
    """M5 holes. (y, world z) on each guard."""
    side = INNER_Y_MM - SHEET_MM / 2.0
    beam = BEAM_Z0_MM + SHEET_MM / 2.0
    concept = (
        (-side, 25.0),
        (-side, 105.0),
        (side, 25.0),
        (side, 105.0),
        (-60.0, beam - PLATE_TOP_MM),
        (60.0, beam - PLATE_TOP_MM),
    )
    return [(y, PLATE_TOP_MM + z) for y, z in concept]


def _concept_frame():
    """Frame in concept coordinates. Z = 0 is the plate top."""
    t = SHEET_MM
    yi = INNER_Y_MM
    depth = DEPTH_MM / 2.0
    beam_z0 = BEAM_Z0_MM - PLATE_TOP_MM
    beam_z1 = BEAM_Z1_MM - PLATE_TOP_MM
    sole = SOLE_Z_MM - PLATE_TOP_MM
    tab = TAB_TOP_MM - PLATE_TOP_MM
    axis = AXIS_Z_MM - PLATE_TOP_MM
    beam = _box(-depth, depth, -yi + t, yi - t, beam_z0, beam_z1)
    # Chain strands and the carriage arm at stroke 0 cross this opening.
    beam = beam - _box(-52.0, 91.0, -22.0, 22.0, beam_z0 - 1.0, beam_z1 + 1.0)
    pads = []
    for centre_y in BEARING_YS_MM:
        for x0, x1 in ((-90.0, -54.0), (54.0, 90.0)):
            pads.append(_box(x0, x1, centre_y - 22.0, centre_y + 22.0, sole, beam_z0))
    # One plate. The wide part and the tab overlap by 1 mm so the fuse is one solid.
    profile_half = MAST_PROFILE_DEPTH_MM / 2.0
    plate = _fuse(
        [
            _box(-depth, depth, -yi, -yi + t, 0.0, beam_z1),
            _box(-profile_half, profile_half, -yi, -yi + t, beam_z1 - 1.0, tab),
        ]
    )
    # The carriage cross-arm at stroke 0 clips the front top corner of each plate.
    plate = plate - _box(76.0, 92.0, -yi - 1.0, -yi + t + 1.0, beam_z1 - 4.0, beam_z1 + 2.0)
    cheek = _box(-depth, depth, yi - t, yi, 0.0, beam_z1)
    cheek = cheek - _box(76.0, 92.0, yi - t - 1.0, yi + 1.0, beam_z1 - 4.0, beam_z1 + 2.0)
    foot_l = _box(-depth, depth, -yi + t, -yi + t + FOOT_MM, 0.0, t)
    foot_r = _box(-depth, depth, yi - t - FOOT_MM, yi - t, 0.0, t)
    frame = _fuse([plate, cheek, beam, foot_l, foot_r, *pads])
    for centre_y in BEARING_YS_MM:
        for dx in (-59.0, 59.0):
            # Through the beam, the pad and out under the sole. The M12x50 starts above the beam.
            z_low = sole - 4.0
            z_high = beam_z1 + 6.0
            hole = Pos(dx, centre_y, (z_low + z_high) / 2.0) * Cylinder(6.75, z_high - z_low)
            frame = frame - hole
    # Cut through the whole 8 mm plate. A cutter that stops inside the plate
    # leaves a web, and the Ø80 spigot sits in that web.
    def hole_y(radius: float, y0: float, y1: float, x: float, z: float):
        return Pos(x, (y0 + y1) / 2.0, z) * _along_y(radius, abs(y1 - y0))

    left_out, left_in = -yi - 2.0, -yi + t + 2.0
    cheek_in, cheek_out = yi - t - 2.0, yi + 2.0
    frame = frame - hole_y(FLANGE_BORE_MM / 2.0, left_out, left_in, 0.0, axis)
    for dx, dz in flange_offsets_mm():
        frame = frame - hole_y(3.3, left_out, left_in, dx, axis + dz)
    tab_holes, cheek_holes = profile_holes_mm()
    for dx, world_z in tab_holes:
        frame = frame - hole_y(4.5, left_out, left_in, dx, world_z - PLATE_TOP_MM)
    for dx, world_z in cheek_holes:
        frame = frame - hole_y(4.5, cheek_in, cheek_out, dx, world_z - PLATE_TOP_MM)
    for dx, dy in foot_holes_mm():
        frame = frame - Pos(dx, dy, t / 2.0) * Cylinder(5.5, t + 8.0)
    for gy, world_z in guard_holes_mm():
        z = world_z - PLATE_TOP_MM
        frame = frame - Pos(depth - 4.0, gy, z) * (Rot(0, 90, 0) * Cylinder(2.9, 28.0))
        frame = frame - Pos(-depth + 4.0, gy, z) * (Rot(0, 90, 0) * Cylinder(2.9, 28.0))
    # Weld nuts on the feet. They are part of this one weldment.
    nuts = []
    for dx, dy in foot_holes_mm():
        nut = Pos(dx, dy, t + 4.0) * Cylinder(8.5, 8.0)
        nut = nut - Pos(dx, dy, t + 2.0) * Cylinder(5.0, 20.0)
        nuts.append(nut)
    frame = _fuse([frame, *nuts])
    return frame


def lower_frame():
    """One weldment, in world coordinates. Feet sit on the plate top."""
    return Pos(0.0, 0.0, PLATE_TOP_MM) * _concept_frame()


def guard_sheets():
    """Front and rear 3 mm sheets. Each is 316.6 mm by 139 mm."""
    t = GUARD_MM
    yi = INNER_Y_MM
    depth = DEPTH_MM / 2.0
    top = BEAM_Z1_MM - PLATE_TOP_MM
    front = _box(depth, depth + t, -yi, yi, 0.0, top)
    rear = _box(-depth - t, -depth, -yi, yi, 0.0, top)
    for gy, world_z in guard_holes_mm():
        z = world_z - PLATE_TOP_MM
        front = front - Pos(depth + t / 2.0, gy, z) * (Rot(0, 90, 0) * Cylinder(2.75, t + 6.0))
        rear = rear - Pos(-depth - t / 2.0, gy, z) * (Rot(0, 90, 0) * Cylinder(2.75, t + 6.0))
    return Pos(0.0, 0.0, PLATE_TOP_MM) * front, Pos(0.0, 0.0, PLATE_TOP_MM) * rear
