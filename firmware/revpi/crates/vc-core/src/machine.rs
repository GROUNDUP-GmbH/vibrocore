//! Machine state codes.
//!
//! The integer values match the Structured Text blocks.
//! Transition logic for hub, sonic, lift and tilt is not ported.

/// Hub carriage. Codes match `FB_HubControl`.
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
}

/// Sonic head. Codes match `FB_SonicHead`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum SonicState {
    Idle = 0,
    Starting = 1,
    Running = 2,
    Stopping = 3,
    FastStop = 4,
    Fault = 5,
}

/// Lift deploy. This is the sampling-position actuator. Codes match `FB_LiftControl`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum LiftState {
    Unknown = 0,
    Deploying = 1,
    Deployed = 2,
    Retracting = 3,
    Retracted = 4,
}

/// Mast tilt. Codes match `FB_TiltControl`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum TiltState {
    Unknown = 0,
    TiltingVertical = 1,
    Vertical = 2,
    TiltingFold = 3,
    Folded = 4,
}

/// Returned by [`Machine::tick`] until the transitions are ported.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CoreError {
    NotImplemented,
}

/// State snapshot. `tick` does not move the machine yet.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Machine {
    pub hub: HubState,
    pub sonic: SonicState,
    pub lift: LiftState,
    pub tilt: TiltState,
}

impl Default for Machine {
    fn default() -> Self {
        Self::new()
    }
}

impl Machine {
    pub const fn new() -> Self {
        Self {
            hub: HubState::Idle,
            sonic: SonicState::Idle,
            lift: LiftState::Unknown,
            tilt: TiltState::Unknown,
        }
    }

    /// Hub, sonic, sampling and tilt transitions are not ported.
    pub const fn tick(&self) -> Result<(), CoreError> {
        let _ = (self.hub, self.sonic, self.lift, self.tilt);
        Err(CoreError::NotImplemented)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn starts_idle_and_does_not_run_transitions() {
        let machine = Machine::new();
        assert_eq!(machine.hub as u8, 0);
        assert_eq!(machine.sonic as u8, 0);
        assert_eq!(machine.lift as u8, 0);
        assert_eq!(machine.tilt as u8, 0);
        assert_eq!(machine.tick(), Err(CoreError::NotImplemented));
    }
}
