"""Parametric solids for parts whose dimensions are already in the BOM.

build123d 0.13 (OpenCascade) writes the STEP file. Dimensions are read from
the YAML bill of materials. A missing dimension is not replaced with a guess:
the part simply has no geometry block and is not exported.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from cad.tools.bom import ROOT, BillOfMaterials, Part, modelled_parts

STEP_DIR = ROOT / "cad" / "export" / "step"
GEOMETRY_JSON = ROOT / "cad" / "export" / "geometry.json"
VENDOR_DIR = ROOT / "cad" / "vendor"


def shape_for(part: Part):
    """Return a build123d solid centered on the origin, in millimetres."""
    if not part.geometry:
        raise ValueError(f"{part.part_number} has no documented geometry")
    geometry = part.geometry
    kind = geometry["kind"]
    if kind == "split_carrier":
        from cad.models.split_carrier import shape_for_geometry

        solid = shape_for_geometry(geometry)
    elif kind == "dt325":
        from cad.models.dt325 import shape_for_geometry

        solid = shape_for_geometry(geometry)
    else:
        from build123d import Box, Cylinder

        if kind == "box":
            solid = Box(geometry["length_mm"], geometry["width_mm"], geometry["height_mm"])
        elif kind == "cylinder":
            solid = Cylinder(geometry["diameter_mm"] / 2.0, geometry["length_mm"])
        else:
            raise ValueError(f"{part.part_number}: unsupported kind {kind}")
    solid.label = part.part_number
    solid.color = None
    return solid


def expected_bbox_mm(part: Part) -> tuple[float, float, float]:
    geometry = part.geometry or {}
    if geometry.get("kind") == "box":
        return (
            float(geometry["length_mm"]),
            float(geometry["width_mm"]),
            float(geometry["height_mm"]),
        )
    if geometry.get("kind") == "cylinder":
        diameter = float(geometry["diameter_mm"])
        return (diameter, diameter, float(geometry["length_mm"]))
    if geometry.get("kind") == "split_carrier":
        from cad.models.split_carrier import bbox_mm

        return bbox_mm(geometry)
    if geometry.get("kind") == "dt325":
        from cad.models.dt325 import bbox_mm

        return bbox_mm(geometry)
    raise ValueError(part.part_number)


def step_path(part: Part) -> Path:
    return STEP_DIR / f"{part.part_number}.step"


def export_step_files(bom: BillOfMaterials, destination: Path | None = None) -> list[Path]:
    from build123d import export_step

    directory = destination or STEP_DIR
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    manifest = []
    for part in modelled_parts(bom):
        solid = shape_for(part)
        path = directory / f"{part.part_number}.step"
        export_step(solid, path)
        _freeze_step_header(path, part.part_number, bom.meta["cad_baseline_date"])
        written.append(path)
        if destination is not None:
            continue
        size = expected_bbox_mm(part)
        manifest.append(
            {
                "part_number": part.part_number,
                "engineering_revision": part.revision_index,
                "kind": part.geometry["kind"],
                "fidelity": part.geometry["fidelity"],
                "bbox_mm": {"x": size[0], "y": size[1], "z": size[2]},
                "source": part.geometry["source"],
                "step": f"cad/export/step/{part.part_number}.step",
                "unknowns": part.unknowns,
            }
        )
    if destination is None:
        GEOMETRY_JSON.parent.mkdir(parents=True, exist_ok=True)
        GEOMETRY_JSON.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return written


def _freeze_step_header(path: Path, part_number: str, baseline_date: str) -> None:
    """OpenCascade stamps FILE_NAME with the clock. Pin it so git and CI match."""
    text = path.read_text(encoding="utf-8")
    frozen = re.sub(
        r"FILE_NAME\('[^']*','[^']*'",
        f"FILE_NAME('{part_number}','{baseline_date}T00:00:00'",
        text,
        count=1,
    )
    if frozen == text:
        raise ValueError(f"{path} has no FILE_NAME timestamp to pin")
    path.write_text(frozen, encoding="utf-8")


def vendor_step_path(part_id: str) -> Path | None:
    """First STEP file in cad/vendor/<part-id>/, or None when the folder is empty."""
    folder = VENDOR_DIR / part_id
    if not folder.is_dir():
        return None
    matches = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in {".step", ".stp"}
    )
    return matches[0] if matches else None


def import_step_solid(path):
    """First solid or compound in a STEP file."""
    from build123d import import_step

    loaded = import_step(str(path))
    if loaded is None:
        raise ValueError(f"{path} did not contain a solid")
    return loaded[0] if isinstance(loaded, (list, tuple)) else loaded


def _without_empty(shape, path: Path):
    """Drop the empty datum compound a manufacturer STEP often carries.

    A later fuse of that empty shape raises Null TopoDS_Shape.
    """
    from build123d import Compound

    solids = [item for item in shape.solids() if abs(float(item.volume)) > 1.0] if hasattr(shape, "solids") else []
    if not solids:
        if abs(float(shape.volume)) <= 1.0:
            raise ValueError(f"{path} did not contain a solid")
        return shape
    if len(solids) == 1:
        return solids[0]
    return Compound(children=solids)


def load_vendor_shape(part_id: str, filename: str | None = None, *, recenter: bool = True):
    """Vendor solid, or None when that STEP is absent.

    The default recenters the bounding box and keeps the file axes.
    The assembly rotates that solid onto the envelope axis.
    The rotation and any extra origin shift are in cad/vendor/<part-id>/SOURCE.md.
    Pass filename when one part is several STEP files.
    Pass recenter=False when the file origin is a mating face, not the box centre.
    A missing file is not an error. The caller keeps the envelope.
    """
    folder = VENDOR_DIR / part_id
    if filename is None:
        path = vendor_step_path(part_id)
    else:
        path = folder / filename
        if not path.is_file():
            path = None
    if path is None:
        return None
    from build123d import Pos

    solid = _without_empty(import_step_solid(path), path)
    if recenter:
        center = solid.bounding_box().center()
        solid = Pos(-float(center.X), -float(center.Y), -float(center.Z)) * solid
    solid.label = part_id
    return solid


def facet_closed(shape, linear_mm: float, angular_rad: float, sew_mm: float):
    """Replace cones, tori and splines with planar triangles.

    FreeCAD draws those faces as long spikes. A triangle stays inside its three
    vertices. A solid that does not close is returned unchanged.
    """
    from OCP.BRepBuilderAPI import (
        BRepBuilderAPI_MakeFace,
        BRepBuilderAPI_MakePolygon,
        BRepBuilderAPI_MakeSolid,
        BRepBuilderAPI_Sewing,
    )
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    from OCP.gp import gp_Pnt
    from build123d import Compound, Shape

    def one(solid):
        verts, tris = solid.tessellate(linear_mm, angular_rad)
        sew = BRepBuilderAPI_Sewing(sew_mm)
        for a, b, c in tris:
            pa, pb, pc = verts[a], verts[b], verts[c]
            poly = BRepBuilderAPI_MakePolygon(
                gp_Pnt(float(pa.X), float(pa.Y), float(pa.Z)),
                gp_Pnt(float(pb.X), float(pb.Y), float(pb.Z)),
                gp_Pnt(float(pc.X), float(pc.Y), float(pc.Z)),
                True,
            )
            if not poly.IsDone():
                continue
            face = BRepBuilderAPI_MakeFace(poly.Wire())
            if face.IsDone():
                sew.Add(face.Face())
        sew.Perform()
        maker = BRepBuilderAPI_MakeSolid()
        exp = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
        shells = 0
        while exp.More():
            maker.Add(TopoDS.Shell(exp.Current()))
            shells += 1
            exp.Next()
        if shells != 1 or not maker.IsDone():
            return None
        raw = maker.Solid()
        if not BRepCheck_Analyzer(raw, True).IsValid():
            return None
        out = Shape.cast(raw)
        if float(out.volume) < 0.0:
            out = Shape.cast(raw.Reversed())
        try:
            out.tessellate(max(linear_mm, 1.8), max(angular_rad, 0.5))
        except Exception:
            return None
        return out

    solids = [item for item in shape.solids() if abs(float(item.volume)) > 1.0] if hasattr(shape, "solids") else []
    if not solids:
        solids = [shape]
    made = []
    for solid in solids:
        faceted = one(solid)
        made.append(solid if faceted is None else faceted)
    if len(made) == 1:
        return made[0]
    return Compound(children=made)


def read_step_bbox_mm(path: Path) -> tuple[float, float, float]:
    """Re-import a STEP file and return its axis-aligned size in millimetres."""
    from build123d import import_step

    loaded = import_step(path)
    if loaded is None:
        raise ValueError(f"{path} did not contain a solid")
    solid = loaded[0] if isinstance(loaded, (list, tuple)) else loaded
    size = solid.bounding_box().size
    return (float(size.X), float(size.Y), float(size.Z))
