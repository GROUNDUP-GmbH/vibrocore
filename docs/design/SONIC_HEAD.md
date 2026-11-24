# Sonic Head — Design Document (V2: OLI MVE 400/6-HF Dual Motor)

## 1. Operating Principle

The head sends waves of axial pressure along the rod for the drill.
It uses two OLI motors of type MVE 400/6-HF.
The motors turn in opposite directions on one rigid plate for vibration (Schwingplatte).
The eccentric shafts of the motors sit square to the axis of the rod.
The horizontal parts of the force cancel.
The vertical parts on the axis add and the sum is constructive.
- The force on the rod is a sine wave and it drives the rod into the soil.
- In each cycle the thin layer at the boundary becomes fluid, as Šporin and Vukelić show in 2017.

### Why OLI Vibration Motors?

| Advantage                        | Detail                                      |
|----------------------------------|----------------------------------------------|
| Purpose-built for vibration      | VPI windings, Class H insulation, IP65       |
| Heavy-duty bearings              | Designed for continuous eccentric loads       |
| No custom eccentrics needed      | Integrated adjustable eccentric weights       |
| Proven industrial technology     | Concrete, foundry, screening — millions sold  |
| Simplified construction          | No timing belts, custom shafts, or housings   |
| Self-synchronising               | Via shared rigid mass at identical VFD freq.  |
| EU-available, off-the-shelf      | OLI S.p.A. (IT) + extensive dealer network   |

### Why Perpendicular Shafts?

If the motor shafts are parallel to the axis of the rod, the centrifugal force sweeps in a plane square to the rod.
That motion is a lateral whip and it is not axial vibration.
With horizontal shafts, square to the rod axis, the vertical parts of the force add.
The sum gives the maximum amplitude on the axis.

```
  ROD AXIS (vertical)
       ↕
  ─────●─────  ← Motor A shaft (horizontal, CW)
       │
  ─────●─────  ← Motor B shaft (horizontal, CCW — 2 phases swapped)
       │
       ↓
    DT325 Rod
```

## 2. Motor Specification: OLI MVE 400/6-HF

### 2.1 Nameplate Data

| Parameter                | Value                | Notes                          |
|--------------------------|----------------------|--------------------------------|
| Model                    | OLI MVE 400/6-HF    | High-Frequency series          |
| Frame size (OLI)         | 20                   |                                |
| Poles                    | 6                    | Designed for VFD high-freq.    |
| Operating speed          | 6,000 rpm            | Via VFD at elevated frequency  |
| Centrifugal force        | 408 kgf (~4.0 kN)   | Per motor at 6,000 rpm         |
| Current draw             | ~1.45 A              | At 230V 3-phase via VFD       |
| Power (estimated)        | ~0.58 kW             | Per motor                      |
| Weight                   | 7.2 kg               | Per motor                      |
| Insulation class         | H (180°C)            | VPI vacuum-pressure impreg.    |
| Protection               | IP65                 | Dust/water-tight               |

### 2.2 Physical Dimensions

```
    SIDE VIEW (one motor)                TOP VIEW (one motor)

    ┌──────────────────────┐            ┌──────────────────┐
    │                      │            │    ○    ○         │
    │                      │ 175 mm     │    M12 holes      │
    │     OLI MVE 400/6-HF│ (H)        │                   │ 154 mm
    │                      │            │    ○    ○         │ (W)
    │                      │            │                   │
    └──────────────────────┘            └──────────────────┘
     ←──── 255 mm (L) ────→             ←── 255 mm (L) ──→

    Bolt pattern:  90 mm (D) × 125 mm (E)
    Bolt holes:    4 × Ø 13 mm (for M12 bolts)
```

## 3. Dual Motor Layout

### 3.1 Counter-Rotating Pair — Concept

OLI tells you to bolt two identical motors as a mirror pair on one rigid structure.
The structure is for linear vibration in one direction.
- If you exchange two phase wires on one motor, that motor turns the other way.
The result is in the figure below.

```
                    Motor A (CW)         Motor B (CCW)
                    ┌─────────┐         ┌─────────┐
                    │ ↻       │         │       ↺ │
                    │  ●──e   │         │   e──●  │
                    │         │         │         │
                    └────┬────┘         └────┬────┘
                         │                   │
                    ═════╪═══════════════════╪═════
                         │   VIBRATING PLATE │
                         │   (Schwingplatte) │
                         └───────┬───────────┘
                                 │
                          CENTER COLUMN
                            Ø 50 mm
                                 │
                                 ▼
                           DT325 Rod
```

The figure below shows the split of the force vectors.

