# Hub System — Design Document

## 1. Purpose

The hub system provides controlled **vertical linear motion** for:
- Pushing the sonic head + DT325 probe rod into the ground (assisted by vibration)
- Pulling the probe rod out of the ground after sampling (vibration OFF)
- Parking the head at the top of the mast for transport

## 2. Architecture

```
    TOP OF MAST
    ┌──────────────────┐
    │  Upper sprocket   │ ← idle (bearing-mounted, no drive)
    │     ┌───┐         │
    │     │ ○ │         │
    │     └─┬─┘         │
    │       │ chain      │
    │       │ (2 runs)   │   ┌──────────────┐
    │ ┌─────┤            │   │  CARRIAGE     │
    │ │     │ ◄──────────│───│  (slider)     │
    │ │     │            │   │  holds sonic  │
    │ │     │            │   │  head via     │
    │ │     │            │   │  isolators    │
    │ │     │            │   └──────────────┘
    │ │     │            │
    │       │            │
    │     └─┬─┘         │
    │     │ ○ │         │   ← drive sprocket
    │     └───┘         │
    │  Lower sprocket   │
    │     ↑              │
    │  GEARBOX + MOTOR  │
    │  (1FL2104 + PLE)  │
    └──────────────────┘
    BOTTOM OF MAST (Steel base plate)
```

### Key Design Decisions

1. **Endless chain loop** — the carriage is attached to one point on the chain.
   Motor CW → carriage down, Motor CCW → carriage up.
2. **Motor at bottom** — keeps center of gravity low; steel base plate carries motor + gearbox weight.
3. **Drive sprocket at bottom** — directly coupled via chain shaft to gearbox output.
4. **Idle sprocket at top** — spring-loaded tensioner for chain slack compensation.
5. **Linear guides on front** — the carriage slides on two profiled rails mounted to the aluminum mast.

## 3. Motor & Drive Train

### 3.1 Siemens 1FL2104 servo

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Type                   | 1FL2104-4AG11-1MC0                 |
| Rated / maximum torque | 3.2 Nm / 10.8 Nm                   |
| Rated speed / power    | 3000 rpm / 1 kW                    |
| Supply                 | 230 V 1~ with SINAMICS S200        |
| Drive                  | 6SL5510-1BB11-0AA0, cabinet item   |
| Encoder                | Absolute multiturn                 |
| Shaft                  | 19 mm × 40 mm, with key            |
| Flange                 | 81 mm square, centering 70 mm      |
| Holding brake          | 3.3 Nm, built into the motor       |
| Mass                   | about 4.1 kg                       |

The sizing and the torque limit are in [LIFT-DRIVE-SIZING.md](../engineering/LIFT-DRIVE-SIZING.md).

### 3.2 Planetary Gearbox

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Model                  | Neugart PLE120, i = 40             |
| Article                | 100460948                          |
| Type code              | PLE120-040-SSSA3AF-Z19/40/70/90/B5/M6 |
| Continuous torque T2D  | 195 Nm                             |
| Cyclic torque T2Z      | 230 Nm                             |
| Maximum torque T2max   | 365 Nm                             |
| Emergency stop T2Stop  | 500 Nm                             |
| Output shaft           | Ø25 h7 × 55 mm, key 8×7×40         |
| Output pilot           | Ø80 h7                             |
| Housing / flange edge  | 115 mm square                      |
| Total length           | 204 mm (47.5 + 101.5 + 55)         |
| Mass                   | 7.65 kg                            |

### 3.3 Chain Drive

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Chain type             | G&G 600-302-0000, 10B-2 duplex     |
| Connecting link        | G&G 600-302-0001                   |
| Pitch                  | 15.875 mm (ISO 606)                |
| Roller / inner width   | 10.16 mm / 9.65 mm                 |
| Transverse pitch       | 16.59 mm                           |
| Breaking load          | Not stated by G&G. Open point.     |
| Working load           | 4.5 kN                             |
| Sprocket (drive)       | G&G 501-302-0515, 10B-2, 15 teeth  |
| Sprocket (idle)        | Same solid, bearing-mounted        |
| Tensioner              | G&G 681-302-1504, range 36–57 mm   |
| Chain length           | 3.2 m placeholder until lift height |
| Lubrication            | Pre-greased + periodic oil          |

### 3.4 Drive Shaft (Separate from Gearbox Output)

The gearbox output connects to a **separately mounted drive shaft** via an
elastomer coupling. This shaft carries the drive sprocket and is supported by
two self-aligning ball bearings in pillow blocks bolted to the base plate.

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Shaft diameter         | 25–30 mm                           |
| Coupling               | R+W EKH / KTR ROTEX 28            |
| Bearings               | UCP 205/206 pillow blocks          |
| Sprocket mount         | Taper-lock bush                    |

**Rationale:** The chain sprocket applies radial loads that would damage the
gearbox output bearings if directly mounted. The separate shaft absorbs these loads.

## 4. Force Analysis

The allowable pull force is **4.5 kN**.
The calculation is in [PULL_FORCE.md](../engineering/PULL_FORCE.md).
Do not use 14.3 kN. That figure is the motor-times-ratio tension. The gearbox cannot deliver it.

### 4.1 Allowable pull force

The chain working load is about 4.5 kN.
The gearbox nominal tension is 5.80 kN.
The allowable pull force is the lower value, 4.5 kN.

### 4.2 Required Forces

| Operation            | Force Needed | Notes                              |
|----------------------|-------------|------------------------------------|
| Push-in (vibration ON) | 0.5–1.5 kN | Vibration does most of the work   |
| Pull-out (required)  | 2.0–4.0 kN  | Process need. Not the drive capacity. |
| Head weight hold     | ~0.3 kN     | Static, when parked                |
| Emergency stop       | —           | Brake engages, motor de-energised  |

