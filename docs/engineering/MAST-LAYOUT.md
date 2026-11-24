# Mast stack layout

The status of this document is preliminary.
This file records a study.
This file is not a manufacturing instruction.
The profile length stays 1500 mm.
Do not change VC-FR-4100 because of this study.

## Question

The open item name is `mast-height-deficit`.
One casing is 1219.2 mm long.
The mast profile is 1500 mm long.
The casing, the sonic head, the cutting shoe and the adapter must stand on that mast.
This study adds those lengths.
The study compares the sum with the mast stroke.

## Height chain

Seven lengths add up to the required height.

1. Ground clearance.
2. Cutting shoe.
3. One casing section.
4. Head-to-casing adapter.
5. Sonic head.
6. Carriage.
7. Top margin.

Required height = ground clearance + shoe + casing + adapter + head + carriage + top margin.

The mast stroke that is available is 1300 mm.
`firmware/codesys/GVL_PARAMS.st` stores that value as `rMAX_STROKE_MM`.
The comment in that file calls the value the physical mast stroke.
The rails VC-HB-3100 are also 1300 mm long.
The margin equals the stroke minus the required height.
A negative margin is a deficit.

The 1500 mm profile is a second comparison.
The study does not treat the profile length as the stroke.
The study leaves the profile length unchanged.

## Result with the current parameters

The motors sit on the left of the rod and on the right of the rod.
The sum does not include their 175 mm height.

Required height: 1761.2 mm.
Mast stroke: 1300 mm.
Deficit against the stroke: 461.2 mm.
Margin against the stroke: -461.2 mm.
Mast profile: 1500 mm.
Deficit against the profile: 261.2 mm.

These numbers use the placeholders in `cad/models/mast_layout.py`.
A newly measured length changes the deficit.
Run `python -m cad.tools.cli export` after that change.
The sheet `cad/export/layout/mast-stack.svg` prints the same deficit.

Documented lengths alone, with every TBD length set to 0, are:

- Casing: 1219.2 mm.
- Column shaft: 200 mm.
- Vibrating plate: 20 mm.
- Sum: 1439.2 mm.

1439.2 mm is 60.8 mm shorter than the 1500 mm profile.
That difference is a margin against the profile.
1439.2 mm is 139.2 mm longer than the 1300 mm stroke.
The documented lengths already contain the stroke deficit.
The TBD lengths make that deficit larger.
The TBD lengths also turn the profile margin into the 261.2 mm deficit.

## Motor placement

SONIC_HEAD.md gives the motor envelope as 255 mm x 154 mm x 175 mm.
That drawing names 175 mm as the height.
The shafts stay perpendicular to the rod axis.
The assembly places both motors on the vibrating plate.
One motor sits on the left of the rod.
One motor sits on the right of the rod.
The head is yawed 90 degrees about the vertical axis.
The 255 mm shaft axis then points at the mast.
The 154 mm width lies along the plate length.
The 175 mm side stays vertical.
That side does not add a serial term to the head.

The documented minimum centre distance is 170 mm.
The layout pitch is 266 mm.
That pitch is TBD.
The pitch keeps both 154 mm widths on the 420 mm plate.
The column flange sits between the motors.
The flange diameter is 80 mm.
The gap between the motor envelopes is 112 mm.

The motor bodies still rise 175 mm above the plate.
The motors are not stacked on the column.
The rear face of each motor is flush with the rear face of the plate.
That rear face is 10 mm in front of the carriage plate.
The 10 mm gap is a draft value.
The isolators sit in the gap between the motors.
The isolators do not stand under the motor bodies.
The free height is unknown.
The sum does not include the free height.
The bracket VC-SH-1350 takes the pull-out load.
`docs/engineering/CARRIAGE-BRACKET.md` holds the sizing.

## Head term

The head term is one length in the chain.
Three lengths add up to that term.

| Piece | Length | Status |
|---|---|---|
| Column shaft VC-SH-1400 | 200 mm | Documented. The shaft solid does not include the flange. |
| Column flange thickness | 12 mm | TBD. The flange diameter 80 mm is documented. |
| Vibrating plate VC-SH-1301 | 20 mm | Documented. |
| Head total | 232 mm | The flange part of this total is TBD. |

This total does not include the motor height.
Isolator free height is unknown.
VC-SH-1600 does not give a free height.
This study leaves out the isolator height.
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

