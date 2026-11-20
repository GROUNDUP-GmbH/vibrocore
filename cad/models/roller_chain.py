"""Parametric ISO 606 10B-2 duplex chain around the placed sprockets.

G&G does not publish chain CAD. The section uses the ISO sizes.
Pitch 15.875 mm. Roller diameter 10.16 mm. Inner width 9.65 mm.
Transverse pitch 16.59 mm.
The straight strands sit on the pitch radius and stop clear of the tooth tip.
The wrap is flat segments outside that tip. It is not a link-by-link mesh.
Cylinders are omitted. FreeCAD draws a thin cylindrical shell as a spike.
"""

from __future__ import annotations

import math

from build123d import Box, Compound, Pos, Rot

from cad.models.mast_layout import (
    CHAIN_INNER_WIDTH_MM,
    CHAIN_ROLLER_DIAMETER_MM,
    CHAIN_TRANSVERSE_PITCH_MM,
)


def _arc_boxes(inner_r: float, outer_r: float, width: float, upper: bool, count: int = 8):
    """Half ring of boxes. Axis along Y. Upper keeps +Z. Lower keeps -Z."""
    mid_r = (inner_r + outer_r) / 2.0
    thick = max(outer_r - inner_r, 0.6)
    span = math.pi / count
    chord = 2.0 * outer_r * math.sin(span / 2.0)
    pieces = []
    for index in range(count):
        theta = span * (index + 0.5)
        if not upper:
            theta = -theta
        block = Box(thick, width, chord)
        turned = Rot(0.0, -math.degrees(theta), 0.0) * block
        pieces.append(Pos(mid_r * math.cos(theta), 0.0, mid_r * math.sin(theta)) * turned)
    return pieces


def duplex_chain(
    z_drive: float,
    z_idler: float,
    pitch_radius: float,
    tip_radius: float,
    axis_x: float,
    gap: float,
    axis_y: float = 0.0,
):
    """One compound for both strands and both wraps. World axes. Z is up."""
    roller_r = CHAIN_ROLLER_DIAMETER_MM / 2.0
    outer_r = pitch_radius + roller_r
    cut_r = tip_radius + gap
    if cut_r >= outer_r - 0.3:
        cut_r = outer_r - 0.3
    row = CHAIN_TRANSVERSE_PITCH_MM / 2.0
    width = CHAIN_INNER_WIDTH_MM
    strand_len = (z_idler - cut_r) - (z_drive + cut_r)
    mid_z = (z_drive + z_idler) / 2.0
    strand = Box(CHAIN_ROLLER_DIAMETER_MM, width, strand_len)
    pieces = []
    for sign in (1.0, -1.0):
        for offset in (row, -row):
            pieces.append(Pos(axis_x + sign * pitch_radius, axis_y + offset, mid_z) * strand)
    for z_center, upper in ((z_drive, False), (z_idler, True)):
        for offset in (row, -row):
            for segment in _arc_boxes(cut_r, outer_r, width, upper):
                pieces.append(Pos(axis_x, axis_y + offset, z_center) * segment)
    if not pieces:
        raise ValueError("duplex chain produced no solid")
    return Compound(children=pieces)
