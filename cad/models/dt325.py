"""Approximation solids for Geoprobe DT325 tooling.

Geoprobe publishes no CAD for these parts. Each solid is the outer envelope
plus a simplified thread zone. The thread form is not a helix. A helix is not
used because Geoprobe does not state the thread. Dimensions that are not in
the SOP, the product sheet or the tooling pages are named in
cad/vendor/DT325/SOURCE.md. Do not manufacture from these solids.
"""

from __future__ import annotations

# Published. 1.85 in x 25.4. The SOP core is written 47 mm.
SHOE_ID_MM = round(1.85 * 25.4, 2)
# Published on the current tooling page for shoe 205449. The 2011 SOP lists
# the same duty as 28508 and does not state this diameter. 3.5 in is 88.90 mm.
SHOE_OD_CATALOG_MM = round(3.45 * 25.4, 2)
# Published liner page, DT325 / DT37. The SOP rounds the outside to 2.1 in.
LINER_OD_MM = round(2.065 * 25.4, 3)
LINER_ID_MM = round(1.965 * 25.4, 3)
# Published. 1.25 in light-weight center rod and the drive-head pin.
PIN_OD_MM = round(1.25 * 25.4, 2)
# Published. SOP part 26719 is the 60 in sample sheath.
SHEATH_CATALOG_LENGTH_MM = round(60 * 25.4, 1)
# Published sample core. It is soil, not a solid in this model.
CORE_DIAMETER_MM = 47.0
CORE_LENGTH_MM = 1499.0

# Assumed. The table in SOURCE.md records the basis of each one.
SHEATH_OD_MM = 60.0
SHEATH_ID_MM = 53.0
SHEATH_THREAD_ID_MM = 56.0
THREAD_BAND_MM = 16.0
SHOE_THREAD_RELIEF_MM = 2.4
HEAD_BODY_OD_MM = 58.0
HEAD_BODY_LENGTH_MM = 44.0
HEAD_LOWER_OD_MM = 52.0
HEAD_LOWER_LENGTH_MM = 8.0
HEAD_LOWER_THREAD_OD_MM = 49.6
HEAD_LOWER_THREAD_MM = 14.0
PIN_THREAD_OD_MM = 29.35
PIN_THREAD_LENGTH_MM = 26.0
PIN_TIP_LENGTH_MM = 10.0
# The placed solids stay this far from the casing ends and the split carrier.
BORE_GAP_MM = 2.0
HEAD_GAP_MM = 0.2

DRIVE_HEAD_LENGTH_MM = (
    HEAD_LOWER_THREAD_MM
    + HEAD_LOWER_LENGTH_MM
    + HEAD_BODY_LENGTH_MM
    + PIN_THREAD_LENGTH_MM
    + PIN_TIP_LENGTH_MM
)


def _center(solid):
    from build123d import Pos

    center = solid.bounding_box().center()
    return Pos(-center.X, -center.Y, -center.Z) * solid


def _stack(segments: list[tuple[float, float]]):
    """Fuse cylinders. Each pair is (diameter, length), bottom to top."""
    from build123d import Cylinder, Pos

    pieces = []
    z_bottom = 0.0
    for diameter, length in segments:
        pieces.append(Pos(0.0, 0.0, z_bottom + length / 2.0) * Cylinder(diameter / 2.0, length))
        z_bottom += length
    solid = pieces[0]
    for piece in pieces[1:]:
        solid = solid + piece
    return solid


def cutting_shoe(od_mm: float, length_mm: float, id_mm: float = SHOE_ID_MM):
    """Hollow shoe. The upper band is the thread zone. The tip stays at full OD."""
    from build123d import Cylinder, Pos

    if length_mm <= THREAD_BAND_MM + 1.0:
        raise ValueError("cutting shoe is shorter than its thread zone")
    if od_mm <= id_mm + SHOE_THREAD_RELIEF_MM:
        raise ValueError("cutting shoe thread relief does not fit the wall")
    band = THREAD_BAND_MM
    outer = Pos(0.0, 0.0, length_mm / 2.0) * Cylinder(od_mm / 2.0, length_mm)
    # The band is a reduced outside diameter, not a helix.
    skin = Cylinder(od_mm / 2.0, band) - Cylinder((od_mm - SHOE_THREAD_RELIEF_MM) / 2.0, band + 0.4)
    skin = Pos(0.0, 0.0, length_mm - band / 2.0) * skin
    bore = Pos(0.0, 0.0, length_mm / 2.0) * Cylinder(id_mm / 2.0, length_mm + 2.0)
    return _center(outer - skin - bore)


