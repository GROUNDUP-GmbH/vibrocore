# VC-FR-4100

Manufacturer: mk Technology Group.
Profile: mk 2004. Order type 51.04.2004.
Configured length file: 51.04.1500. Length 1500 mm.
Section: 50 mm by 100 mm.
Alloy: AlMgSi0.7 F28 / EN AW-6005A T6.
Linear density: 4.850 kg/m. One purchased bar is 7.275 kg.
Catalogue section area: 1805.51 mm².
Second moments: Ix 55.38 cm⁴, Iy 199.96 cm⁴.
Section moduli: Wx 22.15 cm³, Wy 39.99 cm³.

Portal: 3Dfindit, powered by CADENAS.
https://www.3dfindit.com/en/digitaltwin/aluminium-profile-mk-2004?path=maschinenbau_kitz%2F1_profiltechnik%2F1_profile%2F3_serie50%2Fmk_2004.prj

File: `51.04.1500.stp` (144797 bytes).
Downloaded 2026-11-20. The PDF datasheet from that download is not in this repository.
Terms of use: https://www.cadenas.de/terms-of-use-3d-cad-models
This file is stored for this machine design. Do not republish it as a CAD catalogue.

`load_vendor_shape` is called with `recenter=False`.
File X is the extrusion, from 0 mm to 1500 mm.
File Y is the 50 mm side, from 0 mm to 50 mm.
File Z is the 100 mm side, from −100 mm to 0 mm.
`Rot(0, 0, -90)` then `Rot(0, -90, 0)` maps the extrusion onto local Z.
The section is then centred.
Local X is 50 mm. Local Y is 100 mm. Local Z is the length.
The assembly yaw is the same 90 degrees as the old envelope.

A shorter part is scaled on local Z only. The section is not scaled.
The drive-side upright uses that cut. The purchased length stays 1500 mm.
VC-FR-4180 is obsolete and is not placed.
The assembly facets the extrusion before it scales the drive-side length, so a mesher does not draw the splines as spikes.
VC-CS-9460 is a 40 mm profile. It does not use this file.

Measured on this solid:
- One solid. Volume 2,696,492.9 mm³.
- Section from that volume is about 1797.7 mm². The catalogue area is 1805.51 mm².
- Slot opening is 10.10 mm. That is the throat, not the wider T-slot undercut.
- Each 50 mm face has one slot. Each 100 mm face has two slots.
