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
The head is yawed 90 degrees about the vertical axis.
The 255 mm shaft axis then points at the mast.
The 154 mm width lies along the plate length.
The 175 mm side stays vertical.
It does not add a serial term to the head.

The documented minimum centre distance is 170 mm.
The layout pitch is 266 mm.
That pitch is TBD.
It keeps both 154 mm widths on the 420 mm plate.
The column flange sits between the motors.
The flange diameter is 80 mm.
The gap between the motor envelopes is 112 mm.

The motor bodies still rise 175 mm above the plate.
They are not stacked on the column.
The rear face of each motor is flush with the rear face of the plate.
That rear face is 10 mm in front of the carriage plate.
The 10 mm gap is a draft value.
The isolators sit in the gap between the motors.
They do not stand under the motor bodies.
The free height is unknown.
It is not in the sum.
The bracket VC-SH-1350 takes the pull-out load.
The sizing is in `docs/engineering/CARRIAGE-BRACKET.md`.

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
The assembly shows a 40 mm placeholder between the motors.
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
| isolator_diameter_mm | 16 mm | Placeholder in the gap between the motors. |
| rail_section_width_mm | 20 mm | Hiwin HGR20R published width WR. The solid is the envelope. |
| rail_section_height_mm | 17.5 mm | Hiwin HGR20R published height HR. The solid is the envelope. |
| runner_pitch_mm | 200 mm | Centre distance of the two HGH20CA blocks on one rail. Not in the BOM. |
| head_front_gap_mm | 10 mm | Draft gap from the carriage plate to the motor rear face. The plate rear is flush with that face. |
| nema42_body_length_mm | 180 mm | NEMA 42 body length. The 110 mm frame is documented. |
| brake_length_mm | 40 mm | Envelope of VC-HB-3000. The catalogue number is unknown. |
| coupling_diameter_mm | 65 mm | Envelope of VC-HB-2400. The bore pair is unknown. |
| coupling_length_mm | 50 mm | Envelope of VC-HB-2400. The bore pair is unknown. |
| pillow_length_mm | 30 mm | UCP 206 envelope along the shaft. The 30 mm bore is selected. |
| pillow_width_mm | 70 mm | UCP 206 envelope. The housing outline was not downloaded. |
| pillow_height_mm | 45 mm | UCP 206 envelope. The housing outline was not downloaded. |
| chain_section_x_mm | 16 mm | Strand thickness. The pitch is 15.875 mm. The link CAD was not downloaded. |
| chain_section_y_mm | 32 mm | Strand width for duplex 10B-2. The link CAD was not downloaded. |
| rail_bottom_offset_mm | 100 mm | From the bottom of the profile to the bottom of the rail. |
| rib_centre_x_mm | 170 mm | Weld position of VC-SH-1302 from the rod axis. |
| shoe_passage_radial_clearance_mm | 1 mm | Old layout bore. The machine pose uses the 83 mm casing bore instead. |
| column_passage_radial_clearance_mm | 5 mm | Layout bore in the top plate. The bore position is unknown. |
| string_axis_x_mm | 0 mm | Rod axis on the plates. Zero is the plate centre. |
| string_axis_y_mm | 0 mm | Rod axis on the plates. Zero is the plate centre. |

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
The schematic study puts the string through the plate centre.
The machine pose does not.
The 400 mm blank is shifted forward.
Its rear face is flush with the profile rear faces.
It still covers both profiles.
An 83 mm bore is cut on the rod axis.
That bore is the closed guide from VC-FR-4500.
It guides the 82.55 mm casing VC-GP-7100.
The radial clearance is (83 − 82.55) / 2 = 0.225 mm.
The cutting shoe is 87.63 mm outside.
A closed 83 mm bore blocks the shoe.
Stefan deferred the shoe passage.
The open point is a split or removable bushing.
The bore diameter stays 83 mm.

## Assembly pose

The study solid is `cad/export/step/VC-ASM-0000-layout.step`.
It is not a BOM part.
Do not manufacture from it.
Each solid keeps its part number in the STEP name.
FreeCAD 1.1 reads those names.
The mast axis in the file is +Z.
The reference directions do not use a negative zero.

Each profile is yawed 90 degrees about its own vertical axis.
The 100 mm side then lies along X.
The 50 mm side lies along Y.
The rail sits on the +X face.
That face points at the rod.
The rod axis is at X = 227.5 mm.
The motor rear face is flush with the plate rear face.
The draft gap from the carriage plate to that face is 10 mm.
The rail face ends at X = 67.5 mm.
The overhang from that face to the rod axis is 160.0 mm.

Four Hiwin HGH20CA blocks engage the two rails.
The selected block is HGH20CA.
H is 30 mm, W is 44 mm and L is 77.5 mm.
The block pitch on one rail is 200 mm.
That pitch is TBD.
The guided travel is 1022.5 mm.
`STROKE_POSITION_MM` is the travel of the lower block from the rail bottom.
The start value is 1022.5 mm.
That is the top of the travel.
The upper block then ends on the rail top at 1415 mm.
The same solids at stroke 0, at mid travel 511.2 mm and at the top do not overlap.

