//! Hub carriage on the S200.
//!
//! The S200 PTI receives a pulse train. This module emits direction and speed.
//! It does not emit Modbus setpoints. Modbus status registers stay TODO.
//! The motor holding brake is on S200 terminal X108.
//! The RevPi does not drive that brake.
//! Stefan decided on 2026-11-20 that this brake is the only hold.
//! There is no second holding means.
//! Nobody works under the raised head.
//! The chain drive is sized for the load and is inspected regularly.
//! That decision is a deliberate risk acceptance.
//! The brake test is optional. It only monitors slip.
//! SF3 and SF4 are not an ISO 13849 performance level.

use crate::params::{
    step_um, BRAKE_SLIP_LIMIT_UM, BRAKE_TEST_CYCLES, HOME_UM, HOMING_UM_S, JOG_UM_S, LOWERED_UM,
    PENETRATE_UM_S, RETRACT_UM_S, STROKE_UM, TARGET_UM,
};

/// Stefan, 2026-11-20. No bolt, no second brake, no catch.
pub const SF3_SECOND_HOLD_FITTED: bool = false;

/// The brake test runs only when the caller asks for it.
pub const SF3_BRAKE_TEST_DEFAULT: bool = false;

/// Codes 0 to 7 match `FB_HubControl`. Codes 8 to 11 are new.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum HubState {
    Idle = 0,
    Homing = 1,
    DrillWait = 2,
    Drilling = 3,
    StopSonic = 4,
    Retract = 5,
    EstopHold = 6,
    Fault = 7,
    Jog = 8,
    ParkMove = 9,
    BrakeTest = 10,
    Parked = 11,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct HubInput {
    pub safe_state: bool,
    pub stone_detected: bool,
    pub lift_allowed: bool,
    pub enabling_held: bool,
    pub limit_up_reached: bool,
    pub limit_down_reached: bool,
    pub sonic_running: bool,
    pub sonic_confirmed_stopped: bool,
    pub cmd_cycle_start: bool,
    pub cmd_jog_down: bool,
    pub cmd_jog_up: bool,
    pub cmd_park: bool,
    pub cmd_unpark: bool,
    pub cmd_reset: bool,
    /// Optional SF3 monitor. The S200 still holds with its own brake when this is false.
    pub brake_test_enable: bool,
    /// Test input. Added to position during the brake test.
    pub brake_slip_um: i32,
}

