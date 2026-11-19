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

The motors sit left and right of the rod.
Their 175 mm height is not in the sum.

Required height: 1761.2 mm.
Mast stroke: 1300 mm.
Deficit against the stroke: 461.2 mm.
Margin against the stroke: -461.2 mm.
Mast profile: 1500 mm.
Deficit against the profile: 261.2 mm.

These numbers use the placeholders in `cad/models/mast_layout.py`.
A new measured length changes the deficit.
Run `python -m cad.tools.cli export` after that change.
The sheet `cad/export/layout/mast-stack.svg` prints the same deficit.

Documented lengths alone, with every TBD length set to 0:

- Casing: 1219.2 mm.
- Column shaft: 200 mm.
- Vibrating plate: 20 mm.
- Sum: 1439.2 mm.

1439.2 mm is 60.8 mm shorter than the 1500 mm profile.
That is a margin against the profile.
1439.2 mm is 139.2 mm longer than the 1300 mm stroke.
The stroke deficit is already present in the documented lengths.
The TBD lengths make that deficit larger.
The TBD lengths also turn the profile margin into the 261.2 mm deficit.

## Motor placement

SONIC_HEAD.md gives the motor envelope as 255 mm x 154 mm x 175 mm.
That drawing calls 175 mm the height.
The shafts stay perpendicular to the rod axis.
The assembly puts both motors on the vibrating plate.
One motor is on the left of the rod.
One motor is on the right of the rod.
The 255 mm side is the shaft axis.
That axis is horizontal.
The 175 mm side stays vertical.
It does not add a serial term to the head.

The documented minimum centre distance is 170 mm.
The layout pitch is 266 mm.
That pitch is TBD.
It keeps both 154 mm widths on the 420 mm plate.
The carriage block sits between the motors.
The lateral gap from each motor to the carriage is 11 mm.
That gap is TBD.

The motor bodies still rise 175 mm above the plate.
They stand beside the carriage.
They are not stacked on the column.
A carriage plate that covers both motors needs isolators taller than 175 mm.
That free height is unknown.
It is not in the sum.

## Head term

The head term is one length in the chain.
It is the sum of three lengths.

| Piece | Length | Status |
|---|---|---|
| Column shaft VC-SH-1400 | 200 mm | Documented. The shaft solid does not include the flange. |
| Column flange thickness | 12 mm | TBD. The flange diameter 80 mm is documented. |
| Vibrating plate VC-SH-1301 | 20 mm | Documented. |
| Head total | 232 mm | The flange part of this total is TBD. |

The motor height is not in this total.
Isolator free height is unknown.
VC-SH-1600 does not give a free height.
This study does not add the isolator height.
The assembly shows a 40 mm placeholder at the plate corners.
That placeholder is not a catalogue height.
Add the real free height if the isolators lift the carriage.

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
| motor_centre_distance_mm | 266 mm | Layout pitch. The documented minimum is 170 mm. |
| motor_to_carriage_gap_mm | 11 mm | Lateral gap from each motor envelope to the carriage block. |
| carriage_width_mm | 90 mm | Derived from the pitch and the lateral gap. Not a measured plate. |
| carriage_depth_mm | 120 mm | Plan size only. |
| isolator_free_height_mm | 40 mm | Not in the height chain. Not a catalogue height. |
| isolator_diameter_mm | 16 mm | Placeholder sized to the strip beside the 255 mm motor. |
| rail_section_width_mm | 20 mm | Series name only. The catalogue section is not in the repository. |
| rail_section_height_mm | 20 mm | Catalogue section is not in the repository. |
| rail_bottom_offset_mm | 100 mm | From the bottom of the profile to the bottom of the rail. |
| rib_centre_x_mm | 170 mm | Weld position of VC-SH-1302 from the rod axis. |
| shoe_passage_radial_clearance_mm | 1 mm | Layout bore in the bottom plate. The bore position is unknown. |
| column_passage_radial_clearance_mm | 5 mm | Layout bore in the top plate. The bore position is unknown. |
| string_axis_x_mm | 0 mm | Rod axis on the plates. Zero is the plate centre. |
| string_axis_y_mm | 0 mm | Rod axis on the plates. Zero is the plate centre. |

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

## Assembly pose

The study solid is `cad/export/step/VC-ASM-0000-layout.step`.
It is not a BOM part.
Do not manufacture from it.
Each solid keeps its part number in the STEP name.
FreeCAD 1.1 reads those names.

The shoe tip is on the ground line.
Ground clearance is still in the required height.
It is not applied in this pose.
The head is not at the top of the stroke.
The rail top is at 1415 mm with the TBD rail offset.
The carriage bottom is at 1591.2 mm.
The carriage is 176.2 mm above the rail top.
The lengths do not allow the tip on the ground and the head on the rail at the same time.

The plates are stacked on the profile ends.
The solids meet on a face.
They do not share a volume.
At the TBD pitch of 300 mm the profiles overhang the bottom plate by 50 mm.
The top plate covers 0 mm of each profile.
The 200 mm top plate cannot seat both profiles if the shoe passes between them.

Clearances below use that TBD pitch.
Do not treat them as a measured fit.

| Pair | Clearance | Note |
|---|---|---|
| Shoe to profile inner face | 56.2 mm | Pitch is TBD. |
| Casing to profile inner face | 58.7 mm | Pitch is TBD. |
| Motor envelope to carriage | 11.0 mm | Lateral gap. TBD. |
| Motor to nearest profile | 82.3 mm | No collision. |
| Motor to nearest rail | 194.3 mm | No collision. |
| Vibrating plate to top plate | 44.2 mm | The head is above the mast. |

No pair of part solids shares more than 1 mm³.
The ground datum is not a part.

The views are:

- `cad/export/renders/VC-ASM-0000-layout-iso.png`
- `cad/export/renders/VC-ASM-0000-layout-side.png`
- `cad/export/renders/VC-ASM-0000-layout-top.png`

## Values Stefan must get

1. Length of cutting shoe 205449. Ask Geoprobe.
2. Axial length of adapter VC-SH-1500, and the thread.
3. Axial height of the carriage block.
4. Required ground clearance at the start of the stroke.
5. Top margin for the sprocket, the chain and the upper limit switch.
6. Column flange thickness.
7. Isolator free height and diameter for VC-SH-1600.
8. Motor centre distance. The minimum is 170 mm. The 266 mm pitch is only a layout placeholder.
9. Usable stroke position between the plates. The rail offset is TBD.
10. Centre distance of the two mast profiles. The shoe must pass between the profiles. The outside diameter 87.63 mm is known.
11. Guide bore position on both plates. The layout uses the plate centre.
12. Rail section. Size 20 is the series name. The catalogue section is not in the repository.
13. Weld position of the two ribs VC-SH-1302.

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
The machine pose is `cad/export/step/VC-ASM-0000-layout.step`.
The views are in `cad/export/renders/`.
Do not manufacture from the STEP files.
`MAST-LAYOUT` is a document name.
It is not a part number.
