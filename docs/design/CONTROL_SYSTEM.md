# Control System Design

## Overview

The control system of the Vibrocore V1 uses the WAGO PFC200 XTR (750-8212).
This controller is industrial and the backbone is Modbus RTU.
The design uses the XTR variant for the extreme-environment certificate.
The range is −40 °C to +70 °C with 5g of continuous vibration.
The case is IP20 on a DIN-rail and the terminals are CAGE CLAMP.

These terminals are the CAGE CLAMP type and the rating is for the field.

```
┌─────────────────────────────────────────────────────────┐
│                  Instagrid ONE max                      │
│              230V AC, 3.6 kW, 2.1 kWh                 │
└────────┬──────────────────────────────┬─────────────────┘
         │ 230V AC                      │ 230V AC
         ▼                              ▼
  ┌─────────────┐                ┌──────────────────┐
  │ Sonic inverter │ Modbus RTU  │  Two 24 V DIN supplies │
  │  must have STO │◄───────────►│  SDR-120-24 dedicated │
  │  order open    │  RS-485     │  plus an open 24 V slot │
  └──────┬──────┘ Slave addr 1   └────────┬──────────┘
         │ 3× AC                          │ 24 V DC
         ▼                       ┌────────┴──────────┐
  ┌─────────────┐                │  24 V rail         │
  │ 2× OLI MVE │                │  dedicated SDR-120 │
  │ 400/6-HF   │                │  plus open slot    │
  │ 7.2 kg ea. │                └────────┬──────────┘
  └─────────────┘                        │ 24 V DC
                                  ┌──────▼──────────────────────────────┐
                                  │       WAGO PFC200 XTR               │
                                  │  Slot 1: 750-430/040-000  8× DI    │
                                  │  Slot 2: 750-537/040-000  8× DO    │
                                  │  No encoder slot. 1FL2 via S200    │
                                  │  Slot 3: 750-652 candidate RS-485  │
                                  │  Slot 4: 750-600 end module        │
                                  └──────┬──────────────────────────────┘
                                         │ RS-485 Modbus RTU
                               ┌─────────┴──────────────┐
                               │  Slave 1: Siemens V20  │
                               │  Slave 2: S200 drive   │
                               └────────────────────────┘
                                         │ STEP/DIR or CiA 402
                                         ▼
                                  ┌─────────────┐
                                  │  1FL2104    │
                                  │  + PLE120   │
                                  │  + encoder  │
                                  └─────────────┘
```



## WAGO I/O Module Assignment

### Slot 1 — 750-430 XTR: 4× Digital Input 24V DC

| Channel | Signal          | Wiring | Description                         |
|---------|-----------------|--------|-------------------------------------|
| DI 0    | `xLimitUp`      | NC     | Upper carriage limit switch         |
| DI 1    | `xLimitDown`    | NC     | Lower carriage limit switch         |
| DI 2    | `xEStop_NC`     | NC     | Emergency stop (mushroom button)    |
| DI 3    | `xHubAlarm`     | NO     | SINAMICS S200 alarm output          |

The rule for an NC wire is as follows.
A broken wire shows as a fault.
FALSE means a trigger or a break of the wire.

You must apply this rule to each safety input.

### Slot 2 — 750-530 XTR: 4× Digital Output 24V DC

| Channel | Signal           | Active | Description                          |
|---------|------------------|--------|--------------------------------------|
| DO 0    | `xBrakeRelease`  | HIGH   | Spring brake: 24V = released         |
| DO 1    | `xHubEnable`     | HIGH   | SINAMICS S200 enable                 |
| DO 2    | `xVFD_Reset`     | HIGH   | VFD fault reset pulse (200ms)        |
| DO 3    | `xAlarmBeacon`   | HIGH   | VC-CT-6230, 24 V, current at or below 0.5 A |

### Position — 1FL2 absolute encoder through the S200

VC-HB-3410 is obsolete.
Do not fit a chain-shaft encoder of 1000 ppr.
WAGO 750-637 is obsolete.
There is no encoder slot and no `%IW4` / `%IW5` mapping.
Position comes from the absolute encoder of the 1FL2 through the S200.
The constant `rENCODER_PULSES_PER_MM` stays at 671.9.

Do not change that constant in this revision.

### Slot 3 — 750-652 candidate: RS-485 Modbus RTU

| Parameter    | Value            |
|--------------|------------------|
| Baud rate    | 9600             |
| Data bits    | 8                |
| Parity       | Even             |
| Stop bits    | 1                |
| Termination  | 120 Ω (enable on last device in chain) |

