# Dimensioning Calculations

All calculations reference Šporin & Vukelić (2017) and Wang et al. (2015).

## 1. Target Parameters

| Parameter                  | Symbol | Target Value      | Source / Justification               |
|----------------------------|--------|-------------------|--------------------------------------|
| Sampling depth             | d      | 1.0 m             | VM0042 minimum 0–30cm; we go deeper  |
| Core tube OD               | D_t    | 82.55 mm (3.25″) | Geoprobe DT325                       |
| Core tube length           | L_t    | 1,219 mm (48″)   | Geoprobe DT325 rod                   |
| Core tube mass (per pair)  | m_t    | 35.4 kg           | Geoprobe PN 201446 (rod pair)        |
| Operating frequency        | f      | 90 – 110 Hz       | Below rod resonance, soil optimum    |
| Peak axial force           | F_peak | ~8 kN             | Sufficient for 1m in agricultural soil|
| Eccentricity               | e      | 10 mm             | Adjustable 5–15 mm                   |
| Eccentric mass per shaft   | m_e    | 1.0 kg            | Adjustable via bolt-on segments      |

## 2. Force Equations

### 2.1 Centrifugal Force (Single Eccentric)

```
F_single = m_e · e · ω²

where  ω = 2π · f
```

### 2.2 Resultant Axial Force (Two Counter-Rotating Eccentrics)

With two eccentrics in anti-phase, horizontal components cancel and vertical add:

```
F_axial(t) = 2 · m_e · e · ω² · cos(ωt)

F_peak = 2 · m_e · e · ω²
```

### 2.3 Calculation Table

| f [Hz] | ω [rad/s] | ω² [rad²/s²] | F_single [N] | F_peak (2×) [N] | F_peak [kN] |
|--------|-----------|---------------|---------------|------------------|-------------|
|     70 |     439.8 |       193,424 |         1,934 |            3,868 |         3.9 |
|     80 |     502.7 |       252,672 |         2,527 |            5,054 |         5.1 |
|     90 |     565.5 |       319,726 |         3,197 |            6,394 |         6.4 |
|    100 |     628.3 |       394,784 |         3,948 |            7,896 |         7.9 |
|    110 |     691.2 |       477,557 |         4,776 |            9,552 |         9.6 |
|    120 |     753.9 |       568,363 |         5,684 |           11,368 |        11.4 |

**Parameters:** m_e = 1.0 kg, e = 0.010 m

### 2.4 Adjustable Eccentricity Effects

With e = 5 mm (minimum):

| f [Hz] | F_peak [kN] |
|--------|-------------|
|    100 |         3.9 |
|    110 |         4.8 |

With e = 15 mm (maximum):

| f [Hz] | F_peak [kN] |
|--------|-------------|
|    100 |        11.8 |
|    110 |        14.3 |

**This 3:1 force range (e=5 to e=15) combined with VFD frequency control gives a
total dynamic range of approximately 1:10 — from 3.9 kN (100 Hz, e=5) to 14.3 kN
(110 Hz, e=15).**

## 3. Eccentric Rotor Geometry

### 3.1 Design Approach: Segmented Disc with Bolt-On Weights

```
     FRONT VIEW (one rotor disc)

          ┌──── Ø 140 mm ────┐
         ╱                     ╲
        │    ┌───────────┐      │
        │    │  WEIGHT   │      │
        │    │  SEGMENT  │      │
        │    │  (bolt-on)│      │
        │    └───────────┘      │
        │         ┌──┐          │
        │         │○ │ shaft    │
        │         │30│ bore     │
        │         └──┘          │
        │                       │
        │    BASE DISC          │
         ╲   (machined steel)  ╱
          └───────────────────┘

     width: 25 mm
```

### 3.2 Mass Budget

Target: m_e = 1.0 kg total eccentric mass at 10 mm eccentricity.

**Option A — Full unbalance built into disc:**
- Base disc: ~2.5 kg (Ø140 × 25 mm, steel, ρ = 7,850 kg/m³)
- Material removed from one side to create 1.0 kg imbalance at e=10mm
- Permanent imbalance — adjustment only by changing disc

**Option B — Balanced base disc + bolt-on weights (PREFERRED):**
- Base disc: ~2.5 kg (balanced, centered bore)
- 2–4 bolt-on weight segments on one side
- Each segment ~250 g, positioned at r = 40–60 mm from center
- Adjustable: add/remove segments for different m_e values

**Calculation for Option B segment positioning:**

```
Required: m_e · e = 1.0 kg × 10 mm = 10 kg·mm

If weight segments at r_w = 50 mm from shaft center:
  m_weight_total = (m_e · e) / r_w = 10 / 50 = 0.2 kg = 200 g

  → 4 bolt slots: 4 × 50 g segments = 200 g total
  → Add/remove segments: 50g (e≈2.5mm) to 200g (e≈10mm)
  → Or use heavier segments for e=15mm: 4 × 75g = 300g
     300g × 50mm = 15 kg·mm → equivalent e = 15mm at m_e=1.0kg reference
```

