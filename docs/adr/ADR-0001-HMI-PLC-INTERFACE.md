---
title: ADR-0001 HMI–PLC Interface
status: Accepted
date: 2026-11-19
parts:
  - VC-CT-6100
  - VC-CT-6110
  - VC-CT-6120
  - VC-ASM-5000
---

# ADR-0001 — HMI–PLC Interface

## Context

The Vibrocore HMI runs in Node-RED on the controller (WAGO PFC200 XTR or RevPi).
The PLC runs in CODESYS. The two sides exchange data over Modbus TCP holding
registers (`GVL_MODBUS`) and publish events on MQTT (`Mosquitto`).

This ADR fixes the command semantics so that motion is hold-to-run, start and
reset are pulses, and all sides use one fault-code table.

## Decision

### Transport

| Path | Use |
|------|-----|
| Modbus TCP port 502 on the PLC | Command and status registers (`GVL_MODBUS`) |
| MQTT broker service name `mosquitto` | Cycle records, alarms, HMI presence |

MQTT topics:

| Topic | Direction | Retain | Meaning |
|-------|-----------|--------|---------|
| `vibrocore/hmi/status` | HMI → broker | yes | `online` / `offline` |
| `vibrocore/alarm` | HMI → broker | no | Safety fault event (JSON) |
| `vibrocore/cycle/{id}` | logger → broker | no | Signed cycle record (JSON) |
| `vibrocore/status/#` | reserved | yes | Future live status mirror |

Units in payloads use SI with a space (example: `12 mm`, `100 Hz`).

### Command semantics

| Command | Register | Semantics |
|---------|----------|-----------|
| Operating mode | `%MW0` | Change accepted only while the machine is idle (hub IDLE, no safe state, no fault). PLC writes the old mode back if the change is rejected. |
| Cycle start | `%MW1` | Edge-triggered pulse. PLC clears the register to 0 after it reads the rising edge. |
| Jog down / up | `%MW2` / `%MW3` | Momentary (hold-to-run). Do not latch to 1. |
| Jog heartbeat | `%MW33` | HMI increments this value at least every 100 ms while a jog button is pressed. |
| Sonic toggle | `%MW4` | Level in MANUAL mode. |
| Fault reset | `%MW5` | Edge-triggered pulse. PLC clears to 0. After E-stop: accept only a fresh rising edge that arrives while the E-stop circuit is healthy. Never auto-reset. |
| Lift / tilt | `%MW22`–`%MW25` | Momentary. Direction interlock and end-limit stop are in the actuator FBs. No motion while the hub is not IDLE. |

### Jog watchdog

1. While the operator holds a jog control, the HMI writes the direction bit and
   increments `%MW33` about every 100 ms.
2. The PLC starts a 300 ms timer when the heartbeat value stops changing.
3. If the timer ends, the PLC clears jog commands and stops motion.
4. Jog must never stay at 1 without a live heartbeat.

### Fault-code table (canonical)

Used by `FB_Safety.eSafetyReason`, `GVL_MODBUS.eStatus_SafetyReason`, and the
Node-RED `SAFETY_REASON` list:

| Code | Name |
|------|------|
| 0 | OK |
| 1 | ESTOP |
| 2 | LIMIT_UP |
| 3 | LIMIT_DOWN |
| 4 | HUB_ALARM |
| 5 | STONE_DETECTED |
| 6 | VFD_COMM |

Penetrometer Modbus loss uses a local FB fault flag and status force value. It
does not add a seventh safety reason to this table.

### Mode switch

`eMode` follows `%MW0` only when:

- hub state is IDLE, and
- safe state is false, and
- hub and sonic have no fault.

If the HMI writes a new mode while the machine is busy, the PLC restores the
previous mode in `%MW0`.

### NC limit logic

Digital limit inputs use NC contacts:

- TRUE = healthy (circuit closed)
- FALSE = limit reached or wire break

`FB_HubControl` uses `GVL_IO.xLimitUp` / `GVL_IO.xLimitDown` with that meaning.

## Consequences

- Field units must set Node-RED and Mosquitto secrets at commissioning. The
  repository has no default password.
- MQTT port 1883 stays on the internal Docker network. Node-RED binds to
  loopback or a dedicated HMI address, not `0.0.0.0`.
- Reviewers must confirm hold-to-run and E-stop reset on real WAGO or RevPi
  hardware. The Python suite covers the state-machine logic only.

## References

- `firmware/codesys/GVL_MODBUS.st`
- `firmware/codesys/PRG_Main.st`
- `firmware/codesys/FB_Safety.st`
- `firmware/docker/nodered/flows.json`
- `firmware/docker/mosquitto/mosquitto.conf`
