//! Real-time loop, watchdogs and the MQTT bridge.
//!
//! The loop is not implemented. `run` returns [`RuntimeError::NotImplemented`].
//! MQTT topics match ADR-0001. This crate does not open a socket.

use std::time::Duration;

/// Target cycle from ADR-0002.
pub const CYCLE: Duration = Duration::from_millis(vc_core::CYCLE_MS as u64);

/// Linux `MCL_CURRENT`. The skeleton does not call `mlockall`.
pub const MCL_CURRENT: i32 = 1;

/// Linux `MCL_FUTURE`. The skeleton does not call `mlockall`.
pub const MCL_FUTURE: i32 = 2;

/// Linux `SCHED_FIFO`. The skeleton does not call `sched_setscheduler`.
pub const SCHED_FIFO: i32 = 1;

/// ADR-0001 topic. HMI presence. Retain is yes.
pub const MQTT_HMI_STATUS: &str = "vibrocore/hmi/status";

/// ADR-0001 topic. Safety fault event. Retain is no.
pub const MQTT_ALARM: &str = "vibrocore/alarm";

/// ADR-0001 prefix for a signed cycle record. Retain is no.
pub const MQTT_CYCLE_PREFIX: &str = "vibrocore/cycle/";

/// ADR-0001 prefix reserved for a live status mirror.
pub const MQTT_STATUS_PREFIX: &str = "vibrocore/status/";

/// Live hub state. Retain is yes. Codes 8 to 11 are jog, park move, brake test and parked.
pub const MQTT_STATUS_HUB: &str = "vibrocore/status/hub";

/// Live sonic state.
pub const MQTT_STATUS_SONIC: &str = "vibrocore/status/sonic";

/// Live tilt state and angle.
pub const MQTT_STATUS_TILT: &str = "vibrocore/status/tilt";

/// Live rod-rotation state.
pub const MQTT_STATUS_ROTATION: &str = "vibrocore/status/rotation";

/// Live jog gate. The enabling switch must be held.
pub const MQTT_STATUS_JOG: &str = "vibrocore/status/jog";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RuntimeError {
    NotImplemented,
}

/// Planned real-time setup. The flags are requirements, not applied state.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct RtPlan {
    pub cycle: Duration,
    pub isolated_core: bool,
    pub sched_fifo: bool,
    pub mlockall: bool,
    pub software_watchdog: bool,
    pub hardware_watchdog: bool,
}

impl RtPlan {
    pub const fn target() -> Self {
        Self {
            cycle: CYCLE,
            isolated_core: true,
            sched_fifo: true,
            mlockall: true,
            software_watchdog: true,
            hardware_watchdog: true,
        }
    }
}

/// Software stall detector. The time base is supplied by the caller.
/// A monitor that was never kicked is expired.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SoftwareWatchdog {
    limit: Duration,
    last_kick: Option<Duration>,
}

impl SoftwareWatchdog {
    pub const fn new(limit: Duration) -> Self {
        Self {
            limit,
            last_kick: None,
        }
    }

    pub fn kick(&mut self, now: Duration) {
        self.last_kick = Some(now);
    }

    pub fn expired(&self, now: Duration) -> bool {
        match self.last_kick {
            None => true,
            Some(last) => now.saturating_sub(last) > self.limit,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MqttMessage {
    pub topic: String,
    pub payload: String,
    pub retain: bool,
}

/// In-memory outbox. Publishing does not contact a broker.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct MqttBridge {
    outbox: Vec<MqttMessage>,
}

impl MqttBridge {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn publish(&mut self, topic: &str, payload: &str, retain: bool) {
        self.outbox.push(MqttMessage {
            topic: topic.to_string(),
            payload: payload.to_string(),
            retain,
        });
    }

    pub fn drain(&mut self) -> Vec<MqttMessage> {
        std::mem::take(&mut self.outbox)
    }
}

/// Selected hardware named by the linked crates. Useful as a link check.
pub fn selected_drive() -> &'static str {
    vc_modbus::S200_ORDER_CODE
}

pub fn process_image_device() -> &'static str {
    vc_io::DEVICE_PATH
}

/// The cyclic service is not implemented.
pub const fn run() -> Result<(), RuntimeError> {
    Err(RuntimeError::NotImplemented)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn plan_matches_the_architecture_record() {
        let plan = RtPlan::target();
        assert_eq!(plan.cycle, Duration::from_millis(10));
        assert!(plan.isolated_core);
        assert!(plan.sched_fifo);
        assert!(plan.mlockall);
        assert!(plan.software_watchdog);
        assert!(plan.hardware_watchdog);
        assert_eq!(SCHED_FIFO, 1);
        assert_eq!(MCL_CURRENT, 1);
        assert_eq!(MCL_FUTURE, 2);
        assert_eq!(run(), Err(RuntimeError::NotImplemented));
        assert_eq!(selected_drive(), "6SL5510-1BB11-0AA0");
        assert_eq!(process_image_device(), "/dev/piControl0");
    }

    #[test]
    fn software_watchdog_fails_until_kicked_and_then_after_the_limit() {
        let mut watchdog = SoftwareWatchdog::new(Duration::from_millis(30));
        assert!(watchdog.expired(Duration::from_millis(0)));
        watchdog.kick(Duration::from_millis(0));
        assert!(!watchdog.expired(Duration::from_millis(30)));
        assert!(watchdog.expired(Duration::from_millis(31)));
    }

    #[test]
    fn mqtt_bridge_queues_an_adr0001_alarm_without_a_socket() {
        let mut bridge = MqttBridge::new();
        bridge.publish(MQTT_ALARM, "{\"code\":1}", false);
        let queued = bridge.drain();
        assert_eq!(queued.len(), 1);
        assert_eq!(queued[0].topic, "vibrocore/alarm");
        assert!(!queued[0].retain);
        assert!(bridge.drain().is_empty());
        assert_eq!(MQTT_HMI_STATUS, "vibrocore/hmi/status");
        assert_eq!(MQTT_CYCLE_PREFIX, "vibrocore/cycle/");
        assert_eq!(MQTT_STATUS_PREFIX, "vibrocore/status/");
        for topic in [
            MQTT_STATUS_HUB,
            MQTT_STATUS_SONIC,
            MQTT_STATUS_TILT,
            MQTT_STATUS_ROTATION,
            MQTT_STATUS_JOG,
        ] {
            assert!(topic.starts_with(MQTT_STATUS_PREFIX));
        }
    }
}