`cad/models/mast_layout.py` names each placeholder.
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
| rail_section_width_mm | 20 mm | Hiwin HGR20R published width WR. The STEP mounting face sits on the profile. |
| rail_section_height_mm | 17.5 mm | Hiwin HGR20R published height HR. The STEP mounting face sits on the profile. |
| runner_pitch_mm | 200 mm | Centre distance of the two HGH20CA blocks on one rail. Not in the BOM. |
| head_front_gap_mm | 10 mm | Draft gap from the carriage plate to the motor rear face. The plate rear is flush with that face. |
| servo_body_length_mm | 186.6 mm | Siemens 1FL2104 overall length. The envelope is that square prism. No STEP yet. |
| coupling_diameter_mm | 65 mm | Fallback envelope of VC-HB-2400 when no STEP is present. |
| coupling_length_mm | 50 mm | Fallback envelope of VC-HB-2400 when no STEP is present. |
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
That comparison compares lengths.
That comparison is not a located zone on the mast.

## Other assumptions

The bottom plate and the top plate sit on the profile ends.
The clear opening is 1500 mm - 15 mm - 12 mm = 1473 mm.
SAMPLING.md uses the same assumption.
The profile bar stays 1500 mm long.

The layout places the mast bottom on the ground line.
Stabiliser feet can raise the plate.
Foot height is unknown.
The sum does not include the foot height.

The split carrier sits inside the casing.
The study solid uses the VC-SP-7620 placeholders.
That length is 6 x 100 mm = 600 mm.
Tube length is TBD.
The height sum does not include the carrier length.

The ground body in the STEP file is a datum.
The datum is not a part.
Its thickness is 0.5 mm.
The height sum does not include that thickness.

The drawing includes the bottom plate.
The seven-length sum does not include the bottom plate.
The schematic study puts the string through the plate centre.
The machine pose does not.
The 400 mm blank is shifted forward.
The rear face of the blank is flush with the profile rear faces.
The blank still covers both profiles.
An 83 mm bore is cut on the rod axis.
That bore is the closed guide from VC-FR-4500.
The bore guides the 82.55 mm casing VC-GP-7100.
The radial clearance is (83 − 82.55) / 2 = 0.225 mm.
The cutting shoe is 87.63 mm outside.
A closed 83 mm bore blocks the shoe.
Stefan deferred the shoe passage.
The open point is a split or removable bushing.
The bore diameter stays 83 mm.

## Assembly pose

The study solid file is `cad/export/step/VC-ASM-0000-layout.step`.
That file is not a BOM part.
Do not build a part from it.
Each solid keeps its part number in the STEP name.
FreeCAD 1.1 reads those names.
The mast axis in the file is +Z.
The reference directions do not use a negative zero.

Each profile is yawed 90 degrees about its own vertical axis.
The 100 mm side then lies along X.
The 50 mm side lies along Y.
The rail sits on the +X face.
That face points toward the rod.
The rod axis is at X = 227.5 mm.
The motor rear face is flush with the plate rear face.
The draft gap from the carriage plate to that face is 10 mm.
The rail face ends at X = 67.5 mm.
The overhang from that face to the rod axis is 160.0 mm.

Four Hiwin HGH20CA blocks engage the two rails.
The block in this layout is HGH20CA.
H is 30 mm from the rail mounting face.
W is 44 mm.
The STEP solid is 90.4 mm long.
The block pitch on one rail is 200 mm.
That pitch is TBD.
The guided travel is 1009.6 mm.
`STROKE_POSITION_MM` is the travel of the lower block from the rail bottom.
The start value is 1009.6 mm.
That is the top of the travel.
The upper block then ends on the rail top at 1415 mm.
The same solids at stroke 0, at mid travel 511.2 mm and at the top do not overlap.

The machine tilt mechanism keeps the volume behind the profile rear faces.
Those faces are the plane X = −50 mm.
No chain strand, sprocket, shaft, gearbox, brake or motor goes into X < −50 mm.
The rear sheets VC-FR-4195 and VC-FR-4186 are the exceptions.
Each is a 4 mm sheet on the rear face, from X = −54 mm to X = −50 mm.
VC-FR-4195 covers the band above the rails, from Z = 1430 mm to the profile top.
VC-FR-4186 covers the lower bay, up to the short upright.
The tilt mechanism must clear both sheets.
The bottom plate is the base.
The lift motor and the gearbox sit above it.
The separate brake is not in this pose.

