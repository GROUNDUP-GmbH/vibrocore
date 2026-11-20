"""Orient manufacturer STEP files onto the envelope axes.

load_vendor_shape recenters a bounding box and does not rotate.
Each rotation below is the one named in that part's SOURCE.md.
A missing file returns None. The assembly then keeps the envelope.
"""

from __future__ import annotations

import copy

from build123d import Pos, Rot, scale

from cad.tools.geometry import facet_closed, load_vendor_shape

# Faceted copies are expensive. The assembly builds many times in one process.
_FACET = {}


def _mount_to_machine(loaded):
    """Map a HIWIN file onto the machine axes.

    File Z = 0 is the rail mounting plane. File Y is the rail direction.
    The result keeps that plane at X = 0 and the width centred on Y.
    """
    return Rot(90, 0, 0) * Rot(0, 90, 0) * loaded


def oriented_mk2004(length_mm: float | None = None):
    """mk 2004 extrusion. Local X is 50 mm, local Y is 100 mm, local Z is the length.

    The 3Dfindit file is 1500 mm along file X, 50 mm along file Y and 100 mm
    along file Z. The section origin is a corner, not the centre.
    Rot(0, 0, -90) then Rot(0, -90, 0) maps that extrusion onto local Z.
    A length other than 1500 mm scales local Z only.
    A file that is not this 1500 mm extrusion returns None.
    The assembly then keeps the generic vendor path.
    """
    loaded = load_vendor_shape("VC-FR-4100", recenter=False)
    if loaded is None:
        return None
    size = loaded.bounding_box().size
    stock_x = float(size.X)
    if abs(stock_x - 1500.0) > 1.0 or abs(float(size.Y) - 50.0) > 1.0 or abs(float(size.Z) - 100.0) > 1.0:
        return None
    turned = Rot(0, 0, -90) * Rot(0, -90, 0) * loaded
    center = turned.bounding_box().center()
    centered = Pos(-float(center.X), -float(center.Y), -float(center.Z)) * turned
    # The CADENAS solid is all splines. FreeCAD draws those as spikes.
    # Planar facets stay inside the section. Scale that copy along Z only.
    if "mk" not in _FACET:
        _FACET["mk"] = facet_closed(centered, 0.25, 0.25, 0.2)
    centered = _FACET["mk"]
    if length_mm is None or abs(length_mm - stock_x) < 0.05:
        return centered
    # about=(0, 0, 0) is the centred section. The location origin is still one end.
    return scale(copy.deepcopy(centered), by=(1.0, 1.0, length_mm / stock_x), about=(0.0, 0.0, 0.0))


def oriented_motor():
    """Siemens 1FL2104-4AG11-1MC0. Flange face at local Y = 0. Shaft points +Y.

    File Y = 0 is the flange face. The shaft tip is at file Y = -40 mm.
    The body rear is at file Y = 186.6 mm. Rot(0, 0, 180) sends the shaft to +Y.
    The file origin is the shaft axis, so the solid is not recentered.
    A file that is not this motor returns None.
    """
    loaded = load_vendor_shape("VC-HB-2100", recenter=False)
    if loaded is None:
        return None
    box = loaded.bounding_box()
    length = float(box.max.Y - box.min.Y)
    width = float(box.max.X - box.min.X)
    if abs(length - 226.6) > 1.0 or abs(width - 81.0) > 1.0:
        return None
    return Rot(0, 0, 180) * loaded


def oriented_rail():
    """HGR20R. Mounting face at X = 0. Length centred on Z.

    The file origin is the mounting face, so the solid is not bbox-recentered.
    """
    loaded = load_vendor_shape("VC-HB-3100", recenter=False)
    if loaded is None:
        return None
    return Pos(0.0, 0.0, -650.0) * _mount_to_machine(loaded)


def oriented_block():
    """HGH20CA. Same mounting plane as the rail. Length centred on Z.

    The hole pattern is centred on the rail width. The length centre of the
    holes is 5.3 mm from the solid centre. The solid is centred so both ends
    stay on the rail.
    """
    loaded = load_vendor_shape("VC-HB-3110", recenter=False)
    if loaded is None:
        return None
    solid = _mount_to_machine(loaded)
    mid_z = float(solid.bounding_box().center().Z)
    return Pos(0.0, 0.0, -mid_z) * solid


