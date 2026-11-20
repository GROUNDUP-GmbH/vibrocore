//! Play `firmware/revpi/golden/plant-vectors.json` on the Rust plant.
//! `tests/test_revpi_golden.py` plays the same file on `tests/revpi_plant.py`.

use serde_json::{Map, Value};
use vc_core::{Plant, PlantInput, PlantOutput, SamplePlan, CYCLE_MS, SF3_SECOND_HOLD_FITTED};

fn overlay(value: &Value) -> PlantInput {
    let mut input = PlantInput::default();
    let Some(object) = value.as_object() else {
        return input;
    };
    set_bool(&mut input.estop_nc, object, "estop_nc");
    set_bool(&mut input.limit_up_nc, object, "limit_up_nc");
    set_bool(&mut input.limit_down_nc, object, "limit_down_nc");
    set_bool(&mut input.hub_alarm, object, "hub_alarm");
    set_bool(&mut input.sonic_drive_fault, object, "sonic_drive_fault");
    set_i32(
        &mut input.sonic_current_pct_x10,
        object,
        "sonic_current_pct_x10",
    );
    set_bool(&mut input.sonic_sto_healthy, object, "sonic_sto_healthy");
    set_bool(
        &mut input.sonic_actual_running,
        object,
        "sonic_actual_running",
    );
    set_bool(&mut input.tool_engaged, object, "tool_engaged");
    set_bool(&mut input.enabling_held, object, "enabling_held");
    set_bool(
        &mut input.limit_vertical_reached,
        object,
        "limit_vertical_reached",
    );
    set_bool(
        &mut input.limit_folded_reached,
        object,
        "limit_folded_reached",
    );
    set_bool(
        &mut input.limit_deployed_reached,
        object,
        "limit_deployed_reached",
    );
    set_bool(
        &mut input.limit_retracted_reached,
        object,
        "limit_retracted_reached",
    );
    set_bool(&mut input.cmd_vertical, object, "cmd_vertical");
    set_bool(&mut input.cmd_fold, object, "cmd_fold");
    set_bool(&mut input.cmd_extend, object, "cmd_extend");
    set_bool(&mut input.cmd_retract, object, "cmd_retract");
    set_bool(&mut input.cmd_cycle_start, object, "cmd_cycle_start");
    set_bool(&mut input.cmd_jog_down, object, "cmd_jog_down");
    set_bool(&mut input.cmd_jog_up, object, "cmd_jog_up");
    set_bool(&mut input.cmd_park, object, "cmd_park");
    set_bool(&mut input.cmd_unpark, object, "cmd_unpark");
    set_bool(&mut input.cmd_reset, object, "cmd_reset");
    set_bool(&mut input.brake_test_enable, object, "brake_test_enable");
    set_i32(&mut input.brake_slip_um, object, "brake_slip_um");
    set_bool(&mut input.cmd_sample, object, "cmd_sample");
    set_bool(&mut input.cmd_rotate, object, "cmd_rotate");
    set_bool(&mut input.rotation_index, object, "rotation_index");
    set_bool(&mut input.rotate_reverse, object, "rotate_reverse");
    set_i16(
        &mut input.rotation_actual_rpm,
        object,
        "rotation_actual_rpm",
    );
    set_u8(
        &mut input.rotation_torque_pct,
        object,
        "rotation_torque_pct",
    );
    set_bool(&mut input.rotation_fault, object, "rotation_fault");
    set_i32(&mut input.sonic_target_mhz, object, "sonic_target_mhz");
    input
}

fn set_bool(slot: &mut bool, object: &Map<String, Value>, key: &str) {
    if let Some(value) = object.get(key).and_then(Value::as_bool) {
        *slot = value;
    }
}

fn set_i32(slot: &mut i32, object: &Map<String, Value>, key: &str) {
    if let Some(value) = object.get(key).and_then(Value::as_i64) {
        *slot = value as i32;
    }
}

fn set_i16(slot: &mut i16, object: &Map<String, Value>, key: &str) {
    if let Some(value) = object.get(key).and_then(Value::as_i64) {
        *slot = value as i16;
    }
}

fn set_u8(slot: &mut u8, object: &Map<String, Value>, key: &str) {
    if let Some(value) = object.get(key).and_then(Value::as_u64) {
        *slot = value as u8;
    }
}

