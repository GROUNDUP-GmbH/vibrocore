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
| rail_section_width_mm | 20 mm | Hiwin HGR20R published width WR. The STEP mounting face sits on the profile. |
| rail_section_height_mm | 17.5 mm | Hiwin HGR20R published height HR. The STEP mounting face sits on the profile. |
| runner_pitch_mm | 200 mm | Centre distance of the two HGH20CA blocks on one rail. Not in the BOM. |
| head_front_gap_mm | 10 mm | Draft gap from the carriage plate to the motor rear face. The plate rear is flush with that face. |
| servo_body_length_mm | 186.6 mm | Body of Siemens 1FL2104 behind the flange face. The STEP shaft adds 40 mm. |
| chain_pitch_mm | 15.875 mm | ISO 606 size 10B. The placed chain uses this pitch. |
| chain_roller_diameter_mm | 10.16 mm | ISO 606 roller diameter. The strand thickness is this diameter. |
| chain_inner_width_mm | 9.65 mm | ISO 606 inner width of one row. |
| chain_transverse_pitch_mm | 16.59 mm | ISO 606 duplex transverse pitch. |
| coupling_diameter_mm | 65 mm | Fallback envelope of VC-HB-2400 when no STEP is present. |
| coupling_length_mm | 50 mm | Fallback envelope of VC-HB-2400 when no STEP is present. |
| pillow_length_mm | 43.2 mm | SYJ 30 TF along the shaft. Catalogue base width A is 42 mm. |
| pillow_width_mm | 165 mm | SYJ 30 TF foot length L. Bolt spacing J is 118 mm. |
| pillow_height_mm | 82.5 mm | SYJ 30 TF overall height. Catalogue H is 82 mm. Centre height is 42.9 mm. |
| chain_section_x_mm | 16 mm | Old envelope thickness. The placed chain uses the 10.16 mm roller. |
| chain_section_y_mm | 32 mm | Old envelope width. The placed rows use 9.65 mm and a 16.59 mm transverse pitch. |
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
H is 30 mm from the rail mounting face. W is 44 mm. The STEP solid is 90.4 mm long.
The block pitch on one rail is 200 mm.
That pitch is TBD.
The guided travel is 1009.6 mm.
`STROKE_POSITION_MM` is the travel of the lower block from the rail bottom.
The start value is 1009.6 mm.
That is the top of the travel.
The upper block then ends on the rail top at 1415 mm.
The same solids at stroke 0, at mid travel 504.8 mm and at the top do not overlap, except the motor and the gearbox.

The volume behind the profile rear faces is reserved for the machine tilt mechanism.
Those faces are the plane X = −50 mm.
No chain strand, sprocket, shaft, gearbox, brake or motor enters X < −50 mm.
The rear sheets VC-FR-4195 and VC-FR-4186 are the exceptions.
Each is a 4 mm sheet on the rear face, from X = −54 mm to X = −50 mm.
VC-FR-4195 covers the band above the rails, from Z = 1430 mm to the profile top.
VC-FR-4186 covers the lower bay and has a tab on the short upright.
The tilt mechanism must clear both sheets.
The bottom plate is the base.
The lift motor and the gearbox sit above it.
The separate brake is not in this pose.

