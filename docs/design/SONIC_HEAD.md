# Sonic Head — Design Document

## 1. Operating Principle

The sonic head generates **axial pressure waves** along the drill rod by using two
counter-rotating eccentric masses on shafts **perpendicular to the rod axis**.

Horizontal force components cancel out; vertical (axial) components add constructively.
This produces a sinusoidal pushing/pulling force on the rod, driving it into the soil
by cyclically liquefying the thin boundary layer (cf. Šporin & Vukelić, 2017).

### Why Perpendicular Shafts?

If the eccentric shafts were **parallel** to the rod axis, the centrifugal force would
sweep in a plane perpendicular to the rod — generating a *lateral whipping* motion rather
than axial vibration. Correct orientation:

```
  ROD AXIS (vertical)
       ↕
  ─────●─────  ← Shaft A axis (horizontal, perpendicular to rod)
       │
  ─────●─────  ← Shaft B axis (horizontal, perpendicular to rod, counter-rotating)
       │
       ↓
    DT325 Rod
```

## 2. Kinematic Layout

### 2.1 Exploded Schematic

```
              MOTOR (mounted on top plate)
                │
                │  Primary belt drive
                ▼
      ┌─────────────────────┐
      │     TIMING BELT     │ 1:1 synchronisation
      │  ┌────┐     ┌────┐  │
      │  │ S_A│◄───►│ S_B│  │ shaft-to-shaft = 200mm
      │  │ CW │     │ CCW│  │
      │  └──┬─┘     └──┬─┘  │
      │     │           │    │
      │  ┌──┴──┐     ┌──┴──┐│
      │  │DISC │     │DISC ││ Ø 140 mm eccentric rotors
      │  │ A   │     │ B   ││ with adjustable weights
      │  └──┬──┘     └──┬──┘│
      │     │           │    │
      └─────┼───────────┼───┘
            │           │
       ┌────┴───────────┴────┐
       │   CENTER COLUMN     │ Ø 50 mm
       │   (Adapter Shaft)   │
       └─────────┬───────────┘
                 │
                 ▼
           DT325 Probe Rod
            3.25″ OD × 48″
```

### 2.2 Component Layout (Top View, Cross-Section at Shaft Level)

```
    ←────── 280 mm housing width ──────→

    ┌──────────────────────────────────┐
    │         HOUSING (top plate)      │
    │                                  │
    │  ┌────────┐        ┌────────┐   │
    │  │Bearing │        │Bearing │   │ 2× bearing blocks per shaft
    │  │Block A │        │Block B │   │
    │  │  ┌──┐  │        │  ┌──┐  │   │
    │  │  │30│  │        │  │30│  │   │ shaft Ø 30 mm
    │  │  └──┘  │        │  └──┘  │   │
    │  └────┬───┘        └────┬───┘   │
    │       │   ←─ 200mm ─→   │       │
    │       │                 │       │
    │  ╔════╧════╗       ╔════╧════╗  │
    │  ║ DISC A  ║       ║ DISC B  ║  │ Ø 140 mm
    │  ║  Ø 140  ║       ║  Ø 140  ║  │ counter-rotating
    │  ╚════╤════╝       ╚════╤════╝  │
    │       │                 │       │
    │       │   ┌─────────┐   │       │
    │       └───│ CENTER  │───┘       │
    │           │ COLUMN  │           │
    │           │  Ø 50   │           │
    │           └─────────┘           │
    │                                  │
    └──────────────────────────────────┘
```

## 3. Key Dimensions

