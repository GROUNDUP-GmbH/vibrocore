# Vibrocore — Open-Source Compact Electric Sonic Soil Sampler

An open-source, battery-powered, compact sonic vibro-corer for undisturbed soil sampling
(bulk density / core probes) — compatible with Geoprobe DT325 core tubes.

**Company:** Ground UP GmbH · Vienna, Austria
**License:** CERN-OHL-S-2.0 (Hardware) / MIT (Software)
**Status:** Active Development (2026)

---

## What Is This?

Vibrocore is a field-deployable soil sampling machine that uses **high-frequency axial vibration**
(sonic drilling principle) to drive core tubes into the ground with minimal sample disturbance.
Unlike conventional percussion/hammer systems, the sonic method *liquefies* the thin boundary
layer around the tube — reducing friction dramatically and preserving soil structure.

### Key Specs (Target)

| Parameter               | Value                              |
|-------------------------|------------------------------------|
| Core tube               | Geoprobe DT325 (3.25″ OD, 48″)   |
| Sampling depth          | 1.0 m (single rod)                |
| Sonic head frequency    | 90 – 120 Hz (variable)            |
| Axial dynamic force     | ~8 kN peak                         |
| Hub drive               | NEMA 42 closed-loop stepper        |
| Hub force (pull-out)    | ≥2.5 kN (1:1 chain) / ≥5 kN (2:1) |
| Power                   | 48 V LiFePO4 or Instagrid ONE     |
| Frame                   | mk 2004 aluminium profile 50×100   |
| Machine height          | 1.50 – 1.70 m                      |
| Mobility                | UTV-mounted with tilt mechanism    |
| Positioning             | viDoc RTK + AR navigation          |

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    VIBROCORE SYSTEM                   │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │  CONTROL │   │  SONIC HEAD  │   │  HUB SYSTEM  │ │
│  │  (PLC)   │──▶│  (Vibration) │   │  (Lift/Push) │ │
│  └────┬─────┘   └──────┬───────┘   └──────┬───────┘ │
│       │                │                   │         │
│       │         ┌──────┴───────┐   ┌──────┴───────┐ │
│       │         │  1 Motor     │   │  NEMA 42     │ │
│       │         │  2 Eccentric │   │  + Gearbox   │ │
│       │         │  Shafts ⊥    │   │  + Chain     │ │
│       │         │  to rod axis │   │  + Carriage  │ │
│       │         └──────────────┘   └──────────────┘ │
│       │                                              │
│  ┌────┴──────────────────────────────────────────┐  │
│  │              POWER SYSTEM                      │  │
│  │  48V LiFePO4 / Instagrid ONE (230V AC)        │  │
│  │  + VFD (sonic) + DC PSU (hub) + DC/DC (ctrl)  │  │
│  └───────────────────────────────────────────────┘  │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │              FRAME & MOBILITY                  │  │
│  │  mk 2004 Al-profiles · steel end plates        │  │
│  │  linear guides · tilt mechanism · UTV mount     │  │
│  └───────────────────────────────────────────────┘  │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │              POSITIONING                       │  │
│  │  viDoc RTK (cm accuracy) · AR waypoint nav     │  │
│  │  GPS antenna on sonic head · WLAN relay        │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Sonic Head — The Core Innovation

The sonic head follows the principle described in Šporin & Vukelić (2017) and the
Extrica/Wang et al. (2015) vibration head paper:

- **Two eccentric shafts perpendicular to the rod axis**
- Counter-rotating via 1:1 synchronisation (timing belt or gears)
- Horizontal force components cancel; vertical (axial) components add up
- Driven by a single motor through a primary drive stage
- Adjustable eccentric masses for tuning force amplitude
- Center column / adapter shaft connects to the DT325 probe rod below

```
        SIDE VIEW (schematic)               FRONT VIEW (schematic)

     ┌─── Motor ───┐                      ┌──────────────┐
     │   (above)    │                      │   Bearing    │
     └──────┬───────┘                      │   Block      │
            │ timing belt                  ├──────────────┤
    ┌───────┴────────┐                     │ ╔══════════╗ │
    │  Shaft A  ←──→ │  Shaft B            │ ║ Eccentric║ │
    │  (CW)    gears  │  (CCW)             │ ║  Mass    ║ │
    │  ●───────────●  │                    │ ╚══════════╝ │
    └───────┬────────┘                     ├──────────────┤
            │ Center Column                │   Bearing    │
            │ (Adapter Shaft)              │   Block      │
            │                              └──────┬───────┘
            │                                     │
     ┌──────┴──────┐                        Center Column
     │  DT325 Rod  │                              │
     │  (82.55 mm) │                        DT325 Rod
     │             │
     └─────────────┘

  Eccentric shaft axes are PERPENDICULAR to the rod axis.
  This maximises axial amplitude along the drilling direction.
```

