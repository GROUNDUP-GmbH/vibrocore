# Sonic Head — Design Document (V2: OLI MVE 400/6-HF Dual Motor)

## 1. Operating Principle

The sonic head generates **axial pressure waves** along the drill rod by using two
**counter-rotating OLI MVE 400/6-HF vibration motors** mounted on a common rigid
vibrating plate (Schwingplatte). The motors' eccentric shafts are oriented
**perpendicular to the rod axis**.

Horizontal force components cancel out; vertical (axial) components add constructively.
This produces a sinusoidal pushing/pulling force on the rod, driving it into the soil
by cyclically liquefying the thin boundary layer (cf. Šporin & Vukelić, 2017).

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

If the motor shafts were **parallel** to the rod axis, the centrifugal force would
sweep in a plane perpendicular to the rod — generating a *lateral whipping* motion
rather than axial vibration. With horizontal shafts (⊥ to rod axis), the vertical
force components add up for maximum axial amplitude.

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

OLI recommends mounting two identical motors **mirror-image** on a common rigid
structure for **linear (directional) vibration**. By swapping two phase wires on
one motor, it rotates in the opposite direction. The result:

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

**Force vector decomposition:**

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
| DT325 adapter                 | Custom, threaded    | Connects column to Geoprobe rod |

## 4. Force & Frequency Analysis

### 4.1 Combined Axial Force

Each OLI MVE 400/6-HF produces **4.0 kN** centrifugal force at 6,000 rpm.
In counter-rotating pair, horizontal cancels and vertical doubles:

```
F_peak_axial = 2 × 4,002 N = 8,004 N ≈ 8.0 kN

(OLI specifies 408 kgf = 408 × 9.81 = 4,002 N per motor)
```

### 4.2 Force vs. Frequency (VFD-Controlled)

Centrifugal force scales with ω² (i.e., f²). Using the OLI rated force as baseline:

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

**The VFD frequency control alone gives a 1:5 force range — no mechanical
adjustment of eccentric weights required for most field conditions.**

### 4.3 OLI Internal Eccentric Adjustment

OLI MVE motors have **adjustable eccentric weights** at both shaft ends.
The rated force (408 kgf) is the **maximum setting**. By repositioning the
weight segments, the force can be reduced to approximately 0–100% of rated.

This gives a **secondary tuning axis** on top of VFD frequency control —
useful for permanently reducing force for soft-soil-only operations.

### 4.4 Resonance Consideration

From Šporin & Vukelić (2017), Eq. 1:

```
f_rod_resonance = c / (2 · l) = 5,100 / (2 × 1.22) ≈ 2,090 Hz

Operating range: motor speed / (poles/2)
  At 6,000 rpm, 6-pole: electrical freq = 6000 × 3 / 60 = 300 Hz
  Mechanical rotation: 6,000 rpm = 100 rps = 100 Hz vibration frequency
```

The **vibration frequency is 100 Hz** at 6,000 rpm (one eccentric revolution =
one force cycle). Rod resonance at 2,090 Hz is far above.

The **soil-rod system** resonance (50–200 Hz) can be targeted by sweeping the
VFD frequency, finding the optimal penetration speed in real time.

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

Both motors are powered from the **same VFD output**. Wiring:

```
VFD Output:  U  V  W

Motor A:     U → U    V → V    W → W       (CW rotation)
Motor B:     U → U    V → W    W → V       (CCW rotation — V/W swapped)
```

At startup, both motors accelerate identically (same voltage, same frequency).
Because they are mounted on the same rigid mass, mechanical coupling forces
them into anti-phase lock within 1–2 seconds. This is the **standard OLI
recommended method** for linear vibration applications.

### 5.2 Why No Timing Belt or Gears Needed

In the custom eccentric design, timing belts were required because:
- Two separate shafts needed mechanical phase coupling
- Any phase drift would create lateral forces

With OLI motors:
- Each motor is a self-contained unit (motor + eccentric + bearings)
- Shared VFD frequency guarantees identical speed
- Shared mass provides natural self-synchronisation
- Phase lock is maintained by inertial coupling through the vibrating plate
- OLI guarantees this for counter-rotating pairs in their application guides

### 5.3 Startup Sequence