The bus topology for V1.1 includes the penetrometer ADC.

```
WAGO 750-652 candidate ── sonic inverter (addr 1) ── S200 (addr 2) ── Force ADC (addr 3)
                                                                   [120Ω term. here]
```



## V1.1 I/O Expansion: Lift, Tilt, Penetrometer

When you add subsystems §8a–8c from the BOM, the following I/O slots are required.

### WAGO V1.1 — Additional Slots

#### Slot 6 — 750-430 XTR (2nd): 4× Digital Input (Actuators)

| Channel | Signal | Wiring | Description |
|---------|--------|--------|-------------|
| DI 0 | `xLiftDeployedLimit` | NC | Lift actuators fully deployed (drilling position) |
| DI 1 | `xLiftRetractedLimit` | NC | Lift actuators fully retracted (transport position) |
| DI 2 | `xTiltVerticalLimit` | NC | Mast in vertical/drilling position |
| DI 3 | `xTiltFoldedLimit` | NC | Mast folded to horizontal/transport position |

#### Slot 7 — 750-530 XTR (2nd): 4× Digital Output (Actuators)

| Channel | Signal | Active | Description |
|---------|--------|--------|-------------|
| DO 0 | `xLiftExtend` | HIGH | Extend lift actuators (deploy device down) |
| DO 1 | `xLiftRetract` | HIGH | Retract lift actuators (raise device) |
| DO 2 | `xTiltVertical` | HIGH | Drive tilt actuator to vertical/drilling position |
| DO 3 | `xTiltFold` | HIGH | Drive tilt actuator to fold/transport position |

`xLiftExtend` and `xLiftRetract` must never be TRUE at the same time.
The same rule applies to `xTiltVertical` and to `xTiltFold`.
Each pair drives one relay module of the H-bridge type for that group of actuators.

#### Slot 8 (existing 750-600 moves here): End module

#### Penetrometer — RS-485 Slave 3 (no new WAGO slot needed)

The force ADC is the Datexel DAT8017-A or an equal unit.

This ADC connects to the RS-485 bus as slave address 3.
Register 0 holds the force in raw counts from 0 to 65535, which maps to 0 to 5 kN.

```
rForce_raw := ModbusRead(uSlaveAddr := 3, uRegAddr := 0);
rForce_N   := REAL_TO_INT(rForce_raw) / 13.107;  // 0..65535 → 0..5000 N
```



### RevPi V1.1 — No Additional I/O Modules Required

The DIO module of the RevPi has 14 DI and 14 DO.
The count below is after the base system and after the V1.1 additions.

| Signals | Base (V1) | +V1.1 | Total used | DIO capacity |
|---------|-----------|--------|------------|--------------|
| DI (digital in) | 4 (limits, E-stop, alarm) | +4 (actuator limits) | **8** | 14 ✓ |
| DO (digital out) | 4 | +4 (actuator control) | **8** | 14 ✓ |

The RevPi needs only the upgrade of the PSU to the SDR-120-24 for actuator current.
The penetrometer ADC connects as RS-485 slave 3 on the built-in RS-485 port.



## Modbus Register Maps

### Siemens V20 VFD — Slave Address 1

The interface is standard Modbus PKW and PZD and you enable it with P0700=5 and with P1000=5.

| Register (0-based) | Name            | R/W | Scale       | Description                    |
|--------------------|-----------------|-----|-------------|--------------------------------|
| 100                | STW1            | W   | —           | Control word (see table below) |
| 101                | HSW             | W   | ×100 Hz     | Frequency setpoint             |
| 110                | ZSW1            | R   | —           | Status word                    |
| 111                | HIW             | R   | ×100 Hz     | Actual output frequency        |
| 112                | Current actual  | R   | ×10 A       | Output current                 |

- See the STW1 control words in the table below.

| Value    | Meaning                                              |
|----------|------------------------------------------------------|
| `0x047F` | Start (ON + no OFF2 + no OFF3 + operation enabled)   |
| `0x047E` | OFF1 — normal stop, ramp via P1121 (3s)              |
| `0x047B` | **OFF3 — fast stop, ramp via P1135 (0.3s) + DC brake** |
| `0x04FE` | Fault reset                                          |

The table below lists the V20 parameters for a fast stop.

