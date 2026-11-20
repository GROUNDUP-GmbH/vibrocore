//! Shared cycle constants. Integer units avoid float drift in the golden files.

use crate::safety::CYCLE_MS;

/// Carriage travel limit, in micrometres. Matches `rMAX_STROKE_MM`.
pub const STROKE_UM: i32 = 1_300_000;

/// Sample target depth, in micrometres.
pub const TARGET_UM: i32 = 1_200_000;

/// Position is "at home" at or below this value.
pub const HOME_UM: i32 = 2_000;

/// Sonic may run only below this carriage position.
pub const LOWERED_UM: i32 = 50_000;

pub const HOMING_UM_S: i32 = 40_000;
pub const PENETRATE_UM_S: i32 = 15_000;
pub const RETRACT_UM_S: i32 = 50_000;

/// SF4 jog speed. This is slower than penetrate speed.
pub const JOG_UM_S: i32 = 10_000;

/// SF3 brake-hold monitor window.
pub const BRAKE_TEST_MS: u32 = 100;
pub const BRAKE_TEST_CYCLES: u32 = BRAKE_TEST_MS / CYCLE_MS;

/// Slip above this value fails the brake test.
pub const BRAKE_SLIP_LIMIT_UM: i32 = 2_000;

/// SF6. Angle is millidegrees from vertical.
pub const TILT_ANGLE_LIMIT_MDEG: i32 = 5_000;

pub const SONIC_RAMP_MS: u32 = 100;
pub const SONIC_RAMP_CYCLES: u32 = SONIC_RAMP_MS / CYCLE_MS;
pub const SONIC_RAMP_UP_MHZ: i32 = 1_500;
pub const SONIC_SKIP_LOW_MHZ: i32 = 8_000;
pub const SONIC_SKIP_HIGH_MHZ: i32 = 25_000;
pub const SONIC_TARGET_MHZ: i32 = 100_000;
pub const SONIC_STANDSTILL_MS: u32 = 200;
pub const SONIC_STANDSTILL_CYCLES: u32 = SONIC_STANDSTILL_MS / CYCLE_MS;
pub const SONIC_STOP_TIMEOUT_MS: u32 = 5_000;
pub const SONIC_STOP_TIMEOUT_CYCLES: u32 = SONIC_STOP_TIMEOUT_MS / CYCLE_MS;

pub const ROTATION_RPM: i16 = 60;
pub const ROTATION_TORQUE_LIMIT_PCT: u8 = 40;
pub const ROTATION_STALL_MS: u32 = 200;
pub const ROTATION_STALL_CYCLES: u32 = ROTATION_STALL_MS / CYCLE_MS;

pub fn step_um(speed_um_s: i32) -> i32 {
    speed_um_s * (CYCLE_MS as i32) / 1_000
}
