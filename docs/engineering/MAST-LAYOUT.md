# Mast stack layout

Document status: preliminary.
This document is a study.
It is not a manufacturing instruction.
The profile length stays 1500 mm.
Do not change VC-FR-4100 from this study.

## Question

The open item is `mast-height-deficit`.
One casing is 1219.2 mm long.
The mast profile is 1500 mm long.
The casing, the sonic head, the cutting shoe and the adapter must stand on that mast.
This study adds those lengths.
It compares the sum with the mast stroke.

## Height chain

The required height is the sum of seven lengths.

1. Ground clearance.
2. Cutting shoe.
3. One casing section.
4. Head-to-casing adapter.
5. Sonic head.
6. Carriage.
7. Top margin.

Required height = ground clearance + shoe + casing + adapter + head + carriage + top margin.

The available mast stroke is 1300 mm.
`firmware/codesys/GVL_PARAMS.st` stores that value as `rMAX_STROKE_MM`.
The comment in that file calls it the physical mast stroke.
The rails VC-HB-3100 are also 1300 mm long.
The margin is the stroke minus the required height.
A negative margin is a deficit.

The 1500 mm profile is a second comparison.
The study does not treat the profile length as the stroke.
The study does not change the profile length.

## Result with the current parameters

Required height: 1936.2 mm.
Mast stroke: 1300 mm.
Deficit against the stroke: 636.2 mm.
Mast profile: 1500 mm.
Deficit against the profile: 436.2 mm.

These numbers use the placeholders in `cad/models/mast_layout.py`.
A new measured length changes the deficit.
Run `python -m cad.tools.cli export` after that change.
The sheet `cad/export/layout/mast-stack.svg` prints the same deficit.

Documented lengths alone, with every TBD length set to 0:

- Casing: 1219.2 mm.
- Column shaft: 200 mm.
- Vibrating plate: 20 mm.
- Motor height: 175 mm.
- Sum: 1614.2 mm.

1614.2 mm is 114.2 mm longer than the 1500 mm profile.
1614.2 mm is 314.2 mm longer than the 1300 mm stroke.
The TBD lengths make the deficit larger.
They do not create it, while the motor height stays in the stack.

## Motor assumption

SONIC_HEAD.md gives the motor envelope as 255 mm x 154 mm x 175 mm.
That drawing calls 175 mm the height.
The motor shafts are perpendicular to the rod axis.
This study adds the 175 mm height to the axial head.
The two motors are not placed.
The centre distance is only a minimum of 170 mm.

Remove 175 mm if the motor height is not axial.
The documented lengths are then 1439.2 mm.
1439.2 mm is 60.8 mm shorter than the 1500 mm profile.
1439.2 mm is 139.2 mm longer than the 1300 mm stroke.
The TBD lengths then decide the fit on the profile.
A fit is still not shown.

## Head term

The head term is one length in the chain.
It is the sum of four lengths.

| Piece | Length | Status |
|---|---|---|
| Column shaft VC-SH-1400 | 200 mm | Documented. The shaft solid does not include the flange. |
| Column flange thickness | 12 mm | TBD. The flange diameter 80 mm is documented. |
| Vibrating plate VC-SH-1301 | 20 mm | Documented. |
| Motor height VC-SH-1100 | 175 mm | Documented envelope height. See the motor assumption. |
| Head total | 407 mm | The flange part of this total is TBD. |

Isolator free height is unknown.
VC-SH-1600 does not give a free height.
This study does not add the isolator height.
The motors are taken as taller than the isolators.
Add the difference if the isolators are taller.

The carriage is a separate term above the head.
Do not use the 10 mm carriage-plate thickness as the carriage height.

## Known values

| Item | Value | Source |
|---|---|---|
| Motor envelope | 255 x 154 x 175 mm | VC-SH-1100, SONIC_HEAD.md |
| Vibrating plate | 420 x 300 x 20 mm | VC-SH-1301 |
| Column shaft | diameter 50 mm, length 200 mm | VC-SH-1400 |
| Column flange diameter | 80 mm | SONIC_HEAD.md |
| Casing length | 1219.2 mm (48 in) | VC-GP-7100 |
| Casing outside diameter | 82.55 mm (3.25 in) | Design documents |
| Casing inside diameter | 66.675 mm (2.625 in) | Decision 2026-11-19 |
| Shoe outside diameter | 87.63 mm (3.45 in) | PN 205449, VC-GP-7200 |
| Profile | 50 x 100 x 1500 mm, two bars | VC-FR-4100 |
| Bottom plate | 400 x 300 x 15 mm | VC-FR-4300 |
| Top plate | 300 x 200 x 12 mm | VC-FR-4400 |
| Carriage plate thickness | 10 mm | VC-HB-3200. Not the chain term. |
| Rail length | 1300 mm | VC-HB-3100 |
| Firmware stroke | 1300 mm | GVL_PARAMS.st |