```
At any instant t:
  Motor A:  F_A = F₀ · [cos(ωt)·ĵ + sin(ωt)·î]     (CW)
  Motor B:  F_B = F₀ · [cos(ωt)·ĵ − sin(ωt)·î]     (CCW)

  Sum:      F_total = 2·F₀·cos(ωt)·ĵ    ← PURE AXIAL!

  Horizontal: sin(ωt)·î − sin(ωt)·î = 0  ← CANCELS ✓
  Vertical:   cos(ωt)·ĵ + cos(ωt)·ĵ = 2·cos(ωt)·ĵ  ← DOUBLES ✓
```

### 3.2 Physical Arrangement (Front View)

```
    ←─────────── ~420 mm total width ────────────→

    ┌────────────────────────────────────────────┐
    │              TOP ISOLATION PLATE            │ (connected to carriage
    │              (via 4× rubber mounts)         │  via isolators)
    └──────┬─────────────────────────────┬───────┘
           │  M12 rubber                 │  M12 rubber
           │  isolator                   │  isolator
    ┌──────┴─────────────────────────────┴───────┐
    │                                             │
    │  ┌──────────┐               ┌──────────┐   │
    │  │ OLI      │               │ OLI      │   │
    │  │ MVE 400  │               │ MVE 400  │   │
    │  │ /6-HF    │               │ /6-HF    │   │  VIBRATING
    │  │ (Motor A)│               │(Motor B) │   │  PLATE
    │  │  ↻ CW    │               │ CCW ↺    │   │  (Schwingplatte)
    │  └──────────┘               └──────────┘   │
    │                                             │
    │                ┌─────────┐                  │
    │                │ CENTER  │                  │
    │                │ COLUMN  │                  │
    │                │  Ø 50   │                  │
    │                └────┬────┘                  │
    └─────────────────────┼───────────────────────┘
                          │
                          ▼
                    DT325 Probe Rod
                     3.25″ OD × 48″
```

### 3.3 Physical Arrangement (Side View)

```
                    ←── 255 mm ──→
                    ┌─────────────┐
        ISO         │             │         ISO
        MOUNT ──────│  Motor A    │──────── MOUNT
                    │  (front)    │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │ VIBRATING   │
                    │ PLATE       │ 15–20 mm steel
                    │ (S355)      │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Motor B    │ (behind Motor A,
                    │  (rear)     │  or side-by-side)
                    └─────────────┘
                           │
                    CENTER COLUMN
                           │
                       DT325 ROD
```

### 3.4 Key Dimensions (Assembly)

| Parameter                     | Value               | Notes                           |
|-------------------------------|---------------------|---------------------------------|
| Vibrating plate (L × W × t)  | 420 × 300 × 20 mm  | S355J2 steel, machined          |
| Vibrating plate mass          | ~20 kg              | Including stiffener ribs        |
| Motor-to-motor spacing        | ≥ 170 mm center     | Side-by-side arrangement        |
| Total head width              | ~420 mm             | Plate width                     |
| Total head depth              | ~300 mm             | Plate depth (motors on top)     |
| Total head height             | ~220 mm             | Plate + motors + column flange  |
| Combined motor mass           | 14.4 kg (2 × 7.2)  |                                 |
| Total vibrating mass          | ~37 kg              | Plate + motors + column + adapt.|
| Center column OD              | 50 mm               | 42CrMo4, flanged to plate       |
| Casing adapter                | Custom, threaded    | Connects column to the 3.25 in casing |

## 4. Force & Frequency Analysis

### 4.1 Combined Axial Force

Each motor makes 4.0 kN of centrifugal force at 6,000 rpm and the type is OLI MVE 400/6-HF.
In a pair with opposite rotation, the horizontal part cancels and the vertical part doubles.

```
F_peak_axial = 2 × 4,002 N = 8,004 N ≈ 8.0 kN

(OLI specifies 408 kgf = 408 × 9.81 = 4,002 N per motor)
```

### 4.2 Force vs. Frequency (VFD-Controlled)

Centrifugal force scales with ω² and thus with f².
The baseline is the rated force from OLI.

```
F(f) = F_rated × (f / f_rated)²

where  F_rated = 8.0 kN at f_rated corresponding to 6,000 rpm
```

| VFD Speed [rpm] | Frequency Factor | F_single [kN] | F_combined [kN] | Use Case            |
|-----------------|-----------------|----------------|------------------|---------------------|
|          3,000  | (3/6)² = 0.25   |           1.0  |             2.0  | Soft soil / ramp    |
|          4,000  | (4/6)² = 0.44   |           1.8  |             3.5  | Light soil           |
|          5,000  | (5/6)² = 0.69   |           2.8  |             5.5  | Medium soil          |
|          6,000  | (6/6)² = 1.00   |           4.0  |             8.0  | Heavy soil / clay    |
|          6,600  | (6.6/6)² = 1.21 |           4.8  |             9.7  | Very hard (max VFD)  |

