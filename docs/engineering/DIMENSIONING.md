# Dimensioning Calculations (V2: OLI MVE 400/6-HF)

All calculations reference Šporin & Vukelić (2017), Wang et al. (2015),
and OLI MVE 400/6-HF rated data.

## 1. Target Parameters

| Parameter                  | Symbol | Target Value      | Source / Justification               |
|----------------------------|--------|-------------------|--------------------------------------|
| Sampling depth             | d      | 1.0 m             | VM0042 minimum 0–30cm; we go deeper  |
| Core tube OD               | D_t    | 82.55 mm (3.25″) | Geoprobe DT325                       |
| Core tube length           | L_t    | 1,219 mm (48″)   | Geoprobe DT325 rod                   |
| Core tube mass (per pair)  | m_t    | 35.4 kg           | Geoprobe PN 201446 (rod pair)        |
| Operating speed            | n      | 6,000 rpm         | OLI rated, via VFD                   |
| Vibration frequency        | f      | 100 Hz            | = 6,000 rpm / 60                     |
| Peak axial force (pair)    | F_peak | ~8.0 kN           | 2 × 408 kgf OLI rated               |
| Vibration motors           | —      | 2× OLI MVE 400/6-HF | Counter-rotating pair             |

## 2. Force Analysis — OLI Dual Motor

### 2.1 Single Motor Centrifugal Force

OLI MVE 400/6-HF rated: **408 kgf at 6,000 rpm**

```
F_single = 408 × 9.81 = 4,002 N ≈ 4.0 kN per motor
```

### 2.2 Counter-Rotating Pair — Resultant Axial Force

```
F_axial(t) = 2 × F_single × cos(ωt)

F_peak = 2 × 4,002 = 8,004 N ≈ 8.0 kN

Horizontal components cancel:
  F_horizontal = F₀·sin(ωt) − F₀·sin(ωt) = 0  ✓
```

### 2.3 Force vs. VFD Speed

Centrifugal force scales with n² (speed squared):

```
F(n) = F_rated × (n / n_rated)²
F_combined(n) = 2 × F(n)
```

| VFD Speed [rpm] | Speed Ratio | F_single [kN] | F_combined [kN] | Application          |
|-----------------|------------|----------------|------------------|----------------------|
|          2,000  | 0.333      |          0.44  |             0.89 | Startup ramp         |
|          3,000  | 0.500      |          1.00  |             2.00 | Very soft soil       |
|          4,000  | 0.667      |          1.78  |             3.56 | Light loam           |
|          5,000  | 0.833      |          2.78  |             5.56 | Medium clay          |
|          6,000  | 1.000      |          4.00  |             8.00 | Heavy clay / compact |
|          6,600  | 1.100      |          4.84  |             9.68 | Max (110% overdrive) |

**VFD frequency control provides continuous 0.9 – 9.7 kN force range.**

### 2.4 OLI Internal Eccentric Adjustment

OLI MVE motors have adjustable eccentric weights (0–100% of rated force).
Combined with VFD speed control:

| Eccentric Setting | VFD at 6,000 rpm | VFD at 4,000 rpm |
|-------------------|------------------|------------------|
| 100% (max)        | 8.0 kN           | 3.6 kN           |
| 75%               | 6.0 kN           | 2.7 kN           |
| 50%               | 4.0 kN           | 1.8 kN           |
| 25%               | 2.0 kN           | 0.9 kN           |

**Total force range: 0.9 – 9.7 kN (~1:11 ratio) — covers all agricultural soils.**

## 3. Vibrating Plate Dimensioning

### 3.1 Geometry

| Parameter              | Value              | Notes                           |
|------------------------|--------------------|---------------------------------|
| Length                  | 420 mm             | Two motors side by side          |
| Width                  | 300 mm             | Motor depth + clearance          |
| Thickness              | 20 mm              | S355J2 steel                     |
| Ribs (longitudinal)    | 2 × (300×60×10 mm) | Underneath, welded               |
| Column flange          | Ø 80 mm, 6× M10   | Center of plate, underneath      |

### 3.2 Mass Calculation

```
Plate body:
  V_plate = 0.420 × 0.300 × 0.020 = 2.52 × 10⁻³ m³
  m_plate = 7,850 × 2.52 × 10⁻³ = 19.8 kg

Ribs (2×):
  V_rib = 2 × 0.300 × 0.060 × 0.010 = 3.6 × 10⁻⁴ m³
  m_ribs = 7,850 × 3.6 × 10⁻⁴ = 2.8 kg

Total plate assembly: ~22.6 kg
```

### 3.3 Total Vibrating Mass

```
Plate + ribs:         22.6 kg
2× OLI motors:        14.4 kg
Center column:          3.5 kg
DT325 adapter:          1.0 kg
Fasteners:              0.5 kg
─────────────────────────────
Total vibrating mass:  42.0 kg

With DT325 rod (in soil): 42.0 + 35.4 + 1.5 = 78.9 kg
```

### 3.4 Plate Natural Frequency (Bending)