| Parameter | Value | Meaning                            |
|-----------|-------|------------------------------------|
| P1135     | 0.3 s | OFF3 ramp-down time                |
| P1232     | 100 % | DC braking current (% rated)       |
| P1233     | 0.5 s | DC braking duration after ramp     |
| P1121     | 3.0 s | OFF1 normal ramp-down              |
| P1120     | 5.0 s | Ramp-up time                       |

The expected stop time from 100 Hz is 200 to 400 ms with OFF3 and with the DC brake.

### Nanotec C5-E Hub Driver — Slave Address 2 (CiA 402 via Modbus)

The live hub drive is the SINAMICS S200 and the order is 6SL5510-1BB11-0AA0.
The register table below is the previous map for the Nanotec C5-E.
It is not the parameter list for the S200.

| Register (hex) | Name                  | R/W | Description                          |
|----------------|-----------------------|-----|--------------------------------------|
| 6040h          | Controlword           | W   | CiA 402 state machine control        |
| 6041h          | Statusword            | R   | CiA 402 state machine status         |
| 60FFh          | Target velocity       | W   | Signed integer, rpm                  |
| 6064h          | Position actual value | R   | 32-bit signed, encoder counts        |
| 6060h          | Modes of operation    | W   | 3 = velocity mode                    |

The table below lists the CiA 402 control words.

| Value    | Meaning              |
|----------|----------------------|
| `0x0006` | Shutdown             |
| `0x000F` | Switch on + enable   |
| `0x000B` | Quick stop           |
| `0x0080` | Fault reset          |



## Stopping Logic: Sonic Head

- The two stop modes are not the same and you must not mix them.

| Mode         | Trigger                    | VFD Command | Ramp   | Stop Time |
|--------------|----------------------------|-------------|--------|-----------|
| Normal stop  | End of cycle (target depth) | OFF1 `0x047E` | P1121 3s | ~3–5 s |
| **Fast stop** | Stone / E-Stop / Safety    | **OFF3 `0x047B`** | P1135 0.3s + DC brake | **~200–400 ms** |

The interlock for hub retract works as follows.
In `FB_HubControl` state 4 (`STOP_SONIC`) the hub stays in place and the brake stays on until `FB_SonicHead.xConfirmedStopped = TRUE`.
This flag is set only after the two checks below.
1. The VFD reports `xRunning = FALSE` and ZSW1 bit 2 is 0.
2. The PLC confirms standstill for a continuous 200 ms.

A bypass of this interlock is not possible by design.
The hub can enter retract state 5 only from state 4.
That state requires `xConfirmedStopped`.



## SE050 / RDDL Trust Wallet Integration

Each sampling cycle gets the cryptographic signature for VM0042 data provenance.
The signature uses the secure element from NXP SE050.

```
WAGO PFC200 (COM1 / onboard UART)
        │  115200 baud, JSON lines
        ▼
  Xiao ESP32-C3
        │  I2C  (SDA/SCL)
        ▼
  NXP SE050
   secp256k1 key
   (RDDL-provisioned)
        │  signed payload
        ▼
  RDDL / Planetmint
  (VM0042 data notarization)
```

The data flow is as follows.
1. `FB_DataLogger` assembles the JSON payload with `"sign_pending": true` at the end of the cycle.
2. The payload goes on WAGO COM1 to the ESP32-C3 as one JSON line with LF at the end.
3. The ESP32-C3 extracts the payload and the SE050 signs it with the private key secp256k1.
4. The ESP32-C3 adds the `"signature"` field and the `"pubkey"` field and sends them to RDDL on MQTT over WiFi.
5. RDDL records the data on Planetmint for the VM0042 audit trail and the record is immutable.

The ESP32-C3 also receives NMEA from the GPS antenna on the drill head.
The antenna unit is the u-blox ZED-F9P and the mode is RTK.
It pushes `{"lat": …, "lon": …, "fix": "RTK"}` to the WAGO every 1 s on the same COM1 UART.
`FB_DataLogger` reads these values and puts them in each cycle record.



## Mobile Connectivity — Teltonika RUT241

In the field, LTE is required for the WAGO PFC200 for the tasks below.

- Remote debug of CODESYS through the CODESYS Gateway on VPN.
- You update the firmware by OTA with CODESYS Online Change.
- Upload of MQTT data to the RDDL cloud as a backup if WiFi is down.

The selected router is the Teltonika RUT241.
It mounts on a DIN-rail and the rating is IP30.
The temperature range is −40 °C to +75 °C and the radio is Cat4 LTE.
The RUT241 input is 9 to 30 V DC and the draw is below 6.5 W.
Power it from the 24 V rail.

