fn main() {
    let plan = vc_runtime::RtPlan::target();
    println!(
        "vibrocore-ctl skeleton, cycle {} ms, loop not implemented",
        plan.cycle.as_millis()
    );
}
