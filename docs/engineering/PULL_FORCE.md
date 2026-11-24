# Allowable pull force

This note takes the place of the two older hub-force figures.
The allowable pull force is **4.5 kN**.
Use that value in every document.
The inputs come from the approved drive data in LIFT-DRIVE-SIZING.md.

## Inputs

| Input | Value | Source |
|---|---|---|
| Chain pitch | 15.875 mm | HUB_SYSTEM.md, DIN 8187, size 10B |
| Sprocket teeth | 15 | HUB_SYSTEM.md and the BOM |
| Pitch radius used below | 38.18 mm | LIFT-DRIVE-SIZING.md. Exact pitch-circle is 38.177 mm. |
| Gear ratio | 40 | Neugart PLE120-040, article 100460948. No extra gear stage. The ROTEX 28 coupling is 1:1. |
| Gearbox efficiency | 0.97 | LIFT-DRIVE-SIZING.md |
| Chain and bearing efficiency | 0.98 | LIFT-DRIVE-SIZING.md |
| Gearbox idle torque at the motor | 0.85 Nm | LIFT-DRIVE-SIZING.md |
| Continuous torque T2D | 195 Nm | LIFT-DRIVE-SIZING.md, Neugart PLE catalogue 2026-10 |
| Cyclic torque T2Z | 230 Nm | LIFT-DRIVE-SIZING.md |
| Maximum torque T2max | 365 Nm | LIFT-DRIVE-SIZING.md |
| Emergency-stop torque T2Stop | 500 Nm | LIFT-DRIVE-SIZING.md |
| Motor, rated / maximum | 3.2 Nm / 10.8 Nm | Siemens 1FL2104-4AG11-1MC0 |
| Drive torque limit | about 6.7 Nm | LIFT-DRIVE-SIZING.md. This limit is the mechanical fuse. |
| Design chain pull | 5.8 kN | LIFT-DRIVE-SIZING.md: 5 kN load-cell rating plus 0.8 kN for the weight above the cell |
| Chain breaking load | about 44.5 kN | HUB_SYSTEM.md |
| Chain working load | about 4.5 kN | HUB_SYSTEM.md, breaking load divided by 10 |
| Load cell rating | 5 kN | VC-PN-9300 |

44.5 kN / 10 = 4.45 kN.
The design note rounds the working load to 4.5 kN.
This note keeps 4.5 kN.

## Formulas

The pitch radius comes from LIFT-DRIVE-SIZING.md:

    R = 38.18 mm

The exact pitch-circle radius is `pitch / (2 x sin(pi / teeth))` = 38.177 mm.

Chain tension comes from the gearbox output torque:

    F = T2 x 0.98 / R

Motor torque uses the same formula as LIFT-DRIVE-SIZING.md:

    T_mot = T2 / (40 x 0.97) + 0.85 Nm

Use metres for R when T2 is in newton-metres.

## Results

| Case | Torque at the gearbox output | Tension at the chain |
|---|---|---|
| T2D continuous | 195 Nm | 5.01 kN |
| T2Z cyclic | 230 Nm | 5.90 kN |
| Drive torque limit 6.7 Nm | 227 Nm | 5.83 kN |
| Design chain pull | 226 Nm | 5.8 kN |
| T2max | 365 Nm | 9.37 kN |
| T2Stop | 500 Nm | 12.83 kN |
| Motor peak 10.8 Nm, do not use | 419 Nm | 10.75 kN |
| Chain working load | — | 4.5 kN |
| Chain breaking load | — | about 44.5 kN |

Do not allow the motor peak of 10.8 Nm.
419 Nm is above T2max (365 Nm).
The motor-peak row uses 10.8 Nm × 40 × 0.97.
That row leaves out the 0.85 Nm idle torque.
The product matches LIFT-DRIVE-SIZING.md.
The result remains conservative.

The chain working load is 4.5 kN.
The pull at the drive torque limit is about 5.83 kN.
The allowable continuous pull force is the lower of those two values.

**Allowable pull force = 4.5 kN.**

## Withdrawn figures

The old 14.3 kN figure used 15 Nm x 40 x 0.90 at the sprocket.
That path used the previous PLPE120 and a motor that the BOM does not list.
Do not use it.

The README line "2.0-2.6 kN at 90 Nm" used 90 Nm at the sprocket and no 40:1 ratio.
Do not use that line.

The 5.80 kN "gearbox nominal tension" came from the previous 220 Nm PLPE120 rating and the older 37.899 mm radius.
Do not use that derivation.
The 5.8 kN figure in LIFT-DRIVE-SIZING.md is the design chain pull (5 kN load cell plus 0.8 kN weight).
Keep that meaning.

## Required pull and margin

HUB_SYSTEM.md still lists a required pull of 2.0-4.0 kN with vibration off.
That figure is a process need.
That figure is not the drive capacity.

Margin of the allowable pull force on the upper required pull:

    4.5 kN / 4.0 kN = 1.13

The margin is small.
The chain breaking load divided by 4.0 kN is about 11.
Do not add that 11 on top of the working-load factor of 10.
The working load already includes that factor.

## Load cell

VC-PN-9300 is an S-type cell rated 5 kN.
The cell sits in the pull path, between the carriage and the casing adapter.

The drive torque limit can put about 5.83 kN into that path.
T2max can put 9.37 kN into that path.
The chain does not stop the rise at 4.5 kN.
The chain breaks near 44.5 kN.

5 kN is below both of those tensions.
A stall can overload the cell.

Decision:

- Keep the 5 kN cell. It matches the soil-force range.
- Add VC-PN-9340, a mechanical bypass in parallel with the cell.
- The bypass must close before 5 kN.
- The bypass must carry 9.37 kN (chain force at T2max).
- Do not select a higher-rated catalogue cell in this revision. No order code was verified.

The code that repeats these formulas is `cad/tools/pull_force.py`.