| Parameter                  | Symbol  | Value          | Notes                               |
|----------------------------|---------|----------------|--------------------------------------|
| Center column OD           | D_cc    | 50 mm          | Adapter shaft to DT325 head          |
| Eccentric shaft OD         | D_s     | 30 mm          | High-strength steel (42CrMo4)        |
| Shaft center-to-center     | d_cc    | 200 mm         | Allows Ø140 discs + Ø50 column       |
| Eccentric disc OD          | D_e     | 140 mm         | Room for adjustable masses            |
| Eccentric disc width       | w_e     | 25 mm          | Per disc, 2 discs per shaft possible  |
| Eccentricity               | e       | 10 mm          | Adjustable 5–15 mm via bolt pattern   |
| Eccentric mass per shaft   | m_e     | 1.0 kg         | Including additional bolt-on weights  |
| Bearing span per shaft     | L_b     | 100 mm         | Outboard of disc                      |
| Housing width              | W_h     | 280–340 mm     | Depending on bearing block size       |
| Housing height (shaft lvl) | H_h     | ~160 mm        | Bearing + disc + clearance            |
| Total head height          | H_tot   | ~250 mm        | Including motor mount plate           |

### Geometric Check

```
Available space between shafts:
  200 mm (center-to-center) − 2 × 70 mm (disc radius) = 60 mm gap

Center column Ø 50 mm → 5 mm clearance each side ✓
Shaft Ø 30 mm → disc bore 30 mm ✓
```

## 4. Force & Frequency Analysis

### 4.1 Basic Centrifugal Force (Two Eccentrics)

```
F_peak = 2 · m_e · e · ω²

where  ω = 2π · f

    f [Hz]     ω [rad/s]    F_peak [N]    F_peak [kN]
    ──────     ──────────    ──────────    ───────────
      70         439.8        3,871          3.9
      80         502.7        5,054          5.1
      90         565.5        6,397          6.4
     100         628.3        7,896          7.9
     110         691.2        9,550          9.6
     120         753.9       11,368         11.4
```

### 4.2 Resonance Consideration

From Šporin & Vukelić (2017), Eq. 1:

```
f_res = c / (2 · l)

where  c = wave propagation speed in steel ≈ 5,100 m/s
       l = rod length = 1.22 m (48 in.)

f_res = 5100 / (2 × 1.22) ≈ 2,090 Hz
```

This is far above the operating range (90–120 Hz), meaning **we operate well below
first-order longitudinal resonance**. This is intentional — we are applying forced
vibration for soil liquefaction, not seeking resonance amplification in the rod.

However, the *soil-rod system* resonance (depending on soil stiffness, coupling,
and depth) typically sits in the 50–200 Hz range. The VFD allows sweeping through
this range to find the optimal frequency for each soil type.

### 4.3 Power Estimation

From Šporin & Vukelić (2017), Eq. 11 (modified):

```
N = F² · t² · f / (2 · m)

where  F = peak force (N)
       t = impact duration ≈ 1/(2f) per half-cycle
       f = frequency (Hz)
       m = rod + head mass (kg)

For F = 8,000 N, f = 100 Hz, m ≈ 45 kg:
  t = 1 / (2 × 100) = 0.005 s
  N = 8000² × 0.005² × 100 / (2 × 45)
  N ≈ 1,778 W ≈ 1.8 kW

Motor sizing should account for:
  - Bearing friction losses (~10%)
  - Belt drive losses (~5%)
  - Motor efficiency (~85% for async motor at VFD operation)

Recommended minimum motor rating: 2.5 – 3.0 kW
```

## 5. Synchronisation

### 5.1 Timing Belt (Preferred for V1)

The two eccentric shafts must maintain **exact 180° phase opposition** to cancel
horizontal forces. A 1:1 timing belt achieves this mechanically.

| Parameter             | Value                            |
|-----------------------|----------------------------------|
| Belt type             | HTD 8M (8mm pitch)              |
| Pulley teeth          | 36T (each shaft)                 |
| Pitch diameter        | ~91.7 mm each                    |
| Center distance       | 200 mm                           |
| Belt width            | 20–30 mm                         |
| Belt length           | ≈ 690 mm (standard 688 or 696)   |
| Pretension            | ~150 N per strand                 |