The chain lift is VC-ASM-2000. It is not the VC-ASM-8100 actuators.
Both chain strands, the drive sprocket and the idler sprocket sit in the profile gap.
The shaft axis is the mast mid-plane, X = 0.
The axis runs along Y and stops before the inner faces.
The rear strand stays at X = −45.9 mm, 4.1 mm in front of the rear face.
The placed sprocket spans about X = −41.4 mm to 41.4 mm.
The chain strands still stop outside the 83 mm envelope, so they stay clear of the teeth.
The Siemens servo and the PLE120 gearbox sit above the bottom plate, on the drive side, outside the head-plate sweep of Y = ±210 mm.
The PLE120 output is directly coupled to the chain shaft by the KTR ROTEX 28.
The ratio from the gearbox output to the sprocket is 1:1.
There is no gear stage between them.
The chain shaft stays on the mast mid-plane, X = 0.
The gearbox output, the coupling and the chain shaft share that axis.
Do not use an offset lift axis. Do not add drop gears.
This revision of the study solid still places the lift axis off the chain shaft.
The placed axis is at X = 7.5 mm and Z = 79.5 mm.
The offset is 22.9 mm from the chain shaft at Z = 57.9 mm.
That offset is a pose error.
The approved layout does not use that offset.
Correct the pose in cad/models/machine_assembly.py.
Those study-solid positions follow the offset axis.
The 115 mm gearbox in that solid is flush with X = −50 mm.
The motor flange is 81 mm square, so the motor body starts at X = −33 mm.
In that study solid the coupling hub is seated on the gearbox journal.
Its inboard face is at Y = −249 mm.
No solid in that pose joins the hub to the chain shaft.
The motor bolts to the gearbox input, further outboard.
A horizontal flange, VC-FR-4182, sits on the plate and runs out under the gearbox.
Its neck stays inside the profile depth and meets both stiffeners on a face.
A pad under the gearbox reaches X = 65 mm.
That pad is clear of the stiffeners.
The flange does not cross the mast centre.
The gearbox housing rests on that flange.
The drive-side upright is cut short.
It starts above the gearbox, at Z = 139 mm, and still reaches the same top as the other upright.
The idle-side upright stays 1500 mm.
VC-FR-4100 stays 1500 mm as the purchased length.
VC-FR-4185 is a 4 mm sheet on the front face of the lower bay.
It stops under the carriage, because at stroke 0 the carriage web is at Z = 105 mm.
VC-FR-4186 is the matching rear sheet.
VC-HB-2110 is a draft shelf under the motor.
A cut mk 2004 bar, VC-FR-4180, spans the clear gap between the inner faces.
It sits between the chain strands at mid height.
At the 300 mm pitch that cut length is 250 mm.
The idle sprocket sits on a shaft above the profile ends.
Two bearing blocks, VC-HB-2830, bolt to those ends.
Each block has a slotted seat and a tension screw.
The top steel plate VC-FR-4400 is not fitted in this pose.
The blank stays on the BOM.
Two 4 mm sheets, VC-FR-4190 on the front face and VC-FR-4195 on the rear face, bolt to both profiles above the rails.
They replace the stiffness the top plate gave.
Bent 4 mm gussets still tie the profiles at the bottom, at mid height and at the top.
The gusset webs sit between the chain strands.
The chain path still uses the published 83 mm tip diameter.
The placed G&G sprocket tip is about 82.7 mm and its width is 25.5 mm.
The placed model uses a pitch radius of 37.9 mm.
PULL_FORCE.md uses 38.18 mm.
The gearbox solid is Neugart article 100460948.
It is 115 mm square and 204 mm long.
The servo envelope is the datasheet flange, 81 mm by 186.6 mm.
No motor STEP is in the repository.

VC-HB-2100 is an envelope.
VC-HB-2200 is the Neugart STEP.
VC-HB-2400 is a KTR ROTEX 28 coupling.
The coupling joins the gearbox output to the chain shaft, 1:1.
There is no gear stage.
The set is a 32H7 hub, an unbored hub and a 92 Sh-A spider.
The placed length is 87.5 mm.
The 50 mm envelope is only the fallback.
The 32H7 hub faces the gearbox.
The gearbox shaft is Ø25 mm.
The placed STEP hub is 32H7, so the bore is not a finished fit.
The hub is seated on the journal.
The chain-side hub is unbored.
VC-HB-2800 is the G&G 501-302-0515 sprocket.
VC-HB-2810 reuses that solid.
It has no second file.
VC-HB-3100 is the HIWIN HGR20R1300H rail.
VC-HB-3110 is the HIWIN HGH20CAZ0H block.
The rail mounting face sits on the profile front face.
The block top is 30 mm from that face.
The block length is 90.4 mm.
VC-HB-3000 is obsolete and is not placed.
`load_vendor_shape` recenters one STEP file and does not rotate it, unless SOURCE.md says otherwise.
The HIWIN files keep the mounting face, so they are not recentered.
The gearbox file keeps the motor face, so it is not recentered.
The coupling is three files.
They keep the manufacturer origin because the jaw face is not the box centre.
The shaft tip meets the jaw face.
The motor flange meets the gearbox input on a face.
A missing file keeps the catalogue envelope.
The mk 2004 profile, the 10B-2 chain, the UCP 206 blocks and the OLI MVE motors stay envelopes.

