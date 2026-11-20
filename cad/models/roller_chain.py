"""ISO 606 10B-2 duplex chain around the placed sprockets.

G&G, iwis, Renold and Rexnord do not offer a free STEP of this chain
without an account. The links are built here from ISO 606.
Pitch 15.875 mm. Roller diameter 10.16 mm. Inner width 9.65 mm.
Transverse pitch 16.59 mm. Plate height 14.7 mm. Plate thickness 1.6 mm.
Pin diameter 5.08 mm. These plate and pin sizes are the usual 10B values.
The strands sit on the pitch radius and stop clear of the tooth tip.
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


def _along_y(radius: float, length: float):
    return Rot(90, 0, 0) * Cylinder(radius, length)


def _link(inner: bool):
    """One duplex link. Pitch along Z. Pin axis along Y. Centred.

    Rollers are on the inner link only. The next outer link shares those pins.
    """
    from build123d import Box

    pitch = CHAIN_PITCH_MM
    roller = _along_y(CHAIN_ROLLER_DIAMETER_MM / 2.0, CHAIN_INNER_WIDTH_MM)
    # One pin per row. The end stays inside the outer plate.
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
    return solid


def duplex_chain(
    z_drive: float,
    z_idler: float,
    pitch_radius: float,
    tip_radius: float,
    axis_x: float,
    gap: float,
    axis_y: float = 0.0,
):
    """Links on both strands and on both pitch arcs. World axes. Z is up."""
    pitch = CHAIN_PITCH_MM
    cut = tip_radius + gap + CHAIN_ROLLER_DIAMETER_MM / 2.0
    z0 = z_drive + cut
    z1 = z_idler - cut
    count = max(int((z1 - z0) / pitch), 2)
    span = (count - 1) * pitch
    start = (z0 + z1) / 2.0 - span / 2.0
    inner = _link(True)
    outer = _link(False)
    pieces = []
    for sign in (1.0, -1.0):
        x = axis_x + sign * pitch_radius
        for index in range(count):
            link = inner if index % 2 == 0 else outer
            placed = Pos(x, axis_y, start + index * pitch) * link
            pieces.append(placed)
    # The sprocket solid has no tooth gap. Links wrap outside the tip.
    wrap = tip_radius + gap + PLATE_HEIGHT_MM / 2.0
    step = pitch / wrap
    arc_n = max(int(math.pi / step) - 1, 2)
    for z_center, upper in ((z_drive, False), (z_idler, True)):
        for index in range(arc_n):
            theta = math.pi * (index + 0.5) / arc_n
            sign_z = 1.0 if upper else -1.0
            link = inner if index % 2 == 0 else outer
            turned = Rot(0.0, -math.degrees(theta) * sign_z, 0.0) * link
            placed = (
                Pos(
                    axis_x + wrap * math.cos(theta),
                    axis_y,
                    z_center + sign_z * wrap * math.sin(theta),
                )
                * turned
            )
            box = placed.bounding_box()
            # Stay in front of the rear panel and above the beam.
            if float(box.min.X) < -48.0 or float(box.max.X) > 52.0:
                continue
            if float(box.min.Z) < 46.0:
                continue
            pieces.append(placed)
    if not pieces:
        raise ValueError("duplex chain produced no solid")
    return Compound(children=pieces)
