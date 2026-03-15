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
    │  (NEMA 42 + PLPE) │
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

### 3.1 NEMA 42 Closed-Loop Stepper

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Frame size             | NEMA 42 (110×110 mm)              |
| Holding torque         | 12–20 Nm (depending on model)      |
| Rated current          | 6–8 A per phase                    |
| Voltage                | 48–80 VDC (from battery or PSU)    |
| Encoder                | 1000-line incremental (built-in)   |
| Shaft                  | 19 mm with keyway                  |
| Mass                   | ~6–8 kg                            |

**Recommended models (EU-available):**
- Nanotec ST11018 series (Germany)
- Leadshine CS-M series + HBS86H driver
- StepperOnline 110HS / CL86T-V4.1 driver

### 3.2 Planetary Gearbox

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Model                  | Neugart PLPE120                    |
| Ratio                  | 40:1                               |
| Nominal output torque  | 220 Nm                             |
| Emergency torque       | 360 Nm                             |
| Max input speed        | 4,000 rpm                          |
| Output shaft           | 32 mm with keyway                  |
| Backlash               | < 8 arcmin                         |
| Mass                   | ~8 kg                              |

### 3.3 Chain Drive

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Chain type             | 10B-2 duplex roller chain          |
| Pitch                  | 15.875 mm (5/8″)                  |
| Breaking load          | ~44.5 kN (10B-2)                  |
| Working load (10:1 SF) | ~4.5 kN                           |
| Sprocket (drive)       | 10B-2, 15 teeth, taper-lock bore   |
| Sprocket (idle)        | 10B-2, 15 teeth, bearing-mounted   |
| Chain length           | ~3.2 m (for 1.5 m stroke + wrap)   |
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

### 4.1 Available Torque at Chain Sprocket

```
Motor torque (nominal):           ~15 Nm  (NEMA 42)
Gearbox ratio:                     40:1
Gearbox efficiency:                ~90%
→ Output torque (nominal):         15 × 40 × 0.90 = 540 Nm

Sprocket pitch radius (15T, 10B-2):
  R = (p × z) / (2π) = (15.875 × 15) / (2π) ≈ 37.9 mm

Chain force (nominal):
  F = T / R = 540 / 0.0379 ≈ 14,250 N ≈ 14.3 kN
```

### 4.2 Required Forces

| Operation            | Force Needed | Notes                              |
|----------------------|-------------|------------------------------------|
| Push-in (vibration ON) | 0.5–1.5 kN | Vibration does most of the work   |
| Pull-out             | 2.0–4.0 kN  | Full friction, no vibration        |
| Head weight hold     | ~0.3 kN     | Static, when parked                |
| Emergency stop       | —           | Brake engages, motor de-energised  |

**Safety factor:** 14.3 kN available / 4.0 kN max required = **3.6× margin** ✓

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

A **power-off electromagnetic brake** holds the carriage when:
- The motor is de-energised (gravity hold)
- Emergency stop is activated
- The system is in standby

| Parameter          | Value                              |
|--------------------|------------------------------------|
| Type               | 24 VDC spring-applied, EM release  |
| Holding torque     | > 15 Nm (on motor shaft)           |
| Mounting           | Between motor and gearbox          |
| Control            | Relay, released when motor enabled |

At 40:1 gearbox ratio, 15 Nm on motor shaft = 600 Nm effective = ~15.8 kN chain force.
This exceeds any static or dynamic load, ensuring the carriage cannot slip.

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

### DT325 Core Sampling Cycle

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

*References: Neugart PLPE120 datasheet, DIN 8187 (10B chains), Nanotec C5-E manual*
