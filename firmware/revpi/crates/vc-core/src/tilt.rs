//! Tilt actuators and the sampling-position lift actuators.
//!
//! Both pairs use 24 V relays.
//! Stefan removed the tilt-angle limit on 2026-11-20.
//! The machine works on hilly farmland.
//! Tilt keeps two direction outputs and the actuator end stops.
//! There is no tilt sensor.
//! This code is not an ISO 13849 performance level.

/// Codes match `FB_TiltControl`. There is no angle-inhibit code.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum TiltState {
    Unknown = 0,
    TiltingVertical = 1,
    Vertical = 2,
    TiltingFold = 3,
    Folded = 4,
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
        let mut vertical = false;
        let mut fold = false;
        let mut extend = false;
        let mut retract = false;
        let mut fault = false;

        if input.safe_state {
            self.tilt_state = TiltState::Unknown;
            self.lift_state = LiftState::Unknown;
        } else {
            let both_tilt = input.cmd_vertical && input.cmd_fold;
            let both_lift = input.cmd_extend && input.cmd_retract;
            let moving = input.cmd_extend || input.cmd_retract;
            fault = both_tilt || both_lift || !input.hub_idle && moving;
            if !both_tilt && input.cmd_vertical && !input.limit_vertical_reached {
                vertical = true;
                self.tilt_state = TiltState::TiltingVertical;
            } else if !both_tilt && input.cmd_fold && !input.limit_folded_reached {
                fold = true;
                self.tilt_state = TiltState::TiltingFold;
            } else if input.limit_vertical_reached {
                self.tilt_state = TiltState::Vertical;
            } else if input.limit_folded_reached {
                self.tilt_state = TiltState::Folded;
            } else {
                self.tilt_state = TiltState::Unknown;
            }

            if fault || !input.hub_idle {
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
            fault,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fold_ignores_hill_angle_and_stops_on_the_end_switch() {
        let mut tilt = Tilt::new();
        let folding = tilt.tick(TiltInput {
            cmd_fold: true,
            ..TiltInput::default()
        });
        assert!(folding.tilt_fold);
        assert!(!folding.tilt_vertical);
        assert_eq!(folding.tilt_state, TiltState::TiltingFold);

        let stopped = tilt.tick(TiltInput {
            cmd_fold: true,
            limit_folded_reached: true,
            ..TiltInput::default()
        });
        assert!(!stopped.tilt_fold);
        assert_eq!(stopped.tilt_state, TiltState::Folded);
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
