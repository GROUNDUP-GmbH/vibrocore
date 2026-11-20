"""Orient manufacturer STEP files onto the envelope axes.

load_vendor_shape recenters a bounding box and does not rotate.
Each rotation below is the one named in that part's SOURCE.md.
A missing file returns None. The assembly then keeps the envelope.
"""

from __future__ import annotations

from build123d import Pos, Rot

from cad.tools.geometry import load_vendor_shape


def _mount_to_machine(loaded):
    """Map a HIWIN file onto the machine axes.

    File Z = 0 is the rail mounting plane. File Y is the rail direction.
    The result keeps that plane at X = 0 and the width centred on Y.
    """
    return Rot(90, 0, 0) * Rot(0, 90, 0) * loaded


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
