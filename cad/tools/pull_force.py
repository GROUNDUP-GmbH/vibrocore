"""Allowable hub pull force from the approved lift-drive data.

The chain working load is the limit. Do not use the motor peak torque
as an allowable pull force. See docs/engineering/PULL_FORCE.md and
docs/engineering/LIFT-DRIVE-SIZING.md.
"""

from __future__ import annotations

import math

# docs/design/HUB_SYSTEM.md section 3. Pitch of a 10B chain, DIN 8187.
CHAIN_PITCH_MM = 15.875
SPROCKET_TEETH = 15
# docs/engineering/LIFT-DRIVE-SIZING.md. Exact pitch-circle is 38.177 mm.
PITCH_RADIUS_MM = 38.18
GEAR_RATIO = 40
GEARBOX_EFFICIENCY = 0.97
CHAIN_BEARING_EFFICIENCY = 0.98
GEARBOX_IDLE_MOTOR_NM = 0.85
# Neugart PLE120-040, article 100460948, i = 40. No extra gear stage.
GEARBOX_T2D_NM = 195.0
GEARBOX_T2Z_NM = 230.0
GEARBOX_T2MAX_NM = 365.0
GEARBOX_T2STOP_NM = 500.0
# Siemens 1FL2104-4AG11-1MC0. The drive torque limit is the mechanical fuse.
MOTOR_TORQUE_RATED_NM = 3.2
MOTOR_TORQUE_MAX_NM = 10.8
MOTOR_TORQUE_LIMIT_NM = 6.7
# HUB_SYSTEM.md: breaking load about 44.5 kN, working load about 4.5 kN (10:1).
CHAIN_BREAK_N = 44500.0
CHAIN_WORKING_N = 4500.0
LOAD_CELL_RATED_N = 5000.0


def pitch_radius_mm(
    pitch_mm: float = CHAIN_PITCH_MM,
    teeth: int = SPROCKET_TEETH,
) -> float:
    """Older radius R = (pitch x teeth) / (2 pi). Do not use it for chain force."""
    return (pitch_mm * teeth) / (2.0 * math.pi)


def exact_pitch_radius_mm(
    pitch_mm: float = CHAIN_PITCH_MM,
    teeth: int = SPROCKET_TEETH,
) -> float:
    """Pitch-circle radius R = pitch / (2 sin(pi / teeth))."""
    return (pitch_mm / math.sin(math.pi / teeth)) / 2.0


def chain_force_n(torque_nm: float, radius_mm: float | None = None) -> float:
    """Chain tension from gearbox output torque. F = T2 x 0.98 / R."""
    radius = PITCH_RADIUS_MM if radius_mm is None else radius_mm
    return torque_nm * CHAIN_BEARING_EFFICIENCY / (radius / 1000.0)


def gearbox_output_from_motor_nm(motor_nm: float = MOTOR_TORQUE_LIMIT_NM) -> float:
    """Gearbox output torque from motor torque, with idle torque removed.

    T2 = (T_mot - 0.85 Nm) x 40 x 0.97.
    Do not pass the motor peak of 10.8 Nm. That result is above T2max.
    """
    return (motor_nm - GEARBOX_IDLE_MOTOR_NM) * GEAR_RATIO * GEARBOX_EFFICIENCY


def gearbox_nominal_force_n() -> float:
    """Chain force at continuous torque T2D."""
    return chain_force_n(GEARBOX_T2D_NM)


def gearbox_emergency_force_n() -> float:
    """Chain force at T2max. The load-cell bypass must carry this load."""
    return chain_force_n(GEARBOX_T2MAX_NM)


def allowable_pull_n() -> float:
    """Continuous pull the drive can use.

    The chain working load is below the T2D chain force, so the
    chain sets the allowable pull force.
    """
    return min(CHAIN_WORKING_N, gearbox_nominal_force_n())


def load_cell_needs_bypass() -> bool:
    """True when the pull path can load the cell above its rating.

    T2D chain force is already above 5 kN. The bypass load is the
    T2max chain force from gearbox_emergency_force_n.
    """
    return gearbox_nominal_force_n() > LOAD_CELL_RATED_N
