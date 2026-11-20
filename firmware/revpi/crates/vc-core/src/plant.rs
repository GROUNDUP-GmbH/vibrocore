//! One scan of hub, sonic, tilt and rod rotation.
//!
//! Each block only monitors feedback. None of them is an ISO 13849 function.
//! The PNOZ s4 and the drive STO stay hard-wired.

use crate::hub::{Hub, HubInput, HubOutput, HubState};
use crate::params::{LOWERED_UM, SONIC_TARGET_MHZ};
use crate::rotation::{Rotation, RotationInput, RotationOutput};
use crate::safety::{SafetyInput, SafetyMonitor, SafetyOutput};
use crate::sonic::{Sonic, SonicInput, SonicOutput};
use crate::tilt::{Tilt, TiltInput, TiltOutput};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct PlantInput {
    pub estop_nc: bool,
    pub limit_up_nc: bool,
    pub limit_down_nc: bool,
    pub hub_alarm: bool,
    pub sonic_drive_fault: bool,
    pub sonic_current_pct_x10: i32,
    pub sonic_sto_healthy: bool,
    pub sonic_actual_running: bool,
    pub tool_engaged: bool,
    pub enabling_held: bool,
    pub sensor_valid: bool,
    pub angle_mdeg: i32,
    pub limit_vertical_reached: bool,
    pub limit_folded_reached: bool,
    pub limit_deployed_reached: bool,
    pub limit_retracted_reached: bool,
    pub cmd_vertical: bool,
    pub cmd_fold: bool,
    pub cmd_extend: bool,
    pub cmd_retract: bool,
    pub cmd_cycle_start: bool,
    pub cmd_jog_down: bool,
    pub cmd_jog_up: bool,
    pub cmd_park: bool,
    pub cmd_unpark: bool,
    pub cmd_reset: bool,
    pub brake_test_enable: bool,
    pub brake_slip_um: i32,
    pub cmd_rotate: bool,
    pub rotate_reverse: bool,
    pub rotation_actual_rpm: i16,
    pub rotation_torque_pct: u8,
    pub rotation_fault: bool,
    pub sonic_target_mhz: i32,
}

