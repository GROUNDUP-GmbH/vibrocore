"""Draft sizing of the vibration-motor bracket VC-SH-1350.

Pull-out is the governing case. The numbers are a hand check, not a released
calculation. See docs/engineering/CARRIAGE-BRACKET.md.
"""

from __future__ import annotations

from cad.models.machine_assembly import carriage_web_x_mm, rod_axis_x_mm
from cad.models.mast_layout import (
    BRACKET_BOLT_PITCH_Z_MM,
    BRACKET_GUSSET_HEIGHT_MM,
    BRACKET_GUSSET_THICKNESS_MM,
)
from cad.tools.pull_force import CHAIN_WORKING_N, LOAD_CELL_RATED_N

# ISO 898-1. Grade 8.8 proof stress and the tensile stress area of an M12 screw.
M12_PROOF_STRESS_MPA = 580.0
M12_STRESS_AREA_MM2 = 84.3
BOLT_COUNT = 4
GUSSET_COUNT = 2
# EN 10025-2. S355 yield for thickness up to 16 mm.
S355_YIELD_MPA = 355.0
# Allowance for the alternating motor load. This is not a fatigue calculation.
VIBRATION_FACTOR = 3.0


def bolt_line_x_mm() -> float:
    """X of the bolt group on the mid-plane of the carriage plate."""
    inner, outer = carriage_web_x_mm()
    return (inner + outer) / 2.0


def lever_arm_mm() -> float:
    """Distance from the rod axis to the bolt line."""
    return rod_axis_x_mm() - bolt_line_x_mm()


def moment_n_mm(force_n: float) -> float:
    return force_n * lever_arm_mm()


def upper_bolt_tension_n(force_n: float) -> float:
    """Tension in one upper bolt when the pull moment is shared by four bolts.

    Two bolts sit at +pitch/2 and two at -pitch/2. The moment is about the
    horizontal axis through the group.
    """
    z_mm = BRACKET_BOLT_PITCH_Z_MM / 2.0
    sum_z2 = BOLT_COUNT * z_mm * z_mm
    return moment_n_mm(force_n) * z_mm / sum_z2


def proof_load_n() -> float:
    return M12_PROOF_STRESS_MPA * M12_STRESS_AREA_MM2


def gusset_section_modulus_mm3() -> float:
    """Section modulus of one rectangular gusset, bent in its own plane."""
    thickness = BRACKET_GUSSET_THICKNESS_MM
    height = BRACKET_GUSSET_HEIGHT_MM
    return thickness * height * height / 6.0


def gusset_bending_mpa(force_n: float) -> float:
    """Bending stress when the two gussets share the pull moment equally."""
    moment = moment_n_mm(force_n) / GUSSET_COUNT
    return moment / gusset_section_modulus_mm3()


def design_pull_n() -> float:
    """Check load. The load cell full scale is above the allowable chain pull."""
    return LOAD_CELL_RATED_N


def working_pull_n() -> float:
    return CHAIN_WORKING_N
