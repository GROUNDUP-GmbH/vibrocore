"""ISO 606 10B-2 duplex chain as one closed loop.

G&G, iwis, Renold and Rexnord do not offer a free STEP of this chain
without an account. The links are built here from ISO 606.
Pitch 15.875 mm. Roller diameter 10.16 mm. Inner width 9.65 mm.
Transverse pitch 16.59 mm. Plate height 14.7 mm. Plate thickness 1.6 mm.
Pin diameter 5.08 mm. These plate and pin sizes are the usual 10B values.

The vendor sprocket already has 15 tooth gaps. Rollers sit in those gaps
on the ISO pitch circle. The idler is turned by 12 degrees so the straight
runs meet a gap at each end. The centre distance is an integer number of
pitches, so the loop closes and no link is omitted.
"""

from __future__ import annotations

import math

from build123d import Compound, Cylinder, Pos, Rot

from cad.models.mast_layout import (
    CHAIN_INNER_WIDTH_MM,
    CHAIN_PITCH_MM,
    CHAIN_ROLLER_DIAMETER_MM,
    CHAIN_TRANSVERSE_PITCH_MM,
)

PLATE_HEIGHT_MM = 14.7
PLATE_THICKNESS_MM = 1.6
PIN_DIAMETER_MM = 5.08
TOOTH_COUNT = 15
# Pitch circle for 15 teeth. Chord of one tooth angle equals the pitch.
MESH_RADIUS_MM = CHAIN_PITCH_MM / (2.0 * math.sin(math.pi / TOOTH_COUNT))
# Measured on the seated vendor solid. A tooth stands at 6 degrees and a gap at 18.
GAP_CENTER_DEG = 18.0
# Turns the idler so its upper gaps share X with the drive sprocket's lower gaps.
IDLER_TURN_DEG = 12.0
_LINK = {}


def _along_y(radius: float, length: float):
    return Rot(90, 0, 0) * Cylinder(radius, length)


def _link(inner: bool):
    """One duplex link. Pitch along Z. Pin axis along Y. Centred.

    Rollers are on the inner link only. The next outer link shares those pins.
    """
    cached = _LINK.get(inner)
    if cached is not None:
        return cached
    from build123d import Box

    pitch = CHAIN_PITCH_MM
    roller = _along_y(CHAIN_ROLLER_DIAMETER_MM / 2.0, CHAIN_INNER_WIDTH_MM)
    pin = _along_y(PIN_DIAMETER_MM / 2.0, 16.0)
    plate = Box(PLATE_HEIGHT_MM, PLATE_THICKNESS_MM, pitch - 0.6)
    half_gap = CHAIN_INNER_WIDTH_MM / 2.0
    thick = PLATE_THICKNESS_MM
    if inner:
        offset = half_gap + thick / 2.0
    else:
        offset = half_gap + thick + 0.4 + thick / 2.0
    pieces = []
    row = CHAIN_TRANSVERSE_PITCH_MM / 2.0
    for row_y in (row, -row):
        for end in (-1.0, 1.0):
            if inner:
                pieces.append(Pos(0.0, row_y, end * pitch / 2.0) * roller)
            pieces.append(Pos(0.0, row_y, end * pitch / 2.0) * pin)
        for side in (-1.0, 1.0):
            pieces.append(Pos(0.0, row_y + side * offset, 0.0) * plate)
    solid = pieces[0]
    for piece in pieces[1:]:
        solid = solid + piece
    _LINK[inner] = solid
    return solid


def _end_offset_mm() -> float:
    """How far an end roller sits off the sprocket centre, along Z."""
    return MESH_RADIUS_MM * math.sin(math.radians(6.0))


def idler_z_mm(z_drive: float, z_nominal: float) -> float:
    """Idler centre that closes the loop on an even number of pitches.

    The straight run plus the two end-roller offsets is an integer number of
    pitches. The chosen count stays nearest to z_nominal.
    """
    extra = 2.0 * _end_offset_mm()
    nominal_span = (z_nominal - z_drive) + extra
    count = int(round(nominal_span / CHAIN_PITCH_MM))
    if count % 2:
        count += 1
    return z_drive + count * CHAIN_PITCH_MM - extra


def _gap_angles(shift_deg: float, *, upper: bool) -> list[float]:
    """Gap centres on one sprocket, in wrap order."""
    found = []
    for index in range(TOOTH_COUNT):
        deg = (GAP_CENTER_DEG - shift_deg + index * (360.0 / TOOTH_COUNT)) % 360.0
        rad = math.radians(deg)
        if upper and math.sin(rad) > 0.0:
            found.append(deg)
        if not upper and math.sin(rad) < 0.0:
            found.append(deg)
    # Drive wrap runs from the front end, through the bottom, to the rear end.
    # Idler wrap runs from the rear end, through the top, to the front end.
    if upper:
        found.sort(reverse=True)
    else:
        found.sort(reverse=True)
        # 354 before 330 ... before 186. reverse sort already does that if all are > 180,
        # except 354 is the largest. Confirm the front end (near 0 / 360) leads.
        # Angles just below 360 must come first.
        found.sort(key=lambda deg: deg if deg > 180.0 else deg + 360.0, reverse=True)
    return found


def _point(angle_deg: float, z_center: float, axis_x: float, axis_y: float):
    rad = math.radians(angle_deg)
    return (
        axis_x + MESH_RADIUS_MM * math.cos(rad),
        axis_y,
        z_center + MESH_RADIUS_MM * math.sin(rad),
    )


def _between(start, end, count: int):
    """count roller centres strictly between start and end, one pitch apart."""
    if count <= 0:
        return []
    points = []
    for index in range(1, count + 1):
        scale = index / (count + 1)
        points.append(tuple(start[axis] + (end[axis] - start[axis]) * scale for axis in range(3)))
    return points


def _place(link, start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    theta = math.degrees(math.atan2(-dx, dz))
    mid = tuple((start[axis] + end[axis]) / 2.0 for axis in range(3))
    if abs(dy) > 0.01:
        raise ValueError("chain chord leaves the pitch plane")
    return Pos(mid[0], mid[1], mid[2]) * Rot(0.0, -theta, 0.0) * link


def duplex_chain(z_drive: float, z_idler: float, axis_x: float, axis_y: float = 0.0):
    """One closed loop. World axes. Z is up. Rollers sit in the tooth gaps."""
    drive = [_point(deg, z_drive, axis_x, axis_y) for deg in _gap_angles(0.0, upper=False)]
    idle = [_point(deg, z_idler, axis_x, axis_y) for deg in _gap_angles(IDLER_TURN_DEG, upper=True)]
    span = idle[0][2] - drive[-1][2]
    intervals = int(round(span / CHAIN_PITCH_MM))
    if abs(span - intervals * CHAIN_PITCH_MM) > 0.05:
        raise ValueError("chain straight run is not an integer number of pitches")
    rear = _between(drive[-1], idle[0], intervals - 1)
    front = _between(idle[-1], drive[0], intervals - 1)
    path = drive + rear + idle + front
    if len(path) % 2:
        raise ValueError("closed chain needs an even number of links")
    inner = _link(True)
    outer = _link(False)
    pieces = []
    for index in range(len(path)):
        start = path[index]
        end = path[(index + 1) % len(path)]
        link = inner if index % 2 == 0 else outer
        pieces.append(_place(link, start, end))
    return Compound(children=pieces)