fn fields(output: &PlantOutput) -> Map<String, Value> {
    let mut map = Map::new();
    map.insert("hub_state".into(), json_u8(output.hub.state as u8));
    map.insert(
        "position_um".into(),
        json_i64(output.hub.position_um as i64),
    );
    map.insert("speed_um_s".into(), json_i64(output.hub.speed_um_s as i64));
    map.insert("pulse_enable".into(), Value::Bool(output.hub.pulse_enable));
    map.insert(
        "motion_blocked".into(),
        Value::Bool(output.hub.motion_blocked),
    );
    map.insert("hub_fault".into(), Value::Bool(output.hub.fault));
    map.insert("sonic_state".into(), json_u8(output.sonic.state as u8));
    map.insert(
        "sonic_freq_mhz".into(),
        json_i64(output.sonic.freq_mhz as i64),
    );
    map.insert("sonic_run".into(), Value::Bool(output.sonic.run_command));
    map.insert("sonic_fault".into(), Value::Bool(output.sonic.fault));
    map.insert(
        "sonic_sto_fault".into(),
        Value::Bool(output.sonic.sto_monitor_fault),
    );
    map.insert("tilt_state".into(), json_u8(output.tilt.tilt_state as u8));
    map.insert(
        "tilt_vertical".into(),
        Value::Bool(output.tilt.tilt_vertical),
    );
    map.insert("tilt_fold".into(), Value::Bool(output.tilt.tilt_fold));
    map.insert("lift_extend".into(), Value::Bool(output.tilt.lift_extend));
    map.insert(
        "rotation_state".into(),
        json_u8(output.rotation.state as u8),
    );
    map.insert(
        "rotation_speed_rpm".into(),
        json_i64(output.rotation.command.speed_rpm as i64),
    );
    map.insert(
        "rotation_stalled".into(),
        Value::Bool(output.rotation.stalled),
    );
    map.insert(
        "rotation_angle_mdeg".into(),
        json_i64(output.rotation.angle_mdeg as i64),
    );
    map.insert(
        "rotation_indexed".into(),
        Value::Bool(output.rotation.indexed),
    );
    map.insert(
        "rotation_move_done".into(),
        Value::Bool(output.rotation.move_done),
    );
    map.insert("sample_phase".into(), json_u8(output.sample.phase as u8));
    map.insert("sample_stage".into(), json_u8(output.sample.stage));
    map.insert(
        "container_mdeg".into(),
        json_i64(output.sample.container_mdeg as i64),
    );
    map.insert("sample_fault".into(), Value::Bool(output.sample.fault));
    map.insert("safe_state".into(), Value::Bool(output.safety.safe_state));
    map.insert("safety_reason".into(), json_u8(output.safety.reason as u8));
    map
}

fn read_plan(object: &Map<String, Value>) -> SamplePlan {
    let mut plan = SamplePlan::default();
    if let Some(stages) = object.get("stages").and_then(Value::as_u64) {
        plan.stages = stages as u8;
    }
    if let Some(depth) = object.get("in_depth_um").and_then(Value::as_i64) {
        plan.in_depth_um = depth as i32;
    }
    if let Some(depths) = object.get("depth_um").and_then(Value::as_array) {
        for (index, value) in depths.iter().take(4).enumerate() {
            plan.depth_um[index] = value.as_i64().unwrap_or(0) as i32;
        }
    }
    if let Some(angles) = object.get("container_mdeg").and_then(Value::as_array) {
        for (index, value) in angles.iter().take(4).enumerate() {
            plan.container_mdeg[index] = value.as_i64().unwrap_or(0) as i32;
        }
    }
    plan
}

fn json_u8(value: u8) -> Value {
    Value::from(value as u64)
}

fn json_i64(value: i64) -> Value {
    Value::from(value)
}

#[test]
fn golden_vectors_match_the_rust_plant() {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../golden/plant-vectors.json"
    );
    let text = std::fs::read_to_string(path).expect("golden file");
    let data: Value = serde_json::from_str(&text).expect("json");
    assert_eq!(data["source"], "vc-core Plant");
    assert_eq!(data["cycle_ms"], CYCLE_MS);
    assert_eq!(
        data["sf3_second_hold_fitted"].as_bool(),
        Some(SF3_SECOND_HOLD_FITTED)
    );

    for case in data["cases"].as_array().expect("cases") {
        let mut plant = Plant::new();
        if let Some(position) = case["setup"]["position_um"].as_i64() {
            plant.set_position_um(position as i32);
        }
        if case["setup"]["indexed"].as_bool() == Some(true) {
            plant.set_rotation_indexed();
        }
        if let Some(plan) = case["setup"]["sample"].as_object() {
            plant.set_sample_plan(read_plan(plan));
        }
        for step in case["steps"].as_array().expect("steps") {
            let input = overlay(&step["input"]);
            let cycles = step["cycles"].as_u64().expect("cycles");
            let mut output = plant.tick(input);
            for _ in 1..cycles {
                output = plant.tick(input);
            }
            let actual = fields(&output);
            let expect = step["expect"].as_object().expect("expect");
            for (key, value) in expect {
                assert_eq!(
                    actual.get(key),
                    Some(value),
                    "{} {key}",
                    case["name"].as_str().unwrap_or("case")
                );
            }
        }
    }
}