- The VFD control of frequency alone gives the force range of 1 to 5.
- You need no mechanical change of the eccentric weights for most field conditions.

### 4.3 OLI Internal Eccentric Adjustment

These motors from OLI have an eccentric weight.
You can adjust the weights at both ends of the shaft.
The rated force of 408 kgf is the maximum.
If you move the weight segments, you can lower the force to any point from 0 to 100 percent of rated.
This is a second axis of tune on top of the VFD control of frequency.
You can use it to lower the force for good when the work is only in soft soil.

### 4.4 Resonance Consideration

- The source is Šporin and Vukelić, 2017, equation 1.

```
f_rod_resonance = c / (2 · l) = 5,100 / (2 × 1.22) ≈ 2,090 Hz

Operating range: motor speed / (poles/2)
  At 6,000 rpm, 6-pole: electrical freq = 6000 × 3 / 60 = 300 Hz
  Mechanical rotation: 6,000 rpm = 100 rps = 100 Hz vibration frequency
```

The vibration frequency is 100 Hz at 6,000 rpm.
One turn of the eccentric mass is one force cycle.
Rod resonance at 2,090 Hz is far above that cycle.
The resonance of the soil and the rod is 50 to 200 Hz.
You can aim at that band if you change the VFD frequency.
You then get the best speed of penetration at the moment of the work.

### 4.5 Power Consumption

```
Per motor: ~0.58 kW (at 230V, 1.45A, ~cos φ 0.85)
Two motors: ~1.16 kW electrical draw

At VFD efficiency ~95%:
  VFD input power: ~1.22 kW from Instagrid/mains

Compare to custom design (3.0 kW for equivalent force):
  OLI solution uses ~60% LESS power — the integrated motor+eccentric
  design is far more efficient than driving external weights via belts.
```

## 5. Synchronisation

### 5.1 Electrical Self-Synchronisation (Primary Method)

- The two motors take power from one output of the VFD.

```
VFD Output:  U  V  W

Motor A:     U → U    V → V    W → W       (CW rotation)
Motor B:     U → U    V → W    W → V       (CCW rotation — V/W swapped)
```

At startup, the two motors speed up in the same way.
The voltage is the same and the frequency is the same.
They sit on one rigid mass.
The mechanical link then forces an anti-phase lock in 1 to 2 seconds.
This is the standard method from OLI for linear vibration.

### 5.2 Why No Timing Belt or Gears Needed

In the custom design with an eccentric, timing belts are required.
- Two separate shafts need the mechanical phase link.
- If the phase drifts, the force becomes lateral.

The OLI motors work as follows.
- Each motor is one unit and it holds the motor, the eccentric, and the ball races.
- The shared frequency of the VFD gives the same speed.
- The shared mass gives the natural self-sync.
- The lock of phase comes from inertial link through the vibration plate.
- OLI guarantees this for pairs that turn in opposite ways in the application guides.

### 5.3 Startup Sequence

```
1. VFD ramp: 0 → 3,000 rpm in 2 s (low-frequency region, skip resonances)
2. Both motors spinning, self-sync within first 1–2 revolutions
3. VFD ramp: 3,000 → 6,000 rpm in 3 s (working frequency)
4. Skip frequency bands: 15–25 Hz (frame), 40–55 Hz (estimated plate mode)
5. VFD ramp rate: 50 Hz/s (fast through resonance zones)
```

## 6. Vibrating Plate Design (Schwingplatte)

The vibration plate is the central element of the structure.
It must meet the three rules below.
1. Be rigid enough to pass the motor force with no flex and mode 1 must be above 500 Hz.
2. Carry the two motors and the center column.
3. Survive millions of load cycles at about 8 kN that reverses.

### 6.1 Plate Design

```
    TOP VIEW — Vibrating Plate

    ┌──────────────────────────────────────┐
    │                                      │
    │  ┌─ Motor A ──┐    ┌─ Motor B ──┐  │
    │  │  ○    ○     │    │     ○    ○  │  │
    │  │  (M12)      │    │      (M12)  │  │
    │  │  ○    ○     │    │     ○    ○  │  │
    │  └─────────────┘    └─────────────┘  │
    │                                      │
    │           ┌──────────┐               │
    │           │  Column  │               │
    │           │  Flange  │               │
    │           │   Ø 80   │               │
    │           └──────────┘               │
    │                                      │
    │  ○ ISO    ○ ISO          ○ ISO   ○ ISO   ← 4× M12 isolator mounts
    └──────────────────────────────────────┘

    420 mm × 300 mm × 20 mm, S355J2 steel
    Mass ≈ 420 × 300 × 20 × 7.85e-6 = 19.8 kg
    + ribs underneath: ~2 kg
    Total plate: ~22 kg
```