impl Default for PlantInput {
    fn default() -> Self {
        Self {
            estop_nc: true,
            limit_up_nc: true,
            limit_down_nc: true,
            hub_alarm: false,
            sonic_drive_fault: false,
            sonic_current_pct_x10: 0,
            sonic_sto_healthy: true,
            sonic_actual_running: false,
            tool_engaged: false,
            enabling_held: false,
            sensor_valid: true,
            angle_mdeg: 0,
            limit_vertical_reached: false,
            limit_folded_reached: false,
            limit_deployed_reached: false,
            limit_retracted_reached: false,
            cmd_vertical: false,
            cmd_fold: false,
            cmd_extend: false,
            cmd_retract: false,
            cmd_cycle_start: false,
            cmd_jog_down: false,
            cmd_jog_up: false,
            cmd_park: false,
            cmd_unpark: false,
            cmd_reset: false,
            brake_test_enable: false,
            brake_slip_um: 0,
            cmd_rotate: false,
            rotate_reverse: false,
            rotation_actual_rpm: 0,
            rotation_torque_pct: 0,
            rotation_fault: false,
            sonic_target_mhz: SONIC_TARGET_MHZ,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct PlantOutput {
    pub hub: HubOutput,
    pub sonic: SonicOutput,
    pub tilt: TiltOutput,
    pub rotation: RotationOutput,
    pub safety: SafetyOutput,
}

#[derive(Clone, Copy, Debug)]
pub struct Plant {
    hub: Hub,
    sonic: Sonic,
    tilt: Tilt,
    rotation: Rotation,
    safety: SafetyMonitor,
    last_down: bool,
    last_up: bool,
    sonic_running: bool,
    sonic_confirmed: bool,
}

impl Default for Plant {
    fn default() -> Self {
        Self::new()
    }
}

impl Plant {
    pub fn new() -> Self {
        Self {
            hub: Hub::new(),
            sonic: Sonic::new(),
            tilt: Tilt::new(),
            rotation: Rotation::new(),
            safety: SafetyMonitor::new(),
            last_down: false,
            last_up: false,
            sonic_running: false,
            sonic_confirmed: true,
        }
    }

    pub fn set_position_um(&mut self, position_um: i32) {
        self.hub.set_position_um(position_um);
    }

    pub fn tick(&mut self, input: PlantInput) -> PlantOutput {
        let safety = self.safety.tick(SafetyInput {
            estop_nc: input.estop_nc,
            limit_up_nc: input.limit_up_nc,
            limit_down_nc: input.limit_down_nc,
            hub_alarm: input.hub_alarm,
            vfd_fault: input.sonic_drive_fault,
            vfd_current_pct: (input.sonic_current_pct_x10 as f32) / 10.0,
            hub_moving_down: self.last_down,
            hub_moving_up: self.last_up,
        });
        let hub_idle = self.hub.state() == HubState::Idle;
        let tilt = self.tilt.tick(TiltInput {
            safe_state: safety.safe_state,
            hub_idle,
            sensor_valid: input.sensor_valid,
            angle_mdeg: input.angle_mdeg,
            limit_vertical_reached: input.limit_vertical_reached,
            limit_folded_reached: input.limit_folded_reached,
            limit_deployed_reached: input.limit_deployed_reached,
            limit_retracted_reached: input.limit_retracted_reached,
            cmd_vertical: input.cmd_vertical,
            cmd_fold: input.cmd_fold,
            cmd_extend: input.cmd_extend,
            cmd_retract: input.cmd_retract,
        });
        let hub = self.hub.tick(HubInput {
            safe_state: safety.safe_state,
            stone_detected: safety.stone_detected,
            lift_allowed: tilt.lift_allowed,
            enabling_held: input.enabling_held,
            limit_up_reached: safety.limit_up_triggered,
            limit_down_reached: safety.limit_down_triggered,
            sonic_running: self.sonic_running,
            sonic_confirmed_stopped: self.sonic_confirmed,
            cmd_cycle_start: input.cmd_cycle_start,
            cmd_jog_down: input.cmd_jog_down,
            cmd_jog_up: input.cmd_jog_up,
            cmd_park: input.cmd_park,
            cmd_unpark: input.cmd_unpark,
            cmd_reset: input.cmd_reset,
            brake_test_enable: input.brake_test_enable,
            brake_slip_um: input.brake_slip_um,
        });
        let lowered = hub.position_um > LOWERED_UM;
        let sonic = self.sonic.tick(SonicInput {
            safe_state: safety.safe_state,
            fast_stop: hub.need_sonic_stop,
            lowered,
            tool_engaged: input.tool_engaged,
            sto_healthy: input.sonic_sto_healthy,
            drive_fault: input.sonic_drive_fault,
            actual_running: input.sonic_actual_running,
            cmd_reset: input.cmd_reset,
            target_mhz: input.sonic_target_mhz,
        });
        let hub_quiet = matches!(hub.state, HubState::Idle | HubState::Parked);
        let rotation = self.rotation.tick(RotationInput {
            permit: hub_quiet && !sonic.run_command && !safety.safe_state,
            cmd_run: input.cmd_rotate,
            reverse: input.rotate_reverse,
            actual_rpm: input.rotation_actual_rpm,
            torque_pct: input.rotation_torque_pct,
            drive_fault: input.rotation_fault,
        });
        self.last_down = hub.speed_um_s > 0;
        self.last_up = hub.speed_um_s < 0;
        self.sonic_running = sonic.run_command;
        self.sonic_confirmed = sonic.confirmed_stopped;
        PlantOutput {
            hub,
            sonic,
            tilt,
            rotation,
            safety,
        }
    }
}
