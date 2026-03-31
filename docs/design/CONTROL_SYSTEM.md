# Control System Design

## Overview

The Vibrocore V1 control system is built around the **WAGO PFC200 XTR (750-8212)** industrial controller with a Modbus RTU backbone. The XTR variant is chosen for its extreme-environment certification: −40 °C to +70 °C, 5g continuous vibration, IP20 DIN-rail housing, CAGE CLAMP terminals rated for the field.

```
┌─────────────────────────────────────────────────────────┐
│                  Instagrid ONE max                      │
│              230V AC, 3.6 kW, 2.1 kWh                 │
└────────┬──────────────────────────────┬─────────────────┘
         │ 230V AC                      │ 230V AC
         ▼                              ▼
  ┌─────────────┐                ┌──────────────────┐
  │ Siemens V20 │ Modbus RTU     │  Mean Well        │
  │    1.5 kW   │◄──────────────►│  SDR-75-48        │
  │    VFD      │  RS-485        │  48V/1.6A DC PSU  │
  └──────┬──────┘ Slave addr 1   └────────┬──────────┘
         │ 3× AC                          │ 48V DC
         ▼                       ┌────────┴──────────┐
  ┌─────────────┐                │  Mean Well         │
  │ 2× OLI MVE │                │  DDR-60D-24        │
  │ 400/6-HF   │                │  48V→24V/2.5A      │
  │ 7.2 kg ea. │                └────────┬──────────┘
  └─────────────┘                        │ 24V DC
                                  ┌──────▼──────────────────────────────┐
                                  │       WAGO PFC200 XTR (750-8212)    │
                                  │  Slot 1: 750-430 XTR  4× DI 24V DC │
                                  │  Slot 2: 750-530 XTR  4× DO 24V DC │
                                  │  Slot 3: 750-637      Encoder IF    │
                                  │  Slot 4: 750-826      RS-485        │
                                  │  Slot 5: 750-600      End module    │
                                  └──────┬──────────────────────────────┘
                                         │ RS-485 Modbus RTU
                               ┌─────────┴──────────────┐
                               │  Slave 1: Siemens V20  │
                               │  Slave 2: Nanotec C5-E │
                               └────────────────────────┘
                                         │ STEP/DIR or CiA 402
                                         ▼
                                  ┌─────────────┐
                                  │  NEMA 42    │
                                  │  Stepper    │
                                  │  + Encoder  │
                                  └─────────────┘
```

---

## WAGO I/O Module Assignment

### Slot 1 — 750-430 XTR: 4× Digital Input 24V DC

| Channel | Signal          | Wiring | Description                         |
|---------|-----------------|--------|-------------------------------------|
| DI 0    | `xLimitUp`      | NC     | Upper carriage limit switch         |
| DI 1    | `xLimitDown`    | NC     | Lower carriage limit switch         |
| DI 2    | `xEStop_NC`     | NC     | Emergency stop (mushroom button)    |
| DI 3    | `xHubAlarm`     | NO     | Nanotec C5-E alarm output (ALM pin) |

> **NC wiring convention:** a broken wire is detected as a fault (FALSE = triggered OR wire break). This is mandatory for safety-relevant inputs.

### Slot 2 — 750-530 XTR: 4× Digital Output 24V DC

| Channel | Signal           | Active | Description                          |
|---------|------------------|--------|--------------------------------------|
| DO 0    | `xBrakeRelease`  | HIGH   | Spring brake: 24V = released         |
| DO 1    | `xHubEnable`     | HIGH   | Nanotec C5-E ENA pin                 |
| DO 2    | `xVFD_Reset`     | HIGH   | VFD fault reset pulse (200ms)        |
| DO 3    | `xAlarmBeacon`   | HIGH   | Visual alarm beacon / HMI indicator  |

### Slot 3 — 750-637: Incremental Encoder Interface

