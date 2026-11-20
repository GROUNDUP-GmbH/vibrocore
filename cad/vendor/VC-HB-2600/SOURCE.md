# VC-HB-2600

Manufacturer: SKF.
Part: SYJ 30 TF.
Housing: SYJ 506. Insert: YAR 206-2F.
This is the UCP 206 size. The placed solid is the SKF part, not a UCP envelope.

Portal: 3Dfindit, powered by CADENAS. SKF catalogue.
https://www.3dfindit.com/en/digitaltwin/ayp001hchhhy-ayl001hp

File: `SKF_SYJ_30_TF.stp` (497781 bytes).
Downloaded 2026-11-20. The PDF datasheet from that download is not in this repository.
Terms of use: https://www.cadenas.de/terms-of-use-3d-cad-models
This file is stored for this machine design. Do not republish it as a CAD catalogue.

This file is not in `cad/vendor/VC-HB-2700`.
VC-HB-2700 is the G&G chain. A STEP in that folder would replace the chain solid.

`load_vendor_shape` is called with `recenter=False`.
File X is the bore. File Y = -42.9 mm is the foot sole. File Z is the 165 mm foot.
`Rot(90, 0, 0)` then `Rot(0, 0, 90)` stands the sole down and lays the bore on Y.
The assembly places the sole on the seat. The shaft axis stays at local Z = 0.

Catalogue data, SKF SYJ 30 TF:
- Bore d = 30 mm.
- Centre height H1 = 42.9 mm.
- Overall height H = 82 mm. This solid is 82.5 mm.
- Foot length L = 165 mm.
- Bolt spacing J = 118 mm. The slots allow J from 111 mm to 125 mm.
- Slots 24 mm by 17 mm.
- Base width A = 42 mm. This solid is 43.2 mm along the shaft.
- Foot height H2 = 16 mm.
- Bearing width B = 38.1 mm.
- Recommended bolt G = 14 mm.
- Grub screw M6 x 0.75, tightening torque 4 Nm.
- Dynamic load C = 19.5 kN. Static load C0 = 11.2 kN.
- Mass 1.1 kg.

Bolt choice: M12.
The slot is 17 mm wide. An M14 shank passes that slot.
An M14 clearance hole is 15 mm, so the J adjustment cannot be used.
An M12 clearance hole is 13 mm and stays inside the slot.
The study uses M12. The catalogue G = 14 mm is the largest shank that still passes.

Shaft check:
- This bore is Ø30 mm.
- The gearbox output is Ø25 h7 by 55 mm. It does not fit. The radial gap would be 2.5 mm.
- The ROTEX 28 hub in VC-HB-2400 is 32H7. It does not fit. That hub is 2 mm larger than the bore.
- `SHAFT_DIAMETER_MM` is 30 mm. The placed shaft VC-HB-2500 uses that diameter.
- The shaft is modeled 0.2 mm under the bore so the solids do not share a volume.
- The sprocket sits on this Ø30 shaft, between the two housings.

The two housings sit on the chain axis, one on each side of the sprocket.
The axis is at X = 32.5 mm. The rear of the 165 mm foot is on X = −50 mm.
Both soles sit on seats in VC-FR-4183. The sole is at Z = 36.6 mm.
The placed solid is a faceted copy. Two small cubes stay analytic if the facet fails the check.
