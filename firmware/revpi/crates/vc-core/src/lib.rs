//! Domain logic for the RevPi control service.
//!
//! This crate has no device I/O. Device access stays in `vc-io` and `vc-modbus`.
//! The crate is `no_std` outside tests.
//! Each state machine only monitors feedback. None of them is an ISO 13849 function.

#![cfg_attr(not(test), no_std)]

mod hub;
mod params;
mod plant;
mod rotation;
mod safety;
mod sonic;
mod tilt;

pub use hub::{
    Hub, HubInput, HubOutput, HubState, PulseTrainCommand, S200Status, UnverifiedS200Status,
    SF3_BRAKE_TEST_DEFAULT, SF3_SECOND_HOLD_FITTED,
};
pub use plant::{Plant, PlantInput, PlantOutput};
pub use rotation::{
    Rotation, RotationCommand, RotationDrive, RotationFeedback, RotationInput, RotationOutput,
    RotationState, StepDirRotation,
};
pub use safety::{
    SafetyInput, SafetyMonitor, SafetyOutput, SafetyReason, CYCLE_MS, STONE_CURRENT_PCT_THR,
    STONE_DEBOUNCE_MS,
};
pub use sonic::{Sonic, SonicInput, SonicOutput, SonicState};
pub use tilt::{LiftState, Tilt, TiltInput, TiltOutput, TiltState};
