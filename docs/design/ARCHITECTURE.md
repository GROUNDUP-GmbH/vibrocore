# System Architecture

## Overview

The Vibrocore V1 consists of five major subsystems. V1.1 adds three optional
subsystems for full field-readiness: motorised deployment, penetrometry, and
core imaging. See `docs/engineering/BOM.md §8` for BOM and cost details.

```
┌──────────────────────────────────────────────────────────────────────┐
│                       VIBROCORE V1 / V1.1                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  1. SONIC HEAD   │  │  2. HUB      │  │  3. CONTROL SYSTEM     │ │
│  │                  │  │     SYSTEM   │  │                        │ │
│  │  2× OLI MVE      │  │  Linear      │  │  WAGO PFC200 XTR       │ │
│  │  400/6-HF        │  │  push/pull   │  │  OR RevPi Connect 4    │ │
│  │  @100 Hz, 8 kN   │  │  via chain   │  │  + V20 VFD + C5-E drv  │ │
│  └──────────────────┘  └──────────────┘  └────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  4. POWER SYSTEM                              │   │
│  │  Instagrid ONE max (230V AC) → S200 + inverter + two 24 V supplies │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  5. FRAME & MOBILITY                          │   │
│  │  mk 2004 Al-profile mast · steel base · UTV mount            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ╔══════════════════════════════════════════════════════════════╗   │
│  ║         V1.1 EXTENSIONS (optional, addable incrementally)    ║   │
│  ╠══════════════════════════════════════════════════════════════╣   │
│  ║  6. DEPLOYMENT SYSTEM         │  7. PENETROMETER             ║   │
│  ║  2× Lift actuator (400mm)     │  Load cell inline 0-5 kN     ║   │
│  ║  1× Tilt actuator (90° fold)  │  Force-displacement curve    ║   │
│  ║  PLC-controlled, 4 DI + 4 DO  │  via RS-485 ADC (Slave 3)   ║   │
│  ╠═══════════════════════════════╪══════════════════════════════╣   │
│  ║  8. CORE SCANNER (camera sled)                               ║   │
│  ║  RPi 4 + HQ Camera 12MP + GT2 belt sled                     ║   │
│  ║  Intact sealed liner → 1,200 frames → OpenCV stitch         ║   │
│  ║  L*a*b* color profile → horizon detection → JSON            ║   │
│  ║  ⚠ Liner NEVER split — bulk density sample goes to lab      ║   │
│  ╚══════════════════════════════════════════════════════════════╝   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Subsystem Interactions

```
       ┌─────────────────────────────┐
       │  Tablet / HMI (WLAN)        │  viDoc RTK AR navigation
       │  + viDoc RTK Light          │  GPS sample point targeting
       └──────────────┬──────────────┘
                      │ WLAN (WAGO REST API / MQTT)
       ┌──────────────▼──────────────────────────────┐
       │           WAGO PFC200 XTR                   │
       │      (CODESYS V3.5 / IEC 61131-3)           │
       │                                             │
       │  PRG_Main → FB_Safety                       │
       │           → FB_SonicHead                    │
       │           → FB_HubControl                   │
       │           → FB_DataLogger                   │
       └──────┬──────────────────┬───────────────────┘
              │ RS-485             │ RS-485
              │ Modbus RTU         │ Modbus RTU
              │ Slave addr 1       │ Slave addr 2
       ┌──────▼──────┐     ┌──────▼──────┐
       │ Siemens V20 │     │ SINAMICS    │
       │  VFD 1.5kW  │     │ S200        │
       │  OFF3 stop  │     │ 6SL5510     │
       └──────┬──────┘     └──────┬──────┘
              │ 3×AC               │ motor
              ▼                   ▼
       ┌─────────────┐     ┌─────────────────────┐
       │ 2× OLI MVE  │     │ Siemens 1FL2104      │
       │ 400/6-HF    │     │ + Neugart PLE120-040 │
       │ counter-rot.│     │ + ROTEX 28, 1:1      │
       │ 6000 RPM    │     │ + 10B-2 chain        │
       │ 8 kN total  │     └──────────┬──────────┘
       └──────┬──────┘                │
              │ vibration             │ linear push/pull
       ┌──────▼──────┐                │
       │ Vibrating   │                │
       │ plate       ◄────────────────┘
       │ (S355J2)    │   carriage holds sonic head
       └──────┬──────┘
              │ rubber isolators (4× M12, 70 Shore A)
       ┌──────▼──────┐
       │ Center      │
       │ column      │
       │ (42CrMo4)   │
       └──────┬──────┘
              │ threaded adapter
       ┌──────▼──────────────┐
       │ 3.25 in casing      │
       │ rod 201446 x 48 in  │
       │ + cutting shoe      │
       └─────────────────────┘
```

---

## Critical Interlock: Sonic → Hub

The most important safety/quality interlock in the system:

```
DRILLING state:
  Hub moves DOWN  ←→  Sonic RUNNING
        │
        ▼ (target depth OR stone OR lower limit)
        │
STOP_SONIC state:
  Hub BRAKE engaged
  Sonic fast-stop (OFF3) requested
  ↓
  WAIT: xSonicConfirmedStopped = TRUE
  (OLI motors confirmed at standstill for 200ms)
        │
        ▼
RETRACT state:
  Hub moves UP  ←  Sonic CONFIRMED stopped
