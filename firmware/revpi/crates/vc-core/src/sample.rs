//! Staged soil sample on the rod-rotation axis.
//!
//! The carriage drives in with the sonic head.
//! Sonic and lift then stop.
//! The rod turns one revolution to cut the core.
//! The carriage then stops at each depth stage and the rod turns to that container.
//! One to four stages are allowed.
//! A stall or a torque limit aborts to [`SamplePhase::Fault`].
//! Rotation stays blocked while the sonic head runs or the carriage moves.
//! This sequence is not an ISO 13849 performance level.

use crate::params::{
    HOME_UM, PENETRATE_UM_S, RETRACT_UM_S, REV_MDEG, SAMPLE_STAGE_MAX, SAMPLE_STAGE_MIN, TARGET_UM,
};
use crate::rotation::RotationGoal;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum SamplePhase {
    Idle = 0,
    SeekIndex = 1,
    DriveIn = 2,
    StopSonic = 3,
    CoreCut = 4,
    Retract = 5,
    Dump = 6,
    Park = 7,
    Fault = 8,
    Done = 9,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SamplePlan {
    pub stages: u8,
    pub in_depth_um: i32,
    pub depth_um: [i32; 4],
    pub container_mdeg: [i32; 4],
}

impl Default for SamplePlan {
    fn default() -> Self {
        Self {
            stages: 1,
            in_depth_um: TARGET_UM,
            depth_um: [0, 0, 0, 0],
            container_mdeg: [0, 0, 0, 0],
        }
    }
}

impl SamplePlan {
    pub fn valid(self) -> bool {
        if !(SAMPLE_STAGE_MIN..=SAMPLE_STAGE_MAX).contains(&self.stages) {
            return false;
        }
        if self.in_depth_um <= 0 {
            return false;
        }
        let mut previous = self.in_depth_um;
        for index in 0..self.stages as usize {
            let depth = self.depth_um[index];
            let angle = self.container_mdeg[index];
            if depth < 0 || depth >= previous || !(0..REV_MDEG).contains(&angle) {
                return false;
            }
            previous = depth;
        }
        true
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SampleView {
    pub cmd_sample: bool,
    pub cmd_reset: bool,
    pub position_um: i32,
    pub sonic_running: bool,
    pub sonic_confirmed: bool,
    pub indexed: bool,
    pub move_done: bool,
    pub stalled: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SampleCommand {
    pub phase: SamplePhase,
    pub stage: u8,
    pub container_mdeg: i32,
    pub sample_active: bool,
    pub sample_speed_um_s: i32,
    pub hub_park: bool,
    pub fast_stop: bool,
    pub goal: RotationGoal,
    pub target_mdeg: i32,
    pub wants_rotation: bool,
    pub active: bool,
    pub fault: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Sample {
    phase: SamplePhase,
    plan: SamplePlan,
    stage_index: u8,
    prev_sample: bool,
    fault: bool,
    /// True only after a rotation goal was already commanded.
    motion_open: bool,
}

impl Default for Sample {
    fn default() -> Self {
        Self::new()
    }
}

impl Sample {
    pub const fn new() -> Self {
        Self {
            phase: SamplePhase::Idle,
            plan: SamplePlan {
                stages: 1,
                in_depth_um: TARGET_UM,
                depth_um: [0, 0, 0, 0],
                container_mdeg: [0, 0, 0, 0],
            },
            stage_index: 0,
            prev_sample: false,
            fault: false,
            motion_open: false,
        }
    }

    pub fn set_plan(&mut self, plan: SamplePlan) {
        self.plan = plan;
    }

    pub const fn phase(self) -> SamplePhase {
        self.phase
    }

    pub fn begin(&mut self, view: SampleView) -> SampleCommand {
        let start = view.cmd_sample && !self.prev_sample;
        self.prev_sample = view.cmd_sample;
        if view.cmd_reset && self.phase == SamplePhase::Fault {
            self.fault = false;
            self.phase = SamplePhase::Idle;
            self.stage_index = 0;
        }
        if view.stalled && self.phase != SamplePhase::Idle && self.phase != SamplePhase::Done {
            self.fail();
        }
        if start && self.phase == SamplePhase::Idle {
            self.stage_index = 0;
            if !self.plan.valid() {
                self.fail();
            } else if !view.indexed {
                self.phase = SamplePhase::SeekIndex;
            } else {
                self.enter_after_index(view);
            }
        }
        self.advance(view);
        let command = self.command();
        self.motion_open = command.wants_rotation;
        command
    }

    /// Same-tick abort after the rotation block reports a stall.
    pub fn note_stall(&mut self) {
        if self.phase != SamplePhase::Idle && self.phase != SamplePhase::Done {
            self.fail();
        }
    }

    fn enter_after_index(&mut self, view: SampleView) {
        if view.position_um >= self.plan.in_depth_um && view.sonic_confirmed && !view.sonic_running
        {
            self.phase = SamplePhase::CoreCut;
        } else if view.position_um >= self.plan.in_depth_um {
            self.phase = SamplePhase::StopSonic;
        } else {
            self.phase = SamplePhase::DriveIn;
        }
    }

    fn advance(&mut self, view: SampleView) {
        match self.phase {
            SamplePhase::SeekIndex => {
                if self.motion_open && view.indexed {
                    self.motion_open = false;
                    self.enter_after_index(view);
                }
            }
            SamplePhase::DriveIn => {
                if view.position_um >= self.plan.in_depth_um {
                    self.phase = SamplePhase::StopSonic;
                }
            }
            SamplePhase::StopSonic => {
                if view.sonic_confirmed && !view.sonic_running {
                    self.phase = SamplePhase::CoreCut;
                }
            }
            SamplePhase::CoreCut => {
                if self.motion_open && view.move_done {
                    self.motion_open = false;
                    self.stage_index = 0;
                    self.phase = SamplePhase::Retract;
                }
            }
            SamplePhase::Retract => {
                if view.position_um <= self.plan.depth_um[self.stage_index as usize] {
                    self.phase = SamplePhase::Dump;
                }
            }
            SamplePhase::Dump => {
                if self.motion_open && view.move_done {
                    self.motion_open = false;
                    let next = self.stage_index.saturating_add(1);
                    if next >= self.plan.stages {
                        self.phase = SamplePhase::Park;
                    } else {
                        self.stage_index = next;
                        self.phase = SamplePhase::Retract;
                    }
                }
            }
            SamplePhase::Park => {
                if view.position_um <= HOME_UM {
                    self.phase = SamplePhase::Done;
                }
            }
            SamplePhase::Idle | SamplePhase::Fault | SamplePhase::Done => {}
        }
    }

    pub fn command(&self) -> SampleCommand {
        let stage = if matches!(self.phase, SamplePhase::Retract | SamplePhase::Dump) {
            self.stage_index.saturating_add(1)
        } else {
            0
        };
        let container = if self.phase == SamplePhase::Dump {
            self.plan.container_mdeg[self.stage_index as usize]
        } else {
            0
        };
        let mut command = SampleCommand {
            phase: self.phase,
            stage,
            container_mdeg: container,
            sample_active: false,
            sample_speed_um_s: 0,
            hub_park: false,
            fast_stop: !matches!(
                self.phase,
                SamplePhase::Idle | SamplePhase::DriveIn | SamplePhase::Done
            ),
            goal: RotationGoal::Hold,
            target_mdeg: 0,
            wants_rotation: false,
            active: !matches!(self.phase, SamplePhase::Idle | SamplePhase::Done),
            fault: self.fault,
        };
        match self.phase {
            SamplePhase::SeekIndex => {
                command.sample_active = true;
                command.goal = RotationGoal::SeekIndex;
                command.wants_rotation = true;
            }
            SamplePhase::DriveIn => {
                command.sample_active = true;
                command.sample_speed_um_s = PENETRATE_UM_S;
            }
            SamplePhase::StopSonic | SamplePhase::Fault => {
                command.sample_active = true;
            }
            SamplePhase::CoreCut => {
                command.sample_active = true;
                command.goal = RotationGoal::Relative;
                command.target_mdeg = REV_MDEG;
                command.wants_rotation = true;
            }
            SamplePhase::Retract => {
                command.sample_active = true;
                command.sample_speed_um_s = -RETRACT_UM_S;
            }
            SamplePhase::Dump => {
                command.sample_active = true;
                command.goal = RotationGoal::Absolute;
                command.target_mdeg = container;
                command.wants_rotation = true;
            }
            SamplePhase::Park => {
                command.sample_active = true;
                command.sample_speed_um_s = -RETRACT_UM_S;
            }
            SamplePhase::Done => {
                command.hub_park = true;
            }
            SamplePhase::Idle => {}
        }
        command
    }

    fn fail(&mut self) {
        self.fault = true;
        self.motion_open = false;
        self.phase = SamplePhase::Fault;
    }
}