### 3.3 Full Mass Calculation (Steel Disc)

```
V_disc = π/4 × D² × w = π/4 × 0.14² × 0.025 = 3.848 × 10⁻⁴ m³
m_disc = ρ × V = 7,850 × 3.848 × 10⁻⁴ = 3.02 kg

With center bore (Ø 30 mm shaft + keyway):
V_bore = π/4 × 0.030² × 0.025 = 1.767 × 10⁻⁵ m³
m_bore = 0.139 kg

Net disc mass ≈ 2.88 kg (balanced base disc)
```

## 4. Bearing Selection

### 4.1 Load Calculation

Each shaft carries one eccentric generating:

```
F_centrifugal = m_e · e · ω² = 1.0 × 0.010 × 628.3² = 3,948 N (at 100 Hz)

Distributed to 2 bearings per shaft:
F_bearing = F_centrifugal / 2 ≈ 1,974 N per bearing

Add rotor weight (disc + shaft):
m_rotor ≈ 3.0 + 1.5 = 4.5 kg → 44 N (negligible vs. dynamic)

Dynamic bearing load ≈ 2,000 N per bearing, rotating at 100 Hz = 6,000 rpm
```

### 4.2 Bearing Life (L10h)

```
Using NJ 206 ECP (SKF):
  C_dyn = 43.6 kN
  C_static = 36.5 kN
  
  p = 10/3 (roller bearing exponent)

  L10 = (C/P)^p = (43,600 / 2,000)^(10/3) = 21.8^3.33

  L10 = 21.8^3 × 21.8^0.33 ≈ 10,360 × 2.83 ≈ 29,319 million revolutions

  At 6,000 rpm:
  L10h = 29,319 × 10⁶ / (60 × 6,000) = 81,442 hours

  → Far exceeds requirements. NJ 205 could also work.
```

### 4.3 Selected Bearings

| Position             | Type        | Designation    | Notes                    |
|----------------------|-------------|----------------|--------------------------|
| Eccentric shafts (4) | Cyl. roller | NJ 206 ECP     | 30×62×16 mm, SKF         |
| Center column (2)    | Deep groove | 6210-2RS       | 50×90×20 mm              |
| Hub drive shaft (2)  | Self-align  | UCP 206        | Pillow block, 30mm bore  |
| Hub idle sprocket    | Deep groove | 6205-2RS       | 25×52×15 mm              |

## 5. Timing Belt Synchronisation

### 5.1 Belt Selection

```
Operating parameters:
  Speed: 6,000 rpm (at 100 Hz motor speed, if direct drive to shafts)
  Power transmitted: ~1.5 kW per shaft
  Center distance: 200 mm

Belt type: HTD 8M (suitable for high-speed, high-torque)

Pulley: 36 teeth, HTD 8M
  Pitch diameter = 36 × 8 / π = 91.67 mm

Belt length calculation:
  L = 2C + π(d₁+d₂)/2 + (d₂-d₁)²/(4C)
  
  For identical pulleys (d₁ = d₂ = 91.67 mm):
  L = 2 × 200 + π × 91.67 = 400 + 287.9 = 687.9 mm
  
  → Standard belt: 688 mm (86T) or 696 mm (87T)
```

### 5.2 Belt Power Rating Check

```
HTD 8M-30 belt (30 mm wide) at 6,000 rpm on 36T pulley:

Power rating per tooth in mesh ≈ 0.35 kW/tooth (from Gates catalog)
Teeth in mesh = 36/2 = 18 (half wrap)
Available power = 18 × 0.35 = 6.3 kW >> 1.5 kW required ✓

30 mm width provides ample safety margin.
20 mm width: ~4.2 kW → still sufficient.
```

## 6. Motor Power & VFD Sizing

### 6.1 Power Required at Eccentrics

```
P_eccentric = F_peak² / (2 · m_system · ω)     [simplified from Eq. 11]

More practical: P = T_friction × ω + P_acceleration

For continuous operation at 100 Hz with negligible acceleration:
  Main losses: bearing friction + belt losses + windage
  
  Bearing friction power (4 bearings):
    P_bearing = 4 × μ × F × d/2 × ω
    μ ≈ 0.002 (roller bearing)
    F ≈ 2,000 N, d/2 = 0.015 m (shaft radius)
    ω = 628 rad/s
    P_bearing = 4 × 0.002 × 2,000 × 0.015 × 628 ≈ 151 W

  Belt friction:
    P_belt ≈ 5% of transmitted power ≈ 100–200 W

  Windage (at 6,000 rpm with Ø140 discs):
    P_windage ≈ 50–100 W (estimate)

  Total friction losses ≈ 300–450 W

  Soil coupling power (actual drilling work):
    Depends heavily on soil type, depth, rod friction
    Estimate: 500–2,000 W during active penetration

  → Total motor power: 1.0–2.5 kW during drilling
  → Motor rated power: 3.0 kW (provides startup headroom)
```