The vibrating plate bottom is at the same height as the lower guide block.
The plate does not hang below the carriage.
The shoe tip in this pose is at Z = −446.6 mm.
The longer guide blocks reduce the top of the travel, so the tip is 12.9 mm lower than the 77.5 mm block pose.
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
The clearances below are measured on the study solid.
That solid still uses the offset axis named above.
Those clearances are not the approved coaxial layout.
The shoe tip is below the profiles, so the shoe distance includes that vertical gap.
The head clears the rails, the profiles and the gussets at stroke 0, at mid travel and at the top.

| Pair | Clearance | Note |
|---|---|---|
| Shoe to nearest profile | 419.1 mm | 3D distance. The tip is below the mast. |
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
| Lift-motor body to the rear face | 17.0 mm | The 81 mm flange starts at X = −33 mm. |
| Gearbox body to the rear face | 0.0 mm | The 115 mm body is flush at X = −50 mm. |

No pair of part solids shares more than 1 mm³.
The ground datum is not a part.

The views are:

- `cad/export/renders/VC-ASM-0000-layout-iso.png`
- `cad/export/renders/VC-ASM-0000-layout-side.png`
- `cad/export/renders/VC-ASM-0000-layout-top.png`

## Values Stefan must get

1. Length of cutting shoe 205449.
Ask Geoprobe.
2. Axial length of adapter VC-SH-1500, and the thread.
3. Axial height of the carriage block.
4. Required ground clearance at the start of the stroke.
5. Top margin for the sprocket, the chain and the upper limit switch.
6. Column flange thickness.
7. Isolator free height and diameter for VC-SH-1600.
8. Motor centre distance.
The minimum is 170 mm.
The 266 mm pitch is only a layout placeholder.
9. Usable stroke.
The model travel is 1009.6 mm because two 90.4 mm blocks sit 200 mm apart on the 1300 mm rail.
The 200 mm pitch is TBD.
10. Centre distance of the two mast profiles.
The rod is in front of the rails.
The 300 mm pitch is TBD.
11. Front gap from the carriage plate to the motor rear face.
The model uses a draft gap of 10 mm.
The plate rear is flush with that face.
12. Siemens 1FL2104 STEP file.
The motor is still the datasheet envelope.
The PLE120 STEP is loaded.
13. Coupling bore against the Ø25 mm gearbox shaft.
The STEP hub is 32H7 and is seated on the journal.
Pillow-block outline and chain-link section are still open.
14. Weld position of the two ribs VC-SH-1302.

## Options

Do not order a new profile from this study.
Three options remain open.
This study does not choose an option.

1. Longer profile.
   The length must exceed the required height.
   The required height stays open until the team measures the TBD lengths.
   VC-FR-4100 stays 1500 mm until that decision.

2. Telescopic mast.
   One stage carries the head.
   A second stage adds travel.
   The BOM lists no telescopic part.

3. Two-stage push.
   Drive part of the casing section.
   Then add the next casing length.
   The mast then does not hold the full 1219.2 mm above the ground at one time.
   The team has not designed the joint and the clamp for that sequence.

## Earlier remainder

SAMPLING.md shows a remainder of 33.8 mm.
That remainder is 1473 mm minus 200 mm minus 20 mm minus 1219.2 mm.
The remainder leaves out the motor height.
The remainder leaves out the carriage, the shoe, the adapter and the margins.
33.8 mm is not a demonstrated fit.
Use the deficit in this document for `mast-height-deficit`.

## Files

`cad/models/mast_layout.py` holds the parameters.
The sheet is `cad/export/layout/mast-stack.svg`.
`cad/export/layout/mast-stack.pdf` holds the same numbers.
The study solid is `cad/export/layout/mast-stack.step`.
The machine pose is `cad/export/step/VC-ASM-0000-layout.step`.
The bracket check is `docs/engineering/CARRIAGE-BRACKET.md`.
`cad/export/renders/` holds the views.
Do not build a part from the STEP files.
`MAST-LAYOUT` is a document name.
That name is not a part number.