### Dimensioning (Starting Point)

| Parameter                    | Value                    |
|------------------------------|--------------------------|
| Center column Ø              | 50 mm                    |
| Eccentric shaft Ø            | 30 mm                    |
| Shaft center-to-center       | 200 mm                   |
| Eccentric disc OD            | 140 mm                   |
| Eccentric disc width         | 20 – 30 mm              |
| Eccentricity (e)             | 10 mm (adjustable)       |
| Eccentric mass per shaft     | 1.0 kg (adjustable)      |
| Bearing spacing per shaft    | 100 mm                   |
| Bearing type                 | Cylindrical roller NJ    |
| Target frequency             | 90 – 110 Hz              |
| Peak axial force             | ~8 kN                    |
| Head housing width           | ~280 – 340 mm            |
| Head housing height          | ~160 mm                  |

**Force calculation** (two counter-rotating eccentrics):

```
F_peak = 2 · m_e · e · ω²

where  ω = 2π · f

At f = 100 Hz, e = 10 mm, m_e = 1.0 kg:
  ω ≈ 628 rad/s
  F ≈ 2 × 1.0 × 0.01 × 628² ≈ 7,890 N ≈ 7.9 kN
```

---

## Hub System (Lift / Push)

| Parameter           | Value                              |
|---------------------|------------------------------------|
| Motor               | NEMA 42 closed-loop stepper        |
| Gearbox             | Neugart PLPE120, i=40              |
| Drive               | Endless duplex chain 10B-2         |
| Sprocket            | 10B-2, 15–18 teeth, taper-lock     |
| Coupling            | R+W EKH elastomer (torque only)    |
| Drive shaft         | 25–30 mm, separately bearing-mounted |
| Brake               | 24 V power-off electromagnetic     |
| Controller          | Nanotec C5-E or CL86T-V4.1        |
| Speed (est.)        | ~60 mm/s (at 40:1, 600 rpm motor)  |
| Pull-out force      | ~2.0–2.6 kN (1:1 chain, 90 Nm nom) |

### Safety Features

- Closed-loop encoder prevents step loss under load
- Power-off brake holds carriage when de-energised
- Upper + lower limit switches
- Current monitoring for stone detection (auto-stop)
- Emergency stop circuit

---

## Frame

- 2× mk 2004 aluminium profile 50×100×1500 mm (left + right)
- Steel end plates top and bottom (force introduction on tension)
- Front: linear guide rails for sonic head carriage
- Rear: tilt mechanism for transport / horizontal storage
- Bottom steel plate: rod guide hole + NEMA 42 mount + profile base
- All loads in tension along profile long axis
- UTV mounting points on bottom plate

---

## Power System

### Phase 1 — PoC / Development
- **Instagrid ONE max** (230V AC, 3.6 kW cont., 18 kW peak, 2.1 kWh)
- VFD for sonic motors (230V 1ph → 3ph variable frequency)
- DC PSU (230V AC → 48–60V DC) for hub stepper
- DC/DC converters for 24V (brake, relays) and 5V/12V (control)

### Phase 2 — Series / Field
- 48V LiFePO4 main battery (30–50 Ah)
- 100A+ BMS
- DC bus architecture with proper fusing and contactors
- Integrated charging from mains or generator

---

## Control System

- **PLC/Controller:** CONTROLLINO or Arduino Opta (industrial, Arduino-compatible)
- **Hub driver:** Nanotec C5-E-2-09 or Leadshine CL86T-V4.1
- **Sonic VFD:** compact frequency inverter (230V class)
- **Inputs:** limit switches, current sensors, emergency stop, mode selector
- **Outputs:** motor enable, brake release, VFD start/stop/frequency
- **Communication:** WLAN to tablet (viDoc integration)

### Operating Modes

1. **DT325 Mode** — sonic at 90–100 Hz, full stroke, auto-depth-stop
2. **Auger Mode** — sonic at 110–120 Hz, rotation enabled, for 30 mm nut auger
3. **Manual** — joystick up/down, sonic on/off

---

## Positioning & Data

