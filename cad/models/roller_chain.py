"""Parametric ISO 606 10B-2 duplex chain around the placed sprockets.

G&G does not publish chain CAD. The section uses the ISO sizes.
Pitch 15.875 mm. Roller diameter 10.16 mm. Inner width 9.65 mm.
Transverse pitch 16.59 mm.
The straight strands sit on the pitch radius and stop clear of the tooth tip.
The wrap is a shell outside that tip. It is not a link-by-link mesh.
"""

from __future__ import annotations

from build123d import Box, Compound, Cylinder, Pos, Rot

from cad.models.mast_layout import (
    CHAIN_INNER_WIDTH_MM,
    CHAIN_ROLLER_DIAMETER_MM,
    CHAIN_TRANSVERSE_PITCH_MM,
)


def _leaves(shape) -> list:
    solids = [item for item in shape.solids() if abs(float(item.volume)) > 0.5] if hasattr(shape, "solids") else []
    if solids:
        return solids
    if abs(float(shape.volume)) > 0.5:
        return [shape]
    return []


def _half_shell(inner_r: float, outer_r: float, width: float, upper: bool):
    """Half annulus. Axis along Y. Upper keeps +Z. Lower keeps -Z."""
    ring = Rot(90, 0, 0) * (Cylinder(outer_r, width) - Cylinder(inner_r, width + 1.0))
    span = outer_r * 2.0 + 4.0
    side = -1.0 if upper else 1.0
    cutter = Pos(0.0, 0.0, side * span) * Box(span * 2.0, width + 4.0, span * 2.0)
    return ring - cutter


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
    length = z_idler - z_drive
    mid_z = (z_drive + z_idler) / 2.0
    strand = Box(CHAIN_ROLLER_DIAMETER_MM, width, length)
    cutter = Rot(90, 0, 0) * Cylinder(cut_r, CHAIN_TRANSVERSE_PITCH_MM + width + 6.0)
    pieces = []
    for sign in (1.0, -1.0):
        for offset in (row, -row):
            blank = Pos(axis_x + sign * pitch_radius, axis_y + offset, mid_z) * strand
            trimmed = blank - Pos(axis_x, axis_y, z_drive) * cutter - Pos(axis_x, axis_y, z_idler) * cutter
            pieces.extend(_leaves(trimmed))
    for z_center, upper in ((z_drive, False), (z_idler, True)):
        shell = _half_shell(cut_r, outer_r, width, upper)
        for offset in (row, -row):
            pieces.extend(_leaves(Pos(axis_x, axis_y + offset, z_center) * shell))
    if not pieces:
        raise ValueError("duplex chain produced no solid")
    return Compound(children=pieces)
