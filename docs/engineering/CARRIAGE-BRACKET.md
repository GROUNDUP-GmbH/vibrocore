# Vibration-motor bracket VC-SH-1350

Draft sizing.
Not a released calculation.
Do not manufacture from this note.
The bracket holds the two vibration motors on the carriage.
Pull-out is the governing case.
Push-in is smaller.

## Loads

The allowable continuous pull is 4.5 kN.
That is the chain working load in `docs/engineering/PULL_FORCE.md`.
The load cell VC-PN-9300 is rated 0 to 5 kN.
This check uses 5 kN.
That is the top of the load-cell range.
It is above the allowable chain pull.

Push-in with the vibrators running is 0.5 to 1.5 kN.
Each OLI MVE 400/6-HF is rated 4 kN.
Those motor forces are alternating.
This note does not add them to the 5 kN pull as a second static load.
A factor of 3 on the pull is the allowance used here.
That factor is not a fatigue calculation.

The withdrawn 14.3 kN figure is not used.
That torque is above the gearbox rating.

## Geometry used in the check

The rod axis is at X = 227.5 mm.
The carriage plate is 10 mm thick.
Its mid-plane is at X = 85 mm.
The lever arm is 227.5 − 85 = 142.5 mm.

Four M12 bolts, grade 8.8, clamp the bracket to that plate.
The vertical pitch is 160 mm.
Two bolts sit 80 mm above the group centre.
Two bolts sit 80 mm below it.
ISO 898-1 gives a proof stress of 580 MPa.
The tensile stress area of an M12 screw is 84.3 mm².
The proof load is 580 × 84.3 = 48.9 kN.

Two gussets carry the same moment in bending.
Each gusset is 8 mm thick and 80 mm high.
The section modulus of one gusset is t × h² / 6 = 8533 mm³.
The steel is S355.
The yield used here is 355 MPa for thickness up to 16 mm.
These thicknesses are draft sizes.
They are not shop measurements.

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
The bolts are not the governing part.

Bending in one gusset, the two gussets sharing the moment:

```text
σ = (M / 2) / 8533 mm³ = 41.7 MPa
```

With the factor of 3 the stress is 125 MPa.
125 MPa is below the 355 MPa yield.
The same check at the 4.5 kN working pull is 37.6 MPa, or 113 MPa with the factor of 3.

## What this check does not cover

It does not cover fatigue from the 4 kN motors.
It does not cover weld size.
It does not cover prying.
The numbers come from `cad/models/carriage_bracket.py`.
Repeat the check if the rod axis or the bolt pitch changes.
