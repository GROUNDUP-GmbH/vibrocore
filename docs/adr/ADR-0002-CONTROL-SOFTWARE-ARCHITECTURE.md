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

Use Rust for time-critical code and for code next to the safety circuit.
Use Python only for tools.
Do not use CODESYS on this path.
Rust owns the cyclic loop and the machine state machine.
Rust owns the Modbus RTU master and the DIO process image.
Python owns test benches, data analysis, plm-sync and hardware-in-the-loop scripts.
The target cycle is 10 ms on a PREEMPT_RT kernel.
Run the control thread on one isolated core with policy SCHED_FIFO.
Call mlockall before the loop.
Use a software watchdog and the RevPi hardware watchdog.
Do not publish MQTT and do not build JSON on the loop thread.
Measure the cycle on a Connect 4 before you state a jitter value.
The state machine covers hub, sonic, sampling, tilt and faults.
Sampling is the hub drill sequence plus the lift deploy.
Keep the state codes from the Structured Text blocks.
The fault codes stay the table in ADR-0001.
Do not add a fault code.
The controller is RevPi Connect 4, part VC-CT-6800, plus one RevPi DIO, part VC-CT-6810.
The RevPi is the Modbus RTU master on the RS-485 port.
Use device node /dev/piControl0 with ioctl, read and write.
Byte offsets come from PiCtory and are not frozen.
The lift drive is SINAMICS S200 PTI order 6SL5510-1BB11-0AA0 (VC-HB-2300).
That drive is Modbus slave 2 and needs firmware V6.3 HF4 or later.
The S200 executes position control, the speed profile and the brake on X108.
The RevPi sends target values and reads status values.
The RevPi does not close the position loop.
The RevPi does not release the motor brake with a DIO output.
VC-PW-5310, the SDR-120-24, feeds only the S200 24 V input and the brake supply inside the drive.
Position comes from the 1FL2 absolute encoder in part VC-HB-2100.
VC-HB-3410, the chain-shaft encoder, is obsolete.
There is no chain encoder, so do not buy VC-HB-3410.
The sonic-head inverter is slave 1.
The order code is ATV320U15M2C, part VC-SH-1210.
The sonic register map is TODO.
Register 40100 is the example control word, and 40101 is the speed setpoint.
Those two numbers are not verified on this drive.
Mark every unverified register as TODO.
Keep the safety function in the hard-wired circuit.
Wire Pilz PNOZ s4 article 750104 (VC-CT-6220) to S200 STO input X131 and to the ATV320 STO input.
The RevPi software only reads the feedback contacts.
The software can send a normal stop.
Do not credit the RevPi software in any ISO 13849 performance level.
A software crash must not be the only path that removes torque.
ADR-0001 is not changed.
Node-RED, MQTT and Modbus TCP remain the HMI path only.
Do not put a state machine in Node-RED.
The 60 tests in test_safety, test_hub, test_sonic and test_integration stay the reference.
Port the tests to Rust and keep a golden-vector harness.
The Python model and the Rust model must agree on each vector.
This change ports three safety tests as the pattern.
The workspace path is `firmware/revpi/`.
The crates are `vc-core`, `vc-io`, `vc-modbus` and `vc-runtime`.
`vc-core` has no device I/O and stays compatible with no_std where practical.
The full loop is not implemented.

## Alternatives

CODESYS Control Basic M, article 2302000048, was considered.
The list price starts at 69 EUR excluding tax and is not a quote.
This decision rejects CODESYS.
The control loop is native Rust, not a soft PLC.
A demo licence stops after two hours.
Do not ship a demo licence on a field machine.
A Python cyclic service was considered.
This decision rejects Python for the cyclic loop.
Garbage collection can pause the process and can miss the 10 ms cycle.
Python remains the tool language.

## Consequences

Buy the RevPi Connect 4 and one RevPi DIO for this path.
Do not buy a CODESYS Basic M licence for this path.
Do not buy VC-HB-3410.
Confirm the S200 map on firmware V6.3 HF4 or later.
Select the sonic inverter before you fill its register map.
`CONTROL_SYSTEM.md` still describes the WAGO rack and is not changed here.
