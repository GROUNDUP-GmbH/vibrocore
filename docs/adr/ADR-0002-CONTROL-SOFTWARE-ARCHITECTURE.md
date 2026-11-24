---
title: ADR-0002 Control software architecture
status: Accepted
date: 2026-11-20
deciders:
  - Stefan (CTO)
parts:
  - VC-CT-6800
  - VC-CT-6810
  - VC-CT-6220
  - VC-HB-2100
  - VC-HB-2300
  - VC-ASM-5000
---

# ADR-0002 - Control software architecture

## Status

Stefan (CTO) accepted this decision on 2026-11-20.
The accepted rule is: "the right parts in the right language, clean and structured".

## Decision

- Use Rust for time-critical code and for code next to the safety circuit.
- Use Python only for tools.
- Do not use CODESYS on this path.
- Rust owns the cyclic loop and the machine state machine.
- Rust owns the Modbus RTU master and the DIO process image.
- Python owns the test benches and the data analysis.
- Python also owns plm-sync and the hardware-in-the-loop scripts.
- The target cycle is 10 ms on a PREEMPT_RT kernel.
- Run the control thread on one isolated core with policy SCHED_FIFO.
- Call mlockall before the loop.
- Use a software watchdog and the RevPi hardware watchdog.
- Do not publish MQTT on the loop thread.
- Do not build JSON on the loop thread.
- Measure the cycle on a Connect 4 before you state a jitter value.
- The state machine covers the hub and the sonic.
- It also covers sampling and the tilt and the faults.
- Sampling is the hub drill sequence.
- The sequence also has the lift deploy.
- Keep the state codes from the Structured Text blocks.
- The fault codes stay as the table in ADR-0001.
- Do not add a fault code.
- The controller is the RevPi Connect 4, part VC-CT-6800.
- Add one RevPi DIO, part VC-CT-6810.
- The RevPi is the Modbus RTU master on the RS-485 port.
- Use the node /dev/piControl0.
- The calls are ioctl and read and write.
- PiCtory gives the byte offsets.
- Nobody froze the offsets.
- The lift drive is SINAMICS S200 PTI.
- The order code is 6SL5510-1BB11-0AA0.
- The part is VC-HB-2300.
- That drive is Modbus slave 2.
- It needs firmware at V6.3 HF4 or later.
- The S200 executes position control, the speed profile and the brake on X108.
- The RevPi sends the target values.
- The RevPi reads the status values.
- The RevPi does not close the position loop.
- The RevPi does not release the motor brake with a DIO output.
- VC-PW-5310 feeds only the S200.
- The supply is the SDR-120-24.
- It feeds the 24 V input and the brake supply in the drive.
- Position comes from the 1FL2 absolute encoder in part VC-HB-2100.
- VC-HB-3410, the chain-shaft encoder, is obsolete.
- There is no chain encoder.
- Do not buy VC-HB-3410.
- The sonic-head inverter is slave 1.
- The order code is ATV320U15M2C, part VC-SH-1210.
- The sonic register map is TODO.
- Register 40100 is the example control word.
- Register 40101 is the speed setpoint.
- The team did not verify those two numbers on this drive.
- Mark each unverified register as TODO.
- Keep the safety function in the hard-wired circuit.
- Wire the Pilz PNOZ s4.
- The article is 750104 (VC-CT-6220).
- Wire it to the S200 STO input X131.
- Wire it also to the ATV320 STO input.
- The RevPi software only reads the feedback contacts.
- The software can send a normal stop.
- Do not credit the RevPi software for a performance level in ISO 13849.
- A software crash must not be the only path that removes torque.
- This decision does not change ADR-0001.
- Node-RED, MQTT and Modbus TCP remain the HMI path only.
- Do not put a state machine in Node-RED.
- The 60 tests stay the reference.
- The tests are test_safety and test_hub and test_sonic and test_integration.
- Port the tests to Rust.
- Keep a golden-vector harness.
- The Python model and the Rust model must agree on each vector.
- This change ports three safety tests as the pattern.
- The workspace path is `firmware/revpi/`.
- The crates are `vc-core`, `vc-io`, `vc-modbus` and `vc-runtime`.
- `vc-core` has no device I/O and stays compatible with no_std where practical.
- The full loop is not in the code.

## Alternatives

- We considered CODESYS, the Control Basic M product.
- The product is Control Basic M, article 2302000048.
- The list price starts at 69 EUR excluding tax and is not a quote.
- This decision rejects CODESYS.
- The control loop is native Rust, not a soft PLC.
- A demo licence stops when two hours end.
- Do not ship a demo licence on a field machine.
- We considered the Python cyclic service.
- This decision rejects Python for the cyclic loop.
- Garbage collection can pause the process and can miss the 10 ms cycle.
- Python remains the tool language.

## Consequences

- Buy the RevPi Connect 4 and one RevPi DIO for this path.
- Do not buy the CODESYS Basic M licence for this path.
- Do not buy VC-HB-3410.
- Confirm the S200 map on firmware V6.3 HF4 or later.
- Select the sonic inverter before you fill its register map.
- This ADR does not change `CONTROL_SYSTEM.md`.
- That file still describes the WAGO rack.