def sheath(length_mm: float = SHEATH_CATALOG_LENGTH_MM):
    """Tube. Both ends have the same internal thread zone."""
    from build123d import Cylinder, Pos

    if length_mm <= 2.0 * THREAD_BAND_MM + 1.0:
        raise ValueError("sample sheath is shorter than its two thread zones")
    if SHEATH_THREAD_ID_MM >= SHEATH_OD_MM or SHEATH_THREAD_ID_MM <= SHEATH_ID_MM:
        raise ValueError("sample sheath thread zone is outside the wall")
    tube = Cylinder(SHEATH_OD_MM / 2.0, length_mm) - Cylinder(SHEATH_ID_MM / 2.0, length_mm + 2.0)
    for sign in (-1.0, 1.0):
        z_center = sign * (length_mm / 2.0 - THREAD_BAND_MM / 2.0)
        tube = tube - Pos(0.0, 0.0, z_center) * Cylinder(SHEATH_THREAD_ID_MM / 2.0, THREAD_BAND_MM)
    return tube


def drive_head():
    """One envelope for parts 10212 and 201385. The 1.25 in pin is the tip."""
    solid = _stack(
        [
            (HEAD_LOWER_THREAD_OD_MM, HEAD_LOWER_THREAD_MM),
            (HEAD_LOWER_OD_MM, HEAD_LOWER_LENGTH_MM),
            (HEAD_BODY_OD_MM, HEAD_BODY_LENGTH_MM),
            (PIN_THREAD_OD_MM, PIN_THREAD_LENGTH_MM),
            (PIN_OD_MM, PIN_TIP_LENGTH_MM),
        ]
    )
    return _center(solid)


def shape_for_geometry(geometry: dict):
    """Build the solid named by geometry['role']."""
    role = str(geometry.get("role") or "")
    if role == "shoe":
        return cutting_shoe(
            float(geometry["diameter_mm"]),
            float(geometry["length_mm"]),
            float(geometry["id_mm"]),
        )
    if role == "sheath":
        return sheath(float(geometry["length_mm"]))
    if role == "drive_head":
        return drive_head()
    raise ValueError(f"DT325 role must be shoe, sheath or drive_head, got {role}")


def bbox_mm(geometry: dict) -> tuple[float, float, float]:
    """Axis-aligned size of the centered solid."""
    role = str(geometry.get("role") or "")
    if role == "shoe":
        diameter = float(geometry["diameter_mm"])
        return (diameter, diameter, float(geometry["length_mm"]))
    if role == "sheath":
        return (SHEATH_OD_MM, SHEATH_OD_MM, float(geometry["length_mm"]))
    if role == "drive_head":
        return (HEAD_BODY_OD_MM, HEAD_BODY_OD_MM, DRIVE_HEAD_LENGTH_MM)
    raise ValueError(f"DT325 role must be shoe, sheath or drive_head, got {role}")


def _near(geometry: dict, key: str, expected: float) -> None:
    value = float(geometry.get(key) or 0.0)
    if abs(value - expected) > 0.05:
        raise ValueError(f"DT325 {key} {value} does not match the model value {expected}")


def validate_dt325(geometry: dict) -> None:
    role = str(geometry.get("role") or "")
    if role not in {"shoe", "sheath", "drive_head"}:
        raise ValueError(f"DT325 role must be shoe, sheath or drive_head, got {role}")
    if role == "shoe":
        for key in ("diameter_mm", "length_mm", "id_mm"):
            if float(geometry.get(key) or 0.0) <= 0.0:
                raise ValueError(f"DT325 shoe {key} must be > 0")
        _near(geometry, "id_mm", SHOE_ID_MM)
    if role == "sheath":
        _near(geometry, "length_mm", SHEATH_CATALOG_LENGTH_MM)
        _near(geometry, "diameter_mm", SHEATH_OD_MM)
        _near(geometry, "id_mm", SHEATH_ID_MM)
    if role == "drive_head":
        _near(geometry, "length_mm", DRIVE_HEAD_LENGTH_MM)
        _near(geometry, "diameter_mm", HEAD_BODY_OD_MM)