Margin on the upper required pull: 4.5 / 4.0 = 1.13.
That margin is small. See the note.

### 4.3 Speed

```
Motor max speed:                   600 rpm (practical for closed-loop)
Gearbox ratio:                     40:1
→ Output shaft speed:              600 / 40 = 15 rpm
→ Sprocket circumference:          2π × 37.9 mm = 238 mm
→ Chain linear speed:              15 × 238 = 3,570 mm/min ≈ 59.5 mm/s
```

~60 mm/s is adequate for both penetration (typically 10–30 mm/s with vibration)
and retraction (full speed acceptable).

## 5. Carriage & Linear Guides

### 5.1 Linear Guide Rails

| Parameter          | Value                              |
|--------------------|------------------------------------|
| Type               | Profiled rail + ball bearing slider|
| Brand examples     | Hiwin HGR20 / Bosch Rexroth       |
| Rail length        | 1,300 mm (per side)                |
| Quantity           | 2 (left + right on front of mast)  |
| Load rating (dyn)  | > 15 kN per slider                 |

### 5.2 Carriage Plate

- 10 mm steel plate, machined
- 4× slider blocks (2 per rail)
- Chain attachment point (bolted, with hardened pin)
- 4× M12 rubber isolator mounts for sonic head
- Through-hole for center column / DT325 rod passage

## 6. Brake System

The holding brake is the brake built into the Siemens motor.
VC-HB-3000 is obsolete and is not in the machine.

| Parameter          | Value                              |
|--------------------|------------------------------------|
| Type               | 24 V DC spring-applied, in the motor |
| Holding torque     | 3.3 Nm on the motor shaft          |
| At the gearbox output, i = 40 | 132 Nm                    |
| Chain force        | about 3.5 kN                       |
| Control            | SINAMICS S200 brake output         |

A separate 16 Nm brake would put 640 Nm on the gearbox output.
PLE120 T2Stop at this ratio is 500 Nm.
That brake can exceed the gearbox stop torque.
Do not fit it.

The 3.3 Nm brake holds the weight with margin.
It does not hold the full pull-out force.
If power fails during pull-out, the carriage can slide down onto the casing.
The load then moves toward the ground.
That case is a risk-assessment item. See LIFT-DRIVE-SIZING.md.

## 7. Sensors & Safety

| Sensor / Device        | Location          | Function                         |
|------------------------|-------------------|----------------------------------|
| Upper limit switch     | Top of mast       | Prevent over-travel up           |
| Lower limit switch     | Bottom of mast    | Prevent over-travel down         |
| Depth encoder          | Motor encoder     | Track carriage position           |
| Current monitor        | Motor driver      | Detect stones / obstacles        |
| Emergency stop button  | Control panel     | Kill all motion, engage brake    |
| Chain tension switch   | Idle sprocket     | Detect chain break               |

### Stone Detection Algorithm

```
IF motor_current > threshold_current (e.g. 120% rated):
    IF sustained > 200 ms:
        → STOP drive
        → STOP sonic head
        → RETRACT 20 mm
        → ALERT operator
```

The closed-loop stepper driver (CL86T-V4.1 or Nanotec C5-E) provides current
feedback. Combined with VFD current monitoring on the sonic motor, this gives
redundant obstacle detection.

## 8. Controller Integration

```
                    ┌────────────────┐
                    │  MAIN PLC      │
                    │  (CONTROLLINO  │
                    │   or Arduino   │
                    │   Opta)        │
                    └──────┬─────────┘
                           │
          ┌────────────────┼───────────────┐
          │                │               │
  ┌───────┴───────┐  ┌────┴────┐   ┌──────┴──────┐
  │  HUB DRIVER   │  │  VFD    │   │  SAFETY     │
  │  (CL86T /     │  │  (Sonic │   │  (E-Stop,   │
  │   Nanotec)    │  │  Motor) │   │   Brake,    │
  │               │  │         │   │   Limits)   │
  │  STEP/DIR     │  │  Analog │   │  Digital I/O│
  │  + Encoder    │  │  + RS485│   │             │
  └───────────────┘  └─────────┘   └─────────────┘
```

### Step/Dir Interface (Hub Motor)

| Signal    | PLC Pin  | Driver Pin | Notes                     |
|-----------|----------|------------|---------------------------|
| STEP      | PWM out  | PUL+       | Frequency = speed          |
| DIR       | Digital  | DIR+       | HIGH = down, LOW = up      |
| ENABLE    | Digital  | ENA+       | Active LOW (enable motor)  |
| ALARM     | Input    | ALM        | Fault feedback             |

## 9. Operating Sequence

### Casing sampling cycle

```
1. POSITION  — Navigate to GPS waypoint (AR overlay on tablet)
2. PREPARE   — Lower machine to ground, deploy feet/stabilisers
3. ENGAGE    — Start sonic head at low frequency (70 Hz ramp)
4. PENETRATE — Hub drives carriage down at 10–20 mm/s
               Sonic ramps to optimal frequency (90–110 Hz)
               VFD auto-tunes based on current draw
5. DEPTH OK  — Encoder reports target depth reached
               → Stop hub drive
               → Stop sonic head (VFD ramp-down + DC brake)
6. EXTRACT   — Hub reverses, pulls rod out at 40–60 mm/s
               Sonic OFF (preserving core integrity)
7. PARK      — Carriage returns to upper limit
8. LOG       — GPS + depth + time + soil resistance → SD card / WLAN
```

---

*References: docs/engineering/LIFT-DRIVE-SIZING.md, Neugart PLE catalogue 2026-10, Siemens 1FL2104 datasheet, DIN 8187 (10B chains)*
