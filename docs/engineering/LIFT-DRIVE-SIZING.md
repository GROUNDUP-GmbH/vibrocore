# Lift drive sizing

Status: Stefan approved this note on 2026-11-20.
This note selects the lift motor, the gearbox and the brake.
This note is not a manufacturing drawing.

## 1. Selected parts

| Item | Selection |
|---|---|
| Motor VC-HB-2100 | Siemens 1FL2104-4AG11-1MC0 |
| Drive VC-HB-2300 | SINAMICS S200, 6SL5510-1BB11-0AA0, cabinet item |
| Gearbox VC-HB-2200 | Neugart PLE120, i = 40, article 100460948 |
| Brake | The 3.3 Nm brake inside the motor |
| Removed | VC-HB-3000, Kendrion BFK457-10, 16 Nm |

The motor data come from the Siemens datasheet dated 2026-11-20.
Rated torque is 3.2 Nm.
Maximum torque is 10.8 Nm.
Rated speed is 3000 rpm.
Rated power is 1 kW.
The S200 drive supplies the motor from 230 V single phase.
The shaft is Ø19 mm by 40 mm.
The flange is 81 mm square.
The centering diameter is 70 mm.
The pitch circle is 90 mm.
The holding brake is 3.3 Nm.
The encoder is a multiturn absolute encoder.
The mass is about 4.1 kg.
The overall length is 186.6 mm.

The gearbox torques come from the Neugart PLE catalogue, 2026-10.
The vendor solid of article 100460948 gives the sizes and the mass.
At i = 40 and two stages the continuous torque T2D is 195 Nm.
The cyclic torque T2Z is 230 Nm.
The maximum torque T2max is 365 Nm.
The emergency-stop torque T2Stop is 500 Nm.
The housing is 115 mm square.
The total length is 204 mm.
That length is the input adapter 47.5 mm, the housing 101.5 mm and the output shaft 55 mm.
The output shaft is Ø25 h7 by 55 mm, with key DIN 6885-A-8x7x40.
The output pilot is Ø80 h7.
The motor pilot is Ø70.
The motor pitch circle is Ø90.
The motor holes are M6 by 15 mm.
The nameplate mass is 7.65 kg.

## 2. Design case

This note uses a moving mass of 100 kg.
That mass is an assumption.
The known parts are about 61 kg.
The design chain pull is 5.8 kN.
That pull is the 5 kN load-cell rating plus 0.8 kN for the weight above the cell.
The pitch radius used here is 38.18 mm.
Chain and bearing efficiency is 0.98.
Gearbox efficiency is 0.97.
Gearbox idle torque at the motor is 0.85 Nm.

Motor torque is T2 / (i × 0.97) + 0.85 Nm.
At 5.8 kN and i = 40 the motor torque is 6.67 Nm.

## 3. Torque limit

Set the drive torque limit to about 6.7 Nm.
That limit is the mechanical fuse of the axis.
It keeps the gearbox output near 227 Nm.
That output is below T2Z (230 Nm) and below T2max (365 Nm).
The chain pull then stays near 5.8 kN.

Do not allow the motor peak of 10.8 Nm.
10.8 Nm × 40 × 0.97 is 419 Nm at the gearbox output.
That product is above T2max.

The previous PLPE120 at i = 40 has a cyclic torque of 172 Nm.
A hard extraction is about 187 Nm.
That gearbox is above its cyclic torque.
PLE120 at i = 40 stays below T2Z for the same case.
The chain load goes into the separate shaft, not into the gearbox.
The path from the PLE120 output to the sprocket is 1:1.
The KTR ROTEX 28 joins the gearbox output to the chain shaft.
This path has no gear stage.
Stefan confirmed that path on 2026-11-24.

## 4. Power loss during pull-out

The motor brake holds 3.3 Nm.
At i = 40 that hold is about 132 Nm at the output and about 3.5 kN at the chain.
The weight of a 100 kg string is about 1 kN, so the brake holds the parked head.
The design pull is 5.8 kN.
The brake does not hold that pull.

If the supply fails while the chain is pulling, the soil can let go.
The brake then holds only about 3.5 kN.
The carriage can slide down onto the casing.
The load moves down, toward the ground.
Decide in the risk assessment whether one brake is enough.
A second brake, if the assessment requires one, must satisfy brake torque × 40 ≤ 500 Nm.

The old 16 Nm brake gives 640 Nm at the output.
That product is above T2Stop.
Do not use it.

## 5. Sources

1. Siemens datasheet 1FL2104-4AG11-1MC0, generated 2026-11-20.
   https://mall.industry.siemens.com/spice/docuservice/rest/document.spring?articleNumber=1FL21044AG111MC0&documentGroup=TED&documentId=DCS_DATASHEET_CLEANED&language=en&region=ww
2. Neugart Complete Gearbox Catalog 2026-10, PLE chapter.
   https://cdn.neugart.com/fileadmin/user_upload/Downloads/Product_Catalogs/10_2026/Complete_Gearbox_Catalog_2026_10_EN.pdf
3. The calculation workbook that Stefan approved is not stored as a second copy of the vendor PDFs.
   Those PDFs stay out of this repository.
4. Neugart CAD for article 100460948, generated 2026-11-20.
   This repository does not store the PDF and the DXF from that mail.
   See cad/vendor/VC-HB-2200/SOURCE.md.
