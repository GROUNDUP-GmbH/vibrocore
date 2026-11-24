# System Architecture

## Overview

The Vibrocore V1 is a system with five subsystems.
V1.1 adds three optional subsystems for full field use.
These parts include deployment by motor and also penetrometry and core images.
See `docs/engineering/BOM.md §8` for the BOM and for the cost.

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
│  │  @100 Hz, 8 kN   │  │  via chain   │  │  + V20 VFD + S200 drv  │ │
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



## Critical Interlock: Sonic → Hub

This interlock has the top rank for safety and for quality in the system.

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

The hub must not move to the RETRACT state without `FB_SonicHead.xConfirmedStopped = TRUE`.

- The state machine has no direct path from DRILLING to RETRACT.
- OLI motors at 6000 RPM can shake the soil core during the pull-out.
- The sample can then fall out and the loss of the density result follows.



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



## V1.1 Subsystem Integration

```
WAGO / RevPi (CODESYS / Python)
        │
        ├── RS-485 bus ────────────────────────────────────────────────
        │     Slave 1: Siemens V20 (VFD → OLI motors)
        │     Slave 2: SINAMICS S200 (hub servo drive)
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

- Open the [SONIC_HEAD.md](SONIC_HEAD.md) for the vibration head design with 2× OLI MVE 400/6-HF.
- Open the [HUB_SYSTEM.md](HUB_SYSTEM.md) for the 1FL2104 and the Neugart PLE120-040 and the ROTEX 28 and the 10B-2 chain.
- See the [CONTROL_SYSTEM.md](CONTROL_SYSTEM.md) for WAGO and RevPi, the I/O mapping, Modbus, SE050 and the V1.1 expansion.

## Firmware

- See the [PRG_Main.st](../../firmware/codesys/PRG_Main.st) for the main program.
- See the [FB_SonicHead.st](../../firmware/codesys/FB_SonicHead.st) for the sonic state machine.
- See the [FB_HubControl.st](../../firmware/codesys/FB_HubControl.st) for the hub state machine.
- See the [FB_Safety.st](../../firmware/codesys/FB_Safety.st) for the safety monitor.
- See the [FB_ModbusVFD.st](../../firmware/codesys/FB_ModbusVFD.st) for the VFD on Modbus.
- See the [FB_DataLogger.st](../../firmware/codesys/FB_DataLogger.st) for the RDDL data.

## Engineering Calculations

- See [DIMENSIONING.md](../engineering/DIMENSIONING.md) for force, frequency, power, and bearing life.
- See the file [BOM.md](../engineering/BOM.md) for the bill of materials with the EU supply and the price.
