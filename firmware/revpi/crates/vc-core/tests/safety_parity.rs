//! Play `firmware/revpi/golden/safety-vectors.json` on the Rust monitor.
//! `tests/test_revpi_golden.py` plays the same file on `tests/sim.py`.

use serde_json::Value;
use vc_core::{SafetyInput, SafetyMonitor, SafetyReason, CYCLE_MS};

fn input_from(value: &Value) -> SafetyInput {
    SafetyInput {
        estop_nc: value["xEStop_NC"].as_bool().expect("xEStop_NC"),
        limit_up_nc: value["xLimitUp_NC"].as_bool().expect("xLimitUp_NC"),
        limit_down_nc: value["xLimitDown_NC"].as_bool().expect("xLimitDown_NC"),
        hub_alarm: value["xHubAlarm"].as_bool().expect("xHubAlarm"),
        vfd_fault: value["xVFD_Fault"].as_bool().expect("xVFD_Fault"),
        vfd_current_pct: value["rVFD_Current_pct"]
            .as_f64()
            .expect("rVFD_Current_pct") as f32,
        hub_moving_down: value["xHubMovingDown"].as_bool().expect("xHubMovingDown"),
        hub_moving_up: value["xHubMovingUp"].as_bool().expect("xHubMovingUp"),
    }
}

#[test]
fn golden_vectors_match_rust_safety_monitor() {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../golden/safety-vectors.json"
    );
    let text = std::fs::read_to_string(path).expect("golden file");
    let data: Value = serde_json::from_str(&text).expect("json");
    assert_eq!(data["source"], "tests/sim.py FB_Safety");
    assert_eq!(data["cycle_ms"], CYCLE_MS);
    let cases = data["cases"].as_array().expect("cases");
    let names: Vec<_> = cases
        .iter()
        .map(|case| case["name"].as_str().expect("name"))
        .collect();
    assert_eq!(
        names,
        [
            "estop_has_highest_priority",
            "limit_up_causes_safe_state_only_when_moving_up",
            "above_threshold_after_debounce",
        ]
    );

    for case in cases {
        let mut safety = SafetyMonitor::new();
        for step in case["steps"].as_array().expect("steps") {
            let input = input_from(&step["input"]);
            let cycles = step["cycles"].as_u64().expect("cycles");
            let mut output = safety.tick(input);
            for _ in 1..cycles {
                output = safety.tick(input);
            }
            let expect = &step["expect"];
            assert_eq!(output.safe_state, expect["safe_state"].as_bool().unwrap());
            assert_eq!(
                output.stone_detected,
                expect["stone_detected"].as_bool().unwrap()
            );
            assert_eq!(
                output.limit_up_triggered,
                expect["limit_up_triggered"].as_bool().unwrap()
            );
            assert_eq!(
                output.limit_down_triggered,
                expect["limit_down_triggered"].as_bool().unwrap()
            );
            let reason = expect["reason"].as_u64().unwrap() as u8;
            assert_eq!(output.reason, SafetyReason::from_code(reason).unwrap());
        }
    }
}