## TBD values

Each placeholder is named in `cad/models/mast_layout.py`.
The value lets the layout draw.
The value is not a measurement.
The drawing marks each chain placeholder TBD.

| Name | Placeholder | Measure this |
|---|---|---|
| shoe_length_mm | 80 mm | Length of shoe 205449. Ask Geoprobe. The outside diameter is already known. |
| adapter_length_mm | 60 mm | Axial length of VC-SH-1500. Confirm the thread. |
| carriage_height_mm | 80 mm | Axial height of the carriage block. |
| ground_clearance_mm | 50 mm | Gap from the ground line to the shoe tip at the start of the stroke. |
| top_margin_mm | 40 mm | Gap above the carriage for the sprocket, the chain and the upper limit switch. |
| column_flange_thickness_mm | 12 mm | Flange thickness. The 80 mm diameter is known. |

These visual stand-ins are not in the height sum.

| Name | Placeholder | Note |
|---|---|---|
| profile_spacing_mm | 300 mm | Centre distance of the two profiles. Do not claim a shoe clearance from this pitch. |
| adapter_od_mm | 50 mm | Envelope only. The thread is not modelled. |
| carriage width and depth | 160 mm x 120 mm | Plan size only. |

The stroke position along the profile is unknown.
The sprocket diameters are unknown.
The drawing puts the stroke and the profile on the same ground baseline.
That comparison is a length comparison.
It is not a located zone on the mast.

## Other assumptions

The bottom plate and the top plate sit on the profile ends.
The clear opening is 1500 mm - 15 mm - 12 mm = 1473 mm.
SAMPLING.md uses the same assumption.
The profile bar stays 1500 mm long.

The layout places the mast bottom on the ground line.
Stabiliser feet can raise the plate.
Foot height is unknown.
Foot height is not in the sum.

The split carrier sits inside the casing.
The study solid uses the VC-SP-7620 placeholders.
That length is 6 x 100 mm = 600 mm.
Tube length is TBD.
The carrier length is not in the height sum.

The ground body in the STEP file is a datum.
It is not a part.
Its thickness is 0.5 mm.
That thickness is not in the height sum.

The bottom plate is drawn.
The bottom plate is not a term in the seven-length sum.
The string passes through the plate.

## Values Stefan must get

1. Length of cutting shoe 205449. Ask Geoprobe.
2. Axial length of adapter VC-SH-1500, and the thread.
3. Axial height of the carriage block.
4. Required ground clearance at the start of the stroke.
5. Top margin for the sprocket, the chain and the upper limit switch.
6. Column flange thickness.
7. Isolator free height for VC-SH-1600. Confirm that the motors are taller than the isolators.
8. Confirm that the 175 mm motor side is vertical.
9. Usable stroke position between the plates.
10. Centre distance of the two mast profiles. The shoe must pass between the profiles. The outside diameter 87.63 mm is known.

## Options

Do not order a new profile from this study.
Three options stay open.
This study does not select an option.

1. Longer profile.
   The length must exceed the required height.
   The required height is not final until the TBD lengths are measured.
   VC-FR-4100 stays 1500 mm until that decision.

2. Telescopic mast.
   One stage carries the head.
   A second stage adds travel.
   No telescopic part is on the BOM.

3. Two-stage push.
   Drive part of the casing section.
   Then add the next casing length.
   The mast then does not hold the full 1219.2 mm above the ground at one time.
   The joint and the clamp for that sequence are not designed.

## Earlier remainder

SAMPLING.md shows a remainder of 33.8 mm.
That remainder is 1473 mm minus 200 mm minus 20 mm minus 1219.2 mm.
It does not include the motor height.
It does not include the carriage, the shoe, the adapter or the margins.
33.8 mm is not a demonstrated fit.
Use the deficit in this document for `mast-height-deficit`.

## Files

The parameters are in `cad/models/mast_layout.py`.
The sheet is `cad/export/layout/mast-stack.svg`.
The same numbers are in `cad/export/layout/mast-stack.pdf`.
The study solid is `cad/export/layout/mast-stack.step`.
Do not manufacture from the STEP file.
`MAST-LAYOUT` is a document name.
It is not a part number.