### 6.2 Stiffness Estimate

```
Plate 1st bending mode (simply supported, 420 × 300 × 20 mm, steel):

f₁ ≈ (π/2) × √(D / (ρ·h·a⁴))

where D = E·h³ / (12·(1−ν²)) = 210e9 × 0.020³ / (12 × 0.91) = 153,846 N·m
      ρ·h = 7,850 × 0.020 = 157 kg/m²
      a = 0.420 m

f₁ ≈ (π/2) × √(153,846 / (157 × 0.420⁴))
   ≈ 1.57 × √(153,846 / 4.88)
   ≈ 1.57 × √31,524
   ≈ 1.57 × 177.6
   ≈ 279 Hz

With stiffener ribs and bolted motors (added mass + stiffness):
Effective f₁ ≈ 350–450 Hz

This is 3.5–4.5× above operating frequency (100 Hz).
Acceptable but should be verified by FEA.
Adding 2 longitudinal ribs (underneath) can push f₁ above 500 Hz.
```

## 7. Vibration Isolation

You must isolate the vibration plate assembly from the carriage and from the frame.
This block stops the pass of vibration.

| Parameter                | Value                              |
|--------------------------|------------------------------------|
| Isolator type            | Cylindrical rubber buffers, M12    |
| Quantity                 | 4 (rectangular pattern)            |
| Shore hardness           | 55–70 Shore A                      |
| Static load per mount    | ~90 N (37 kg / 4)                 |
| Dynamic load per mount   | ~2,000 N peak (8 kN / 4)          |
| Required mount stiffness | ~70 kN/m per mount                 |
| Mount natural frequency  | ~7–12 Hz                           |
| Isolation ratio at 100 Hz| > 98% (f/f₀ > 8)                  |

```
Transmissibility at operating frequency:

T = 1 / ((f/f₀)² − 1)

At f = 100 Hz, f₀ = 10 Hz:
T = 1 / (100 − 1) = 0.0101 = ~1% transmitted

→ 99% of vibration energy stays in the vibrating plate assembly.
→ Carriage and frame experience < 80 N dynamic load.
```

### Isolator Selection

- Use cylindrical buffers from Schwingmetall or from Paulstra in DE or FR.
- Trelleborg also makes mounts that block vibration.
- Or use 4 conical mounts of rubber, for example from AMC MECANOCAUCHO.
- The thread is M12 at the top and at the bottom for easy assembly.
- The temperature range in service is −20°C to +80°C.

## 8. Center Column and Casing Connection

```
    CROSS-SECTION

    ╔═══════════════╗  ← Vibrating plate (20 mm)
    ║               ║
    ║  ┌─────────┐  ║
    ║  │ Column  │  ║
    ║  │ Flange  │  ║  Ø 80 mm flange, 6× M10 bolts
    ║  │ (bolted)│  ║
    ╚══╪═════════╪══╝
       │         │
       │  CENTER │
       │  COLUMN │  Ø 50 mm, 42CrMo4
       │         │  Length: ~200 mm
       │         │
       └────┬────┘
            │
       ┌────┴────┐
       │ ADAPTER │  Custom adapter VC-SH-1500
       │         │  Must push and pull the casing
       │         │  Do not use the GH60 cap
       └────┬────┘
            │
       ┌────┴────────┐
       │  CASING     │  3.25 in OD x 48 in
       │  PN: 201446 │  one rod, 17.7 kg, shoe PN 205449
       └─────────────┘
```

The center column is a solid shaft of 42CrMo4 and a flange ties it to the vibration plate.
It passes the full axial force of 8 kN to the casing and the force reverses.
If you need rotation for auger mode, the column can sit on thrust races and on radial races in the plate.
For casing sampling with no rotation, the rigid flange link is simpler and stronger.

## 9. Assembly Mass Budget