def oriented_gearbox():
    """PLE120 article 100460948. Motor face at local Y = 0. Output points +Y.

    File X = 0 is the motor flange face. File X = 204 mm is the shaft tip.
    The 115 mm square is centred on the axis. The file is not recentered.
    Rot(0, 0, 90) maps the shaft onto +Y. The key then points toward +X.
    """
    loaded = load_vendor_shape("VC-HB-2200", recenter=False)
    if loaded is None:
        return None
    return Rot(0, 0, 90) * loaded


def oriented_pillow():
    """SKF SYJ 30 TF. Bore along Y. Base at local Z = -42.9 mm. Shaft axis at Z = 0.

    The 3Dfindit file has the bore on file X and the 165 mm foot on file Z.
    The base is the plane file Y = -42.9 mm. The shaft axis is the file origin.
    Rot(90, 0, 0) stands the base down. Rot(0, 0, 90) then lays the bore on Y.
    The file origin is the bore, so the solid is not recentered.
    A file that is not this housing returns None.
    """
    loaded = load_vendor_shape("VC-HB-2600", recenter=False)
    if loaded is None:
        return None
    size = loaded.bounding_box().size
    if abs(float(size.Z) - 165.0) > 1.0 or abs(float(size.Y) - 82.5) > 1.0:
        return None
    turned = Rot(0, 0, 90) * Rot(90, 0, 0) * loaded
    # Cones and tori on this housing are the grey spikes under the foot.
    if "pillow" not in _FACET:
        _FACET["pillow"] = facet_closed(turned, 0.8, 0.5, 0.25)
    return _FACET["pillow"]


def oriented_sprocket():
    """G&G 10B-2 sprocket. The file axis is Z. The chain shaft is Y.

    VC-HB-2810 reuses this solid. It has no second file.
    The vendor body has 15 gaps. Each gap is opened so an ISO roller
    on the pitch circle sits in it with clearance.
    """
    loaded = load_vendor_shape("VC-HB-2800")
    if loaded is None:
        return None
    turned = Rot(90, 0, 0) * loaded
    # Tooth fillets are tori. FreeCAD draws them as spikes.
    if "sprocket" not in _FACET:
        _FACET["sprocket"] = _seat_gaps(facet_closed(turned, 0.45, 0.35, 0.1))
    return _FACET["sprocket"]


def _seat_gaps(solid):
    """Open each vendor gap for a Ø10.16 roller on the ISO pitch circle.

    The file already has a gap at 18 degrees and a tooth at 6 degrees.
    A roller on the exact pitch circle still kisses the flanks, so each
    gap is cut 0.5 mm larger than the roller.
    """
    import math

    from build123d import Cylinder, Pos, Rot

    from cad.models.mast_layout import CHAIN_TRANSVERSE_PITCH_MM
    from cad.models.roller_chain import GAP_CENTER_DEG, MESH_RADIUS_MM, TOOTH_COUNT

    radius = MESH_RADIUS_MM
    row = CHAIN_TRANSVERSE_PITCH_MM / 2.0
    # Roller radius is 5.08 mm. The cutter leaves about 0.5 mm of clearance.
    cutter_r = 5.58
    seated = solid
    for index in range(TOOTH_COUNT):
        deg = GAP_CENTER_DEG + index * (360.0 / TOOTH_COUNT)
        rad = math.radians(deg)
        center_x = radius * math.cos(rad)
        center_z = radius * math.sin(rad)
        for row_y in (row, -row):
            tool = Pos(center_x, row_y, center_z) * Rot(90, 0, 0) * Cylinder(cutter_r, 14.0)
            seated = seated - tool
    return seated


def oriented_coupling():
    """ROTEX 28. The 32H7 hub faces -Y, toward the gearbox.

    Jaw ends of the two hubs meet at Z = 0 to 17.5 mm in the file frame.
    The second hub is yawed 45 degrees so the jaws sit in the gaps.
    The spider sits on that same band. Rot(-90, 0, 0) then lays the axis on Y.
    The file origin is the jaw face, so these files are not bbox-recentered.
    """
    names = ("020285103200.stp", "020285100040.stp", "020281000045.stp")
    pieces = [load_vendor_shape("VC-HB-2400", name, recenter=False) for name in names]
    if any(piece is None for piece in pieces):
        return None
    hub32, hub0, spider = pieces
    other = Pos(0.0, 0.0, 17.5) * Rot(0, 180, 0) * Rot(0, 0, 45) * hub0
    ring = Pos(0.0, 0.0, 8.75) * spider
    # The jaws and the spider share about 39 mm³. A fuse of that fit is rejected.
    # One compound is still one part, so the shared volume is not a collision.
    from build123d import Compound

    return Rot(-90, 0, 0) * Compound(children=[hub32, other, ring])
