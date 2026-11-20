"""Allowable hub pull force from the drive data in the design notes.

The chain working load is the limit. The motor-times-ratio tension is not
an allowable pull force. See docs/engineering/PULL_FORCE.md.
"""

from __future__ import annotations

import math

# docs/design/HUB_SYSTEM.md section 3. Pitch of a 10B chain, DIN 8187.
CHAIN_PITCH_MM = 15.875
SPROCKET_TEETH = 15
# HUB_SYSTEM.md uses 90 percent. This is the figure in the design note.
GEARBOX_EFFICIENCY = 0.90
GEAR_RATIO = 40
# HUB_SYSTEM.md section 3.2. Output torque, so do not apply efficiency again.
GEARBOX_NOMINAL_NM = 220.0
GEARBOX_EMERGENCY_NM = 360.0
# HUB_SYSTEM.md section 4.1 calls 15 Nm the nominal motor torque.
# The BOM line says about 20 Nm. The motor catalogue number is not selected.
MOTOR_TORQUE_NOMINAL_NM = 15.0
MOTOR_TORQUE_BOM_NM = 20.0
# HUB_SYSTEM.md section 4. The working load is 4.5 kN.
# G&G does not state a breaking load for 600-302-0000. Do not store a substitute.
CHAIN_WORKING_N = 4500.0
LOAD_CELL_RATED_N = 5000.0


def pitch_radius_mm(
    pitch_mm: float = CHAIN_PITCH_MM,
    teeth: int = SPROCKET_TEETH,
) -> float:
    """Radius used in HUB_SYSTEM.md: R = (pitch x teeth) / (2 pi)."""
    return (pitch_mm * teeth) / (2.0 * math.pi)


def exact_pitch_radius_mm(
    pitch_mm: float = CHAIN_PITCH_MM,
    teeth: int = SPROCKET_TEETH,
) -> float:
    """Pitch-circle radius R = pitch / (2 sin(pi / teeth))."""
    return (pitch_mm / math.sin(math.pi / teeth)) / 2.0


def chain_force_n(torque_nm: float, radius_mm: float | None = None) -> float:
    radius = pitch_radius_mm() if radius_mm is None else radius_mm
    return torque_nm / (radius / 1000.0)


def motor_path_torque_nm(motor_nm: float = MOTOR_TORQUE_NOMINAL_NM) -> float:
    return motor_nm * GEAR_RATIO * GEARBOX_EFFICIENCY


def gearbox_nominal_force_n() -> float:
    return chain_force_n(GEARBOX_NOMINAL_NM)


def gearbox_emergency_force_n() -> float:
    return chain_force_n(GEARBOX_EMERGENCY_NM)


def allowable_pull_n() -> float:
    """Continuous pull the drive may use.

    The chain working load is below the gearbox nominal tension, so the
    chain sets the allowable pull force.
    """
    return min(CHAIN_WORKING_N, gearbox_nominal_force_n())


def load_cell_needs_bypass() -> bool:
    """True when the pull path can load the cell above its rating."""
    return gearbox_nominal_force_n() > LOAD_CELL_RATED_N
