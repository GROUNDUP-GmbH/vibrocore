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

The Vibrocore HMI runs in Node-RED.
The HMI runs on the controller.
The controller is a WAGO PFC200 XTR or a RevPi.
The PLC runs in CODESYS.
The two sides exchange data on Modbus TCP.
The sides use the registers that hold values (`GVL_MODBUS`).

- The sides also publish events on MQTT (`Mosquitto`).
- This ADR fixes the rules for commands.
- Motion is hold-to-run.
- Start and reset are pulses.
- All sides use one fault-code table.

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

The units in a payload use SI with a space (example: `12 mm`, `100 Hz`).

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

1. While the operator holds the jog control, the HMI writes the direction bit. The HMI adds one to `%MW33` about each 100 ms.
2. The PLC starts the 300 ms timer when the heartbeat value does not change.
3. If the timer ends, the PLC clears the jog commands and stops the motion.
4. Jog must not stay at 1 with no live heartbeat.

### Fault-code table (canonical)

`FB_Safety.eSafetyReason`, `GVL_MODBUS.eStatus_SafetyReason` and the Node-RED `SAFETY_REASON` list use this table.

| Code | Name |
|------|------|
| 0 | OK |
| 1 | ESTOP |
| 2 | LIMIT_UP |
| 3 | LIMIT_DOWN |
| 4 | HUB_ALARM |
| 5 | STONE_DETECTED |
| 6 | VFD_COMM |

A loss of Modbus on the penetrometer uses the local fault flag in the FB.
The loss also uses the status force value.
It does not add the seventh safety reason to this table.

### Mode switch

`eMode` follows `%MW0` only when all of these are true.

- The hub state is IDLE.
- The safe state is false.
- The hub and the sonic have no fault.

If the HMI writes the new mode while the machine is busy, the PLC restores the previous mode in `%MW0`.

### NC limit logic

The inputs for a limit are digital NC contacts.

- TRUE means the healthy state, and the circuit stays closed.
- FALSE means the reached limit or an open wire.

`FB_HubControl` uses `GVL_IO.xLimitUp` / `GVL_IO.xLimitDown` with that meaning.

## Consequences

- Field units must set Node-RED and Mosquitto secrets when you start the unit.
- The repository has no default password.
- MQTT port 1883 stays on the internal Docker network.
- Node-RED binds to loopback or to a dedicated HMI address, not to `0.0.0.0`.
- Reviewers must confirm hold-to-run and the E-stop reset on real WAGO hardware or RevPi hardware.
- The Python suite covers only the logic of the state machine.

## References

- `firmware/codesys/GVL_MODBUS.st`
- `firmware/codesys/PRG_Main.st`
- `firmware/codesys/FB_Safety.st`
- `firmware/docker/nodered/flows.json`
- `firmware/docker/mosquitto/mosquitto.conf`
