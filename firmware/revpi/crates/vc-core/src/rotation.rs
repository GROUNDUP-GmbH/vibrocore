//! Rod rotation on top of the vibro head.
//!
//! The drive order code is not chosen. The default adapter is step/dir.
//! A Modbus RTU map may replace it later. Registers stay TODO.
//! This interlock is not an ISO 13849 performance level.
//! Absolute moves need a homed index. The index input is one DIO channel.

use crate::params::{
    step_mdeg, wrap_mdeg, ROTATION_RPM, ROTATION_STALL_CYCLES, ROTATION_TORQUE_LIMIT_PCT,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum RotationState {
    Off = 0,
    Run = 1,
    Stall = 2,
    Fault = 3,
    Inhibit = 4,
}

/// Position goal for the rod axis. `Hold` plus `cmd_run` is a speed jog.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum RotationGoal {
    Hold = 0,
    SeekIndex = 1,
    Absolute = 2,
    Relative = 3,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct RotationCommand {
    pub enable: bool,
    pub speed_rpm: i16,
    pub torque_limit_pct: u8,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct RotationFeedback {
    pub actual_rpm: i16,
    pub torque_pct: u8,
    pub fault: bool,
}

/// The selected motor must accept this command. The bus map is TODO.
pub trait RotationDrive {
    fn set_command(&mut self, command: RotationCommand);
    fn feedback(&self) -> RotationFeedback;
}

/// Step and direction adapter. TODO: confirm step/dir or Modbus RTU on the unit.
#[derive(Clone, Copy, Debug)]
pub struct StepDirRotation {
    command: RotationCommand,
    feedback: RotationFeedback,
}

impl Default for StepDirRotation {
    fn default() -> Self {
        Self::new()
    }
}

impl StepDirRotation {
    pub const fn new() -> Self {
        Self {
            command: RotationCommand {
                enable: false,
                speed_rpm: 0,
                torque_limit_pct: ROTATION_TORQUE_LIMIT_PCT,
            },
            feedback: RotationFeedback {
                actual_rpm: 0,
                torque_pct: 0,
                fault: false,
            },
        }
    }

    pub const fn command(self) -> RotationCommand {
        self.command
    }
}

impl RotationDrive for StepDirRotation {
    fn set_command(&mut self, command: RotationCommand) {
        self.command = command;
    }

    fn feedback(&self) -> RotationFeedback {
        self.feedback
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct RotationInput {
    pub permit: bool,
    pub cmd_run: bool,
    pub reverse: bool,
    pub actual_rpm: i16,
    pub torque_pct: u8,
    pub drive_fault: bool,
    pub goal: RotationGoal,
    pub target_mdeg: i32,
    pub index_seen: bool,
}

impl Default for RotationInput {
    fn default() -> Self {
        Self {
            permit: true,
            cmd_run: false,
            reverse: false,
            actual_rpm: 0,
            torque_pct: 0,
            drive_fault: false,
            goal: RotationGoal::Hold,
            target_mdeg: 0,
            index_seen: false,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct RotationOutput {
    pub state: RotationState,
    pub command: RotationCommand,
    pub stalled: bool,
    pub fault: bool,
    pub angle_mdeg: i32,
    pub indexed: bool,
    pub move_done: bool,
}

#[derive(Clone, Copy, Debug)]
pub struct Rotation {
    state: RotationState,
    stall_ticks: u32,
    angle_mdeg: i32,
    indexed: bool,
    remaining_mdeg: i32,
    tracking: RotationGoal,
}

impl Default for Rotation {
    fn default() -> Self {
        Self::new()
    }
}

impl Rotation {
    pub const fn new() -> Self {
        Self {
            state: RotationState::Off,
            stall_ticks: 0,
            angle_mdeg: 0,
            indexed: false,
            remaining_mdeg: 0,
            tracking: RotationGoal::Hold,
        }
    }

    /// Test and setup aid. The index sensor is the normal way to set this.
    pub fn mark_indexed(&mut self) {
        self.indexed = true;
        self.angle_mdeg = 0;
    }

    pub fn tick(&mut self, input: RotationInput) -> RotationOutput {
        if input.drive_fault {
            self.state = RotationState::Fault;
            self.stall_ticks = 0;
            return self.stopped(true, false, false);
        }
        if !input.permit {
            self.state = RotationState::Inhibit;
            self.stall_ticks = 0;
            return self.stopped(false, false, false);
        }
        let moving = input.cmd_run || input.goal != RotationGoal::Hold;
        if !moving {
            self.tracking = RotationGoal::Hold;
            self.state = RotationState::Off;
            self.stall_ticks = 0;
            return self.stopped(false, false, false);
        }
        if self.stuck(input) {
            return self.stopped(false, true, false);
        }
        match input.goal {
            RotationGoal::SeekIndex => self.seek_index(input.index_seen),
            RotationGoal::Absolute => self.move_absolute(input.target_mdeg),
            RotationGoal::Relative => self.move_relative(input.target_mdeg),
            RotationGoal::Hold => {
                let speed = if input.reverse {
                    -ROTATION_RPM
                } else {
                    ROTATION_RPM
                };
                self.integrate(speed);
                self.running(speed, false)
            }
        }
    }

    fn stuck(&mut self, input: RotationInput) -> bool {
        let loaded = input.actual_rpm == 0 && input.torque_pct >= ROTATION_TORQUE_LIMIT_PCT;
        if loaded {
            self.stall_ticks = self.stall_ticks.saturating_add(1);
        } else {
            self.stall_ticks = 0;
        }
        if self.stall_ticks >= ROTATION_STALL_CYCLES {
            self.state = RotationState::Stall;
            true
        } else {
            false
        }
    }

    fn seek_index(&mut self, index_seen: bool) -> RotationOutput {
        if index_seen {
            self.angle_mdeg = 0;
            self.indexed = true;
            self.tracking = RotationGoal::Hold;
            self.state = RotationState::Off;
            return self.stopped(false, false, true);
        }
        self.integrate(ROTATION_RPM);
        self.running(ROTATION_RPM, false)
    }

    fn move_absolute(&mut self, target_mdeg: i32) -> RotationOutput {
        if !self.indexed {
            self.state = RotationState::Fault;
            return self.stopped(true, false, false);
        }
        let target = wrap_mdeg(target_mdeg);
        if self.tracking != RotationGoal::Absolute {
            self.tracking = RotationGoal::Absolute;
        }
        let distance =
            (target - self.angle_mdeg + crate::params::REV_MDEG) % crate::params::REV_MDEG;
        if distance == 0 {
            self.state = RotationState::Off;
            return self.stopped(false, false, true);
        }
        let step = step_mdeg(ROTATION_RPM);
        if step >= distance {
            self.angle_mdeg = target;
            self.state = RotationState::Off;
            return self.stopped(false, false, true);
        }
        self.angle_mdeg = wrap_mdeg(self.angle_mdeg + step);
        self.running(ROTATION_RPM, false)
    }

    fn move_relative(&mut self, travel_mdeg: i32) -> RotationOutput {
        if self.tracking != RotationGoal::Relative {
            self.tracking = RotationGoal::Relative;
            self.remaining_mdeg = travel_mdeg.max(0);
        }
        if self.remaining_mdeg <= 0 {
            self.tracking = RotationGoal::Hold;
            self.state = RotationState::Off;
            return self.stopped(false, false, true);
        }
        let step = step_mdeg(ROTATION_RPM);
        if step >= self.remaining_mdeg {
            self.angle_mdeg = wrap_mdeg(self.angle_mdeg + self.remaining_mdeg);
            self.remaining_mdeg = 0;
            self.tracking = RotationGoal::Hold;
            self.state = RotationState::Off;
            return self.stopped(false, false, true);
        }
        self.remaining_mdeg -= step;
        self.angle_mdeg = wrap_mdeg(self.angle_mdeg + step);
        self.running(ROTATION_RPM, false)
    }

    fn integrate(&mut self, rpm: i16) {
        self.angle_mdeg = wrap_mdeg(self.angle_mdeg + step_mdeg(rpm));
    }

    fn running(&mut self, speed_rpm: i16, move_done: bool) -> RotationOutput {
        self.state = RotationState::Run;
        RotationOutput {
            state: RotationState::Run,
            command: RotationCommand {
                enable: true,
                speed_rpm,
                torque_limit_pct: ROTATION_TORQUE_LIMIT_PCT,
            },
            stalled: false,
            fault: false,
            angle_mdeg: self.angle_mdeg,
            indexed: self.indexed,
            move_done,
        }
    }

    fn stopped(&self, fault: bool, stalled: bool, move_done: bool) -> RotationOutput {
        RotationOutput {
            state: self.state,
            command: RotationCommand {
                enable: false,
                speed_rpm: 0,
                torque_limit_pct: ROTATION_TORQUE_LIMIT_PCT,
            },
            stalled,
            fault,
            angle_mdeg: self.angle_mdeg,
            indexed: self.indexed,
            move_done,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::params::{ROTATION_RPM, ROTATION_STALL_CYCLES, ROTATION_TORQUE_LIMIT_PCT};

    #[test]
    fn stall_drops_the_enable_at_the_torque_limit() {
        let mut rotation = Rotation::new();
        let input = RotationInput {
            cmd_run: true,
            torque_pct: ROTATION_TORQUE_LIMIT_PCT,
            ..RotationInput::default()
        };
        let mut output = rotation.tick(input);
        for _ in 1..ROTATION_STALL_CYCLES - 1 {
            output = rotation.tick(input);
        }
        assert_eq!(output.state, RotationState::Run);
        output = rotation.tick(input);
        assert_eq!(output.state, RotationState::Stall);
        assert!(output.stalled);
        assert!(!output.command.enable);
        assert_eq!(output.command.speed_rpm, 0);
    }

    #[test]
    fn step_dir_adapter_stores_the_command_and_has_no_register_map() {
        let mut drive = StepDirRotation::new();
        drive.set_command(RotationCommand {
            enable: true,
            speed_rpm: ROTATION_RPM,
            torque_limit_pct: ROTATION_TORQUE_LIMIT_PCT,
        });
        assert_eq!(drive.command().speed_rpm, ROTATION_RPM);
        assert!(!drive.feedback().fault);
    }

    #[test]
    fn sonic_or_motion_inhibits_rotation() {
        let mut rotation = Rotation::new();
        let output = rotation.tick(RotationInput {
            permit: false,
            cmd_run: true,
            ..RotationInput::default()
        });
        assert_eq!(output.state, RotationState::Inhibit);
        assert_eq!(output.command.speed_rpm, 0);
    }
}