**Advantages over gears at this spacing:**
- No intermediate idler needed (200mm spacing > 2× gear PD)
- Lower noise and vibration transmission through belt
- Self-damping polymer material
- Easy tensioning via motor plate adjustment

### 5.2 Gear Alternative (If Belt Proves Unreliable)

If timing belt lifetime is insufficient due to continuous high-frequency operation,
a spur/helical gear train with an intermediate idler gear could be used. This would
require three gears and additional bearing support. Deferred to V2 evaluation.

## 6. Motor Selection

### Requirements

| Parameter          | Value                             |
|--------------------|-----------------------------------|
| Power              | 2.5 – 3.0 kW continuous           |
| Speed at 100 Hz    | 6,000 rpm (direct) or geared      |
| Type               | 3-phase async (for VFD control)   |
| Voltage            | 230V 1ph → VFD → 3ph motor        |
| Vibration-rated    | Yes (VPI-windings desirable)       |
| Mass               | < 15 kg ideally                    |
| Mounting           | Flange (B14) or foot (B3)          |

### Candidates

1. **OLI MVE 1300/6N-HF** — 0.6 kW high-frequency vibration motor
   - Built for vibration, VPI windings, Class H insulation
   - Too low power for driving external eccentrics
   - Could serve as reference for bearing/winding design

2. **Standard IEC 71 / IEC 80 motor** — 2.2–3.0 kW, 2-pole
   - Widely available, VFD-compatible
   - Would need vibration-proofing (rubber isolators, VPI option)
   - Marathon, ABB, Siemens, WEG, etc.

3. **Custom design** — purpose-built vibration motor
   - Ideal but expensive; deferred to series production

**Recommendation for V1:** IEC 80 frame, 3.0 kW, 2-pole motor on
anti-vibration mounts, driven by a compact VFD.

## 7. Vibration Isolation

The sonic head must be **mechanically isolated from the hub carriage** to prevent
vibration from destroying electronics, bearings, and the frame.

| Component               | Spec                              |
|--------------------------|-----------------------------------|
| Mounts                   | 4× M12 rubber buffers, 70 Shore A |
| Deflection at 8 kN       | ~2 mm max                         |
| Natural freq. of mounts  | 15–25 Hz (well below 90 Hz)       |
| Material                 | Neoprene or polyurethane           |
| Mounting pattern          | Rectangular, symmetric             |

The mounts should be sized so that the system's natural frequency on the
isolators (including head mass) is **at least 3× below** the minimum operating
frequency (90 Hz → mount natural freq. < 30 Hz).

## 8. Materials

| Component        | Material              | Notes                              |
|------------------|-----------------------|------------------------------------|
| Housing          | Steel S355 / EN-GJS   | Welded or cast                     |
| Eccentric shafts | 42CrMo4 (quenched)   | High fatigue strength              |
| Eccentric discs  | S355J2 steel          | Machined, balanced                 |
| Add-on weights   | S355J2 or cast iron   | Bolted segments                    |
| Center column    | 42CrMo4               | Threaded bottom for DT325 adapter  |
| Bearings         | NJ 206 ECP (SKF)     | Cylindrical roller, axial play     |
| Timing belt      | Gates PowerGrip HTD   | 8M pitch, glass cord               |
| Pulleys          | Aluminium 7075-T6    | Machined, anodised                 |

## 9. Open Questions

- [ ] Exact motor model and VFD pairing
- [ ] Belt lifetime under continuous 100 Hz operation (testing required)
- [ ] Optimal eccentricity range for different soil types (field testing)
- [ ] Housing fabrication: welded steel vs. machined billet vs. cast
- [ ] DT325 adapter thread specification (verify with Geoprobe)
- [ ] Balancing procedure for eccentric discs
- [ ] Temperature management at high speed (bearing + belt heat)

---

*References: Šporin & Vukelić (2017), Wang et al. (2015), OLI CIV Catalogue*
