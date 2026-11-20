//! Tilt actuators and the sampling-position lift actuators.
//!
//! Both pairs use 24 V relays. The angle monitor is SF6.
//! SF6 is not an ISO 13849 performance level. The safety relay is hard-wired.

use crate::params::TILT_ANGLE_LIMIT_MDEG;

/// Codes 0 to 4 match `FB_TiltControl`. Code 5 is the angle inhibit.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum TiltState {
    Unknown = 0,
    TiltingVertical = 1,
    Vertical = 2,
    TiltingFold = 3,
    Folded = 4,
    Inhibited = 5,
}

/// Codes match `FB_LiftControl`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum LiftState {
    Unknown = 0,
    Deploying = 1,
    Deployed = 2,
    Retracting = 3,
    Retracted = 4,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct TiltInput {
    pub safe_state: bool,
    pub hub_idle: bool,
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
}

impl Default for TiltInput {
    fn default() -> Self {
        Self {
            safe_state: false,
            hub_idle: true,
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
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct TiltOutput {
    pub tilt_state: TiltState,
    pub lift_state: LiftState,
    pub tilt_vertical: bool,
    pub tilt_fold: bool,
    pub lift_extend: bool,
    pub lift_retract: bool,
    pub lift_allowed: bool,
    pub fault: bool,
}

#[derive(Clone, Copy, Debug)]
pub struct Tilt {
    tilt_state: TiltState,
    lift_state: LiftState,
}

impl Default for Tilt {
    fn default() -> Self {
        Self::new()
    }
}

impl Tilt {
    pub const fn new() -> Self {
        Self {
            tilt_state: TiltState::Unknown,
            lift_state: LiftState::Unknown,
        }
    }

    pub fn tick(&mut self, input: TiltInput) -> TiltOutput {
        let lift_allowed = input.sensor_valid && input.angle_mdeg <= TILT_ANGLE_LIMIT_MDEG;
        let mut vertical = false;
        let mut fold = false;
        let mut extend = false;
        let mut retract = false;
        let mut fault = false;

        if input.safe_state || !input.sensor_valid {
            self.tilt_state = TiltState::Inhibited;
            self.lift_state = LiftState::Unknown;
        } else {
            let both_tilt = input.cmd_vertical && input.cmd_fold;
            let both_lift = input.cmd_extend && input.cmd_retract;
            fault = both_tilt
                || both_lift
                || (!input.hub_idle && (both_lift || input.cmd_extend || input.cmd_retract));
            if !both_tilt && input.cmd_vertical && !input.limit_vertical_reached {
                vertical = true;
                self.tilt_state = TiltState::TiltingVertical;
            } else if !both_tilt && input.cmd_fold && lift_allowed && !input.limit_folded_reached {
                fold = true;
                self.tilt_state = TiltState::TiltingFold;
            } else if input.limit_vertical_reached {
                self.tilt_state = TiltState::Vertical;
            } else if input.limit_folded_reached {
                self.tilt_state = TiltState::Folded;
            } else if !lift_allowed {
                self.tilt_state = TiltState::Inhibited;
            } else {
                self.tilt_state = TiltState::Unknown;
            }

            if fault || !input.hub_idle || !lift_allowed {
                self.lift_state = LiftState::Unknown;
            } else if input.cmd_extend && !input.limit_deployed_reached {
                extend = true;
                self.lift_state = LiftState::Deploying;
            } else if input.cmd_retract && !input.limit_retracted_reached {
                retract = true;
                self.lift_state = LiftState::Retracting;
            } else if input.limit_deployed_reached {
                self.lift_state = LiftState::Deployed;
            } else if input.limit_retracted_reached {
                self.lift_state = LiftState::Retracted;
            } else {
                self.lift_state = LiftState::Unknown;
            }
        }

        if fault {
            vertical = false;
            fold = false;
            extend = false;
            retract = false;
        }

        TiltOutput {
            tilt_state: self.tilt_state,
            lift_state: self.lift_state,
            tilt_vertical: vertical,
            tilt_fold: fold,
            lift_extend: extend,
            lift_retract: retract,
            lift_allowed,
            fault,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn angle_limit_blocks_fold_and_lift_but_allows_a_return_to_vertical() {
        let mut tilt = Tilt::new();
        let blocked = tilt.tick(TiltInput {
            angle_mdeg: 10_000,
            cmd_fold: true,
            cmd_extend: true,
            ..TiltInput::default()
        });
        assert!(!blocked.tilt_fold);
        assert!(!blocked.lift_extend);
        assert!(!blocked.lift_allowed);
        assert_eq!(blocked.tilt_state, TiltState::Inhibited);

        let back = tilt.tick(TiltInput {
            angle_mdeg: 10_000,
            cmd_vertical: true,
            ..TiltInput::default()
        });
        assert!(back.tilt_vertical);
        assert!(!back.lift_allowed);
        assert_eq!(back.tilt_state, TiltState::TiltingVertical);
    }

    #[test]
    fn both_tilt_commands_drop_both_outputs() {
        let mut tilt = Tilt::new();
        let output = tilt.tick(TiltInput {
            cmd_vertical: true,
            cmd_fold: true,
            ..TiltInput::default()
        });
        assert!(output.fault);
        assert!(!output.tilt_vertical);
        assert!(!output.tilt_fold);
    }
}