The chain lift is VC-ASM-2000, not the VC-ASM-8100 actuators.
The drive sprocket sits on the gearbox output shaft.
The chain and the idler share that axis.
The axis is at X = 32.5 mm and Z = 82.9 mm.
The rear strand stays at X = −35.5 mm, 14.5 mm in front of the rear face.
The chain is an ISO 606 section on the pitch radius.
The wrap is a shell outside the tooth tip. It is not a meshed link.
The Siemens servo is the SiePortal STEP. The PLE120 gearbox is the Neugart STEP.
They sit above the bottom plate.
The head plate sweeps Y = ±210 mm down to the rail, so this train stands outside that sweep, on the drive side.
The chain axis is at X = 32.5 mm.
That puts the rear of the 165 mm bearing foot on the rear face, X = −50 mm.
The sprocket is at Y = 0, between the uprights.
The order along the shaft, from the gearbox toward the idle upright, is the PLE120, the ROTEX 28, the drive-side SYJ 30 TF, the sprocket, and the idle-side SYJ 30 TF.
The bearing centres are 72.7 mm apart. The sprocket is in the middle.
The gearbox shaft sees torque only. It does not see the chain radial load.
VC-FR-4182 is one 10 mm laser-cut plate with one bend, plus three welded gussets. No notch and no inspection window.
The vertical leg sits on the output flange. Four M6 screws on PCD 90 mm hold it. The bore is Ø84 mm.
The plate stops at Z = 100 mm, under the carriage. A narrow ear behind the rail reaches the upper screw.
Two 6 mm gussets stand on the output side of the bend, one each side of the shaft.
One 6 mm rib stands on the ear and stops below the upper screw.
Each gusset has a fillet weld a5 on both sides, along the joint with the plate.
The gussets do not meet the profiles or the bottom plate.
The foot sits on the bottom plate and takes two M8 through bolts.
VC-FR-4183 is two 25 mm flats, one under each bearing. The M12 bolts pass through the bottom plate.
VC-FR-4184 is one 40 mm by 40 mm by 6 mm angle.
It bolts to the idle profile inner side slots and to the bottom plate with two through bolts.
Those joints stay bolted. A weld is not used there.
The drive-side upright is cut short.
It starts at Z = 142.4 mm and reaches the same top as the idle upright.
The idle upright stays 1500 mm and stands on the bottom plate.
The purchased length of VC-FR-4100 stays 1500 mm.
VC-FR-4185 is a 4 mm pad on the idle front face only.
VC-FR-4186 is the rear sheet. It is one removable panel.
Two screws hold the idle rear slot. A tab on the drive profile takes two more screws.
Remove that panel to reach the coupling, the flange screws and the motor.
The carriage arm stays in front of the rail and meets the chain.
VC-FR-4150, VC-FR-4160, VC-FR-4170 and VC-FR-4180 are obsolete and are not placed.
The lower mount VC-FR-4183 and the upper mount VC-FR-4198 take their job.
The idle sprocket is on the same axis as the drive sprocket.
One bearing block, VC-HB-2830, bolts to the drive-side profile end.
Each block has a slotted seat and a tension screw.
The top steel plate VC-FR-4400 is not fitted in this pose.
The blank stays on the BOM.
Two 4 mm sheets, VC-FR-4190 on the front face and VC-FR-4195 on the rear face, bolt to both profiles above the rails.
They replace the stiffness the top plate gave.
The chain path still uses the published 83 mm tip diameter.
The placed G&G sprocket tip is about 82.7 mm and its width is 25.5 mm.
The pitch radius is the documented 37.9 mm.
The gearbox solid is Neugart article 100460948. It is 115 mm square and 204 mm long.
The servo is the SiePortal solid of 1FL2104-4AG11-1MC0.
The flange face meets the gearbox. The 40 mm shaft enters the bore.
The motor flange is 81 mm square and 6.4 mm thick. The centering spigot is Ø70 mm.
It enters the adapter recess. Four ISO 4762 M6x16 screws hold the flange.
The holes are Ø6.6 mm on PCD 90 mm. The screw length is 6.4 mm plus 9.6 mm of thread.
The minimum thread is 1.5 times the diameter, so 9 mm. The adapter thread is 15 mm deep.
The clamp-screw size and its torque are TBD. The PLE manual is not in the vendor folder.
The access plug is drawn clear of the Ø8 mm mouth so the clamp screw shows in the hole.
The oil seal and the key share about 5110 mm³ with the gearbox.
That pair is the open adapter check. Every other pair stays under 1 mm³.

VC-HB-2100 is the Siemens STEP.
VC-HB-2200 is the Neugart STEP.
VC-HB-2400 is the ROTEX 28. The placed solids are the 32H7 hub, an unbored hub opened to Ø30.4, and the 92 Sh-A spider.
VC-HB-2800 is the G&G 501-302-0515 sprocket.
It sits on the Ø30 shaft between the two bearings.
VC-HB-2810 reuses that solid.
It has no second file.
VC-HB-3100 is the HIWIN HGR20R1300H rail.
VC-HB-3110 is the HIWIN HGH20CAZ0H block.
The rail mounting face sits on the profile front face.
The block top is 30 mm from that face. The block length is 90.4 mm.
VC-HB-3000 is obsolete and is not placed.
`load_vendor_shape` recenters one STEP file and does not rotate it, unless SOURCE.md says otherwise.
The HIWIN files keep the mounting face, so they are not recentered.
The gearbox file keeps the motor face, so it is not recentered.
The motor flange meets the gearbox input on a face.
The drive sprocket sits on the Ø30 shaft.
A missing file keeps the catalogue envelope.
The mk 2004 uprights use the 3Dfindit extrusion.
The placed profile, the pillow block and the sprocket are faceted copies, so a mesher does not draw cones and splines as spikes.
The 10B-2 chain is an ISO 606 section. G&G publishes no chain CAD.
VC-HB-2600 is the SKF SYJ 30 TF solid. The OLI MVE motors stay envelopes.

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
The shoe tip is below the profiles, so the shoe distance includes that vertical gap.
The head clears the rails, the profiles and the mounts at stroke 0, at mid travel and at the top.

## Slot faces