The volume behind the profile rear faces is reserved for the machine tilt mechanism.
Those faces are the plane X = −50 mm.
No chain strand, sprocket, shaft, gearbox, brake or motor enters X < −50 mm.
The rear stiffener VC-FR-4195 is the one exception.
It is a 4 mm sheet on the rear face, from X = −54 mm to X = −50 mm.
It covers only the band above the rails, from Z = 1430 mm to the profile top.
The tilt mechanism must clear that sheet.
The bottom plate and the gearbox are flush with X = −50 mm.
The gearbox top is at Z = −2 mm, below the plate.

The chain lift is VC-ASM-2000, not the VC-ASM-8100 actuators.
Both chain strands, the drive sprocket and the idler sprocket sit in the profile gap.
The shaft axis is the mast mid-plane, X = 0.
The axis runs along Y and stops before the inner faces.
The rear strand stays at X = −45.9 mm, 4.1 mm in front of the rear face.
The sprocket disk spans X = −41.5 mm to 41.5 mm.
The NEMA 42 motor, the brake and the PLPE120 gearbox are parallel to that shaft.
They sit below the bottom plate.
A 120 mm gearbox on the chain axis would cross the rear face, so its axis is at X = 10 mm.
The housing rear face is then flush with the profiles.
VC-HB-2110 is the draft bracket and the draft drop-drive envelope between the two axes.
The gear teeth are not selected.
A cut mk 2004 bar, VC-FR-4180, spans the clear gap between the inner faces.
It sits between the chain strands at mid height.
At the 300 mm pitch that cut length is 250 mm.
The two uprights stay 1500 mm.
The idle sprocket sits on a shaft above the profile ends.
Two bearing blocks, VC-HB-2830, bolt to those ends.
Each block has a slotted seat and a tension screw.
The top steel plate VC-FR-4400 is not fitted in this pose.
The blank stays on the BOM.
Two 4 mm sheets, VC-FR-4190 on the front face and VC-FR-4195 on the rear face, bolt to both profiles above the rails.
They replace the stiffness the top plate gave.
Bent 4 mm gussets still tie the profiles at the bottom, at mid height and at the top.
The gusset webs sit between the chain strands.
The sprocket envelope uses the published 83 mm tip diameter.
The pitch radius is the documented 37.9 mm.
The gearbox envelope is the published PLPE120 two-stage minimum, 120 mm by 219.5 mm.
The NEMA 42 frame is 110 mm.
The body length is TBD.

A file in `cad/vendor/<part-id>/*.step` replaces the envelope for that part.
The solid is recentered and placed with the envelope pose.
A missing file keeps the envelope.
No vendor STEP is in this revision.

The vibrating plate bottom is at the same height as the lower guide block.
The plate does not hang below the carriage.
That pose lifts the shoe tip by 70 mm, to Z = −433.7 mm.
The parameter chain still adds the head and the carriage in series.
The required height is still 1761.2 mm.
The deficit against the 1300 mm stroke is still 461.2 mm.
Moving the head up does not remove a term from that sum.
The string is still longer than the distance down to the ground line.
Ground clearance stays in the required height.
It is not a shift of this pose.

The bottom plate meets the profiles on a face.
The solids do not share a volume.
At the TBD pitch of 300 mm the profiles overhang the bottom plate by 25 mm.
The length study still subtracts the 12 mm top-plate blank.
The machine pose does not mount that plate.

Clearances below use that TBD pitch and the draft 10 mm front gap.
Do not treat them as a measured fit.
The shoe tip is below the profiles, so the shoe distance includes that vertical gap.
The head clears the rails, the profiles and the gussets at stroke 0, at mid travel and at the top.

| Pair | Clearance | Note |
|---|---|---|
| Shoe to nearest profile | 407.4 mm | 3D distance. The tip is below the mast. It was 471.7 mm before the head moved up. |
| Casing to nearest profile | 175.8 mm | The casing passes the mast height. |
| Casing to the 83 mm bore wall | 0.225 mm | Radial clearance on the 82.55 mm casing. The bore is unchanged. |
| Rod axis past the rail face | 160.0 mm | Overhang from the rail to the rod. |
| Motor envelope to carriage | 10.0 mm | Draft gap at the motor rear face. |
| Motor to nearest profile | 50.0 mm | No collision. |
| Motor to nearest rail | 32.5 mm | No collision. |
| Vibrating plate to nearest profile | 50.0 mm | The plate rear is flush with the motors. |
| Vibrating plate to nearest rail | 32.5 mm | The plate shares the guide-block height. |
| Carriage to chain strand | 0.0 mm | The lug meets the front strand on a face. |
| Rear chain strand to the rear face | 4.1 mm | The strand stays in the gap, at X = −45.9 mm. |

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
9. Usable stroke. The model travel is 1022.5 mm because two 77.5 mm blocks sit 200 mm apart on the 1300 mm rail. The 200 mm pitch is TBD.
10. Centre distance of the two mast profiles. The rod is in front of the rails. The 300 mm pitch is TBD.
11. Front gap from the carriage plate to the motor rear face. The model uses a draft gap of 10 mm. The plate rear is flush with that face.
12. NEMA 42 catalogue number and body length. The frame is 110 mm. The model uses a TBD length of 180 mm.
13. Brake catalogue number, coupling bores, pillow-block outline and chain-link section.
14. Weld position of the two ribs VC-SH-1302.

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
The bracket check is `docs/engineering/CARRIAGE-BRACKET.md`.
The views are in `cad/export/renders/`.
Do not manufacture from the STEP files.
`MAST-LAYOUT` is a document name.
It is not a part number.
