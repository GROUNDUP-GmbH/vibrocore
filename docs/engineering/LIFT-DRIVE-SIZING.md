# Lift drive sizing

Status: approved by Stefan on 2026-11-20.
This note selects the lift motor, the gearbox and the brake.
It is not a manufacturing drawing.

## 1. Selected parts

| Item | Selection |
|---|---|
| Motor VC-HB-2100 | Siemens 1FL2104-4AG11-1MC0 |
| Drive VC-HB-2300 | SINAMICS S200, 6SL5510-1BB11-0AA0, cabinet item |
| Gearbox VC-HB-2200 | Neugart PLE120, i = 40, article 100460948 |
| Brake | The 3.3 Nm brake inside the motor |
| Removed | VC-HB-3000, Kendrion BFK457-10, 16 Nm |

The motor data are from the Siemens datasheet dated 2026-11-20.
Rated torque is 3.2 Nm. Maximum torque is 10.8 Nm.
Rated speed is 3000 rpm. Rated power is 1 kW.
The supply is 230 V single phase through the S200 drive.
The shaft is Ø19 mm by 40 mm. The flange is 81 mm square.
The centering diameter is 70 mm. The pitch circle is 90 mm.
The holding brake is 3.3 Nm. The encoder is a multiturn absolute encoder.
The mass is about 4.1 kg.
The body behind the flange face is 186.6 mm.
The SiePortal STEP adds the 40 mm shaft, so the overall length is 226.6 mm.

The gearbox torques are from the Neugart PLE catalogue, 2026-10.
The sizes and the mass are from the vendor solid of article 100460948.
At i = 40 and two stages the continuous torque T2D is 195 Nm.
The cyclic torque T2Z is 230 Nm. The maximum torque T2max is 365 Nm.
The emergency-stop torque T2Stop is 500 Nm.
The housing is 115 mm square.
The total length is 204 mm.
That length is the input adapter 47.5 mm, the housing 101.5 mm and the output shaft 55 mm.
The output shaft is Ø25 h7 by 55 mm, with key DIN 6885-A-8x7x40.
The output pilot is Ø80 h7.
The motor pilot is Ø70. The motor pitch circle is Ø90. The motor holes are M6 by 15 mm.
The nameplate mass is 7.65 kg.

## 2. Design case

The moving mass used for this note is 100 kg.
That mass is an assumption. The known parts are about 61 kg.
The design chain pull is 5.8 kN.
That is the 5 kN load-cell rating plus 0.8 kN for the weight above the cell.
The pitch radius used here is 38.18 mm.
Chain and bearing efficiency is 0.98. Gearbox efficiency is 0.97.
Gearbox idle torque at the motor is 0.85 Nm.

Motor torque is T2 / (i × 0.97) + 0.85 Nm.
At 5.8 kN and i = 40 the motor torque is 6.67 Nm.

## 3. Torque limit

Set the drive torque limit to about 6.7 Nm.
That limit is the mechanical fuse of the axis.
It keeps the gearbox output near 227 Nm.
That is below T2Z (230 Nm) and below T2max (365 Nm).
The chain pull then stays near 5.8 kN.

Do not allow the motor peak of 10.8 Nm.
10.8 Nm × 40 × 0.97 is 419 Nm at the gearbox output.
That is above T2max.

The previous PLPE120 at i = 40 has a cyclic torque of 172 Nm.
A hard extraction is about 187 Nm. That gearbox is above its cyclic torque.
PLE120 at i = 40 stays below T2Z for the same case.
The sprocket does not sit on the gearbox shaft.
Neugart PLE_2026_05_EN.pdf rates the PLE120 output at Fr max 2000 N, Fa max 3800 N and MK max 115 Nm.
The design chain pull is 5.8 kN. That is above Fr max.
At 25 mm from the flange, 5.8 kN gives 145 Nm, which is above MK max.
The chain radial load goes into the two SYJ bearings. The gearbox shaft sees torque only.
No chain pretension is stated. The radial load used here is the pull itself. Pretension would add twice the slack-side tension.

## 4. Power loss during pull-out

The motor brake holds 3.3 Nm.
At i = 40 that is about 132 Nm at the output and about 3.5 kN at the chain.
The weight of a 100 kg string is about 1 kN, so the brake holds the parked head.
The design pull is 5.8 kN. The brake does not hold that pull.

If the supply fails while the chain is pulling, the soil can let go.
The brake then holds only about 3.5 kN.
The carriage can slide down onto the casing.
The load moves down, toward the ground.
Decide in the risk assessment whether one brake is enough.
A second brake, if one is required, must satisfy brake torque × 40 ≤ 500 Nm.

The old 16 Nm brake gives 640 Nm at the output.
That is above T2Stop. Do not use it.

## 5. Phase-out

1FL2104-4AG11-1MC0 is Phase Out Announce.
The Siemens successor is SH40 New, order pattern 1FL2104-4BG□1-□□C0.
The announcement is Siemens document 109997329, dated 2026-01-29.
The S200 PN / 1FL2 operating instructions are 06/2026, document 110005040.
The S200 drive 6SL5510-1BB11-0AA0 stays.

| Item | Successor | This motor |
|---|---|---|
| Length with brake | 192.6 mm | 226.6 mm |
| Flange thickness | 8 mm | 6.4 mm |
| Usable IP65 shaft | 19 mm by 37 mm | 19 mm by 32 mm |
| Mass | 3.2 kg | 4.1 kg |
| Inertia | 0.97 kgcm² | not used here |
| Maximum torque | 11.2 Nm | 10.8 Nm |
| Enclosure | always IP65 | IP65 on this order |