Do not fit a converter from 24 V to 9 V.

```
Instagrid ONE max
      │ 230V AC
      ▼
  ┌──────────────┐
  │ Teltonika    │  LTE Cat4 (SIM)
  │ RUT241       │──────────────────► Internet / RDDL / Cloud
  │ DIN-rail     │  WiFi AP (2.4 GHz)
  └──────┬───────┘
         │ Ethernet (LAN)
         ▼
  WAGO PFC200 XTR (ETH1)
```

The RUT241 configuration is as follows.

- The WAN is a data-only SIM, for example Teltonika Mobile, and 1 GB each month is enough.
- The LAN gateway is static IP 192.168.1.1 and the WAGO is on 192.168.1.10.
- The VPN is a WireGuard tunnel to the developer workstation for remote access.
- The firewall opens only outbound MQTT on port 1883 or 8883 and WireGuard on UDP 51820.

The power input is 9 to 30 V DC.
The 24 V rail feeds it through the step-down and the draw is about 3 W.
An alternative for better cellular coverage is the Teltonika TRB140.
The unit has an mPCIe form and it fits in the Rittal enclosure of rating IP65.
Or use the RUT956 if you need redundancy of two SIM cards.



## Braking Energy Analysis — Why No External Resistor is Needed

You must dissipate the kinetic energy in the fast OFF3 stop.

The energy is in the two rotors of the OLI MVE 400/6-HF.
The open point is if an external brake resistor is necessary.

### Energy calculation

```
Per motor:
  I (moment of inertia) ≈ m_eccentric × r² = 0.5 kg × (0.02 m)² = 0.0002 kg·m²
  ω = 6000 RPM = 628 rad/s
  E_kin = ½ × I × ω² = ½ × 0.0002 × 628² ≈ 39 J

Both motors: E_total ≈ 80 J
```

### Dissipation path: DC injection braking (P1232 = 100%)

After the ramp-down of 0.3 s (P1135), the V20 applies 100 percent of rated current as DC to the stator.
The stator turns that energy into heat in the motor windings.

```
Motor thermal mass: m = 7.2 kg, c ≈ 450 J/(kg·°C)
ΔT per stop = E / (m × c) = 39 / (7200 × 0.45) = 0.012 °C per motor
```

At 100 stops in a day, the cumulative temperature rise is 1.2 °C.
This rise is small next to the thermal rating of the motor and next to the continuous self-cool flow.

### DC bus overvoltage risk during the ramp phase

During the 0.3 s ramp from 100 Hz to 0, the motor sends the short burst of energy back.

That energy goes back to the DC bus in the V20.
The V20 handles this as follows.

| V20 Parameter | Value | Effect |
|---------------|-------|--------|
| P1240 | 1 (ON) | Vdc-max controller — auto-extends ramp if bus voltage rises |
| P1135 | 0.3 s | OFF3 ramp time (0.3s is aggressive; increase to 0.5s if bus trips) |
| P1232 | 100 % | DC braking current after ramp |
| P1233 | 0.5 s | DC braking duration |

With P1240 set to 1, the control is active.
If the voltage of the DC bus nears the trip level in the ramp, the V20 extends the ramp.
The motor still stops, and the stop is much faster than OFF1 at 3 s.
This avoids the fault DC-link overvoltage.

### Decision: no external braking resistor in V1

| Option | Cost | Complexity | Needed? |
|--------|------|------------|---------|
| DC injection braking (P1232=100%) | €0 | None | ✅ Default |
| Increase P1135 to 0.5s if trips | €0 | None | If needed |
| V20 external braking resistor module | ~€80 | Wiring | Only if P1240 doesn't help |

At the first start, use P1135 = 0.3 s and use P1240 = 1.

If the DC bus trips on overvoltage in a fast stop in the field, increase P1135 to 0.5 s.
Do not expect a need for an external brake resistor.



## Operator HMI — Docker Stack on PFC200 XTR

The PFC200 XTR with firmware at or above 23 has Docker in the unit.
Two containers run beside the CODESYS runtime.

```
WAGO PFC200 XTR (192.168.1.10)
├── CODESYS Runtime  → Modbus TCP Slave (port 502)
└── Docker
    ├── vibrocore-hmi   (Node-RED + Dashboard  → port 1880)
    └── vibrocore-mqtt  (Mosquitto MQTT broker  → port 1883)
```

