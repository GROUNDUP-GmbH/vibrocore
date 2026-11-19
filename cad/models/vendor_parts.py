"""Orient manufacturer STEP files onto the envelope axes.

load_vendor_shape recenters a bounding box and does not rotate.
Each rotation below is the one named in that part's SOURCE.md.
A missing file returns None. The assembly then keeps the envelope.
"""

from __future__ import annotations

from build123d import Pos, Rot

from cad.tools.geometry import load_vendor_shape


def oriented_motor():
    """Nanotec body. Shaft along +Y. The connector hangs on -Z.

    The file shaft is +Z. Rot(0, 90, 0) maps that to +X.
    Rot(180, 0, 0) then Rot(0, 0, 90) maps the shaft to +Y.
    load_vendor_shape puts the bounding-box centre at the origin.
    That centre is not the shaft axis. The shift puts the Ø19 shaft on X = 0 and Z = 0.
    Rot(0, 180, 0) about that shaft points the connector up, clear of the bottom plate.
    """
    loaded = load_vendor_shape("VC-HB-2100")
    if loaded is None:
        return None
    solid = Rot(0, 0, 90) * Rot(180, 0, 0) * Rot(0, 90, 0) * loaded
    shaft = next(
        item
        for item in solid.solids()
        if item.bounding_box().size.Y > 50.0 and item.bounding_box().size.X < 30.0
    )
    center = shaft.bounding_box().center()
    return Rot(0, 180, 0) * Pos(-float(center.X), 0.0, -float(center.Z)) * solid


def oriented_brake():
    """BFK457-10 Compact. Shaft along Y, cable on +X, lug on +Z.

    The file shaft is +X and the cable runs toward -Y.
    Rot(90, 270, 0) maps the shaft onto Y and the cable onto -Z.
    load_vendor_shape recenters the bounding box. The cable pulls that centre off the shaft.
    The rotor, not the cable, defines the axis.
    Rot(0, -90, 0) about the shaft then sends the cable forward and the lug up.
    A cable on -Z would pass through the bottom plate.
    """
    loaded = load_vendor_shape("VC-HB-3000")
    if loaded is None:
        return None
    solid = Rot(90, 270, 0) * loaded
    rotor = min(solid.solids(), key=lambda item: abs(item.volume))
    center = rotor.bounding_box().center()
    return Rot(0, -90, 0) * Pos(-float(center.X), 0.0, -float(center.Z)) * solid


def oriented_sprocket():
    """G&G 10B-2 sprocket. The file axis is Z. The chain shaft is Y.

    VC-HB-2810 reuses this solid. It has no second file.
    """
    loaded = load_vendor_shape("VC-HB-2800")
    if loaded is None:
        return None
    return Rot(90, 0, 0) * loaded


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
