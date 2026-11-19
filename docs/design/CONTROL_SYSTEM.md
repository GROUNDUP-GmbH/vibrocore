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
  │    1.5 kW   │◄──────────────►│  SDR-480-48       │
  │    VFD      │  RS-485        │  48V/10A DC PSU   │
  └──────┬──────┘ Slave addr 1   └────────┬──────────┘
         │ 3× AC                          │ 48V DC
         ▼                       ┌────────┴──────────┐
  ┌─────────────┐                │  Mean Well         │
  │ 2× OLI MVE │                │  SDR-120-24 (V1.1) │
  │ 400/6-HF   │                │  230V to 24V/5A    │
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
| DO 3    | `xAlarmBeacon`   | HIGH   | VC-CT-6230, 24 V, current at or below 0.5 A |

### Slot 3 — 750-637: Incremental Encoder Interface

| Parameter | Value                                |
|-----------|--------------------------------------|
| Encoder   | 1000 ppr quadrature. VC-HB-3410 is specified on the chain shaft. |
| Register  | `%IW4` (low word) + `%IW5` (high word). FB_HubControl does not read these words. |
| Scale     | `rENCODER_PULSES_PER_MM` stays 671.9. Do not change it in this revision. |
| Zero      | Set in Nanotec C5-E on home (upper limit) |

671.9 equals (1000 x 4 x 40) / (15 x 15.875). The factor 40 is the gearbox ratio.
That scale fits an encoder on the motor shaft.
A chain-shaft encoder at 1000 ppr is (1000 x 4) / (15 x 15.875) = 16.80 counts per mm.
The hub position in firmware comes from the C5-E Modbus word, divided by 671.9.
The chain-shaft encoder is the 750-637 input. The two scales are not the same.
Do not retune 671.9 until one encoder location is chosen.

### Slot 4 — 750-826: RS-485 Modbus RTU

| Parameter    | Value            |
|--------------|------------------|
| Baud rate    | 9600             |
| Data bits    | 8                |
| Parity       | Even             |
| Stop bits    | 1                |
| Termination  | 120 Ω (enable on last device in chain) |

**Bus topology (V1.1 — with penetrometer ADC):**

```
WAGO 750-826 ── Siemens V20 (addr 1) ── Nanotec C5-E (addr 2) ── Force ADC (addr 3)
                                                                   [120Ω term. here]
```

---

## V1.1 I/O Expansion: Lift, Tilt, Penetrometer

When subsystems §8a–8c from the BOM are added, the following I/O slots are required.

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

> **Wiring note:** `xLiftExtend` and `xLiftRetract` must never be TRUE simultaneously
> (mutual interlock in CODESYS). Same applies to `xTiltVertical` / `xTiltFold`.
> Both pairs drive an H-bridge relay module (one per actuator group).

#### Slot 8 (existing 750-600 moves here): End module

#### Penetrometer — RS-485 Slave 3 (no new WAGO slot needed)

The force ADC (Datexel DAT8017-A or equivalent) connects to the existing RS-485 bus
as Slave address 3. Holding Register 0 = force in raw counts (0–65535 → 0–5 kN).

```
rForce_raw := ModbusRead(uSlaveAddr := 3, uRegAddr := 0);
rForce_N   := REAL_TO_INT(rForce_raw) / 13.107;  // 0..65535 → 0..5000 N
```

---

### RevPi V1.1 — No Additional I/O Modules Required

The RevPi DIO module has 14 DI and 14 DO. After base system and V1.1 additions:

| Signals | Base (V1) | +V1.1 | Total used | DIO capacity |
|---------|-----------|--------|------------|--------------|
| DI (digital in) | 6 (4 limits + 2 encoder) | +4 (actuator limits) | **10** | 14 ✓ |
| DO (digital out) | 4 | +4 (actuator control) | **8** | 14 ✓ |

RevPi only needs the **PSU upgrade** (SDR-120-24) for actuator current.
The penetrometer ADC connects as RS-485 Slave 3 on the built-in RS-485 port.

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

