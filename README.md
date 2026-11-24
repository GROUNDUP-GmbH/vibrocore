# Vibrocore — Open-Source Compact Electric Sonic Soil Sampler

- Vibrocore is an open-source machine.
- The machine takes power from the battery.
- The machine is the compact sonic vibro-corer.
- The machine takes the soil sample.
- The sample stays undisturbed.
- The sample is for bulk density.
- The sample is also for the core probe.
- The machine drives the 3.25 in Geoprobe casing.

- The firm is Ground UP GmbH in Vienna, Austria.
- The hardware licence is CERN-OHL-S-2.0.
- The software licence is MIT.
- Development is active in 2026.

---

## What Is This?

- Vibrocore is the machine for the soil sample in the field.
- The machine uses vibration.
- The vibration is axial.
- The frequency of that vibration is high.
- This principle is sonic drill.
- The vibration drives the core tubes into the ground.
- The sample stays undisturbed.
- The percussion system hits the tube.
- The hammer system also hits the tube.
- The sonic method is different.
- The method turns the thin layer at the tube into the fluid.
- Friction at the tube falls.
- The structure of the soil stays.

### Key Specs (Target)

| Parameter               | Value                              |
|-------------------------|------------------------------------|
| Casing                  | Geoprobe 3.25 in x 48 in rod, part 201446 |
| Sampling depth          | 1.0 m (single rod)                |
| Sonic head              | 2× OLI MVE 400/6-HF (counter-rot.)|
| Vibration frequency     | ~100 Hz at 6,000 rpm (VFD-tunable) |
| Axial dynamic force     | ~8 kN peak (2× 4 kN)              |
| Sonic power draw        | ~1.2 kW (2× 0.58 kW)              |
| Hub drive               | Siemens 1FL2104 + PLE120-040 + ROTEX 28 |
| Allowable pull force    | 4.5 kN (10B-2 working load)        |
| Power                   | Instagrid ONE max (230V AC, 2.1 kWh)|
| Frame                   | mk 2004 aluminium profile 50×100   |
| Machine height          | 1.50 – 1.70 m                      |
| Mobility                | UTV-mounted with tilt mechanism    |
| Positioning             | viDoc RTK + AR navigation          |
| Energy per core         | ~0.029 kWh (~72 cores per charge)  |

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
│       │         │  2× OLI MVE │   │  1FL2104     │ │
│       │         │  400/6-HF   │   │  + PLE120    │ │
│       │         │  counter-   │   │  + ROTEX 28  │ │
│       │         │  rotating   │   │  + chain     │ │
│       │         └──────────────┘   └──────────────┘ │
│       │                                              │
│  ┌────┴──────────────────────────────────────────┐  │
│  │              POWER SYSTEM                      │  │
│  │  48V LiFePO4 / Instagrid ONE (230V AC)        │  │
│  │  + VFD (sonic) + S200 (lift) + DC/DC (ctrl)   │  │
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

## Sonic Head — 2× OLI MVE 400/6-HF

- The sonic head uses two motors.
- The type is OLI MVE 400/6-HF.
- The motors are for industrial vibration.
- The two motors turn in opposite directions.
- Both motors sit on one rigid plate.
- The plate is the Schwingplatte.
- The plate vibrates.
- The principle is in Šporin and Vukelić, 2017.
- The same principle is in the OLI guide for linear vibration.
- Each motor shaft is square to the rod axis.
- The force on the rod is axial.
- The horizontal forces cancel.
- The axial forces add.
- The sum is about 8 kN.
- The motors synchronise on one rigid mass.
- The head does not need the timing belt.
- The VFD sets the frequency.
- The force can change with that frequency.
- The force range is 0.9 to 9.7 kN.
- The OLI weights are eccentric.
- The weights give the second trim.
- You can adjust those weights.

```
    FRONT VIEW (schematic)

    ┌──────────────────────────────────┐   ISOLATION
    │         CARRIAGE (slider)        │   PLATE
    └──┬──────────────────────────┬────┘
       │ rubber                   │ rubber
       │ isolator                 │ isolator
    ┌──┴──────────────────────────┴────┐
    │                                   │
    │  ┌──────────┐   ┌──────────┐    │   VIBRATING
    │  │ OLI MVE  │   │ OLI MVE  │    │   PLATE
    │  │ 400/6-HF │   │ 400/6-HF │    │   (Schwingplatte)
    │  │  ↻ CW    │   │  CCW ↺   │    │
    │  └──────────┘   └──────────┘    │
    │                                   │
    │          ┌───────────┐           │
    │          │  CENTER   │           │
    │          │  COLUMN   │           │
    │          │   Ø 50    │           │
    └──────────┼───────────┼───────────┘
               │           │
               └─────┬─────┘
                     │
              ┌──────┴──────┐
              │  3.25 in rod │
              │  (82.55 mm) │
              └─────────────┘
```

