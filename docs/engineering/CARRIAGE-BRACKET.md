# Vibration-motor bracket VC-SH-1350

This note sizes the bracket.
The calculation is not released.
Do not make the part from this note.
The bracket carries both vibration motors on the carriage.
Pull-out governs the check.
The push-in load is lower.

## Loads

`docs/engineering/PULL_FORCE.md` sets the allowable continuous pull at the chain working load, 4.5 kN.
VC-PN-9300 is a load cell with a rating of 0 to 5 kN.
This check uses 5 kN.
That value is the top of the load-cell range.
That value sits above the allowable chain pull.

With the vibrators running, push-in is 0.5 to 1.5 kN.
Each OLI MVE 400/6-HF has a rating of 4 kN.
Those motor forces alternate.
This note does not add the motor forces to the 5 kN pull as a second static load.
The allowance in this note is a factor of 3 on the pull.
That factor is not a fatigue calculation.

This note does not use the withdrawn 14.3 kN figure.
That torque sits above the gearbox rating.

## Geometry used in the check

The rod axis is at X = 227.5 mm.
The carriage plate is 10 mm thick.
The mid-plane of the plate is at X = 85 mm.
The lever arm is 227.5 − 85 = 142.5 mm.

Four M12 bolts, grade 8.8, clamp the bracket to that plate.
The vertical pitch is 160 mm.
Two bolts sit 80 mm above the centre of the group.
Two bolts sit 80 mm below that centre.
ISO 898-1 gives a proof stress of 580 MPa.
The tensile stress area of an M12 screw is 84.3 mm².
The proof load is 580 × 84.3 = 48.9 kN.

Two gussets carry the same moment in bending.
Each gusset is 8 mm thick and 80 mm high.
The section modulus of one gusset is t × h² / 6 = 8533 mm³.
The steel is S355.
This check uses a yield of 355 MPa for thickness up to 16 mm.
These thicknesses are draft sizes.
They are not measurements from the shop.

## Hand calculation

Moment at 5 kN:

```text
M = 5000 N × 142.5 mm = 712500 N·mm
```

Tension in one upper bolt, four bolts at ±80 mm:

```text
T = M × 80 / (4 × 80²) = 2227 N
```

2227 N is 4.6 percent of the 48.9 kN proof load.
Shear is smaller.
The bolts do not govern the check.

Bending in one gusset, the two gussets sharing the moment:

```text
σ = (M / 2) / 8533 mm³ = 41.7 MPa
```

With the factor of 3 the stress is 125 MPa.
125 MPa is below the 355 MPa yield.
The same check at the 4.5 kN working pull is 37.6 MPa.
With the factor of 3 that stress is 113 MPa.

## What this check does not cover

The check does not cover fatigue from the 4 kN motors.
The check does not cover the weld size.
The check does not cover prying.
The numbers come from `cad/models/carriage_bracket.py`.
Repeat the check if the rod axis changes.
Repeat the check if the bolt pitch changes.
