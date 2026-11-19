"""Study model of one split-carrier half (VC-SP-7620 / VC-SP-7621).

The carrier holds 4 to 6 open sample tubes end to end inside the 3.25 in
casing. The tubes are a lab consumable. They are not a Vibrocore part.
Push-on caps are not in the casing during driving. This model has no cap
parameter and no cap clearance.

Tube outside diameter and tube length are placeholders. Do not manufacture
from the STEP file. Replace the placeholder values after RadicleLab confirms
the tube.
"""

from __future__ import annotations

REQUIRED = (
    "side",
    "casing_id_mm",
    "radial_clearance_mm",
    "pocket_clearance_mm",
    "wall_thickness_mm",
    "tube_od_mm",
    "tube_length_mm",
    "tube_count",
)
# These numbers exist so a study solid can be exported. They are not measurements.
PLACEHOLDER_FIELDS = (
    "radial_clearance_mm",
    "pocket_clearance_mm",
    "wall_thickness_mm",
    "tube_od_mm",
    "tube_length_mm",
    "tube_count",
)
FORBIDDEN_CAP_FIELDS = (
    "cap_od_mm",
    "cap_height_mm",
    "cap_clearance_mm",
    "cap_od",
    "cap_height",
)


def validate_split_carrier(geometry: dict) -> None:
    """Reject a carrier definition that hides a placeholder or adds a cap."""
    if geometry.get("kind") != "split_carrier":
        raise ValueError("split carrier geometry.kind must be split_carrier")
    for key in FORBIDDEN_CAP_FIELDS:
        if key in geometry:
            raise ValueError(f"split carrier must not define {key}; caps are not in the casing")
    missing = [key for key in REQUIRED if geometry.get(key) in (None, "")]
    if missing:
        raise ValueError(f"split carrier missing {missing}")
    side = str(geometry["side"])
    if side not in {"A", "B"}:
        raise ValueError(f"split carrier side must be A or B, got {side}")
    placeholders = list(geometry.get("placeholders") or [])
    for key in ("tube_od_mm", "tube_length_mm"):
        if key not in placeholders:
            raise ValueError(f"{key} must be listed in placeholders")
    count = int(geometry["tube_count"])
    if count not in {4, 5, 6}:
        raise ValueError(f"tube_count must be 4, 5 or 6, got {count}")
    casing_id = float(geometry["casing_id_mm"])
    radial = float(geometry["radial_clearance_mm"])
    pocket_gap = float(geometry["pocket_clearance_mm"])
    wall = float(geometry["wall_thickness_mm"])
    tube_od = float(geometry["tube_od_mm"])
    tube_length = float(geometry["tube_length_mm"])
    for name, value in (
        ("casing_id_mm", casing_id),
        ("radial_clearance_mm", radial),
        ("pocket_clearance_mm", pocket_gap),
        ("wall_thickness_mm", wall),
        ("tube_od_mm", tube_od),
        ("tube_length_mm", tube_length),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be > 0")
    outer_r = (casing_id - 2.0 * radial) / 2.0
    pocket_r = tube_od / 2.0 + pocket_gap
    if outer_r <= pocket_r:
        raise ValueError("tube pocket does not fit inside the casing")
    if outer_r - pocket_r < wall:
        raise ValueError("wall_thickness_mm is thicker than the material outside the pocket")


def outer_radius_mm(geometry: dict) -> float:
    validate_split_carrier(geometry)
    return (float(geometry["casing_id_mm"]) - 2.0 * float(geometry["radial_clearance_mm"])) / 2.0


def stack_length_mm(geometry: dict) -> float:
    validate_split_carrier(geometry)
    return float(geometry["tube_count"]) * float(geometry["tube_length_mm"])


def bbox_mm(geometry: dict) -> tuple[float, float, float]:
    """Axis-aligned size of one centred half. X is the thin direction."""
    radius = outer_radius_mm(geometry)
    return (radius, 2.0 * radius, stack_length_mm(geometry))


def shape_for_geometry(geometry: dict):
    """One half-shell, centred on the origin, in millimetres.

    Side B is the mirror of side A. With a round pocket the two solids are
    congruent. The two part numbers stay so a later asymmetric feature can differ.
    """
    validate_split_carrier(geometry)
    from build123d import Box, Cylinder, Plane, Pos

    radius = outer_radius_mm(geometry)
    length = stack_length_mm(geometry)
    pocket_r = float(geometry["tube_od_mm"]) / 2.0 + float(geometry["pocket_clearance_mm"])
    body = Cylinder(radius, length)
    # Keep the +X half. The box covers X < 0 and is longer than the body.
    negative = Pos(-radius, 0, 0) * Box(2.0 * radius, 4.0 * radius, length + 2.0)
    # The pocket is one open bore. Tubes sit end to end. There is no cap gap.
    pocket = Cylinder(pocket_r, length + 1.0)
    half = body - negative - pocket
    if str(geometry["side"]) == "B":
        half = half.mirror(Plane.YZ)
    center = half.bounding_box().center()
    return Pos(-center.X, -center.Y, -center.Z) * half