- **viDoc Light** RTK rover on UTV (cm-level global position)
- **GPS antenna** on sonic head (exact bore point)
- WLAN bridge between head GPS and viDoc
- Auto-logging: GPS coordinates, depth, cycle time, VFD current (soil resistance)
- AR waypoint navigation to pre-calculated sampling points

---

## Repository Structure

```
vibrocore/
├── README.md                    # This file
├── LICENSE                      # CERN-OHL-S-2.0
├── docs/
│   ├── design/
│   │   ├── ARCHITECTURE.md      # System architecture
│   │   ├── SONIC_HEAD.md        # Sonic head design & kinematic analysis
│   │   ├── HUB_SYSTEM.md        # Hub/lift mechanism design
│   │   └── POWER_SYSTEM.md      # Electrical architecture
│   ├── engineering/
│   │   ├── DIMENSIONING.md      # Force/frequency/mass calculations
│   │   ├── BOM.md               # Bill of materials with EU suppliers
│   │   └── RESONANCE.md         # Resonance analysis & skip frequencies
│   └── references/
│       ├── REFERENCES.md        # Academic papers & patents
│       └── (PDFs — not in repo, linked)
├── hardware/
│   ├── sonic-head/              # CAD files, drawings
│   ├── hub-system/              # Hub mechanism drawings
│   ├── frame/                   # Frame assembly
│   └── bom/                     # Structured BOM files
├── firmware/
│   └── control/                 # Arduino/PLC control code
└── scripts/
    └── (calculation scripts, helpers)
```

---

## References

### Academic Papers

1. **Šporin, J. & Vukelić, Ž.** (2017). *Structural drilling using the high-frequency (sonic) rotary method.* RMZ – M&G, Vol. 64, pp. 1–10. DOI: 10.1515/rmzmag-2017-0001
   - Key equations: resonance frequency `f = c / 2l`, power `N = F²·t²·f / 2m`
   - Sonic head diagram (Resodyn Corporation)
   - Comparison: sonic vs. classical core drilling (4× faster progression)

2. **Wang, Y. et al.** (2015). *Design and model analysis of the sonic vibration head.* Journal of Vibroengineering, Vol. 17(5), pp. 2121–2131. [Link](https://www.extrica.com/article/15873)
   - 3D FEM analysis of dual-eccentric vibration head
   - Mathematical model: Lagrange equations for damped forced vibration
   - Natural frequencies, isolation design, experimental validation

3. **Lucon, P.A.** (2013). *Resonance: The Science Behind the Art of Sonic Drilling.* Dissertation, Montana State University.

### Related Open-Source Projects

- [Open-Source Drilling Community](https://github.com/Open-Source-Drilling-Community) — drillstring models
- [ARTS Lab Smart Penetrometer](https://github.com/ARTS-Laboratory/Smart-Penetrometer-with-Edge-Computing-and-Intelligent-Embedded-Systems) — UAV-deployable smart penetrometer
- [NASA USDC](https://ndeaa.jpl.nasa.gov/nasa-nde/usdc/usdc.htm) — Ultrasonic/Sonic Driller/Corer (piezoelectric, different principle)

### Equipment References

- [Geoprobe DT325 System](https://geoprobe.com/) — DT325 probe rods, cutting shoes, liners
- [OLI Vibrators MVE-HF](https://www.olivibra.com/) — high-frequency industrial vibration motors
- [Neugart PLPE Gearboxes](https://www.neugart.com/) — precision planetary gearboxes
- [Nanotec NEMA 42 Steppers](https://www.nanotec.com/) — hybrid stepper motors
- [mk Technology Group](https://www.mk-group.com/) — aluminium profile systems
- [Instagrid ONE](https://instagrid.co/) — portable battery power station

---

## Contributing

This is an active development project by Ground UP GmbH. We welcome contributions:

- **Mechanical engineers** — CAD, FEA, manufacturing drawings
- **Electrical engineers** — power electronics, motor control
- **Firmware developers** — Arduino/PLC control logic
- **Field testers** — soil sampling validation data

Please open an issue before submitting PRs for major changes.

---

## License

- **Hardware:** [CERN Open Hardware Licence Version 2 — Strongly Reciprocal (CERN-OHL-S-2.0)](https://ohwr.org/cern_ohl_s_v2.txt)
- **Software/Firmware:** [MIT License](https://opensource.org/licenses/MIT)
- **Documentation:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

---

*Ground UP GmbH · Iglasegasse 21-23, A-1190 Wien · FN 481220 b*
