"""Simplified solids for vendor STEP files that are too large to store.

The measured bounding box comes from the manufacturer file.
The solid keeps that box.
A DIN-rail groove, a terminal recess and a connector face are cut into it.
Those cuts do not pass the outer box.
The original files are not in git. Each one is above 10 MB.
"""

from __future__ import annotations

from pathlib import Path

from cad.tools.bom import ROOT

VENDOR = ROOT / "cad" / "vendor"

# File bounding boxes read from the manufacturer STEP on 2026-11-20.
# Axes are the file axes, in millimetres.
MEASURED_FILE_BBOX_MM = {
    "VC-PW-5310": (126.26, 40.00, 128.96),
    "VC-CT-6220": (45.00, 120.35, 98.05),
    "VC-CT-6600": (83.00, 25.00, 80.25),
}

# Simplified file axes: X width along the rail, Y depth, Z height.
SIMPLIFIED_BBOX_MM = {
    "VC-PW-5310": (40.00, 126.26, 128.96),
    "VC-CT-6220": (45.00, 120.35, 98.05),
    "VC-CT-6600": (83.00, 80.25, 25.00),
}

STEP_NAME = {
    "VC-PW-5310": "SDR-120-ENVELOPE.step",
    "VC-CT-6220": "PNOZ-M-B0-ENVELOPE.step",
    "VC-CT-6600": "RUT241-ENVELOPE.step",
}


def simplified_solid(part_id: str):
    """Outer envelope with a rail groove, terminal recesses and a connector face."""
    from build123d import Box, Pos

    width, depth, height = SIMPLIFIED_BBOX_MM[part_id]
    body = Box(width, depth, height)
    groove_width = min(35.0, width - 4.0)
    if part_id == "VC-CT-6600":
        # The router sits flat. The rail clip is on the bottom face.
        groove = Pos(0, 0, -height / 2 + 0.8) * Box(groove_width, depth * 0.62, 1.8)
        terminals = Pos(0, -depth / 2 + 0.7, 0) * Box(width * 0.55, 1.6, height * 0.45)
        connectors = Pos(0, depth / 2 - 0.7, 0) * Box(width * 0.7, 1.6, height * 0.5)
    else:
        groove = Pos(0, -depth / 2 + 0.9, 0) * Box(groove_width, 2.0, height * 0.62)
        terminals = Pos(0, 0, height / 2 - 0.7) * Box(width * 0.72, depth * 0.42, 1.6)
        connectors = Pos(0, depth / 2 - 0.7, 0) * Box(width * 0.62, 1.6, height * 0.38)
    solid = body - groove - terminals - connectors
    solid.label = part_id
    return solid


def export_simplified(part_id: str, destination: Path | None = None) -> Path:
    from build123d import export_step

    from cad.tools.geometry import _freeze_step_header
    from cad.tools.bom import load_bom

    folder = destination or (VENDOR / part_id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / STEP_NAME[part_id]
    export_step(simplified_solid(part_id), path)
    _freeze_step_header(path, part_id, load_bom().meta["cad_baseline_date"])
    return path


def export_all_simplified() -> list[Path]:
    return [export_simplified(part_id) for part_id in STEP_NAME]