```
Simplified plate bending (1st mode, simply supported edges):

f₁ ≈ (π/2) × √(D / (ρ_eff × a⁴))

where:
  D = E·h³/(12·(1−ν²)) = 210e9 × 0.020³ / (12 × 0.91) = 153,846 N·m
  ρ_eff = total_mass / (L × W) = 42.0 / (0.420 × 0.300) = 333 kg/m²
  a = 0.420 m (longer dimension)

f₁ ≈ (π/2) × √(153,846 / (333 × 0.0311))
   ≈ 1.57 × √(153,846 / 10.36)
   ≈ 1.57 × √14,849
   ≈ 1.57 × 121.9
   ≈ 191 Hz

With ribs (increased stiffness, FEA verification needed):
Estimated f₁ ≈ 250–350 Hz

Ratio to operating frequency: 250/100 = 2.5× minimum
Target: > 3× → may need additional ribs or thicker plate (25 mm).
FEA should verify and optimize.
```

## 4. Vibration Isolation

### 4.1 Isolator Requirements

```
Total vibrating mass: m_vib = 42.0 kg
Peak dynamic force:   F_peak = 8,000 N
Number of isolators:  n = 4

Static load per mount:   P_stat = m_vib × g / n = 42 × 9.81 / 4 = 103 N
Dynamic load per mount:  P_dyn = F_peak / n = 8,000 / 4 = 2,000 N
```

### 4.2 Isolator Natural Frequency

For > 95% isolation at 100 Hz, the mount system natural frequency must be:

```
f₀ < f_operating / 3 = 100 / 3 ≈ 33 Hz

For > 99% isolation:
f₀ < f_operating / √(100) ≈ 100 / 10 = 10 Hz

Target: f₀ = 8–12 Hz

Required stiffness per mount:
  k = (2π·f₀)² × m_vib / n = (2π × 10)² × 42 / 4
  k = 3,948 × 10.5 = 41,450 N/m ≈ 41.5 kN/m per mount

Static deflection at mount:
  δ_stat = P_stat / k = 103 / 41,450 = 2.5 mm
```

### 4.3 Transmissibility

```
At f = 100 Hz, f₀ = 10 Hz, undamped:

T = 1 / |((f/f₀)² − 1)| = 1 / |(100)² − 1| = 1 / 9,999 ≈ 0.01%

With damping (ζ = 0.1 typical for rubber):
T ≈ 1 / ((f/f₀)² − 1) ≈ 1.01%

Force transmitted to carriage per mount: 2,000 × 0.01 = 20 N
Total transmitted to frame: 4 × 20 = 80 N (negligible)
```

### 4.4 Selected Isolator

| Parameter          | Value                              |
|--------------------|------------------------------------|
| Type               | Cylindrical rubber buffer, M12     |
| Shore hardness     | 55–65 Shore A (soft)               |
| Static stiffness   | ~40–50 kN/m                        |
| Dynamic stiffness  | ~60–75 kN/m (×1.5 rubber factor)  |
| Max dynamic load   | 3,000 N                            |
| Natural frequency  | ~8–12 Hz (with 10.5 kg per mount)  |
| Brand              | Schwingmetall, Paulstra, Trelleborg|

## 5. Bearing Analysis (Hub System — Unchanged)

### 5.1 Hub Bearings (Pillow Blocks)

Hub drive shaft bearings — same as V1:

| Position             | Type        | Designation    | Notes                    |
|----------------------|-------------|----------------|--------------------------|
| Hub drive shaft (2)  | Self-align  | UCP 206        | Pillow block, 30mm bore  |
| Hub idle sprocket    | Deep groove | 6205-2RS       | 25×52×15 mm              |

*Note: Sonic head bearings are now INTERNAL to OLI motors — no external
bearing selection needed. OLI's heavy-duty bearings are rated for continuous
high-frequency operation.*

## 6. Power & Energy Analysis

### 6.1 Sonic Head Power (V2 — OLI)

```
Per motor:  ~0.58 kW (230V × 1.45A × cos φ ~0.85 × η ~0.93)
Two motors: ~1.16 kW electrical input

VFD losses: ~5% → 1.22 kW from source

Compare V1 (custom 3.0 kW motor):
  V2 saves ~1.8 kW = 60% less power draw for equivalent force!
  
Reason: OLI motors drive eccentrics directly on the motor shaft —
no belt losses, no external bearing friction, optimised mass/speed ratio.
```

### 6.2 VFD Sizing

```
Motor total: 2 × ~0.58 kW = 1.16 kW
VFD rating: 1.5 kW (next standard size, 30% margin)

At 230V input: 1.5 kW / 230V = 6.5 A max → standard socket OK
Instagrid ONE max: 3.6 kW continuous → ~3× headroom for sonic ✓
```

### 6.3 Energy per Sampling Cycle (Updated)