```

**Rule:** The hub carriage CANNOT transition to the RETRACT state without
`FB_SonicHead.xConfirmedStopped = TRUE`. This is structural in the state
machine — there is no path from DRILLING directly to RETRACT.

Reason: OLI motors at 6000 RPM shaking the soil core during extraction would
cause the sample to fall out, destroying the density measurement.

---

## Data / Trust Layer

```
Sampling cycle complete
        │
        ▼
FB_DataLogger (WAGO PFC200)
  → assembles JSON payload
  → includes GPS coords, depth, freq, current, cycle ID
  → sends over COM1 (UART 115200) to:
        │
        ▼
Xiao ESP32-C3 (RDDL Trust Wallet)
  → receives JSON from WAGO
  → reads GPS fix (u-blox ZED-F9P on drill head, NMEA → RTK)
  → calls NXP SE050 (I2C) for secp256k1 signing
  → appends {"signature":…, "pubkey":…}
        │
        ▼
RDDL / Planetmint (via MQTT over WiFi/LTE)
  → immutable data notarization
  → VM0042 Section 6.2 data provenance compliance
```

---

## V1.1 Subsystem Integration

```
WAGO / RevPi (CODESYS / Python)
        │
        ├── RS-485 bus ────────────────────────────────────────────────
        │     Slave 1: Siemens V20 (VFD → OLI motors)
        │     Slave 2: Nanotec C5-E (Hub stepper driver)
        │     Slave 3: Force ADC (penetrometer, 50ms updates)  [V1.1]
        │
        ├── 4× DI (Slot 1) ─── Limit switches: hub up/down, E-Stop, alarm
        ├── 4× DO (Slot 2) ─── Brake, hub enable, VFD reset, alarm beacon
        ├── Position ── 1FL2 absolute encoder through the S200
        │                 VC-HB-3410 and 750-637 are obsolete
        │
        ├── 4× DI (Slot 5) ─── Lift deployed/retracted, Tilt vertical/folded  [V1.1]
        ├── 4× DO (Slot 6) ─── Lift extend/retract, Tilt vertical/fold         [V1.1]
        │
        └── MQTT (via Mosquitto Docker)
              │
              ├── vibrocore/cycle/{id}     ← FB_DataLogger payload + force array
              ├── vibrocore/alarm          ← Safety fault events
              ├── vibrocore/core_image/{id}← Raspberry Pi 4 camera JPEG  [V1.1]
              └── vibrocore/hmi/status     ← HMI online/offline

RPi 4 2GB (Core Scanner, autonomous)  [V1.1]
        │  WiFi → Teltonika RUT241
        │
        ├── MQTT subscribe: vibrocore/cycle/+ (receive cycle_id after drilling)
        │
        │   SAMPLE WORKFLOW: open tubes stay in the casing during driving.
        │   Caps go on after extraction. Tubes are a lab consumable, not a BOM line.
        │   The cradle opening follows the tube OD. That OD is TBD. See SAMPLING.md.
        │
        ├── Stepper control (NEMA 17 + A4988 via GPIO)
        │   Sled over the tube in the V-cradle
        │   Do not assume a clear polycarbonate wall
        │
        ├── RPi HQ Camera (12.3 MP, 5000K CRI≥97 LED at 45°)
        │   Through-wall colour correction is not confirmed
        │   Munsell tile stays available for a later calibration
        │
        ├── OpenCV linear mosaic stitching (1D, no feature matching)
        │   Output: ~82mm × 1,200mm composite JPEG at ~0.05mm/pixel
        │
        ├── L*a*b* color analysis per 1mm depth slice
        │   → Liner-corrected Munsell-calibrated color profile
        │   → Horizon boundary detection (ΔL* > 8 or Δa* > 3)
        │
        └── MQTT publish:
              vibrocore/core_scan/{cycle_id}    ← composite JPEG
              vibrocore/core_color/{cycle_id}   ← JSON color + horizons
```

## Detailed Design Documents

- [SONIC_HEAD.md](SONIC_HEAD.md) — 2× OLI MVE 400/6-HF vibration head design
- [HUB_SYSTEM.md](HUB_SYSTEM.md) — 1FL2104, Neugart PLE120-040, ROTEX 28, 10B-2 chain
- [CONTROL_SYSTEM.md](CONTROL_SYSTEM.md) — WAGO/RevPi, I/O mapping, Modbus, SE050, V1.1 expansion

## Firmware

- [firmware/codesys/PRG_Main.st](../../firmware/codesys/PRG_Main.st) — Main program
- [firmware/codesys/FB_SonicHead.st](../../firmware/codesys/FB_SonicHead.st) — Sonic state machine
- [firmware/codesys/FB_HubControl.st](../../firmware/codesys/FB_HubControl.st) — Hub state machine
- [firmware/codesys/FB_Safety.st](../../firmware/codesys/FB_Safety.st) — Safety monitor
- [firmware/codesys/FB_ModbusVFD.st](../../firmware/codesys/FB_ModbusVFD.st) — VFD Modbus
- [firmware/codesys/FB_DataLogger.st](../../firmware/codesys/FB_DataLogger.st) — RDDL data

## Engineering Calculations

- [DIMENSIONING.md](../engineering/DIMENSIONING.md) — Force, frequency, power, bearing life
- [BOM.md](../engineering/BOM.md) — Bill of materials with EU suppliers and prices