| Parameter | Value                                |
|-----------|--------------------------------------|
| Encoder   | 1000 ppr quadrature on chain shaft   |
| Register  | `%IW4` (low word) + `%IW5` (high word) → 32-bit signed position |
| Scale     | 671.9 encoder counts per mm of carriage travel |
| Zero      | Set in Nanotec C5-E on home (upper limit) |

### Slot 4 — 750-826: RS-485 Modbus RTU

| Parameter    | Value            |
|--------------|------------------|
| Baud rate    | 9600             |
| Data bits    | 8                |
| Parity       | Even             |
| Stop bits    | 1                |
| Termination  | 120 Ω (enable on last device in chain) |

**Bus topology:**

```
WAGO 750-826 ──── cable ──── Siemens V20 (addr 1) ──── cable ──── Nanotec C5-E (addr 2)
                                                                    [120Ω termination here]
```

---

## Modbus Register Maps

### Siemens V20 VFD — Slave Address 1

Standard Modbus PKW + PZD interface (enable via P0700=5, P1000=5).

| Register (0-based) | Name            | R/W | Scale       | Description                    |
|--------------------|-----------------|-----|-------------|--------------------------------|
| 100                | STW1            | W   | —           | Control word (see table below) |
| 101                | HSW             | W   | ×100 Hz     | Frequency setpoint             |
| 110                | ZSW1            | R   | —           | Status word                    |
| 111                | HIW             | R   | ×100 Hz     | Actual output frequency        |
| 112                | Current actual  | R   | ×10 A       | Output current                 |

**STW1 Control Words:**

| Value    | Meaning                                              |
|----------|------------------------------------------------------|
| `0x047F` | Start (ON + no OFF2 + no OFF3 + operation enabled)   |
| `0x047E` | OFF1 — normal stop, ramp via P1121 (3s)              |
| `0x047B` | **OFF3 — fast stop, ramp via P1135 (0.3s) + DC brake** |
| `0x04FE` | Fault reset                                          |

**V20 Parameter Settings for Fast Stop:**

| Parameter | Value | Meaning                            |
|-----------|-------|------------------------------------|
| P1135     | 0.3 s | OFF3 ramp-down time                |
| P1232     | 100 % | DC braking current (% rated)       |
| P1233     | 0.5 s | DC braking duration after ramp     |
| P1121     | 3.0 s | OFF1 normal ramp-down              |
| P1120     | 5.0 s | Ramp-up time                       |

Expected stop time from 100 Hz: **200–400 ms** with OFF3 + DC braking.

### Nanotec C5-E Hub Driver — Slave Address 2 (CiA 402 via Modbus)

| Register (hex) | Name                  | R/W | Description                          |
|----------------|-----------------------|-----|--------------------------------------|
| 6040h          | Controlword           | W   | CiA 402 state machine control        |
| 6041h          | Statusword            | R   | CiA 402 state machine status         |
| 60FFh          | Target velocity       | W   | Signed integer, rpm                  |
| 6064h          | Position actual value | R   | 32-bit signed, encoder counts        |
| 6060h          | Modes of operation    | W   | 3 = velocity mode                    |

**CiA 402 Control Words:**

| Value    | Meaning              |
|----------|----------------------|
| `0x0006` | Shutdown             |
| `0x000F` | Switch on + enable   |
| `0x000B` | Quick stop           |
| `0x0080` | Fault reset          |

---

## Stopping Logic: Sonic Head

The two stopping modes are fundamentally different and must never be confused:

| Mode         | Trigger                    | VFD Command | Ramp   | Stop Time |
|--------------|----------------------------|-------------|--------|-----------|
| Normal stop  | End of cycle (target depth) | OFF1 `0x047E` | P1121 3s | ~3–5 s |
| **Fast stop** | Stone / E-Stop / Safety    | **OFF3 `0x047B`** | P1135 0.3s + DC brake | **~200–400 ms** |