```
Phase 1 — Ramp up sonic (0 → 6,000 rpm):      3 s × 1.0 kW avg =   3 kJ
Phase 2 — Penetration (1.0 m at 15 mm/s):     67 s × 1.2 kW    =  80 kJ
Phase 3 — Sonic stop (DC brake via VFD):        2 s × 0.3 kW    =   1 kJ
Phase 4 — Extraction (1.0 m at 50 mm/s):      20 s × 0.3 kW    =   6 kJ
Phase 5 — Return to top (0.5 m at 60 mm/s):    8 s × 0.2 kW    =   2 kJ

Sonic subtotal:  ~86 kJ

Hub power (all phases):
  Penetration: 48V × 4A = 192 W × 67s = 12.9 kJ
  Extraction:  48V × 6A = 288 W × 20s =  5.8 kJ
  Return:      48V × 2A =  96 W ×  8s =  0.8 kJ
  Hub subtotal: ~19.5 kJ

Grand total per cycle: 86 + 20 = 106 kJ ≈ 0.029 kWh
```

### 6.4 Daily Energy Budget (100 cores)

```
100 cycles × 0.029 kWh = 2.9 kWh

Instagrid ONE max: 2.1 kWh → sufficient for ~72 cores per charge
→ With 2 charges: 144 cores/day — covers 100 cores easily ✓

48V 50Ah LiFePO4 battery: 2.4 kWh → ~83 cores per charge

V2 (OLI) uses ~48% less energy per cycle vs. V1 (custom 3 kW motor).
```

## 7. Hub System Forces (Unchanged from V1)

### 7.1 Available Force

```
NEMA 42 motor:        ~15 Nm
Gearbox (PLPE120):    40:1, η = 90%
Output torque:         15 × 40 × 0.90 = 540 Nm

Sprocket (15T, 10B-2): R = 37.9 mm
Chain force:           540 / 0.0379 = 14,250 N ≈ 14.3 kN
```

### 7.2 Required Forces

| Operation            | Force Needed | Notes                              |
|----------------------|-------------|------------------------------------|
| Push-in (vibration ON) | 0.5–1.5 kN | Vibration does most of the work   |
| Pull-out             | 2.0–4.0 kN  | Full friction, no vibration        |
| Head weight hold     | ~0.4 kN     | Static (42 kg head assembly)       |

Safety factor: 14.3 / 4.0 = **3.6×** ✓

### 7.3 Hub Speed

```
Motor: 600 rpm → Output: 15 rpm → Chain speed: 59.5 mm/s ≈ 60 mm/s
```

## 8. Resonance & Skip Frequencies

### 8.1 System Resonances

| Component              | Est. Natural Freq. | Action              |
|------------------------|--------------------|-----------------------|
| Isolator mounts        | 8–12 Hz            | By design (isolation) |
| Frame (mast bending)   | 15–25 Hz           | Below operating range |
| Vibrating plate        | 250–350 Hz         | Above range (verify)  |
| Rod longitudinal       | ~2,090 Hz          | Far above range       |

### 8.2 VFD Skip Frequency Configuration

```
Skip Frequency 1: 8–15 Hz   (isolator resonance zone)
Skip Frequency 2: 15–25 Hz  (frame resonance zone)
Skip Band Width: ±3 Hz around each center

Ramp rate: 50 Hz/s → pass through 0–25 Hz zone in 0.5 s
Operating zone: 50–110 Hz (3,000–6,600 rpm)
```

*Note: No belt resonance to skip (V1 had belt resonance at 40–60 Hz).
V2 eliminates this concern entirely.*

## 9. Summary: Key Component Specifications (V2)

| Component                   | Specification                      | Supplier Region |
|-----------------------------|------------------------------------|-----------------|
| Sonic motors (2×)           | OLI MVE 400/6-HF, 7.2 kg each     | IT/EU           |
| VFD                         | 1.5 kW, 230V 1ph, V/f, 0–400 Hz   | EU              |
| Vibrating plate             | S355J2, 420×300×20 mm + ribs       | Custom/EU       |
| Center column               | 42CrMo4, Ø50×200 mm               | Custom/EU       |
| DT325 adapter               | Steel, custom threaded             | Custom/EU       |
| Rubber isolators (4×)       | M12, 55–65 Shore A, f₀ ~10 Hz     | EU              |
| Hub motor                   | NEMA 42 CL stepper, 20 Nm         | Nanotec/EU      |
| Hub gearbox                 | Neugart PLPE120, 40:1              | DE              |
| Hub chain                   | 10B-2 duplex roller                | EU              |
| Hub sprockets (2×)          | 10B-2, 15T, taper-lock             | EU              |
| Hub driver                  | CL86T-V4.1 or Nanotec C5-E        | EU              |
| Brake                       | 24V power-off EM, 15 Nm           | EU              |
| Frame profiles (2×)         | mk 2004, 50×100×1500 mm           | DE              |
| Linear guides (2×)          | Hiwin HGR20, 1300 mm               | TW/EU           |
| PLC                         | CONTROLLINO MAXI / Arduino Opta    | AT/IT           |

---

*Last updated: 2026-03-15*
