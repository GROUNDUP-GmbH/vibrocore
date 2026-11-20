# VC-HB-2200

Manufacturer: Neugart GmbH.
Article: 100460948.
Type code: PLE120-040-SSSA3AF-Z19/40/70/90/B5/M6.
Ratio 40. Output shaft with a feather key. Standard output flange.
The motor adaptation is shaft Ø19 × 40 mm, centering Ø70, pitch circle Ø90, B5, M6.
The CAD generator used a Siemens 1FL2104-4AG10, 200 V, with brake.
That check is geometric. The machine motor is 1FL2104-4AG11-1MC0.
The shaft and the flange match that motor.

File: `PLE120-040-SSSA3AF-Z19_40_70_90_B5_M6.stp` (401565 bytes).
The file starts with `ISO-10303-21`.
Generated: 2026-11-20 by the Neugart CAD generator, Creo Parametric.
Received by email from cad-generator@neugart.com.
The 2D PDF and the DXF from that mail are not in this repository.
The contact named in the mail is BIBUS Austria GmbH.

`load_vendor_shape` is called with `recenter=False`.
File X = 0 is the motor flange face. File X = 204 mm is the shaft tip.
The 115 mm square is centred on the axis.
`Rot(0, 0, 90)` maps the shaft onto +Y.
The assembly places that motor face against the servo flange.

Measured on this solid:
- Total length 204 mm. Input adapter 47.5 mm, housing 101.5 mm, output shaft 55 mm.
- Output shaft Ø25. The journal runs from X = 155 mm to the tip.
- Feather key DIN 6885-A-8x7x40, from X = 159 mm to X = 199 mm, on the file −Y side.
- After the rotation the key points toward +X.
- Output flange square 115 mm. Pilot Ø80 from X = 149 mm to X = 153 mm.
- Output holes lie on a Ø100 mm circle.
- Motor-side holes are M6, 15 mm deep, on a Ø90 mm circle. Centering diameter Ø70.
- Nameplate mass 7.65 kg.

The coupling hub sits on the output journal.
The shaft tip meets the jaw face of the 32H7 hub.
The chain sprocket stays on the separate chain shaft.

The centering recess on the motor face is about Ø70 mm and 4.3 mm deep.
A radial pocket sits at local X = −17 mm, Y = 12.5 mm. The STEP mouth on the underside is Ø8 mm and does not pierce that pocket.
The placed assembly opens a Ø7.2 mm hole so the clamp screw can be seen. The vendor file is not edited.
The PLE manual PDF is not in this folder. The clamp-screw size and the tightening torque are TBD.
The Siemens 1FL2104-4AG11 STEP has an oil seal about 8 mm long.
That seal and the motor key share volume with this solid.
The adapter was configured for 1FL2104-4AG10.
Re-check it for that seal and for the successor 1FL2104-4BG.
