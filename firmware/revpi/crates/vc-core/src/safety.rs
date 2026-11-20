//! Software safety monitor.
//!
//! This is the first port of `FB_Safety`. It reads feedback and sets a stop
//! request. It is not an ISO 13849 safety function. See ADR-0002.

/// PLC cycle used by the Python reference model, in milliseconds.
pub const CYCLE_MS: u32 = 10;

/// Stone-detection threshold, percent of rated sonic current.
pub const STONE_CURRENT_PCT_THR: f32 = 130.0;

/// Stone-detection debounce, in milliseconds. Matches `tSTONE_DEBOUNCE`.
pub const STONE_DEBOUNCE_MS: u32 = 250;

/// Fault codes from ADR-0001. Do not add a code.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum SafetyReason {
    Ok = 0,
    EStop = 1,
    LimitUp = 2,
    LimitDown = 3,
    HubAlarm = 4,
    StoneDetected = 5,
    VfdComm = 6,
}

impl SafetyReason {
    pub const fn code(self) -> u8 {
        self as u8
    }

    pub const fn from_code(code: u8) -> Option<Self> {
        match code {
            0 => Some(Self::Ok),
            1 => Some(Self::EStop),
            2 => Some(Self::LimitUp),
            3 => Some(Self::LimitDown),
            4 => Some(Self::HubAlarm),
            5 => Some(Self::StoneDetected),
            6 => Some(Self::VfdComm),
            _ => None,
        }
    }
}

/// One scan of feedback. NC inputs are true when the circuit is healthy.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct SafetyInput {
    pub estop_nc: bool,
    pub limit_up_nc: bool,
    pub limit_down_nc: bool,
    pub hub_alarm: bool,
    pub vfd_fault: bool,
    pub vfd_current_pct: f32,
    pub hub_moving_down: bool,
    pub hub_moving_up: bool,
}

/// Result of one scan. `safe_state` is a software stop request, not a PL claim.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SafetyOutput {
    pub safe_state: bool,
    pub stone_detected: bool,
    pub limit_up_triggered: bool,
    pub limit_down_triggered: bool,
    pub reason: SafetyReason,
}

#[derive(Clone, Copy, Debug, Default)]
struct OnDelay {
    cycles: u32,
    q: bool,
}

impl OnDelay {
    fn tick(&mut self, input: bool, pt_ms: u32) {
        let pt_cycles = (pt_ms / CYCLE_MS).max(1);
        if input {
            if self.cycles < pt_cycles {
                self.cycles += 1;
            }
            self.q = self.cycles >= pt_cycles;
        } else {
            self.cycles = 0;
            self.q = false;
        }
    }
}

/// Port of `FB_Safety` / `tests/sim.py`.
#[derive(Clone, Copy, Debug, Default)]
pub struct SafetyMonitor {
    stone: OnDelay,
}

impl SafetyMonitor {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn tick(&mut self, input: SafetyInput) -> SafetyOutput {
        let limit_up_triggered = !input.limit_up_nc;
        let limit_down_triggered = !input.limit_down_nc;
        self.stone.tick(
            input.vfd_current_pct > STONE_CURRENT_PCT_THR,
            STONE_DEBOUNCE_MS,
        );
        let stone_detected = self.stone.q;

        let (safe_state, reason) = if !input.estop_nc {
            (true, SafetyReason::EStop)
        } else if input.hub_alarm {
            (true, SafetyReason::HubAlarm)
        } else if input.vfd_fault {
            (true, SafetyReason::VfdComm)
        } else if stone_detected {
            (true, SafetyReason::StoneDetected)
        } else if limit_up_triggered && input.hub_moving_up {
            (true, SafetyReason::LimitUp)
        } else if limit_down_triggered && input.hub_moving_down {
            (true, SafetyReason::LimitDown)
        } else {
            (false, SafetyReason::Ok)
        };

        SafetyOutput {
            safe_state,
            stone_detected,
            limit_up_triggered,
            limit_down_triggered,
            reason,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn healthy() -> SafetyInput {
        SafetyInput {
            estop_nc: true,
            limit_up_nc: true,
            limit_down_nc: true,
            hub_alarm: false,
            vfd_fault: false,
            vfd_current_pct: 0.0,
            hub_moving_down: false,
            hub_moving_up: false,
        }
    }

    /// `tests/test_safety.py::TestEStop::test_estop_has_highest_priority`
    #[test]
    fn estop_has_highest_priority() {
        let mut safety = SafetyMonitor::new();
        let output = safety.tick(SafetyInput {
            estop_nc: false,
            hub_alarm: true,
            vfd_fault: true,
            ..healthy()
        });
        assert!(output.safe_state);
        assert_eq!(output.reason, SafetyReason::EStop);
    }

    /// `tests/test_safety.py::TestLimitSwitches::test_limit_up_causes_safe_state_only_when_moving_up`
    #[test]
    fn limit_up_causes_safe_state_only_when_moving_up() {
        let mut safety = SafetyMonitor::new();
        let idle = safety.tick(SafetyInput {
            limit_up_nc: false,
            hub_moving_up: false,
            ..healthy()
        });
        assert!(!idle.safe_state);
        assert!(idle.limit_up_triggered);
        assert_eq!(idle.reason, SafetyReason::Ok);

        let moving = safety.tick(SafetyInput {
            limit_up_nc: false,
            hub_moving_up: true,
            ..healthy()
        });
        assert!(moving.safe_state);
        assert_eq!(moving.reason, SafetyReason::LimitUp);
    }

    /// `tests/test_safety.py::TestStoneDetection::test_above_threshold_after_debounce`
    #[test]
    fn above_threshold_after_debounce() {
        let mut safety = SafetyMonitor::new();
        let input = SafetyInput {
            vfd_current_pct: STONE_CURRENT_PCT_THR + 10.0,
            ..healthy()
        };
        let cycles = STONE_DEBOUNCE_MS / CYCLE_MS;
        let mut output = safety.tick(input);
        for _ in 1..cycles {
            output = safety.tick(input);
        }
        assert!(output.stone_detected);
        assert!(output.safe_state);
        assert_eq!(output.reason, SafetyReason::StoneDetected);
    }
}
