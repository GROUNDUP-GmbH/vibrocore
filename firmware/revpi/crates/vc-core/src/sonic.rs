//! Sonic head. Two OLI motors share one inverter.
//!
//! STO is hard-wired from the safety relay to the inverter.
//! This module only reads the STO feedback. It is not an ISO 13849 function.

use crate::params::{
    SONIC_RAMP_CYCLES, SONIC_RAMP_UP_MHZ, SONIC_SKIP_HIGH_MHZ, SONIC_SKIP_LOW_MHZ,
    SONIC_STANDSTILL_CYCLES, SONIC_STOP_TIMEOUT_CYCLES, SONIC_TARGET_MHZ,
};

/// Codes match `FB_SonicHead`.
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

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SonicInput {
    pub safe_state: bool,
    pub fast_stop: bool,
    pub lowered: bool,
    pub tool_engaged: bool,
    pub sto_healthy: bool,
    pub drive_fault: bool,
    pub actual_running: bool,
    pub cmd_reset: bool,
    pub target_mhz: i32,
}

impl Default for SonicInput {
    fn default() -> Self {
        Self {
            safe_state: false,
            fast_stop: false,
            lowered: false,
            tool_engaged: false,
            sto_healthy: true,
            drive_fault: false,
            actual_running: false,
            cmd_reset: false,
            target_mhz: SONIC_TARGET_MHZ,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SonicOutput {
    pub state: SonicState,
    pub freq_mhz: i32,
    pub run_command: bool,
    pub confirmed_stopped: bool,
    pub sto_monitor_fault: bool,
    pub fault: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Sonic {
    state: SonicState,
    freq_mhz: i32,
    ramp_ticks: u32,
    still_ticks: u32,
    stop_ticks: u32,
}

impl Default for Sonic {
    fn default() -> Self {
        Self::new()
    }
}

impl Sonic {
    pub const fn new() -> Self {
        Self {
            state: SonicState::Idle,
            freq_mhz: 0,
            ramp_ticks: 0,
            still_ticks: 0,
            stop_ticks: 0,
        }
    }

    pub const fn state(self) -> SonicState {
        self.state
    }

    pub fn tick(&mut self, input: SonicInput) -> SonicOutput {
        let unexpected_sto = !input.sto_healthy && !input.safe_state;
        let permit = input.lowered
            && input.tool_engaged
            && input.sto_healthy
            && !input.drive_fault
            && !input.safe_state
            && !input.fast_stop;
        if input.drive_fault || unexpected_sto {
            self.state = SonicState::Fault;
            self.freq_mhz = 0;
        } else if input.safe_state || input.fast_stop {
            if !matches!(self.state, SonicState::Idle | SonicState::Fault) {
                self.state = SonicState::FastStop;
            }
            self.freq_mhz = 0;
        }
        match self.state {
            SonicState::Idle => {
                self.freq_mhz = 0;
                self.still_ticks = 0;
                if permit {
                    self.state = SonicState::Starting;
                    self.ramp_ticks = 0;
                }
            }
            SonicState::Starting => {
                self.ramp(input.target_mhz);
                if self.freq_mhz >= input.target_mhz {
                    self.freq_mhz = input.target_mhz;
                    self.state = SonicState::Running;
                }
                if !permit && !input.fast_stop && !input.safe_state {
                    self.state = SonicState::Stopping;
                }
            }
            SonicState::Running => {
                self.freq_mhz = input.target_mhz;
                if !permit && !input.fast_stop && !input.safe_state {
                    self.state = SonicState::Stopping;
                }
            }
            SonicState::Stopping => {
                self.ramp_down();
                if self.at_rest(input) {
                    self.state = SonicState::Idle;
                    self.freq_mhz = 0;
                }
            }
            SonicState::FastStop => {
                self.freq_mhz = 0;
                self.stop_ticks = self.stop_ticks.saturating_add(1);
                if self.at_rest(input) {
                    self.stop_ticks = 0;
                    if !input.fast_stop && !input.safe_state {
                        self.state = SonicState::Idle;
                    }
                } else if self.stop_ticks >= SONIC_STOP_TIMEOUT_CYCLES {
                    self.state = SonicState::Fault;
                }
            }
            SonicState::Fault => {
                self.freq_mhz = 0;
                if input.cmd_reset && !input.drive_fault && !unexpected_sto {
                    self.state = SonicState::Idle;
                }
            }
        }
        let confirmed = matches!(self.state, SonicState::Idle | SonicState::FastStop)
            && !input.actual_running
            && self.freq_mhz == 0
            && (self.state == SonicState::Idle || self.still_ticks >= SONIC_STANDSTILL_CYCLES);
        SonicOutput {
            state: self.state,
            freq_mhz: self.freq_mhz,
            run_command: matches!(self.state, SonicState::Starting | SonicState::Running),
            confirmed_stopped: confirmed,
            sto_monitor_fault: unexpected_sto,
            fault: self.state == SonicState::Fault,
        }
    }

    fn ramp(&mut self, target_mhz: i32) {
        self.ramp_ticks = self.ramp_ticks.saturating_add(1);
        if self.ramp_ticks < SONIC_RAMP_CYCLES {
            return;
        }
        self.ramp_ticks = 0;
        self.freq_mhz += SONIC_RAMP_UP_MHZ;
        if self.freq_mhz > SONIC_SKIP_LOW_MHZ && self.freq_mhz < SONIC_SKIP_HIGH_MHZ {
            self.freq_mhz = SONIC_SKIP_HIGH_MHZ;
        }
        if self.freq_mhz > target_mhz {
            self.freq_mhz = target_mhz;
        }
    }

    fn ramp_down(&mut self) {
        self.ramp_ticks = self.ramp_ticks.saturating_add(1);
        if self.ramp_ticks < SONIC_RAMP_CYCLES {
            return;
        }
        self.ramp_ticks = 0;
        self.freq_mhz = (self.freq_mhz - SONIC_RAMP_UP_MHZ * 3).max(0);
    }

    fn at_rest(&mut self, input: SonicInput) -> bool {
        if input.actual_running || self.freq_mhz > 0 {
            self.still_ticks = 0;
            return false;
        }
        self.still_ticks = self.still_ticks.saturating_add(1);
        self.still_ticks >= SONIC_STANDSTILL_CYCLES
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn permit() -> SonicInput {
        SonicInput {
            lowered: true,
            tool_engaged: true,
            target_mhz: 3_000,
            ..SonicInput::default()
        }
    }

    #[test]
    fn sonic_stays_off_until_lowered_and_engaged() {
        let mut sonic = Sonic::new();
        let blocked = sonic.tick(SonicInput {
            tool_engaged: true,
            ..SonicInput::default()
        });
        assert_eq!(blocked.state, SonicState::Idle);
        assert!(!blocked.run_command);
    }

    #[test]
    fn sonic_reaches_a_short_target_on_the_ramp() {
        let mut sonic = Sonic::new();
        let mut output = sonic.tick(permit());
        for _ in 1..21 {
            output = sonic.tick(permit());
        }
        assert_eq!(output.state, SonicState::Running);
        assert_eq!(output.freq_mhz, 3_000);
    }

    #[test]
    fn sto_feedback_loss_is_a_monitor_fault_and_drops_the_run() {
        let mut sonic = Sonic::new();
        let _ = sonic.tick(permit());
        let fault = sonic.tick(SonicInput {
            sto_healthy: false,
            ..permit()
        });
        assert_eq!(fault.state, SonicState::Fault);
        assert!(fault.sto_monitor_fault);
        assert_eq!(fault.freq_mhz, 0);
        assert!(!fault.run_command);
    }
}