```
1. VFD ramp: 0 → 3,000 rpm in 2 s (low-frequency region, skip resonances)
2. Both motors spinning, self-sync within first 1–2 revolutions
3. VFD ramp: 3,000 → 6,000 rpm in 3 s (working frequency)
4. Skip frequency bands: 15–25 Hz (frame), 40–55 Hz (estimated plate mode)
5. VFD ramp rate: 50 Hz/s (fast through resonance zones)
```

## 6. Vibrating Plate Design (Schwingplatte)

The vibrating plate is the central structural element. It must:
1. Be **rigid enough** to transmit motor forces without flexing (≥ 1st mode > 500 Hz)
2. Carry both motors and the center column
3. Survive millions of load cycles at ~8 kN alternating

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

The vibrating plate assembly must be **mechanically isolated** from the carriage
and frame to prevent vibration transmission.

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

- **Schwingmetall / Paulstra** cylindrical buffers (DE/FR)
- **Trelleborg** anti-vibration mounts
- Alternatively: 4× conical rubber mounts (e.g., AMC MECANOCAUCHO)
- M12 thread top and bottom for easy assembly
- Operating temperature: −20°C to +80°C

## 8. Center Column & DT325 Connection

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
       │ DT325   │  Custom adapter
       │ ADAPTER │  Thread to Geoprobe spec
       │         │  Internally threaded for DT325 drive cap
       └────┬────┘
            │
       ┌────┴────────┐
       │  DT325 Rod  │  3.25″ OD × 48″
       │  PN: 201446 │  with cutting shoe PN: 205449
       └─────────────┘
```

The center column is a **solid 42CrMo4 shaft** flanged to the vibrating plate.
It transmits the full 8 kN alternating axial force to the DT325 system.

Bearing option: If rotation is needed (for auger mode), the column can be
mounted with thrust/radial bearings in the plate. For DT325 core sampling
(no rotation), a rigid flange connection is simpler and stronger.

## 9. Assembly Mass Budget

| Component                     | Mass [kg] | Notes                        |
|-------------------------------|-----------|------------------------------|
| OLI MVE 400/6-HF × 2         | 14.4      | 7.2 kg each                  |
| Vibrating plate (+ ribs)     | 22.0      | 420×300×20 mm S355 + ribs    |
| Center column (+ flange)     | 3.5       | Ø50×200 mm, 42CrMo4         |
| DT325 adapter                | 1.0       | Steel, machined              |
| Fasteners (M12 motor bolts)  | 0.5       | 8× M12×40, washers           |
| **Total vibrating mass**     | **41.4**  | Moves with vibration         |
| 4× rubber isolators          | 0.8       | Static on carriage           |
| DT325 rod (per pair)         | 35.4      | Geoprobe PN 201446           |
| DT325 cutting shoe           | 1.5       | PN 205449                    |
| **Total moved mass (in soil)**| **78.3** | Vibrating + rod + shoe       |

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

**V2 (OLI) is the clear winner for production and rapid prototyping.**

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

**Important: The VFD must be rated for the elevated output frequency needed
to drive the motors at 6,000 rpm. Standard VFDs go to 400 Hz max, which is
sufficient (6,000 rpm on 6-pole = 300 Hz electrical).**

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

Cable sizing for 2 × 1.45 A = 2.9 A total:
- VFD to motors: 3 × 1.5 mm² shielded motor cable
- Cable length: < 5 m (short runs within machine)
- Shielding: grounded at VFD end (EMC)

## 13. Open Questions

- [ ] Verify OLI MVE 400/6-HF availability and lead time in EU
- [ ] Confirm exact VFD frequency needed for 6,000 rpm (pole count verification)
- [ ] Vibrating plate FEA (natural frequencies, stress under cyclic 8 kN)
- [ ] Optimal plate rib pattern for maximum stiffness vs. weight
- [ ] DT325 adapter thread specification (verify with Geoprobe)
- [ ] Field test: optimal VFD frequency ramp for different soil types
- [ ] Temperature monitoring: motor surface temp during extended operation
- [ ] Eccentric weight adjustment procedure (OLI manual)

---

*References: Šporin & Vukelić (2017), Wang et al. (2015), OLI CIV Catalogue,
OLI Application Guide for Linear Vibration*