The mk 2004 section is type 51.04. The slot is slot 10. The measured throat is 10.10 mm.
The price list is mk Profiltechnik-Komponenten 01/2024.
https://www.mk-group.com/fileadmin/media/documents/Preisliste_Profltechnik-Komponenten_01_2024.pdf

The chain pull is vertical. The bolted angle and the cap lips carry the shear that the three gussets used to carry.
There is no end-thread machining.

The front face is the 50 mm face at world +X. It has one slot on the profile centre line.
The rail covers this face from Z = 115 mm to Z = 1415 mm, so the stiffener does not use it.

The inner side face is the 100 mm face toward the bay. It has two slots, at world X = +25 mm and X = −25 mm.
The measured throat is 10.10 mm. The two slots are 50 mm apart in X, so the pair resists twist.
VC-FR-4184 uses both idle slots at Z = 48 mm.
VC-FR-4198 uses the forward slot of each profile, at X = +25 mm, just under the cap.
The nuts are Lasche 1 mit Feder, M8, order 34.01.0050.
The slot screws are M8x20, order D0912820.
Each nut is a plain 8 mm box in the throat. It is not the full T-head.
The through bolts are M8x30, order D0912830, with ISO 4032 nuts under the bottom plate.
The flange screws are ISO 4762 M6x20.
The plate is 10 mm thick. The specified thread depth is 15 mm.
The engagement is 10 mm. That is more than 9 mm.

The rear-face slot is used by VC-FR-4186.
Four Lasche 1 nuts and four M8x20 screws hold that sheet.
The volume behind X = −50 mm stays reserved for the tilt mechanism.
The sheet and its screws stay inside the 4 mm band.

## Assembly and access

Fit the bottom plate.
Stand the two profiles on the plate.
Bolt the two bearing flats to the plate.
Set the welded mount plate on the gearbox flange.
Fit the four M6x20 screws.
Bolt the plate foot to the bottom plate with two M8x30 screws and two nuts.
Bolt the angle to the idle slots and to the bottom plate.
Fit the coupling on the gearbox shaft.
Bolt the motor to the gearbox with four M6x16 screws.
Fit the rear sheet with four M8x20 screws and four T-slot nuts.

Stop the machine.
Remove the power.
Remove the four screws of VC-FR-4186.
Take the sheet off.
Reach the coupling, the three reachable flange screws and the motor through that opening.
The upper flange screw stays behind the rail. The plate has no inspection window.
Fit the sheet again.
Tighten the four screws.

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
| Carriage to chain strand | 0.0 mm | The arm meets the front strand on a face. |
| Rear chain strand to the rear face | 38.7 mm | The strand is at X = −11.3 mm. |
| Lift-motor body to the rear face | 42.0 mm | The motor body starts at X = −8 mm. |
| Gearbox body to the rear face | 25.0 mm | The 115 mm body starts at X = −25 mm. The foot stays on X = −50 mm. |

No pair of part solids shares more than 1 mm³, except VC-HB-2100 and VC-HB-2200.
The ground datum is not a part.

The views are:

- `cad/export/renders/VC-ASM-0000-layout-iso.png`
- `cad/export/renders/VC-ASM-0000-layout-side.png`
- `cad/export/renders/VC-ASM-0000-layout-top.png`
- `cad/export/renders/VC-ASM-0000-layout-drive-iso.png`
- `cad/export/renders/VC-ASM-0000-layout-drive-front.png`

## Values Stefan must get

1. Length of cutting shoe 205449. Ask Geoprobe.
2. Axial length of adapter VC-SH-1500, and the thread.
3. Axial height of the carriage block.
4. Required ground clearance at the start of the stroke.
5. Top margin for the sprocket, the chain and the upper limit switch.
6. Column flange thickness.
7. Isolator free height and diameter for VC-SH-1600.
8. Motor centre distance. The minimum is 170 mm. The 266 mm pitch is only a layout placeholder.
9. Usable stroke. The model travel is 1009.6 mm because two 90.4 mm blocks sit 200 mm apart on the 1300 mm rail. The 200 mm pitch is TBD.
10. Centre distance of the two mast profiles. The rod is in front of the rails. The 300 mm pitch is TBD.
11. Front gap from the carriage plate to the motor rear face. The model uses a draft gap of 10 mm. The plate rear is flush with that face.
12. Neugart input adapter. Article 100460948 was configured for 1FL2104-4AG10. Re-check it for the current oil seal and for successor 1FL2104-4BG.
13. Coupling bore against the Ø25 mm gearbox shaft. The STEP hub is 32H7 and is seated on the journal. Pillow-block outline is still open.
14. Chain purchase length. 3.2 m stays a placeholder until the lift height is decided. G&G states no breaking load.
15. Weld position of the two ribs VC-SH-1302.

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