**Selected router: Teltonika RUT241** (DIN-rail mountable, IP30, −40 °C to +75 °C, Cat4 LTE).

The RUT241 input is 9–30 V DC and the draw is below 6.5 W.
Power it from the 24 V rail. Do not fit a 24 V to 9 V converter.

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

## Operator HMI — Docker Stack on PFC200 XTR

The PFC200 XTR (Firmware ≥ 23) has Docker built-in.
Two containers run alongside the CODESYS Runtime:

```
WAGO PFC200 XTR (192.168.1.10)
├── CODESYS Runtime  → Modbus TCP Slave (port 502)
└── Docker
    ├── vibrocore-hmi   (Node-RED + Dashboard  → port 1880)
    └── vibrocore-mqtt  (Mosquitto MQTT broker  → port 1883)
```

**Resource budget:** ~45 MB RAM + < 5% CPU idle — well within 512 MB / 1 GHz headroom.

### Dashboard screens

| Tab | Content |
|-----|---------|
| Betrieb | Cycle Start, Fault Reset, Jog Up/Down, depth/freq sliders, live gauges |
| Status | State machine text (System / Hub / Sonic), safety reason, trend charts |
| Protokoll | Per-cycle log table (depth, freq, GPS, signed flag) |

Node-RED polls CODESYS every **500 ms** via Modbus TCP (FC3 read, registers 0–21).
HMI write commands (buttons, sliders) use FC6/FC16 on the same registers.

See `firmware/docker/` for the full stack and `firmware/docker/README.md` for setup.

### Modbus TCP Slave configuration in CODESYS

1. Device Tree → Add Device → `Modbus TCP Slave` (WagoAppModbusSlaveTcp)
2. Port: 502, Unit ID: 1
3. Map `%MW0..%MW21` per `firmware/codesys/GVL_MODBUS.st`

---

## Development Environment

### CODESYS V3.5 (WAGO PFC200 target)

