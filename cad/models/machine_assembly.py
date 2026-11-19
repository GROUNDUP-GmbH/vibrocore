"""Study assembly of the machine in the start pose. Not a manufacturing model.

Every length comes from cad.models.mast_layout. A value marked TBD there is not
a measurement. The shoe tip is on the ground. The motors sit left and right of
the rod, so their 175 mm height is not in the axial chain.

Solids that already exist are built with cad.tools.geometry.shape_for.
This module only places them. It does not add a BOM line.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cad.models.mast_layout import (
    ADAPTER_LENGTH_MM,
    ADAPTER_OD_MM,
    BOTTOM_PLATE_THICKNESS_MM,
    BOTTOM_PLATE_WIDTH_MM,
    CARRIAGE_DEPTH_MM,
    CARRIAGE_HEIGHT_MM,
    CARRIAGE_WIDTH_MM,
    CASING_ID_MM,
    CASING_LENGTH_MM,
    CASING_OD_MM,
    COLUMN_DIAMETER_MM,
    COLUMN_FLANGE_DIAMETER_MM,
    COLUMN_FLANGE_THICKNESS_MM,
    COLUMN_PASSAGE_RADIAL_CLEARANCE_MM,
    COLUMN_SHAFT_LENGTH_MM,
    GROUND_CLEARANCE_MM,
    GROUND_DATUM_THICKNESS_MM,
    ISOLATOR_COUNT,
    ISOLATOR_DIAMETER_MM,
    ISOLATOR_FREE_HEIGHT_MM,
    MAST_PROFILE_DEPTH_MM,
    MAST_PROFILE_LENGTH_MM,
    MAST_PROFILE_WIDTH_MM,
    MOTOR_CENTRE_DISTANCE_MIN_MM,
    MOTOR_CENTRE_DISTANCE_MM,
    MOTOR_HEIGHT_MM,
    MOTOR_LENGTH_MM,
    MOTOR_TO_CARRIAGE_GAP_MM,
    MOTOR_WIDTH_MM,
    PROFILE_SPACING_MM,
    RAIL_BOTTOM_OFFSET_MM,
    RAIL_LENGTH_MM,
    RAIL_SECTION_HEIGHT_MM,
    RAIL_SECTION_WIDTH_MM,
    RIB_CENTRE_X_MM,
    SHOE_LENGTH_MM,
    SHOE_OD_MM,
    SHOE_PASSAGE_RADIAL_CLEARANCE_MM,
    STRING_AXIS_X_MM,
    STRING_AXIS_Y_MM,
    TOP_MARGIN_MM,
    TOP_PLATE_THICKNESS_MM,
    TOP_PLATE_WIDTH_MM,
    VIBRATING_PLATE_LENGTH_MM,
    VIBRATING_PLATE_THICKNESS_MM,
    VIBRATING_PLATE_WIDTH_MM,
    _mm,
    head_length_mm,
    required_total_mm,
)
from cad.tools.bom import ROOT

ASSEMBLY_ID = "VC-ASM-0000-layout"
RENDER_DIR = ROOT / "cad" / "export" / "renders"
STEP_NAME = f"{ASSEMBLY_ID}.step"
OVERLAP_TOLERANCE_MM3 = 1.0
RENDER_VIEWS = ("iso", "side", "top")

# Datum plan for this pose. Not a part and not a chain term.
_DATUM_LENGTH_MM = 420.0
_DATUM_WIDTH_MM = 400.0


@dataclass(frozen=True)
class Placed:
    name: str
    shape: object


def posed_stack_height_mm() -> float:
    """Shoe tip to the top of the carriage. Ground clearance and the top margin are not in this pose."""
    return _mm(
        SHOE_LENGTH_MM
        + CASING_LENGTH_MM
        + ADAPTER_LENGTH_MM
        + head_length_mm()
        + CARRIAGE_HEIGHT_MM
    )


def pose_stations() -> dict[str, float]:
    """Bottom Z of each axial piece. Z is up. The shoe tip is Z = 0."""
    shoe = 0.0
    casing = shoe + SHOE_LENGTH_MM
    adapter = casing + CASING_LENGTH_MM
    column = adapter + ADAPTER_LENGTH_MM
    flange = column + COLUMN_SHAFT_LENGTH_MM
    plate = flange + COLUMN_FLANGE_THICKNESS_MM
    carriage = plate + VIBRATING_PLATE_THICKNESS_MM
    profile_bottom = BOTTOM_PLATE_THICKNESS_MM
    profile_top = profile_bottom + MAST_PROFILE_LENGTH_MM
    rail_bottom = profile_bottom + RAIL_BOTTOM_OFFSET_MM
    rail_top = rail_bottom + RAIL_LENGTH_MM
    return {
        "shoe": shoe,
        "casing": casing,
        "adapter": adapter,
        "column": column,
        "flange": flange,
        "vibrating_plate": plate,
        "carriage": carriage,
        "carriage_top": carriage + CARRIAGE_HEIGHT_MM,
        "profile_bottom": profile_bottom,
        "profile_top": profile_top,
        "top_plate": profile_top,
        "rail_bottom": rail_bottom,
        "rail_top": rail_top,
    }


def assembly_parts(bom=None) -> list[Placed]:
    """One named solid per instance. Labels are the part numbers FreeCAD shows."""
    from build123d import Box, Cylinder, Pos, Rot

    from cad.tools.geometry import shape_for

    if bom is None:
        from cad.tools.bom import load_bom

        bom = load_bom()

    station = pose_stations()
    axis_x = STRING_AXIS_X_MM
    axis_y = STRING_AXIS_Y_MM
    parts: list[Placed] = []

    def add(name: str, shape, x: float, y: float, z: float, turn=None) -> None:
        moved = Pos(x, y, z) * (turn * shape if turn else shape)
        moved.label = name
        parts.append(Placed(name, moved))

    def vertical_cylinder(name: str, radius: float, length: float, z_bottom: float, x: float, y: float) -> None:
        if length <= 0:
            return
        add(name, Cylinder(radius, length), x, y, z_bottom + length / 2.0)

    # Ground datum. Below Z = 0. Not a part.
    add(
        "GROUND-DATUM",
        Box(_DATUM_LENGTH_MM, _DATUM_WIDTH_MM, GROUND_DATUM_THICKNESS_MM),
        0.0,
        0.0,
        -GROUND_DATUM_THICKNESS_MM / 2.0,
    )

    bottom = shape_for(bom.part("VC-FR-4300"))
    shoe_hole = Cylinder(
        SHOE_OD_MM / 2.0 + SHOE_PASSAGE_RADIAL_CLEARANCE_MM,
        BOTTOM_PLATE_THICKNESS_MM + 2.0,
    )
    add(
        "VC-FR-4300",
        bottom - shoe_hole,
        axis_x,
        axis_y,
        BOTTOM_PLATE_THICKNESS_MM / 2.0,
    )

    half_pitch = PROFILE_SPACING_MM / 2.0
    profile_center_z = station["profile_bottom"] + MAST_PROFILE_LENGTH_MM / 2.0
    for index, sign in enumerate((-1.0, 1.0), start=1):
        add(
            f"VC-FR-4100-{index}",
            shape_for(bom.part("VC-FR-4100")),
            0.0,
            sign * half_pitch,
            profile_center_z,
        )

    top = shape_for(bom.part("VC-FR-4400"))
    column_hole = Cylinder(
        COLUMN_DIAMETER_MM / 2.0 + COLUMN_PASSAGE_RADIAL_CLEARANCE_MM,
        TOP_PLATE_THICKNESS_MM + 2.0,
    )
    add(
        "VC-FR-4400",
        top - column_hole,
        axis_x,
        axis_y,
        station["top_plate"] + TOP_PLATE_THICKNESS_MM / 2.0,
    )

    rail_center_z = station["rail_bottom"] + RAIL_LENGTH_MM / 2.0
    rail_x = MAST_PROFILE_WIDTH_MM / 2.0 + RAIL_SECTION_HEIGHT_MM / 2.0
    for index, sign in enumerate((-1.0, 1.0), start=1):
        add(
            f"VC-HB-3100-{index}",
            Box(RAIL_SECTION_HEIGHT_MM, RAIL_SECTION_WIDTH_MM, RAIL_LENGTH_MM),
            rail_x,
            sign * half_pitch,
            rail_center_z,
        )

    # Carriage block. The 10 mm plate thickness is not this height.
    add(
        "VC-HB-3200",
        Box(CARRIAGE_WIDTH_MM, CARRIAGE_DEPTH_MM, CARRIAGE_HEIGHT_MM),
        axis_x,
        axis_y,
        station["carriage"] + CARRIAGE_HEIGHT_MM / 2.0,
    )

    plate_bottom = station["vibrating_plate"]
    add(
        "VC-SH-1301",
        shape_for(bom.part("VC-SH-1301")),
        axis_x,
        axis_y,
        plate_bottom + VIBRATING_PLATE_THICKNESS_MM / 2.0,
    )
    # Rib blank is 300 x 10 x 60, length along local X. Turn it along Y, under the plate.
    rib_turn = Rot(0, 0, 90)
    rib_height = float(bom.part("VC-SH-1302").geometry["height_mm"])
    rib_z = plate_bottom - rib_height / 2.0
    for index, sign in enumerate((-1.0, 1.0), start=1):
        add(
            f"VC-SH-1302-{index}",
            shape_for(bom.part("VC-SH-1302")),
            axis_x + sign * RIB_CENTRE_X_MM,
            axis_y,
            rib_z,
            rib_turn,
        )

    # The BOM solid is the shaft only. Place that solid. Do not draw a second shaft.
    add(
        "VC-SH-1400",
        shape_for(bom.part("VC-SH-1400")),
        axis_x,
        axis_y,
        station["column"] + COLUMN_SHAFT_LENGTH_MM / 2.0,
    )
    # The shaft solid from shape_for has no flange. The flange uses the documented diameter.
    vertical_cylinder(
        "VC-SH-1400-FLANGE",
        COLUMN_FLANGE_DIAMETER_MM / 2.0,
        COLUMN_FLANGE_THICKNESS_MM,
        station["flange"],
        axis_x,
        axis_y,
    )

    # Shaft along Y (the 255 mm side). That axis is perpendicular to the rod (Z).
    # Local box is 255 x 154 x 175. A yaw of 90 degrees swaps length and width.
    motor_turn = Rot(0, 0, 90)
    motor_z = station["carriage"] + MOTOR_HEIGHT_MM / 2.0
    half_centres = MOTOR_CENTRE_DISTANCE_MM / 2.0
    for index, sign in enumerate((-1.0, 1.0), start=1):
        add(
            f"VC-SH-1100-{index}",
            shape_for(bom.part("VC-SH-1100")),
            axis_x + sign * half_centres,
            axis_y,
            motor_z,
            motor_turn,
        )

    iso_x = VIBRATING_PLATE_LENGTH_MM / 2.0 - ISOLATOR_DIAMETER_MM / 2.0
    iso_y = VIBRATING_PLATE_WIDTH_MM / 2.0 - ISOLATOR_DIAMETER_MM / 2.0
    corners = ((1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0))
    if len(corners) != ISOLATOR_COUNT:
        raise ValueError("isolator count and corner list disagree")
    for index, (sx, sy) in enumerate(corners, start=1):
        vertical_cylinder(
            f"VC-SH-1600-{index}",
            ISOLATOR_DIAMETER_MM / 2.0,
            ISOLATOR_FREE_HEIGHT_MM,
            station["carriage"],
            axis_x + sx * iso_x,
            axis_y + sy * iso_y,
        )

    vertical_cylinder(
        "VC-SH-1500",
        ADAPTER_OD_MM / 2.0,
        ADAPTER_LENGTH_MM,
        station["adapter"],
        axis_x,
        axis_y,
    )
    casing = Cylinder(CASING_OD_MM / 2.0, CASING_LENGTH_MM) - Cylinder(
        CASING_ID_MM / 2.0, CASING_LENGTH_MM + 1.0
    )
    add(
        "VC-GP-7100",
        casing,
        axis_x,
        axis_y,
        station["casing"] + CASING_LENGTH_MM / 2.0,
    )
    vertical_cylinder(
        "VC-GP-7200",
        SHOE_OD_MM / 2.0,
        SHOE_LENGTH_MM,
        station["shoe"],
        axis_x,
        axis_y,
    )

    # shape_for recentres each half on its own box. Move the flat face back to the rod axis
    # so the two halves meet on the split and stay inside the casing bore.
    carrier_z = station["casing"] + CASING_LENGTH_MM / 2.0
    for number in ("VC-SP-7620", "VC-SP-7621"):
        part = bom.part(number)
        half = shape_for(part)
        box = half.bounding_box()
        if str(part.geometry["side"]) == "A":
            shift = -float(box.min.X)
        else:
            shift = -float(box.max.X)
        add(number, half, axis_x + shift, axis_y, carrier_z)

    _check_pose(parts, station)
    return parts


def assembly_shape(bom=None):
    from build123d import Compound

    parts = assembly_parts(bom)
    compound = Compound(children=[item.shape for item in parts])
    compound.label = ASSEMBLY_ID
    return compound


def _check_pose(parts: list[Placed], station: dict[str, float]) -> None:
    by_name = {item.name: item.shape for item in parts}
    shoe = by_name["VC-GP-7200"].bounding_box()
    carriage = by_name["VC-HB-3200"].bounding_box()
    if abs(float(shoe.min.Z)) > 0.05:
        raise ValueError("shoe tip is not on the ground")
    height = float(carriage.max.Z) - float(shoe.min.Z)
    if abs(height - posed_stack_height_mm()) > 0.05:
        raise ValueError("carriage top does not match the sum of the pose lengths")
    motors = [by_name["VC-SH-1100-1"], by_name["VC-SH-1100-2"]]
    centres = []
    for motor in motors:
        box = motor.bounding_box()
        size_x = float(box.max.X - box.min.X)
        size_y = float(box.max.Y - box.min.Y)
        size_z = float(box.max.Z - box.min.Z)
        if abs(size_z - MOTOR_HEIGHT_MM) > 0.05:
            raise ValueError("motor height is not vertical")
        if abs(size_y - MOTOR_LENGTH_MM) > 0.05 or abs(size_x - MOTOR_WIDTH_MM) > 0.05:
            raise ValueError("motor shaft is not perpendicular to the rod")
        centres.append((float(box.center().X), float(box.center().Y)))
    pitch = ((centres[0][0] - centres[1][0]) ** 2 + (centres[0][1] - centres[1][1]) ** 2) ** 0.5
    if pitch + 0.05 < MOTOR_CENTRE_DISTANCE_MIN_MM:
        raise ValueError("motor centre distance is below 170 mm")
    if abs(pitch - MOTOR_CENTRE_DISTANCE_MM) > 0.05:
        raise ValueError("motor centre distance does not match the shared parameter")
    gap = pitch - MOTOR_WIDTH_MM
    if CARRIAGE_WIDTH_MM > gap - 2.0 * MOTOR_TO_CARRIAGE_GAP_MM + 0.05:
        raise ValueError("carriage block overlaps the motor envelopes in plan")
    del station


def _boxes_overlap(left, right, pad: float = 0.2) -> bool:
    a = left.bounding_box()
    b = right.bounding_box()
    return not (
        a.max.X < b.min.X - pad
        or a.min.X > b.max.X + pad
        or a.max.Y < b.min.Y - pad
        or a.min.Y > b.max.Y + pad
        or a.max.Z < b.min.Z - pad
        or a.min.Z > b.max.Z + pad
    )


def intersection_volume_mm3(left, right) -> float:
    """Shared solid volume. Face contact and a missed pair both return 0."""
    if not _boxes_overlap(left, right):
        return 0.0
    common = left.intersect(right)
    if common is None:
        return 0.0
    shapes = common if hasattr(common, "volume") else list(common)
    total = 0.0
    for shape in shapes:
        total += abs(float(shape.volume))
    return total


def shape_distance_mm(left, right) -> float:
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape

    tool = BRepExtrema_DistShapeShape(left.wrapped, right.wrapped)
    tool.Perform()
    if not tool.IsDone():
        raise RuntimeError("shape distance failed")
    return float(tool.Value())


def overlap_pairs(parts: list[Placed] | None = None, bom=None) -> list[tuple[str, str, float]]:
    """Pairs whose shared volume is above the tolerance. Face contact is not an overlap."""
    items = parts if parts is not None else assembly_parts(bom)
    hits = []
    for index, left in enumerate(items):
        for right in items[index + 1 :]:
            if left.name == "GROUND-DATUM" or right.name == "GROUND-DATUM":
                continue
            volume = intersection_volume_mm3(left.shape, right.shape)
            if volume > OVERLAP_TOLERANCE_MM3:
                hits.append((left.name, right.name, volume))
    return hits


def _find(parts: list[Placed], name: str):
    for item in parts:
        if item.name == name:
            return item.shape
    raise KeyError(name)


def clearance_report(parts: list[Placed] | None = None, bom=None) -> dict[str, float]:
    """Clearances in millimetres. Profile figures use the TBD profile pitch."""
    items = parts if parts is not None else assembly_parts(bom)
    station = pose_stations()
    shoe_r = SHOE_OD_MM / 2.0
    casing_r = CASING_OD_MM / 2.0
    inner_face = PROFILE_SPACING_MM / 2.0 - MAST_PROFILE_DEPTH_MM / 2.0
    motor_inner = MOTOR_CENTRE_DISTANCE_MM / 2.0 - MOTOR_WIDTH_MM / 2.0
    carriage_outer = CARRIAGE_WIDTH_MM / 2.0
    profile_outer = PROFILE_SPACING_MM / 2.0 + MAST_PROFILE_DEPTH_MM / 2.0
    motor = _find(items, "VC-SH-1100-1")
    profile = _find(items, "VC-FR-4100-1")
    rail = _find(items, "VC-HB-3100-1")
    plate = _find(items, "VC-SH-1301")
    top = _find(items, "VC-FR-4400")
    return {
        "shoe_to_profile_mm": _mm(inner_face - shoe_r),
        "casing_to_profile_mm": _mm(inner_face - casing_r),
        "motor_to_carriage_mm": _mm(motor_inner - carriage_outer),
        "motor_to_profile_mm": _mm(shape_distance_mm(motor, profile)),
        "motor_to_rail_mm": _mm(shape_distance_mm(motor, rail)),
        "vibrating_plate_to_top_plate_mm": _mm(shape_distance_mm(plate, top)),
        "carriage_above_rail_mm": _mm(station["carriage"] - station["rail_top"]),
        "profile_overhang_past_bottom_plate_mm": _mm(profile_outer - BOTTOM_PLATE_WIDTH_MM / 2.0),
        "top_plate_cover_of_profile_mm": _mm(
            max(
                0.0,
                min(profile_outer, TOP_PLATE_WIDTH_MM / 2.0)
                - max(inner_face, -TOP_PLATE_WIDTH_MM / 2.0),
            )
        ),
        "motor_above_plate_mm": _mm(MOTOR_HEIGHT_MM),
        "posed_stack_mm": posed_stack_height_mm(),
        "required_mm": required_total_mm(),
        "rail_top_mm": _mm(station["rail_top"]),
        "carriage_bottom_mm": _mm(station["carriage"]),
    }


def assembly_bbox_mm(shape=None, bom=None) -> tuple[float, float, float]:
    solid = shape if shape is not None else assembly_shape(bom)
    size = solid.bounding_box().size
    return (float(size.X), float(size.Y), float(size.Z))


def export_machine_assembly(bom, step_dir: Path, render_dir: Path) -> list[Path]:
    """Write the assembly STEP and the three PNG views. Both directories are created."""
    from build123d import Compound, export_step

    from cad.tools.geometry import _freeze_step_header

    parts = assembly_parts(bom)
    step_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    shape = Compound(children=[item.shape for item in parts])
    shape.label = ASSEMBLY_ID
    step_path = step_dir / STEP_NAME
    export_step(shape, step_path)
    _freeze_step_header(step_path, ASSEMBLY_ID, bom.meta["cad_baseline_date"])
    written = [step_path]
    for view in RENDER_VIEWS:
        path = render_dir / f"{ASSEMBLY_ID}-{view}.png"
        _render_png(parts, view, path)
        written.append(path)
    return written


def render_paths() -> list[Path]:
    return [RENDER_DIR / f"{ASSEMBLY_ID}-{view}.png" for view in RENDER_VIEWS]


def _render_png(parts: list[Placed], view: str, path: Path) -> None:
    import numpy as np
    from PIL import Image

    eyes = {
        "iso": (np.array([1.0, -1.0, 0.72]), np.array([0.0, 0.0, 1.0])),
        "side": (np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])),
        "top": (np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0])),
    }
    eye, up = eyes[view]
    forward = -eye / np.linalg.norm(eye)
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    true_up = np.cross(right, forward)
    light = np.array([0.45, -0.35, 0.82])
    light = light / np.linalg.norm(light)

    triangles = []
    shades = []
    for item in parts:
        color = _color_for(item.name)
        vertices, faces = item.shape.tessellate(1.8)
        if not faces:
            continue
        points = np.array([(vertex.X, vertex.Y, vertex.Z) for vertex in vertices], dtype=np.float64)
        for face in faces:
            tri = points[list(face)]
            normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            norm = np.linalg.norm(normal)
            if norm < 1e-9:
                continue
            shade = 0.38 + 0.62 * abs(float(np.dot(normal / norm, light)))
            # The third column grows toward the camera so a nearer face wins the depth test.
            cam = np.column_stack(
                (
                    tri @ right,
                    tri @ true_up,
                    tri @ -forward,
                )
            )
            triangles.append(cam)
            shades.append((color[0] * shade, color[1] * shade, color[2] * shade))

    width, height = 960, 720
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:, :] = (236, 236, 232)
    depth = np.full((height, width), -1e30, dtype=np.float64)
    if not triangles:
        raise ValueError("assembly render has no triangles")
    cloud = np.concatenate(triangles, axis=0)
    span_x = float(cloud[:, 0].max() - cloud[:, 0].min())
    span_y = float(cloud[:, 1].max() - cloud[:, 1].min())
    span_x = max(span_x, 1.0)
    span_y = max(span_y, 1.0)
    scale = min((width * 0.88) / span_x, (height * 0.88) / span_y)
    center_x = float(cloud[:, 0].min() + cloud[:, 0].max()) / 2.0
    center_y = float(cloud[:, 1].min() + cloud[:, 1].max()) / 2.0

    for tri, color in zip(triangles, shades):
        px = width / 2.0 + (tri[:, 0] - center_x) * scale
        py = height / 2.0 - (tri[:, 1] - center_y) * scale
        z = tri[:, 2]
        _paint_triangle(image, depth, px, py, z, color)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image, mode="RGB").save(path, format="PNG", compress_level=9, optimize=False)


def _paint_triangle(image, depth, px, py, z, color) -> None:
    import numpy as np

    height, width = depth.shape
    min_x = max(int(np.floor(px.min())), 0)
    max_x = min(int(np.ceil(px.max())), width - 1)
    min_y = max(int(np.floor(py.min())), 0)
    max_y = min(int(np.ceil(py.max())), height - 1)
    if min_x > max_x or min_y > max_y:
        return
    xs = np.arange(min_x, max_x + 1, dtype=np.float64) + 0.5
    ys = np.arange(min_y, max_y + 1, dtype=np.float64) + 0.5
    grid_x, grid_y = np.meshgrid(xs, ys)
    x0, x1, x2 = px
    y0, y1, y2 = py
    denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(float(denom)) < 1e-8:
        return
    w0 = ((y1 - y2) * (grid_x - x2) + (x2 - x1) * (grid_y - y2)) / denom
    w1 = ((y2 - y0) * (grid_x - x2) + (x0 - x2) * (grid_y - y2)) / denom
    w2 = 1.0 - w0 - w1
    inside = (w0 >= -0.001) & (w1 >= -0.001) & (w2 >= -0.001)
    if not inside.any():
        return
    zee = w0 * z[0] + w1 * z[1] + w2 * z[2]
    window = depth[min_y : max_y + 1, min_x : max_x + 1]
    update = inside & (zee > window)
    window[update] = zee[update]
    rgb = np.array(color, dtype=np.float64)
    patch = image[min_y : max_y + 1, min_x : max_x + 1]
    patch[update] = np.clip(rgb, 0, 255).astype(np.uint8)


def _color_for(name: str) -> tuple[int, int, int]:
    table = (
        ("GROUND-DATUM", (210, 206, 196)),
        ("VC-FR-4100", (148, 163, 184)),
        ("VC-FR-4300", (100, 116, 139)),
        ("VC-FR-4400", (71, 85, 105)),
        ("VC-HB-3100", (15, 118, 110)),
        ("VC-HB-3200", (22, 163, 74)),
        ("VC-SH-1301", (234, 88, 12)),
        ("VC-SH-1302", (194, 65, 12)),
        ("VC-SH-1400", (202, 138, 4)),
        ("VC-SH-1100", (185, 28, 28)),
        ("VC-SH-1600", (126, 34, 206)),
        ("VC-SH-1500", (120, 80, 40)),
        ("VC-GP-7100", (37, 99, 235)),
        ("VC-GP-7200", (30, 64, 175)),
        ("VC-SP-7620", (13, 148, 136)),
        ("VC-SP-7621", (15, 118, 110)),
    )
    for prefix, color in table:
        if name.startswith(prefix):
            return color
    return (120, 120, 120)


def chain_matches_pose() -> bool:
    """The pose height is the required height without ground clearance and the top margin."""
    expected = _mm(required_total_mm() - GROUND_CLEARANCE_MM - TOP_MARGIN_MM)
    return abs(posed_stack_height_mm() - expected) < 0.05
