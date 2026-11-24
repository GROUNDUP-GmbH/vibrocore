# RevPi control service

This tree is the Option B control program.
ADR-0002 is the decision record.
The state machines live in `vc-core`.
The cyclic thread, `mlockall` and the device watchdog ioctl are not the field service.
Do not run this binary as a machine controller.

## Structure

```text
firmware/revpi/
  Cargo.toml                 workspace
  rust-toolchain.toml        Rust 1.83.0, rustfmt, clippy
  .cargo/config.toml         aarch64 linker
  golden/                    shared safety and plant vectors
  crates/vc-core/            domain logic, no device I/O, no_std outside tests
  crates/vc-io/              /dev/piControl0 process image
  crates/vc-modbus/          S200 and sonic register maps
  crates/vc-runtime/         loop, watchdogs, MQTT bridge, vibrocore-ctl
```

- `vc-core` contains the safety monitor and the machine plant.
- The plant covers the hub and the sonic and the tilt.
- The plant also covers the jog and the rod rotation and soil sampling.
- Hub motion is a logical pulse train for the S200 PTI.
- Modbus setpoints are not the motion path.
- Modbus registers that we did not verify stay TODO.
- SF3 uses only the S200 hold brake.
- Stefan decided on 2026-11-20 that there is no second hold means.
- Nobody works under the raised head.
- The team sizes the chain drive for the load.
- The team inspects the chain drive on a regular schedule.
- The brake test is optional.
- That decision is a risk acceptance, not a performance level.
- Jog runs only while you hold the enable switch.
- The sonic head runs only when you lower the tool and engage it.
- Tilt has two direction outputs and the actuator end stops.
- There is no tilt angle limit and no tilt sensor.
- The sample sequence drives in.
- The sequence then cuts one revolution.
- The sequence then dumps at each stage.
- One to four depth stages are parameters.
- A stall aborts to a fault state.
- The control blocks the rotation when the sonic head runs.
- The control also blocks rotation when the lift moves.
- None of these monitors is an ISO 13849 performance level.
- `vc-io` names `/dev/piControl0` and the piControl ioctl numbers.
- Byte offsets come from PiCtory.
- Those offsets are not in this tree.
- The output-watchdog argument layout is TODO.
- `vc-modbus` types the S200 map and the sonic map and the rotation map.
- Register 40100 and register 40101 come from the public S7-1200 example.
- The team did not verify them on the drive.
- The proposed sonic inverter is ATV320U15M2C.
- Every sonic register is still TODO.
- The slave address for rotation stays empty.
- It stays empty until the team freezes the drive.
- `vc-runtime` plans the 10 ms cycle, one isolated core, `SCHED_FIFO` and `mlockall`.
- It does not call those kernel functions yet.
- The bridge for MQTT keeps the messages in memory.
- It does not open a socket.
- The topic names are the same as ADR-0001.
- New topics for live data use the reserved prefix `vibrocore/status/`.
- The names are `hub`, `sonic`, `tilt`, `rotation`, `jog`, `sample`, `stage` and `container`.

## Tests on the host

Run these commands from `firmware/revpi`:

```bash
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
```

- The parity tests in Rust read `golden/safety-vectors.json`.
- The tests also read `golden/plant-vectors.json`.
- The parity test in Python plays the same files.

Run it from the repository root:

```bash
python -m pytest tests/test_revpi_golden.py -q
```

- The Python files `test_safety.py`, `test_hub.py`, `test_sonic.py` and `test_integration.py` stay the reference specification.
- The plant vectors cover the new states.
- They do not replace those 60 tests.
- The channel list is `docs/engineering/IO-LIST.md`.
- The proposed parts are `docs/engineering/CABINET-ADDITIONS.md`.

## Build for aarch64

The Connect 4 is aarch64.
Use `cross` from an x86_64 host:

```bash
cargo install cross --locked
cross build --target aarch64-unknown-linux-gnu --release
```

You can also use a system linker.
Install the linker.
Then build.

```bash
sudo apt-get install gcc-aarch64-linux-gnu
rustup target add aarch64-unknown-linux-gnu
cargo build --target aarch64-unknown-linux-gnu --release
```

- `.cargo/config.toml` selects `aarch64-linux-gnu-gcc` for that target.
- The CI job builds the host target.
- The CI job tests the host target.
- The CI job does not cross-compile.