### OLI MVE 400/6-HF Specs

| Parameter              | Value                          |
|------------------------|--------------------------------|
| Centrifugal force      | 408 kgf (~4.0 kN) per motor   |
| Combined axial force   | ~8.0 kN (counter-rotating pair)|
| Operating speed        | 6,000 rpm (via VFD)            |
| Weight                 | 7.2 kg per motor               |
| Dimensions (L×W×H)    | 255 × 154 × 175 mm            |
| Bolt pattern           | 90 × 125 mm, 4× M12           |
| Current                | ~1.45 A at 230V 3-phase        |
| Insulation             | Class H (VPI windings)         |

### Why OLI Instead of Custom Eccentrics?

- The head does not need the custom shaft.
- The head does not need the custom disc.
- The head does not need the timing belt.
- The head does not need an external shaft support.
- The power draw is about 60% lower.
- The motors are reliable in industry.
- Assembly takes 1 to 2 weeks.
- The custom build takes 4 to 8 weeks.
- The cost is about 1,000 € lower.

---

## Hub System (Lift / Push)

| Parameter           | Value                              |
|---------------------|------------------------------------|
| Motor               | Siemens 1FL2104-4AG11-1MC0         |
| Gearbox             | Neugart PLE120, i=40, article 100460948 |
| Chain               | Endless duplex chain 10B-2         |
| Sprocket            | 10B-2, 15 teeth, taper-lock        |
| Coupling            | KTR ROTEX 28, 1:1, to the chain shaft |
| Drive shaft         | 25–30 mm, separately bearing-mounted |
| Brake               | 3.3 Nm brake in the motor          |
| Drive               | SINAMICS S200, 6SL5510-1BB11-0AA0  |
| Speed (est.)        | ~60 mm/s (at 40:1, 600 rpm motor)  |
| Allowable pull force | 4.5 kN (chain working load)       |

### Safety Features

- The encoder has the closed loop.
- The encoder stops loss of the step under the load.
- The brake holds the carriage when power is off.
- The brake torque is in the motor.
- One switch marks the upper end.
- One switch marks the lower end.
- The control reads the current.
- If the current shows the stone, the drive stops.
- An emergency stop is in the circuit.

---

## Frame

- The frame has 2 profiles of mk 2004.
- Each profile is aluminium.
- The section is 50×100 mm.
- The length is 1500 mm.
- One profile is on the left.
- One profile is on the right.
- Steel plates close the top and the bottom.
- Those plates put the tension into the profiles.
- Linear rails on the front carry the sonic head.
- The tilt device on the rear is for transport.
- The same device gives the horizontal store position.
- The bottom plate has the hole for the rod.
- The bottom plate also holds the lift drive.
- The bottom plate is the base for the profiles.
- The loads are tension along the long axis.
- The bottom plate has the mount points.
- The mount is for the UTV.

---

## Power System

### Phase 1 — PoC / Development

- Phase 1 uses an Instagrid ONE max.
- The output is 230 V AC.
- Continuous power is 3.6 kW.
- Peak power is 18 kW.
- Stored energy is 2.1 kWh.
- The VFD feeds the sonic motors.
- The input is 230 V with 1 phase.
- The output is 3 phases at the variable frequency.
- The SINAMICS S200 on 230 V AC drives the 1FL2104.
- DC converters make 24 V for the brake and the relays.
- DC converters also make 5 V and 12 V for the control.

### Phase 2 — Series / Field

- Phase 2 uses the 48 V LiFePO4 battery.
- The capacity is 30 to 50 Ah.
- The rating of the BMS is above 100 A.
- The DC bus has the fuses.
- The DC bus has the contactors.
- Charge can come from the mains.
- Charge can also come from the generator.

---

## Control System

- Option the for the controller is the WAGO PFC200 XTR.
- Option B is the RevPi Connect 4.
- The hub drive is the SINAMICS S200.
- The order code is 6SL5510-1BB11-0AA0.
- The sonic VFD is the compact inverter.
- The inverter class is 230 V.
- Inputs are limit switches and current sensors.
- Inputs also include the emergency stop and the mode selector.
- Outputs enable the motor and release the brake.
- Outputs also start the VFD, stop the VFD, and set the frequency.
- WLAN links the control to the tablet.
- The tablet link is for viDoc.

### Operating Modes

- Casing mode uses the sonic head.
- The frequency is 90 to 100 Hz.
- Casing mode uses the full stroke.
- Casing mode stops at the set depth.
- Auger mode uses the sonic head.
- The frequency is 110 to 120 Hz.
- Auger mode turns the string.
- Auger mode is for the 30 mm nut auger.
3. Manual mode uses the joystick for up and for down.
- Manual mode can start the sonic head.
- Manual mode can stop the sonic head.

---

## Positioning & Data