- Download: [CODESYS Store](https://store.codesys.com) — free runtime for WAGO PFC
- WAGO Extension: **WAGO-I/O-PRO** or **CODESYS for WAGO** package
- Required libraries:
  - `WagoAppModbusMasterRtu` ≥ 1.1.0.0
  - `WagoAppModbusSlaveTcp` (HMI Modbus TCP Slave interface)
  - `WagoSysTimeRtc` (timestamp in DataLogger)
- Target: WAGO PFC200 XTR (Arm Linux)
- Programming: Structured Text (ST), IEC 61131-3

**Note on CODESYS Go:** CODESYS Go is a browser-based IDE (edit + deploy), not an
HMI app. It is used to write and deploy ST code to the PFC from any browser —
useful when a Windows VM is not available. It is **not** the operator dashboard.

### Running on Mac (no Windows required)

Option A — UTM virtual machine (recommended for full IDE comfort):
```bash
# Install UTM from https://mac.getutm.app
# Create Windows 11 ARM VM (free via Azure Dev) or Windows 10 x86 via Rosetta
# Install CODESYS V3.5 in the VM
# Connect to WAGO PFC via WAGO USB-Service-Cable or Ethernet/VPN
```

Option B — CODESYS Go (browser-based, no VM needed):
```
# Open: https://go.codesys.com
# Target: WAGO PFC200 (IP: 192.168.1.10, port 1740)
# Full ST editor + online debugging in any Chromium browser
```

Option C — Cloud VM:
- AWS EC2 t3.small (Windows Server) — ~$15/month
- Install CODESYS V3.5, connect to WAGO via WireGuard VPN
- OTA updates via CODESYS Online Change

---

## Remote Access and OTA Updates

The WAGO PFC200 provides built-in remote access:

| Feature | Method | URL / Config |
|---------|--------|--------------|
| Web UI | HTTP | `http://192.168.1.10` |
| SSH | OpenSSH | `ssh admin@192.168.1.10` |
| VPN | OpenVPN / WireGuard | Configure in WBM |
| CODESYS Online | TCP/IP | Port 1740 (CODESYS Gateway) |
| OTA firmware | CODESYS Online Change | No service stop required |
| MQTT broker | Mosquitto | Docker container (port 1883) |
| Node-RED | HTTP | `http://192.168.1.10:1880` |

For field use on mobile LTE: the **Teltonika RUT241** provides the LTE uplink and
WireGuard VPN — the WAGO PFC connects as LAN client, developer connects from anywhere.
See the [Mobile Connectivity section](#mobile-connectivity--teltonika-rut241) above.

---

## Controller Comparison: WAGO PFC200 XTR vs. Revolution Pi Connect 4

Two viable controller options exist for Vibrocore V1. The WAGO is the primary
recommendation for production; the RevPi Connect 4 is a lower-cost alternative
well-suited for prototyping or cost-sensitive builds.

### Hardware comparison

| Feature | WAGO PFC200 XTR (750-8212) | RevPi Connect 4 |
|---------|---------------------------|-----------------|
| CPU | 1 GHz ARM Cortex-A8 (single) | 1.5 GHz Quad-Core Cortex-A72 |
| RAM | 512 MB DDR3 | 2 / 4 / 8 GB LPDDR4 |
| Flash | 4 GB eMMC | 8 / 32 GB eMMC |
| **Temp range** | **−40 °C … +70 °C** | −25 °C … +55 °C |
| **Vibration** | **5g (EN 60068-2-6)** | EN 61131-2 (less explicit) |
| RS-485 | Via 750-826 module | **Built-in** (4-pin screw) |
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
| Encoder (quadrature) | 750-637 (€100–150) | **RevPi DIO** (built-in counter/encoder mode) |
| RS-485 Modbus RTU | 750-826 (€80–120) | **Built into Connect 4 base** |
| End module | 750-600 (€10–20) | Not required |
| **I/O total** | **€310–470** (4 modules) | **€196** (1× RevPi DIO) |

The RevPi DIO (€196) replaces four WAGO modules in one unit because its 14 DI
channels are individually configurable as digital input, counter, or **quadrature
encoder** — sufficient for the 1000 ppr chain encoder at max ~10 kHz count rate.

### Controller cost summary

| Item | WAGO Option A | RevPi Option B |
|------|--------------|----------------|
| Base controller | €600–900 | ~€450 (Connect 4 4 GB + RAM surcharge) |
| I/O modules | €310–470 | €196 (1× DIO) |
| **Controller subtotal** | **€910–1,370** | **~€646** |
| Savings vs. WAGO | — | **~€270–720** |

### Decision guidance

Use **WAGO PFC200 XTR** when:
- Ambient temperature may drop below −25 °C (e.g., Eastern European winter storage)
- Maximum vibration resistance is required (drilling in rocky, high-vibration terrain)
- Dedicated CODESYS Runtime timing guarantees are needed
- Long-term industrial support contracts are required

Use **RevPi Connect 4** when:
- Cost is a primary constraint (saves ~€300–500 on controller alone)
- More RAM/CPU for edge computing or data logging is beneficial
- The control enclosure can be kept above −25 °C (standard field conditions)
- Full Linux flexibility (Python, Node-RED, Docker) without any Windows dependency
- V1 prototype / proof-of-concept phase

> **Temperature note:** Hungarian/Austrian field conditions rarely drop below −25 °C
> during active drilling season (March–November). However, equipment stored outdoors
> overnight in January can reach −20 °C. If the enclosure is insulated or heated
> (self-adhesive heater strip, €15), the RevPi remains in spec. The WAGO's −40 °C
> rating provides comfort margin without any mitigation.

### RevPi-specific software notes

The RevPi ships with **Raspberry Pi OS** (Debian-based). No Windows toolchain
is needed at any stage:

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

The Docker Compose stack in `firmware/docker/` runs identically on RevPi (also arm/v8).
Change the platform tag in `docker-compose.yml`:

```yaml
platform: linux/arm/v8   # RevPi Connect 4 (CM4 = armv8)
# platform: linux/arm/v7  # WAGO PFC200 XTR (Cortex-A8 = armv7)
```
