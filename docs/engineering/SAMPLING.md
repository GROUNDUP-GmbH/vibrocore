# Sampling concept

Decision date: 2026-11-19.
The sampling string is only the 3.25 in outer casing.
The cutting shoe sits at the bottom of that casing.
Open lab tubes sit inside the casing.
The split carrier holds those tubes.
The machine does not use an inner string.

Do not add centre rods, a centring drive cap, a sample sheath, PVC liners, core catchers, end caps, a lift cap, a leaf puller, a rod clamp or a retainer wrench.

## What stays on the kit

VC-KIT-6000 has six lines.

| Part | Role | Offer 26100096, EUR net, freight excluded |
|---|---|---|
| VC-GP-7100, rod 201446 | One 48 in outer casing. Mass 17.7 kg. Inside diameter 2.625 in = 66.675 mm. | 389.99 each |
| VC-GP-7200, shoe 205449 | Cutting shoe at the bottom of the casing. Outside diameter 3.45 in = 87.63 mm. | 300.78 each |
| VC-GP-7150, O-rings 201325 | Seal the joints between 3.25 in casing sections. Pack of 25. | 24.75 per pack |
| VC-SP-7620 | Draft half-shell A. | No price |
| VC-SP-7621 | Draft half-shell B. | No price |
| VC-SP-7630 | Clamp fasteners for the half-shells. Size TBD. | No price |

The kit holds two rods.
That quantity is two rods, not two pairs.
The old 35.4 kg "pair" mass was two rods.

VC-SH-1500 is the adapter on the sonic head.
It must push the casing and it must pull the casing.
The thread is still unknown.

## What leaves the kit

VC-GP-7300 is the GH60 threadless drive cap, part 201275.
The offer price is EUR 586.47.
The cap can only push.
It cannot pull.
It can rattle at 100 Hz.
It does not fit this sonic head.
The part is obsolete and is not on the kit.

VC-GP-7400 was a polycarbonate 3.25 in liner.
That liner is the wrong concept.
The part is obsolete.
Do not buy liners.

## Parts that are not on the BOM

Sample tubes are a lab consumable.
RadicleLab supplies them.
They are Geoprobe-type plastic tubes.
A photo shows orange tubes with a ribbed outside, a recessed label area, and a row of tubes stacked end to end.
Four tubes are visible in that photo.
The design range is 4 to 6 tubes.
Exact outside diameter and length are unknown.

Push-on caps (Steckdeckel) close the tubes after extraction.
The black part in the photo is a push-on cap, not a screw cap.
During driving the tubes are open.
A cap in the tube would stop the soil.
Caps are a lab consumable.
Do not put tubes or caps on this BOM.

## Offer parts that are not the sampling string

Stefan must confirm these three decisions.
The source pages are the Geoprobe tooling pages cited below.
Offer 26100096 gives the prices.
Prices are EUR net and exclude freight.

| Part | Decision | Reason |
|---|---|---|
| O-ring 201325, VC-GP-7150 | Keep on VC-KIT-6000. Quantity 1 pack. | Geoprobe names it "O-Ring (3.25 in. Probe Rod)", quantity 25. It seals the joints between outer casing sections. https://geoprobe.com/tooling/dt325-soil-sampling-system/mn201325 |
| Drive head 201385, VC-GP-7310 | Obsolete. Not on any BOM. History price EUR 171.34. | Geoprobe names it "DT325 Drive Head" with a 1.25 in pin. That pin fits the centre rod. It does not join 3.25 in casing sections. VC-SH-1500 connects the casing to the sonic head. https://geoprobe.com/tooling/dt37-soil-sampling-system/mn201385 |
| Retainer HD 208472, VC-GP-7410 | Obsolete. Not on any BOM. History price EUR 161.93. | Geoprobe names it "DT325 Retainer HD" and notes "No O-ring". It holds a liner. This machine does not use a liner. https://geoprobe.com/tooling/dt325-soil-sampling-system/mn208472 |

## Split carrier

VC-SP-7620 and VC-SP-7621 are one pair of half-shells.
They are draft make-parts.
VC-SP-7630 is the clamp fastener set.
The fastener size is unknown.

The halves sit inside the casing.
They hold 4 to 6 open tubes end to end at the sampling depths.
The pocket has no cap clearance.

Known input:

- Casing inside diameter: 2.625 in = 66.675 mm.
  REFERENCES.md did not previously state this inside diameter.
  The value is the 2026-11-19 decision.
  2.625 x 25.4 = 66.675 mm.

Placeholder values in the study solid (not measurements):

| Parameter | Placeholder | Status |
|---|---|---|
| Tube outside diameter | 30 mm | TBD. Confirm with RadicleLab. |
| Tube length | 100 mm | TBD. Confirm with RadicleLab. |
| Tube count in the study solid | 6 | The carrier must accept 4, 5 or 6. The solid shows the longest stack. |
| Wall thickness | 3 mm | TBD. |
| Radial clearance to the casing | 0.5 mm | Design allowance, not a measured fit. |
| Pocket radial clearance | 0.5 mm | Design allowance, not a measured fit. |
| Material | TBD | No mass is stored. |

The photo ratio of length to diameter is about 2.2 to 2.5.
That ratio is not a measurement.
The model does not use it.
Rib depth and the label recess are not in the solid.

The study STEP is `cad/export/step/VC-SP-7620.step` and `VC-SP-7621.step`.
Do not manufacture from those files.
Side B is the mirror of side A.
With a round pocket the two solids are congruent.

Stack length in the study solid = 6 x 100 mm = 600 mm.
The casing is 48 x 25.4 = 1219.2 mm long.
600 mm fits in that length.
The real stack length is unknown until the tube length is known.
Thread length inside the casing is also unknown.

## Rod guide

VC-FR-4500 was a closed bushing with an 83 mm bore.
The casing outside diameter is 82.55 mm.
The shoe outside diameter is 87.63 mm.
87.63 mm cannot pass an 83 mm bore.

The bushing is now a split bushing.
Close it to 83 mm on the casing.
Open it to pass the shoe.
Then close it again.
Length, flange and the latch are still unknown.

## Core scanner cradle

VC-CS-9480 was sized for an 82.6 mm casing, and the text called that body a polycarbonate liner.
That text is wrong.

The cradle must fit one sample tube.
The tube outside diameter is TBD.
Do not cut an 82.6 mm opening.
The tubes in the photo are orange plastic.
Do not assume the wall is clear.
Do not plan a through-wall colour correction until RadicleLab confirms the tube.

## Mast height

Known lengths:

| Item | Length |
|---|---|
| Mast profile | 1500 mm |
| Top plate thickness | 12 mm |
| Bottom plate thickness | 15 mm |
| Opening between those plates, if the plates sit on the profile ends | 1473 mm |
| Centre-column shaft | 200 mm |
| Vibrating plate | 20 mm |
| Casing | 1219.2 mm |
| Sum of the three known stack parts | 1439.2 mm |
| Remainder | 33.8 mm |

The remainder must hold the column flange, the adapter, the cutting shoe and the running clearance.
Those three lengths are unknown.
33.8 mm is not a demonstrated fit.

The carriage stroke in the firmware is 1300 mm.
The casing is 1219.2 mm.
The head still has to sit above the casing at the start of the stroke.

Do not change the 1500 mm profile in this revision.
Measure the shoe length and the adapter length first.
Then set the mast length.

The published machine height remains the range 1.50-1.70 m.
That range is not a checked stack.