The resource budget is about 45 MB of RAM, with under 5 percent of CPU at idle.
This load is well inside the headroom of 512 MB and 1 GHz.

### Dashboard screens

| Tab | Content |
|-----|---------|
| Betrieb | Cycle Start, Fault Reset, Jog Up/Down, depth/freq sliders, live gauges |
| Status | State machine text (System / Hub / Sonic), safety reason, trend charts |
| Protokoll | Per-cycle log table (depth, freq, GPS, signed flag) |

On each span of 500 ms, Node-RED polls the CODESYS unit on Modbus TCP.

The read is FC3 on registers 0 to 21.
HMI write commands from buttons and from sliders use FC6 and FC16 on the same registers.

See `firmware/docker/` for the full stack and see `firmware/docker/README.md` for the setup.

### Modbus TCP Slave configuration in CODESYS

In CODESYS, set the Modbus TCP slave as follows.
1. In the device tree, add the device of type `Modbus TCP Slave` (WagoAppModbusSlaveTcp).
2. Set the port to 502 and set the unit ID to 1.
3. Map `%MW0..%MW21` as in `firmware/codesys/GVL_MODBUS.st`.



## Development Environment

### CODESYS V3.5 (WAGO PFC200 target)

- Download the free runtime for the WAGO PFC from the [CODESYS Store](https://store.codesys.com)
- The WAGO extension is **WAGO-I/O-PRO** or the package CODESYS for WAGO.
- Required libraries:
  - `WagoAppModbusMasterRtu` ≥ 1.1.0.0
  - `WagoAppModbusSlaveTcp` is the slave interface for HMI on Modbus TCP.
  - `WagoSysTimeRtc` (timestamp in DataLogger)
- The target is the WAGO PFC200 XTR on Arm Linux.
- You write in Structured Text (ST) and the norm is IEC 61131-3.

CODESYS Go is an IDE in the browser for edit and for deploy, and it is not an HMI app.
You use it to write ST code and to deploy that code to the PFC from any browser.
This path helps when a Windows VM is not on hand.
It is not the operator dashboard.

### Running on Mac (no Windows required)

Option A is a UTM virtual machine. It is recommended for full comfort in the IDE.
```bash
# Install UTM from https://mac.getutm.app
# Create Windows 11 ARM VM (free via Azure Dev) or Windows 10 x86 via Rosetta
# Install CODESYS V3.5 in the VM
# Connect to WAGO PFC via WAGO USB-Service-Cable or Ethernet/VPN
```

Option B is CODESYS Go in the browser and it needs no VM.
```
# Open: https://go.codesys.com
# Target: WAGO PFC200 (IP: 192.168.1.10, port 1740)
# Full ST editor + online debugging in any Chromium browser
```

- Option C is a cloud VM.
- AWS EC2 t3.small on Windows Server is about $15 each month.
- Install CODESYS V3.5 and connect it to the WAGO on the WireGuard VPN.
- You do OTA updates with CODESYS Online Change.



## Remote Access and OTA Updates

The WAGO PFC200 gives you remote access from the unit.

| Feature | Method | URL / Config |
|---------|--------|--------------|
| Web UI | HTTP | `http://192.168.1.10` |
| SSH | OpenSSH | `ssh admin@192.168.1.10` |
| VPN | OpenVPN / WireGuard | Configure in WBM |
| CODESYS Online | TCP/IP | Port 1740 (CODESYS Gateway) |
| OTA firmware | CODESYS Online Change | No service stop required |
| MQTT broker | Mosquitto | Docker container (port 1883) |
| Node-RED | HTTP | `http://192.168.1.10:1880` |

For field use on mobile LTE, the Teltonika RUT241 gives the LTE uplink and the WireGuard VPN.
The WAGO PFC connects as a LAN client and the developer connects from any place.
See the [section on mobile connectivity](#mobile-connectivity--teltonika-rut241) above.



## Controller Comparison: WAGO PFC200 XTR vs. Revolution Pi Connect 4

Two controller options are viable for the Vibrocore V1.
The WAGO is the primary choice for production.

The RevPi Connect 4 is a low-cost alternative for a first build or for a low-cost build.

### Hardware comparison

| Feature | WAGO PFC200 XTR (750-8212) | RevPi Connect 4 |
|---------|---------------------------|-----------------|
| CPU | 1 GHz ARM Cortex-A8 (single) | 1.5 GHz Quad-Core Cortex-A72 |
| RAM | 512 MB DDR3 | 2 / 4 / 8 GB LPDDR4 |
| Flash | 4 GB eMMC | 8 / 32 GB eMMC |
| **Temp range** | **−40 °C … +70 °C** | −25 °C … +55 °C |
| **Vibration** | **5g (EN 60068-2-6)** | EN 61131-2 (less explicit) |
| RS-485 | Via 750-652 candidate | **Built-in** (4-pin screw) |
| Ethernet | 2× 10/100 | 2× Gigabit |
| Docker | FW ≥ 23 (built-in) | **Native** (full Raspberry Pi OS) |
| CODESYS | Dedicated Runtime (licensed w/ HW) | Soft PLC on PREEMPT_RT Linux |
| Real-time | Dedicated CODESYS RTOS | PREEMPT_RT kernel patch |
| Terminals | CAGE CLAMP (vibration-proof) | Screw terminals |
| TPM 2.0 | No | Yes |
| Origin | Made in Germany (WAGO) | Made in Germany (KUNBUS) |
| License fees | Runtime included with hardware | **None** (open source Linux) |

### I/O module comparison

| I/O function | WAGO (Option A) | RevPi (Option B) |
|-------------|-----------------|------------------|
| 4× DI 24V | 750-430 XTR (€60–90) | **RevPi DIO** covers all → |
| 4× DO 24V | 750-530 XTR (€60–90) | **RevPi DIO** covers all → |
| Chain encoder | Obsolete. VC-HB-3410 and 750-637 are not fitted. | Position is the 1FL2 through the S200 |
| RS-485 Modbus RTU | 750-652 candidate (€80–120) | **Built into Connect 4 base** |
| End module | 750-600 (€10–20) | Not required |
| **I/O total** | **€210–320** (DI, DO, serial, end) | **€196** (1× RevPi DIO) |

The RevPi DIO replaces the modules for digital input and for digital output.
It does not replace a module for an encoder.
The chain encoder is obsolete.
Do not use the DIO encoder mode for a chain encoder.

### Controller cost summary

| Item | WAGO Option A | RevPi Option B |
|------|--------------|----------------|
| Base controller | €600–900 | ~€450 (Connect 4 4 GB + RAM surcharge) |
| I/O modules | €210–320 | €196 (1× DIO) |
| **Controller subtotal** | **€810–1,220** | **~€646** |
| Savings vs. WAGO | — | **€164–574** |

### Decision guidance

Use the WAGO PFC200 XTR when the conditions below are true.

- The ambient temperature can drop below −25 °C, as in winter storage in Eastern Europe.
- The maximum resistance to vibration is required for rocky ground with high vibration.
- You need a time guarantee from the dedicated CODESYS runtime.
- A long-term contract for industrial support is required.

Use the RevPi Connect 4 when the conditions below are true.

- Cost is the main limit and the saving is about 300 to 500 euro on the controller alone.
- More RAM or CPU for edge tasks or for data logging is a benefit.
- You can keep the control enclosure above −25 °C in standard field conditions.
- You get full flexibility of Linux with Python, Node-RED, Docker, and with no Windows tie.
- The phase is the V1 prototype or a proof of the concept.

In Hungary or in Austria, the temperature in the field rarely drops to a point below −25 °C.
That is the active bore season from March to November.
Gear that stays outdoors overnight in January can reach −20 °C.
If you insulate the enclosure or if you heat it, the RevPi stays in spec.
A self-adhesive heater strip at 15 euro does that heat task.
The WAGO rating of −40 °C gives a comfort margin and you need no extra mitigation.

The RevPi ships with Raspberry Pi OS and the base is Debian.

### RevPi-specific software notes

You need no Windows toolchain at any stage.

```bash
# Node-RED (native, no Docker needed — but Docker works too):
ssh user@192.168.1.10
sudo apt install nodered
node-red-start

# CODESYS Soft PLC for RevPi (download from CODESYS Store):
# Target package: "CODESYS Control for Raspberry Pi SL"
# Programming: same ST code as WAGO, same IEC 61131-3

# Python automation alternative (no CODESYS license needed):
pip install pymodbus asyncio
# → full Vibrocore logic in Python on RevPi Linux
```

The Docker Compose stack in `firmware/docker/` runs in the same way on the RevPi, also on arm/v8.
Change the platform tag in `docker-compose.yml`.

```yaml
platform: linux/arm/v8   # RevPi Connect 4 (CM4 = armv8)
# platform: linux/arm/v7  # WAGO PFC200 XTR (Cortex-A8 = armv7)
```