impl Default for HubInput {
    fn default() -> Self {
        Self {
            safe_state: false,
            stone_detected: false,
            lift_allowed: true,
            enabling_held: false,
            limit_up_reached: false,
            limit_down_reached: false,
            sonic_running: false,
            sonic_confirmed_stopped: true,
            cmd_cycle_start: false,
            cmd_jog_down: false,
            cmd_jog_up: false,
            cmd_park: false,
            cmd_unpark: false,
            cmd_reset: false,
            brake_test_enable: SF3_BRAKE_TEST_DEFAULT,
            brake_slip_um: 0,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct HubOutput {
    pub state: HubState,
    pub position_um: i32,
    pub speed_um_s: i32,
    pub pulse_enable: bool,
    pub direction_down: bool,
    pub need_sonic_stop: bool,
    pub moving: bool,
    pub motion_blocked: bool,
    pub fault: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Hub {
    state: HubState,
    position_um: i32,
    test_ticks: u32,
    stop_ticks: u32,
    origin_um: i32,
    prev_reset: bool,
    fault: bool,
}

impl Default for Hub {
    fn default() -> Self {
        Self::new()
    }
}

impl Hub {
    pub const fn new() -> Self {
        Self {
            state: HubState::Idle,
            position_um: 0,
            test_ticks: 0,
            stop_ticks: 0,
            origin_um: 0,
            prev_reset: false,
            fault: false,
        }
    }

    pub const fn state(self) -> HubState {
        self.state
    }

    pub const fn position_um(self) -> i32 {
        self.position_um
    }

    pub fn set_position_um(&mut self, position_um: i32) {
        self.position_um = position_um.clamp(0, STROKE_UM);
    }

    pub fn tick(&mut self, input: HubInput) -> HubOutput {
        let reset_edge = input.cmd_reset && !self.prev_reset;
        self.prev_reset = input.cmd_reset;

        if input.safe_state && self.state != HubState::EstopHold {
            self.state = HubState::EstopHold;
            self.stop_ticks = 0;
            return self.stopped(true, false);
        }

        match self.state {
            HubState::Idle => self.idle(input),
            HubState::Jog => self.jog(input),
            HubState::Homing => self.home(input),
            HubState::DrillWait => self.drill_wait(input),
            HubState::Drilling => self.drill(input),
            HubState::StopSonic => self.stop_sonic(input),
            HubState::Retract => self.retract(input),
            HubState::ParkMove => self.park_move(input),
            HubState::BrakeTest => self.brake_test(input),
            HubState::Parked => self.parked(input),
            HubState::EstopHold => self.estop(input, reset_edge),
            HubState::Fault => self.fault_state(input, reset_edge),
        }
    }

    fn idle(&mut self, input: HubInput) -> HubOutput {
        self.fault = false;
        let motion_cmd =
            input.cmd_jog_down || input.cmd_jog_up || input.cmd_cycle_start || input.cmd_park;
        if !input.lift_allowed && motion_cmd {
            return self.stopped(false, true);
        }
        if input.cmd_park && input.lift_allowed {
            self.origin_um = self.position_um;
            self.test_ticks = 0;
            if self.at_home() {
                return self.enter_hold(input);
            }
            self.state = HubState::ParkMove;
            return self.park_move(input);
        }
        if input.cmd_cycle_start && input.lift_allowed {
            self.state = HubState::Homing;
            return self.home(input);
        }
        if self.jog_allowed(input) {
            self.state = HubState::Jog;
            return self.jog(input);
        }
        self.stopped(false, false)
    }

    fn jog(&mut self, input: HubInput) -> HubOutput {
        if !self.jog_allowed(input) {
            self.state = HubState::Idle;
            return self.stopped(false, !input.lift_allowed);
        }
        let down = input.cmd_jog_down && !input.limit_down_reached;
        let up = input.cmd_jog_up && !down && !input.limit_up_reached;
        if down {
            self.move_by(JOG_UM_S);
            self.motion(HubState::Jog, JOG_UM_S)
        } else if up {
            self.move_by(-JOG_UM_S);
            self.motion(HubState::Jog, -JOG_UM_S)
        } else {
            self.state = HubState::Idle;
            self.stopped(false, false)
        }
    }

    fn jog_allowed(self, input: HubInput) -> bool {
        input.enabling_held
            && input.lift_allowed
            && !input.safe_state
            && (input.cmd_jog_down || input.cmd_jog_up)
    }

    fn home(&mut self, input: HubInput) -> HubOutput {
        if !input.lift_allowed {
            self.state = HubState::Idle;
            return self.stopped(false, true);
        }
        if self.at_home() || input.limit_up_reached {
            self.position_um = 0;
            self.state = HubState::DrillWait;
            return self.stopped(false, false);
        }
        self.move_by(-HOMING_UM_S);
        self.motion(HubState::Homing, -HOMING_UM_S)
    }

    fn drill_wait(&mut self, input: HubInput) -> HubOutput {
        if !input.lift_allowed {
            self.state = HubState::Idle;
            return self.stopped(false, true);
        }
        if self.position_um <= LOWERED_UM {
            self.move_by(PENETRATE_UM_S);
            return self.motion(HubState::DrillWait, PENETRATE_UM_S);
        }
        if input.sonic_running {
            self.state = HubState::Drilling;
        }
        self.stopped(false, false)
    }

    fn drill(&mut self, input: HubInput) -> HubOutput {
        if self.position_um >= TARGET_UM || input.stone_detected || input.limit_down_reached {
            self.state = HubState::StopSonic;
            self.stop_ticks = 0;
            return self.stopped(true, false);
        }
        self.move_by(PENETRATE_UM_S);
        self.motion(HubState::Drilling, PENETRATE_UM_S)
    }

    fn stop_sonic(&mut self, input: HubInput) -> HubOutput {
        self.stop_ticks = self.stop_ticks.saturating_add(1);
        if input.sonic_confirmed_stopped {
            self.stop_ticks = 0;
            self.state = HubState::Retract;
            return self.stopped(false, false);
        }
        if self.stop_ticks >= crate::params::SONIC_STOP_TIMEOUT_CYCLES {
            self.fault = true;
            self.state = HubState::Fault;
        }
        self.stopped(true, false)
    }

    fn retract(&mut self, input: HubInput) -> HubOutput {
        if !input.lift_allowed {
            return self.stopped(false, true);
        }
        if self.at_home() || input.limit_up_reached {
            self.position_um = 0;
            self.state = HubState::Idle;
            return self.stopped(false, false);
        }
        self.move_by(-RETRACT_UM_S);
        self.motion(HubState::Retract, -RETRACT_UM_S)
    }

    fn park_move(&mut self, input: HubInput) -> HubOutput {
        if !input.lift_allowed {
            self.state = HubState::Idle;
            return self.stopped(false, true);
        }
        if self.at_home() || input.limit_up_reached {
            return self.enter_hold(input);
        }
        self.move_by(-HOMING_UM_S);
        self.motion(HubState::ParkMove, -HOMING_UM_S)
    }

    fn enter_hold(&mut self, input: HubInput) -> HubOutput {
        self.position_um = 0;
        self.origin_um = 0;
        self.test_ticks = 0;
        if input.brake_test_enable {
            self.state = HubState::BrakeTest;
            return self.brake_test(input);
        }
        self.state = HubState::Parked;
        self.stopped(false, false)
    }

    fn brake_test(&mut self, input: HubInput) -> HubOutput {
        self.position_um = (self.position_um + input.brake_slip_um).clamp(0, STROKE_UM);
        self.test_ticks = self.test_ticks.saturating_add(1);
        if (self.position_um - self.origin_um).abs() > BRAKE_SLIP_LIMIT_UM {
            self.fault = true;
            self.state = HubState::Fault;
            return self.stopped(false, false);
        }
        if self.test_ticks >= BRAKE_TEST_CYCLES {
            self.state = HubState::Parked;
        }
        self.stopped(false, false)
    }

    fn parked(&mut self, input: HubInput) -> HubOutput {
        if input.cmd_unpark && !input.safe_state {
            self.state = HubState::Idle;
            return self.stopped(false, false);
        }
        let requested =
            input.cmd_jog_down || input.cmd_jog_up || input.cmd_cycle_start || input.cmd_park;
        self.stopped(false, requested)
    }

    fn estop(&mut self, input: HubInput, reset_edge: bool) -> HubOutput {
        if !input.safe_state && reset_edge {
            self.state = HubState::Homing;
        }
        self.stopped(true, false)
    }

    fn fault_state(&mut self, input: HubInput, reset_edge: bool) -> HubOutput {
        if reset_edge && !input.safe_state {
            self.fault = false;
            self.state = HubState::Idle;
        }
        let mut output = self.stopped(false, false);
        output.fault = true;
        output
    }

    fn at_home(self) -> bool {
        self.position_um <= HOME_UM
    }

    fn move_by(&mut self, speed_um_s: i32) {
        self.position_um = (self.position_um + step_um(speed_um_s)).clamp(0, STROKE_UM);
    }

    fn motion(&self, state: HubState, speed_um_s: i32) -> HubOutput {
        HubOutput {
            state,
            position_um: self.position_um,
            speed_um_s,
            pulse_enable: speed_um_s != 0,
            direction_down: speed_um_s > 0,
            need_sonic_stop: false,
            moving: speed_um_s != 0,
            motion_blocked: false,
            fault: self.fault,
        }
    }

    fn stopped(&self, need_stop: bool, blocked: bool) -> HubOutput {
        HubOutput {
            state: self.state,
            position_um: self.position_um,
            speed_um_s: 0,
            pulse_enable: false,
            direction_down: false,
            need_sonic_stop: need_stop,
            moving: false,
            motion_blocked: blocked,
            fault: self.fault,
        }
    }
}

/// Logical pulse-train command. The pulse rate scale is not verified.
/// The RevPi DIO cannot source the S200 PTI. This command is not a DIO bit.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct PulseTrainCommand {
    pub enable: bool,
    pub direction_down: bool,
    /// TODO. Pulses per millimetre are not verified on the 1FL2 encoder.
    pub pulses_per_mm: Option<u32>,
}

impl From<HubOutput> for PulseTrainCommand {
    fn from(output: HubOutput) -> Self {
        Self {
            enable: output.pulse_enable,
            direction_down: output.direction_down,
            pulses_per_mm: None,
        }
    }
}

/// S200 status that this crate will not invent.
pub trait S200Status {
    fn position_um(&self) -> Option<i32>;
    fn fault(&self) -> bool;
    fn sto_healthy(&self) -> bool;
}

/// Every Modbus field stays empty until the drive map is verified.
#[derive(Clone, Copy, Debug, Default)]
pub struct UnverifiedS200Status {
    pub sto_healthy: bool,
    pub fault: bool,
}

impl S200Status for UnverifiedS200Status {
    fn position_um(&self) -> Option<i32> {
        None
    }

    fn fault(&self) -> bool {
        self.fault
    }

    fn sto_healthy(&self) -> bool {
        self.sto_healthy
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sf3_has_no_second_hold_and_the_brake_test_is_optional() {
        let mut hub = Hub::new();
        let parked = hub.tick(HubInput {
            cmd_park: true,
            ..HubInput::default()
        });
        assert_eq!(parked.state, HubState::Parked);
        assert!(!parked.pulse_enable);
        assert_eq!(parked.speed_um_s, 0);
    }

    #[test]
    fn jog_requires_the_enabling_switch_and_uses_reduced_speed() {
        let mut hub = Hub::new();
        hub.set_position_um(100_000);
        let blocked = hub.tick(HubInput {
            cmd_jog_down: true,
            ..HubInput::default()
        });
        assert_eq!(blocked.state, HubState::Idle);
        assert_eq!(blocked.position_um, 100_000);

        let jogging = hub.tick(HubInput {
            cmd_jog_down: true,
            enabling_held: true,
            ..HubInput::default()
        });
        assert_eq!(jogging.state, HubState::Jog);
        assert_eq!(jogging.speed_um_s, JOG_UM_S);
        assert!(jogging.speed_um_s < PENETRATE_UM_S);
        assert_eq!(jogging.position_um, 100_100);

        let released = hub.tick(HubInput::default());
        assert_eq!(released.state, HubState::Idle);
        assert_eq!(released.speed_um_s, 0);
        assert_eq!(released.position_um, 100_100);
    }
}