**Hub retract interlock:** `FB_HubControl` state 4 (`STOP_SONIC`) holds the hub with brake engaged until `FB_SonicHead.xConfirmedStopped = TRUE`. This flag is set only after:
1. VFD reports `xRunning = FALSE` (ZSW1 bit 2 = 0), **AND**
2. Standstill confirmed for 200 ms continuous.

Bypassing this interlock is not possible by design — the hub retract state (5) is only reachable from state 4, which requires `xConfirmedStopped`.

---

## SE050 / RDDL Trust Wallet Integration

For VM0042-compliant data provenance, each sampling cycle is cryptographically signed using the **NXP SE050** secure element.

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

**Data flow:**

1. `FB_DataLogger` assembles JSON payload with `"sign_pending": true` at cycle completion.
2. Payload sent over WAGO COM1 to ESP32-C3 (JSON line, LF-terminated).
3. ESP32-C3 extracts the payload, calls SE050 to sign with secp256k1 private key.
4. ESP32-C3 appends `"signature"` and `"pubkey"` fields and publishes to RDDL via MQTT over WiFi.
5. RDDL records data on Planetmint for immutable VM0042 audit trail.

**GPS data source:** ESP32-C3 also receives NMEA from the drill-head GPS antenna (u-blox ZED-F9P in RTK mode) and pushes `{"lat": …, "lon": …, "fix": "RTK"}` to WAGO every 1 s over the same COM1 UART. `FB_DataLogger` reads these variables and includes them in each cycle record.

---

## Mobile Connectivity — Teltonika RUT241

For field use the WAGO PFC200 needs LTE connectivity for:
- Remote CODESYS debugging (CODESYS Gateway over VPN)
- OTA firmware updates (CODESYS Online Change)
- MQTT data upload to RDDL/cloud (backup path if WiFi unavailable)

**Selected router: Teltonika RUT241** (DIN-rail mountable, IP30, −40 °C to +75 °C, Cat4 LTE)

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

**RUT241 configuration:**
- WAN: SIM card (data-only SIM, e.g. Teltonika Mobile, 1 GB/month sufficient)
- LAN: static IP 192.168.1.1 gateway, WAGO on 192.168.1.10
- VPN: WireGuard tunnel to developer workstation for remote access
- Firewall: only outbound MQTT (port 1883/8883) and WireGuard (UDP 51820) open

**Power:** 9–30V DC input — powered from 24V rail via step-down, draws ~3W.

Alternative for better cellular coverage: **Teltonika TRB140** (mPCIe form factor, fits
inside the Rittal IP65 enclosure) or **RUT956** if dual-SIM redundancy is needed.

---

## Braking Energy Analysis — Why No External Resistor is Needed

During OFF3 fast stop, the kinetic energy of the two OLI MVE 400/6-HF rotors
must be dissipated. The question is whether an external braking resistor is needed.

### Energy calculation

```
Per motor:
  I (moment of inertia) ≈ m_eccentric × r² = 0.5 kg × (0.02 m)² = 0.0002 kg·m²
  ω = 6000 RPM = 628 rad/s
  E_kin = ½ × I × ω² = ½ × 0.0002 × 628² ≈ 39 J

Both motors: E_total ≈ 80 J
```

### Dissipation path: DC injection braking (P1232 = 100%)

After the 0.3s ramp-down (P1135), the V20 applies 100% rated current as DC to
the stator. The energy is converted to heat **in the motor windings**:

```
Motor thermal mass: m = 7.2 kg, c ≈ 450 J/(kg·°C)
ΔT per stop = E / (m × c) = 39 / (7200 × 0.45) = 0.012 °C per motor
```

At 100 stops/day: **1.2 °C cumulative temperature rise**. This is negligible
relative to the motor's thermal rating and continuous self-cooling.

### DC bus overvoltage risk during the ramp phase

During the 0.3s ramp from 100 Hz to 0, the motor briefly regenerates energy
back into the V20's DC bus. The V20 handles this via:

