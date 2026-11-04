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


def shape_for(part: Part):
    """Return a build123d solid centered on the origin, in millimetres."""
    if not part.geometry:
        raise ValueError(f"{part.part_number} has no documented geometry")
    from build123d import Box, Cylinder

    geometry = part.geometry
    kind = geometry["kind"]
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


def read_step_bbox_mm(path: Path) -> tuple[float, float, float]:
    """Re-import a STEP file and return its axis-aligned size in millimetres."""
    from build123d import import_step

    loaded = import_step(path)
    if loaded is None:
        raise ValueError(f"{path} did not contain a solid")
    solid = loaded[0] if isinstance(loaded, (list, tuple)) else loaded
    size = solid.bounding_box().size
    return (float(size.X), float(size.Y), float(size.Z))