### 6.2 VFD Selection

| Parameter          | Value                              |
|--------------------|------------------------------------|
| Motor rating       | 3.0 kW                            |
| Input voltage      | 230V 1-phase (from Instagrid)      |
| Output             | 3-phase, 0–400 Hz                  |
| Features needed    | V/f control, skip frequencies      |
|                    | DC injection braking               |
|                    | Analog frequency input (0–10V)     |
|                    | RS485 Modbus (optional)            |
| Brand candidates   | Siemens V20, ABB ACS150, Lenze i510|
| Size               | Compact, IP20 minimum              |

## 7. Resonance & Skip Frequencies

### 7.1 System Resonances to Avoid

| Component              | Est. Natural Freq. | Action              |
|------------------------|--------------------|-----------------------|
| Frame (mast bending)   | 10–25 Hz           | Below operating range |
| Isolator mounts        | 15–25 Hz           | By design (isolation) |
| Belt resonance         | 40–60 Hz           | Skip during ramp-up   |
| Housing modes          | 200–500 Hz         | Above operating range |
| Rod longitudinal       | ~2,090 Hz          | Far above range       |

### 7.2 VFD Skip Frequency Configuration

```
Skip Frequency 1: 15–25 Hz (frame/isolator resonance)
Skip Frequency 2: 45–55 Hz (estimated belt resonance)
Skip Band Width: ±3 Hz around each center

Ramp rate: 10 Hz/s (70 Hz → 100 Hz in 3 seconds)
Ramp avoids lingering in skip bands.
```

## 8. Energy Consumption per Cycle

### 8.1 DT325 Core Sampling Cycle

```
Phase 1 — Ramp up sonic (70 → 100 Hz):           3 s × 2.0 kW avg = 6 kJ
Phase 2 — Penetration (1.0 m at 15 mm/s):        67 s × 2.5 kW    = 168 kJ
Phase 3 — Sonic stop (DC brake):                  2 s × 0.5 kW     = 1 kJ
Phase 4 — Extraction (1.0 m at 50 mm/s):         20 s × 0.3 kW    = 6 kJ
Phase 5 — Return to top (0.5 m at 60 mm/s):       8 s × 0.2 kW    = 2 kJ

Total per cycle:                                  ~100 s, ~183 kJ ≈ 0.051 kWh

Hub power (all phases):
  Penetration: 48V × 4A = 192 W × 67s = 12.9 kJ
  Extraction:  48V × 6A = 288 W × 20s = 5.8 kJ
  Return:      48V × 2A = 96 W × 8s   = 0.8 kJ
  Hub total: ~19.5 kJ

Grand total per cycle: ~183 + 20 = 203 kJ ≈ 0.056 kWh
```

### 8.2 Daily Energy Budget (100 cores)

```
100 cycles × 0.056 kWh = 5.6 kWh

Instagrid ONE max: 2.1 kWh → sufficient for ~37 cores per charge
→ Need 3 charges or additional battery for 100 cores/day

48V 50Ah LiFePO4 battery: 2.4 kWh → ~43 cores
→ Combined system or larger battery recommended for high-volume days
```

## 9. Summary: Key Component Specifications

| Component                   | Specification                      | Supplier Region |
|-----------------------------|------------------------------------|-----------------|
| Sonic motor                 | 3.0 kW, 2-pole, IEC 80 frame      | EU              |
| VFD                         | 3.0 kW, 230V 1ph, V/f             | EU              |
| Eccentric shafts (2×)       | 42CrMo4, Ø30×250 mm              | Custom/EU       |
| Eccentric discs (2×)        | S355J2, Ø140×25 mm, machined      | Custom/EU       |
| Shaft bearings (4×)         | SKF NJ 206 ECP                     | EU              |
| Timing belt                 | HTD 8M-30, 688 mm                  | Gates/EU        |
| Timing pulleys (2×)         | 36T HTD 8M, Ø92 mm, Al 7075       | Custom/EU       |
| Hub motor                   | NEMA 42 CL stepper, 20 Nm         | Nanotec/EU      |
| Hub gearbox                 | Neugart PLPE120, 40:1              | DE              |
| Hub chain                   | 10B-2 duplex roller                | EU              |
| Hub sprockets (2×)          | 10B-2, 15T, taper-lock             | EU              |
| Hub driver                  | CL86T-V4.1 or Nanotec C5-E        | EU              |
| Brake                       | 24V power-off EM, 15 Nm           | EU              |
| Frame profiles (2×)         | mk 2004, 50×100×1500 mm           | DE              |
| Linear guides (2×)          | Hiwin HGR20, 1300 mm               | TW/EU           |
| Rubber isolators (4×)       | M12, 70 Shore A, neoprene          | EU              |
| PLC                         | CONTROLLINO MAXI / Arduino Opta    | AT/IT           |

---

*Last updated: 2026-03-15*
