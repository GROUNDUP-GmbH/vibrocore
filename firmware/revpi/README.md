# RevPi control skeleton

This tree is the Option B control program.
ADR-0002 is the decision record.
The program is a skeleton.
The cyclic loop is not implemented.
Do not run this binary as a machine controller.

## Structure

```text
firmware/revpi/
  Cargo.toml                 workspace
  rust-toolchain.toml        Rust 1.83.0, rustfmt, clippy
  .cargo/config.toml         aarch64 linker
  golden/safety-vectors.json shared safety vectors
  crates/vc-core/            domain logic, no device I/O, no_std outside tests
  crates/vc-io/              /dev/piControl0 process image
  crates/vc-modbus/          S200 and sonic register maps
  crates/vc-runtime/         loop, watchdogs, MQTT bridge, vibrocore-ctl
```

`vc-core` contains the safety monitor and the state codes.
The safety monitor is the first port of `FB_Safety`.
Hub, sonic, lift and tilt transitions are not ported.
`Machine::tick` returns `NotImplemented`.

`vc-io` names `/dev/piControl0` and the piControl ioctl numbers.
Byte offsets come from PiCtory.
Those offsets are not in this tree.
The output-watchdog argument layout is TODO.

`vc-modbus` types the S200 map and the sonic map.
Register 40100 and register 40101 come from the public S7-1200 example.
They are not verified on the drive.
The sonic order code is not selected.
Every sonic register is TODO.

`vc-runtime` plans a 10 ms cycle, one isolated core, `SCHED_FIFO` and `mlockall`.
It does not call those kernel functions yet.
The MQTT bridge stores messages in memory.
It does not open a socket.
Topic names match ADR-0001.

## Tests on the host

Run these commands from `firmware/revpi`:

```bash
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
```

The Rust parity test reads `golden/safety-vectors.json`.
The Python parity test plays the same file on `tests/sim.py`.
Run it from the repository root:

```bash
python -m pytest tests/test_revpi_golden.py -q
```

The Python files `test_safety.py`, `test_hub.py`, `test_sonic.py` and `test_integration.py` stay the reference specification.
Three safety tests are ported.
The other tests are not ported yet.

## Build for aarch64

The Connect 4 is aarch64.
Use `cross` from an x86_64 host:

```bash
cargo install cross --locked
cross build --target aarch64-unknown-linux-gnu --release
```

You can also use a system linker.
Install the linker, then build:

```bash
sudo apt-get install gcc-aarch64-linux-gnu
rustup target add aarch64-unknown-linux-gnu
cargo build --target aarch64-unknown-linux-gnu --release
```

`.cargo/config.toml` selects `aarch64-linux-gnu-gcc` for that target.
The CI job builds and tests the host target.
The CI job does not cross-compile.
