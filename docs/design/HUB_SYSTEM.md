# Hub System — Design Document

## 1. Purpose

The hub system gives you controlled motion that is vertical and linear for the tasks below.
- The hub pushes the sonic head and the DT325 rod into the ground and vibration helps.
- The hub pulls the probe rod out of the ground after sampling and vibration is OFF.
- The hub parks the head at the top of the mast for transport.

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

1. The chain is an endless loop and the carriage attaches at one point.
Motor CW moves the carriage down and motor CCW moves the carriage up.
2. The motor at the bottom keeps the center of gravity low.
The plate of steel carries the motor and the weight of the gearbox.
3. The drive sprocket at the bottom joins the chain shaft to the gearbox output.
4. The idle sprocket at the top uses the spring-loaded tensioner for slack in the chain.
5. The linear guides on the front let the carriage slide on two rails of the aluminum mast.

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
| Chain type             | 10B-2 duplex roller chain          |
| Pitch                  | 15.875 mm (5/8″)                  |
| Breaking load          | ~44.5 kN (10B-2)                  |
| Working load (10:1 SF) | ~4.5 kN                           |
| Sprocket (drive)       | 10B-2, 15 teeth, taper-lock bore   |
| Sprocket (idle)        | 10B-2, 15 teeth, bearing-mounted   |
| Chain length           | ~3.2 m (for 1.5 m stroke + wrap)   |
| Lubrication            | Pre-greased + periodic oil          |

### 3.4 Drive Shaft (Separate from Gearbox Output)

The gearbox output connects to a drive shaft and the shaft has its own mounts.
The connection is an elastomer coupler.
This shaft carries the drive sprocket.
Two ball races support the shaft and the races align by themselves in pillow blocks on the base plate.

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Shaft diameter         | 25–30 mm                           |
| Coupling               | KTR ROTEX 28, 1:1, on the chain shaft |
| Bearings               | UCP 205/206 pillow blocks          |
| Sprocket mount         | Taper-lock bush                    |

The sprocket of the chain applies the radial load.
- That load would damage the output races of the gearbox if the sprocket sits on the gearbox.
The separate shaft takes these loads.
The coupler is 1 to 1.
There is no gear stage between the output of the PLE120 and the chain shaft.

## 4. Force Analysis

The allowable pull force is 4.5 kN.
The calculation is in [PULL_FORCE.md](../engineering/PULL_FORCE.md).
Do not use 14.3 kN.
- That figure is the tension from the motor times the ratio and the gearbox cannot deliver it.

### 4.1 Allowable pull force

The service load of the chain is about 4.5 kN.
The pull at the limit of drive torque is about 5.83 kN.
See the note in LIFT-DRIVE-SIZING.md and in the PULL_FORCE.md.
The allowable pull force is the lower value, 4.5 kN.

### 4.2 Required Forces

| Operation            | Force Needed | Notes                              |
|----------------------|-------------|------------------------------------|
| Push-in (vibration ON) | 0.5–1.5 kN | Vibration does most of the work   |
| Pull-out (required)  | 2.0–4.0 kN  | Process need. Not the drive capacity. |
| Head weight hold     | ~0.3 kN     | Static, when parked                |
| Emergency stop       | —           | Brake engages, motor de-energised  |

The margin on the upper required pull is 4.5 / 4.0 = 1.13.
That margin is small and the note explains it.
- A speed of about 60 mm/s meets the need.

### 4.3 Speed

```
Motor max speed:                   600 rpm (practical for closed-loop)
Gearbox ratio:                     40:1
→ Output shaft speed:              600 / 40 = 15 rpm
→ Sprocket circumference:          2π × 38.18 mm = 239.89 mm
→ Chain linear speed:              15 × 239.89 = 3,598 mm/min ≈ 60.0 mm/s
```

Penetration is typically 10 to 30 mm/s with vibration.
Retraction can use full speed.

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

- Use a steel plate of 10 mm and machine that plate.
- Use 4 slider blocks and put 2 blocks on each rail.
- Bolt the chain at one point with a hardened pin.
- Fit mounts of rubber for the sonic head and the count is 4 of size M12.
- Leave a through hole for the center column and for the rod DT325.

## 6. Brake System

The motor brake is the brake inside the Siemens motor.
VC-HB-3000 is obsolete and it is not in the machine.

| Parameter          | Value                              |
|--------------------|------------------------------------|
| Type               | 24 V DC spring-applied, in the motor |
| Holding torque     | 3.3 Nm on the motor shaft          |
| At the gearbox output, i = 40 | 132 Nm                    |
| Chain force        | about 3.5 kN                       |
| Control            | SINAMICS S200 brake output         |

A separate brake of 16 Nm would put the torque of 640 Nm on the gearbox output.
The stop torque T2Stop of the PLE120 at this ratio is 500 Nm.
That brake can go above the stop torque of the gearbox.
Do not fit it.
- The brake of 3.3 Nm holds the weight with margin.
It does not hold the full force of pull-out.
If power fails in the pull-out, the carriage can slide down onto the casing.
The load then moves toward the ground.
That case is an item for risk assessment and the file is LIFT-DRIVE-SIZING.md.

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

The SINAMICS S200 provides the current of the lift motor.
The VFD also monitors current on the sonic motor and the two signals together give the second path for obstacle detection.
- The CL86T and the Nanotec C5-E are not the hub drive.

## 8. Controller Integration

The selected hub drive is the SINAMICS S200 and the order is 6SL5510-1BB11-0AA0.
In the diagram below, the names CL86T and Nanotec C5-E still appear.
Those names are the previous driver for the stepper.
The pin table is not a released wire list for the S200.

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



References: the file LIFT-DRIVE-SIZING.md, the Neugart PLE catalogue of 2026-10, the datasheet for the Siemens 1FL2104, and DIN 8187 for 10B chains.
