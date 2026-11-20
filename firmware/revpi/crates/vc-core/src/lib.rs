//! Domain logic for the RevPi control service.
//!
//! This crate has no device I/O. Device access stays in `vc-io` and `vc-modbus`.
//! The crate is `no_std` outside tests.

#![cfg_attr(not(test), no_std)]

mod machine;
mod safety;

pub use machine::{CoreError, HubState, LiftState, Machine, SonicState, TiltState};
pub use safety::{
    SafetyInput, SafetyMonitor, SafetyOutput, SafetyReason, CYCLE_MS, STONE_CURRENT_PCT_THR,
    STONE_DEBOUNCE_MS,
};