These items stay the same.
Flange 81 mm square. Centering diameter 70 mm. Pitch circle 90 mm. Four holes Ø6.6 mm.
Shaft 19 h6. Key 6 mm by 6 mm by 25 mm. Holding brake 3.3 Nm.

The selected mass stays 4.1 kg. Do not switch the model to 3.2 kg.
The Neugart input adapter of article 100460948 was configured for 1FL2104-4AG10.
Re-check that adapter for the successor.
The current STEP oil seal extends about 8 mm. The gearbox recess is 4.4 mm deep and has no keyway.

## 6. Mount

VC-FR-4187 is one welded S355 frame. VC-FR-4182, VC-FR-4183, VC-FR-4184 and VC-FR-4188 are obsolete.
The pads and the feet are in the weldment. There is no separate weld solid.
The profile joints and the bottom-plate joints stay bolted. VC-FR-4186 stays a bolted sheet.
Four ISO 4762 M6x20 screws hold the flange.
They sit on the Ø100 mm circle, on the diagonals, and they pass through the STEP holes.
The concept sketch shows a 90 mm circle. The model follows the STEP.
The plate is 8 mm. The screws enter from the inside of the frame.
The output pilot is Ø80 mm. The plate bore is Ø86 mm.
The gearbox and the motor hang from that plate. No bracket supports the overhang.
Remove one guard, VC-FR-4191 or VC-FR-4192, to reach the coupling.
The motor uses four ISO 4762 M6x16 screws. The flange is 6.4 mm. The thread engagement is 9.6 mm.
The clamp-screw size and the tightening torque are TBD.
Six M8x20 screws hold the short profile to the tab. Six M8x20 screws hold the long profile to the cheek.
The bearing bolts are M12x50. The nuts are under the hanging feet.

T2max is 365 Nm.
Each flange bolt sees 365000 N·mm / (4 × 50 mm) = 1825 N.
An M6-8.8 proof load is about 11.6 kN. The bolts are inside that load.
The STEP holes are on a 50 mm radius. A 45 mm radius would raise this load.

The chain shaft is Ø30 mm, C45, between the two bearings.
The placed centres are 83.4 mm apart. The sprocket is centred. The shaft solid is 162.6 mm long.
The bending moment is 5800 N × 83.4 mm / 4 = 120930 N·mm.
The full section modulus is 2651 mm³. With one DIN 6885 keyway, 8 mm by 4 mm, it is about 2290 mm³.
Bending stress is 45.6 MPa on the full section and 52.8 MPa with the keyway.
Torsion at T2max 365 Nm is 68.8 MPa on the full section. The keyway raises that torsion to 79.7 MPa.
Von Mises stress is 128 MPa on the full section and 148 MPa with the keyway.
EN 10083-2 gives C45E, normalized, 16 mm to 100 mm, a minimum yield of 305 MPa.
The safety factor is 2.38 on the full section and 2.06 with the keyway.
The chain torque at 5.8 kN and 37.9 mm is 220 Nm. That case is lower.
The modelled shaft is Ø29.6 mm, 0.2 mm under the bore. This stress uses the design diameter Ø30 mm.
A quenched shaft is stronger than this normalized figure.

Each SYJ 30 TF sees 2.9 kN. C0 is 11.2 kN, so the static safety factor is 3.86.
C is 19.5 kN. No pretension is included. Pretension would raise both loads.
Each foot takes two M12 bolts. The slot is 17 mm wide, so M12 leaves the J adjustment.
The housings hang under the beam. The sole is above the shaft.

The coupling is G&G 591-301-0018. It is rated 380 Nm. That covers T2max 365 Nm.
The pilot bore is 14 mm. The purchase finish is 25H7 and 30H7.
The model opens the gearbox half to Ø25.4 mm and the shaft half to Ø30.4 mm.

## 7. Sources

1. Siemens datasheet 1FL2104-4AG11-1MC0, generated 2026-11-20.
   https://mall.industry.siemens.com/spice/docuservice/rest/document.spring?articleNumber=1FL21044AG111MC0&documentGroup=TED&documentId=DCS_DATASHEET_CLEANED&language=en&region=ww
2. Neugart Complete Gearbox Catalog 2026-10, PLE chapter.
   https://cdn.neugart.com/fileadmin/user_upload/Downloads/Product_Catalogs/10_2026/Complete_Gearbox_Catalog_2026_10_EN.pdf
3. The calculation workbook that Stefan approved is not stored as a second copy of the vendor PDFs.
   Those PDFs stay out of this repository.
4. Neugart CAD for article 100460948, generated 2026-11-20.
   The PDF and the DXF from that mail are not stored here.
   See cad/vendor/VC-HB-2200/SOURCE.md.
5. Siemens SiePortal STEP 1FL2104-4AG11-1MC0_3D_en.STP.
   See cad/vendor/VC-HB-2100/SOURCE.md.
6. Siemens document 109997329, 2026-01-29. Successor announcement.
7. Siemens document 110005040. S200 PN / 1FL2 operating instructions, 06/2026.
8. Neugart PLE operating instructions PLE_2026_05_EN.pdf. PLE120 Fr max 2000 N, Fa max 3800 N, MK max 115 Nm.
9. EN 10083-2. C45E normalized, 16 mm to 100 mm, Re min 305 MPa.
10. G&G chain coupling 591-301-0018. Rated 380 Nm. Pilot bore 14 mm. Overall length 68 mm.