| Component                     | Mass [kg] | Notes                        |
|-------------------------------|-----------|------------------------------|
| OLI MVE 400/6-HF × 2         | 14.4      | 7.2 kg each                  |
| Vibrating plate (+ ribs)     | 22.0      | 420×300×20 mm S355 + ribs    |
| Center column (+ flange)     | 3.5       | Ø50×200 mm, 42CrMo4         |
| Casing adapter               | 1.0       | Steel, machined              |
| Fasteners (M12 motor bolts)  | 0.5       | 8× M12×40, washers           |
| **Total vibrating mass**     | **41.4**  | Moves with vibration         |
| 4× rubber isolators          | 0.8       | Static on carriage           |
| Casing rod (one)             | 17.7      | Geoprobe PN 201446, one rod  |
| Cutting shoe                 | 1.5       | PN 205449                    |
| **Total moved mass (in soil)**| **60.6** | 41.4 + 17.7 + 1.5            |

## 10. Comparison: OLI Dual Motor vs. Custom Eccentric

| Criterion                 | Custom (V1 design)          | OLI Dual Motor (V2)        |
|---------------------------|-----------------------------|----------------------------|
| Force (peak axial)        | ~8 kN (adjustable)          | ~8 kN (adjustable)         |
| Operating frequency       | 90–110 Hz (VFD)             | ~100 Hz (VFD)              |
| Custom machined parts     | 12+ (shafts, discs, housing)| 3 (plate, column, adapter) |
| Timing belt / gears       | Required                    | Not needed                 |
| External bearings          | 4× NJ 206                  | None (internal to motor)   |
| Motor power (elec.)       | ~3.0 kW (1 motor)           | ~1.2 kW (2 motors)        |
| Total head mass           | ~35–40 kg                   | ~41 kg                     |
| Assembly complexity       | High (precision alignment)  | Low (bolt-on)              |
| Reliability               | Unproven (custom)           | Proven (industrial)        |
| Spare parts               | Custom order                | OLI stock / dealer          |
| Estimated cost (head)     | ~1,930–3,110 €              | ~1,100–1,800 €            |
| Time to build             | 4–8 weeks (custom fab)      | 1–2 weeks                  |

V2 from OLI is the clear winner for production and for a fast first build.

## 11. VFD Requirements

| Parameter              | Value                              |
|------------------------|------------------------------------|
| Motor rating (total)   | 2 × ~0.58 kW = ~1.16 kW          |
| VFD size               | 1.5 kW (next standard size)        |
| Input                  | 230V 1-phase (Instagrid/mains)     |
| Output                 | 3-phase, 0–400 Hz                  |
| V/f control            | Yes (OLI motors are V/f type)      |
| Skip frequencies       | Configurable (frame + plate modes) |
| DC injection braking   | Yes (for quick stop)               |
| Analog input           | 0–10V for frequency setpoint       |
| RS485 / Modbus         | Optional (for PLC control)         |
| Protection             | IP20 min (in control enclosure)    |
| **Candidates**         | Siemens V20, ABB ACS150, Lenze i510, Invertek Optidrive |

Important: you must rate the VFD for the high output frequency.
- The motors must run at 6,000 rpm.
Standard VFDs go to 400 Hz maximum and that limit is enough.
At 6,000 rpm on a 6-pole motor, the electrical frequency is 300 Hz.

## 12. Electrical Wiring

```
    INSTAGRID / MAINS (230V 1ph)
              │
              ▼
    ┌─────────────────┐
    │      VFD        │  1.5 kW, 230V 1ph → 3ph
    │  (Siemens V20)  │
    └───┬───────┬─────┘
        │       │
    U V W    U V W
        │       │
  ┌─────┴──┐ ┌──┴─────┐
  │Motor A │ │Motor B  │    Motor B: V and W swapped for CCW
  │  CW    │ │  CCW    │
  │  U-V-W │ │  U-W-V  │
  └────────┘ └─────────┘
```

The cable size for 2 times 1.45 A is 2.9 A in total.
- The run from the VFD to the motors is cable of 3 by 1.5 mm² with a shield.
- The cable length is under 5 m and the runs in the machine are short.
- Ground the shield at the VFD end for EMC.

## 13. Open Questions

- [ ] Verify the lead time in the EU for the OLI MVE 400/6-HF.
- [ ] Confirm the exact VFD frequency for 6,000 rpm and verify the pole count.
- [ ] Run FEA on the vibration plate for natural frequency and for stress at cyclic 8 kN.
- [ ] Find the best rib pattern of the plate for maximum stiffness and for low weight.
- [ ] Specify the thread of the casing adapter and verify it with Geoprobe.
- [ ] Test in the field for the best ramp of VFD frequency on each soil type.
- [ ] Monitor the surface temperature of the motor during the long run.
- [ ] Write the procedure for eccentric weight adjustment from the OLI manual.



The references are Šporin and Vukelić (2017) and Wang and others (2015).
Also see the OLI CIV catalogue and the OLI guide for linear vibration.