- The rover is the viDoc Light RTK.
- The rover sits on the UTV.
- The rover gives the global position at cm level.
- The GPS antenna sits on the sonic head.
- That antenna marks the bore point.
- WLAN links the head GPS to the viDoc.
- The log stores the GPS coordinates.
- The log stores the depth and the cycle time.
- The log stores the VFD current.
- That current shows the soil resistance.
- AR navigation leads the operator to the sample points.

---



## Repository Structure

```
vibrocore/
├── README.md                    # This file
├── LICENSE                      # CERN-OHL-S-2.0
├── cad/                         # BOM source, STEP/PDF, OdooPLM import (see docs/cad/)
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

## CAD, drawings and Odoo

- Mechanical data is in [`cad/bom/vibrocore.bom.yaml`](cad/bom/vibrocore.bom.yaml).
- The part number is the Odoo internal reference.
- The same number is the OdooPLM code.
- CI checks the BOM.
- CI builds the STEP files and the PDF files.
- CI also builds the Odoo 19 import files.
- The setup notes are in [`docs/cad/CAD_SETUP.md`](docs/cad/CAD_SETUP.md).
- OdooPLM is the product database for design.
- OdooPLM holds the BOM for design, the documents, and the revisions.
- The plain BOM for production is built beside it.
- The install list is in [`docs/cad/ODOOPLM.md`](docs/cad/ODOOPLM.md).
- Open questions on the model go to [`cad/OPEN_POINTS.md`](cad/OPEN_POINTS.md).

```bash
pip install -r tests/requirements.txt -r requirements-cad.txt
python -m cad.tools.cli validate
python -m cad.tools.cli plm-sync
```

## References

### Academic Papers

1. Šporin, J. and Vukelić, Ž. (2017).
- The paper is in RMZ – M&G, Vol. 64, pp. 1–10.
- The DOI is 10.1515/rmzmag-2017-0001.
- The title is about sonic drill.
- The drill is rotary.
- The frequency is high.
- One equation is `f = c / 2l`.
- One equation is `N = F²·t²·f / 2m`.
- The Resodyn diagram shows the sonic head.
- The paper compares two methods.
- One method is sonic drill.
- The other method is core drill.
- Sonic drill is 4 times faster in that comparison.

2. Wang, Y. and others (2015).
- The paper is in Journal of Vibroengineering, Vol. 17(5), pp. 2121–2131.
- The link is [the paper](https://www.extrica.com/article/15873)
- The paper analyses the sonic vibration head.
- The model is 3D FEM of the head with two eccentrics.
- The math uses the equations of Lagrange.
- The case damps the motion.
- The drive forces the vibration.
- The paper gives the natural frequencies.
- The paper gives the isolation design.
- The paper also gives the test check.

3. Lucon, P.A. (2013).
- The work is the dissertation at Montana State University.
- The subject is resonance in sonic drill.



### Related Open-Source Projects

- The project is the [Open-Source Drilling Community](https://github.com/Open-Source-Drilling-Community)
- The project has models of the drill string.
- The tool is the [ARTS Lab](https://github.com/ARTS-Laboratory/Smart-Penetrometer-with-Edge-Computing-and-Intelligent-Embedded-Systems)
- The product is the Smart Penetrometer.
- The tool is for the UAV.
- [NASA USDC](https://ndeaa.jpl.nasa.gov/nasa-nde/usdc/usdc.htm) is an ultrasonic and sonic corer.
- The NASA unit uses the piezo element.
- The NASA principle is different.



### Equipment References

- [Geoprobe](https://geoprobe.com/) makes 3.25 in probe rods and shoes that cut.
- Geoprobe liners are not used.
- [OLI](https://www.olivibra.com/) makes the MVE-HF motors.
- The motors are for industry.
- The frequency is high.
- [Neugart](https://www.neugart.com/) makes the PLE gearbox.
- The gearbox is planetary.
- [Siemens 1FL2 and SINAMICS S200](https://www.siemens.com/) is the lift motor and the drive.
- [mk](https://www.mk-group.com/) makes the profiles.
- The group is Technology Group.
- The profiles are aluminium.
- [Instagrid ONE](https://instagrid.co/) is the portable battery station.

---

## Contributing

- This project is in active development at Ground UP GmbH.
- The project accepts contributions.
- The mechanical contributor can work on CAD, on FEA, and on production sheets.
- An electrical contributor can work on power circuits and on motor control.
- The firmware contributor can work on the control logic.
- The field contributor can bring data from soil samples.
- Open an issue before the large pull request.

---

## License

- The hardware licence is [CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt)
- The full name is the CERN licence.
- The licence is for open hardware.
- The version is 2.
- The form is Strongly Reciprocal.
- The software licence is [MIT](https://opensource.org/licenses/MIT)
- The firmware uses the same MIT licence.
- The documentation licence is [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

---

- The firm is Ground UP GmbH.
- The street is Iglasegasse 21-23.
- The place is A-1190 Wien.
- The register is FN 481220 b.