| V20 Parameter | Value | Effect |
|---------------|-------|--------|
| P1240 | 1 (ON) | Vdc-max controller — auto-extends ramp if bus voltage rises |
| P1135 | 0.3 s | OFF3 ramp time (0.3s is aggressive; increase to 0.5s if bus trips) |
| P1232 | 100 % | DC braking current after ramp |
| P1233 | 0.5 s | DC braking duration |

**With P1240 = 1 active:** if the DC bus voltage approaches the trip threshold
during the ramp, the V20 automatically extends the deceleration ramp. The motor
still stops much faster than OFF1 (3s), but avoids a "DC link overvoltage" fault.

### Decision: no external braking resistor in V1

| Option | Cost | Complexity | Needed? |
|--------|------|------------|---------|
| DC injection braking (P1232=100%) | €0 | None | ✅ Default |
| Increase P1135 to 0.5s if trips | €0 | None | If needed |
| V20 external braking resistor module | ~€80 | Wiring | Only if P1240 doesn't help |

**Recommendation for commissioning:** start with P1135 = 0.3s and P1240 = 1.
If DC bus overvoltage trips occur during fast stops in the field, increase P1135
to 0.5s. An external braking resistor is not expected to be necessary.

---

## Development Environment

### CODESYS V3.5 (WAGO PFC200 target)

- Download: [CODESYS Store](https://store.codesys.com) — free runtime for WAGO PFC
- WAGO Extension: **WAGO-I/O-PRO** or **CODESYS for WAGO** package
- Required libraries:
  - `WagoAppModbusMasterRtu` ≥ 1.1.0.0
  - `WagoAppModbusSlaveTcp` (optional, for HMI Modbus access)
  - `WagoSysTimeRtc` (for timestamp in DataLogger)
- Target: WAGO PFC200 XTR (Arm Linux)
- Programming: Structured Text (ST), IEC 61131-3

### Running on Mac (no Windows required)

Option A — UTM virtual machine (recommended):
```bash
# Install UTM from https://mac.getutm.app
# Create Windows 11 ARM VM (free via Azure Dev) or Windows 10 x86 via Rosetta
# Install CODESYS V3.5 in the VM
# Connect to WAGO PFC via WAGO USB-Service-Cable or Ethernet
```

Option B — Python / Node-RED directly on PFC Linux:
```bash
# SSH into PFC200 (default: admin / wago)
ssh admin@192.168.1.1

# Install Node-RED
npm install -g node-red

# Use node-red-contrib-modbus for VFD/hub control
# Use node-red-contrib-mqtt for cloud publishing
# Vibrocore logic: firmware/python/ (future — see README)
```

Option C — Cloud VM:
- AWS EC2 t3.small (Windows Server) — ~$15/month
- Install CODESYS V3.5, connect to WAGO via VPN (WAGO VPN client on PFC)
- OTA updates via CODESYS Online Change or WAGO Web-Based-Management

---

## Remote Access and OTA Updates

The WAGO PFC200 provides built-in remote access:

| Feature | Method | URL / Config |
|---------|--------|--------------|
| Web UI | HTTP | `http://192.168.1.1` |
| SSH | OpenSSH | `ssh admin@192.168.1.1` |
| VPN | OpenVPN / WireGuard | Configure in WBM |
| CODESYS Online | TCP/IP | Port 1740 (CODESYS Gateway) |
| OTA firmware | CODESYS Online Change | No service stop required |
| MQTT broker | Mosquitto | Pre-installed on PFC Linux |
| Node-RED | HTTP | `http://192.168.1.1:1880` |

For field use on mobile LTE: the **Teltonika RUT241** provides the LTE uplink and
WireGuard VPN — the WAGO PFC connects as LAN client, developer connects from anywhere.
See the [Mobile Connectivity section](#mobile-connectivity--teltonika-rut241) above.
