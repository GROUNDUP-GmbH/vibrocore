# Open points on the Vibrocore CAD model

Generated from `cad/bom/vibrocore.bom.yaml`. Do not edit by hand.
The Odoo-side work is in `docs/cad/ODOOPLM.md`.

## Known conflicts in the source BOM

- `legacy-row-numbers`: BOM.md skips rows 9-16 and reuses rows 56-63 in Control, Geoprobe and Positioning. legacy_ref is section.row.
- `control-subtotal-mismatch`: Control line estimates sum to EUR 1515-2420. BOM.md prints 1475-2610 in the section and 1345-2220 in the summary. Line estimates are kept.
- `positioning-gps-duplicate`: Section 7 items 61-62 repeat the GPS antenna and ZED-F9P of section 5 items 59-60. One of each is kept on the control BOM. The positioning kit is viDoc plus the WLAN bridge. The published positioning subtotal is EUR 200-350 higher, which matches that duplicate pair.
- `power-psu-conflict`: BOM.md specifies 48 V / 10 A. CONTROL_SYSTEM.md draws Mean Well SDR-75-48 at 1.6 A. The part follows the BOM text and does not take the diagram order code.
- `dc-converter-candidate`: CONTROL_SYSTEM.md names Mean Well DDR-60D-24. BOM.md does not. It stays a note, not a manufacturer PN.
- `plc-name-in-dimensioning`: DIMENSIONING.md section 9 still says CONTROLLINO or Arduino Opta. The later BOM and CONTROL_SYSTEM.md specify the WAGO PFC200 XTR.
- `instagrid-rental`: The power rollup uses the EUR 2500 purchase price. BOM.md's low scenario is a rental and is not a stock component.
- `fastener-kits`: Fasteners stay as the single kit lines from BOM.md. The 8x M12x40 and 6x M10 mentions in SONIC_HEAD.md are not exploded.

## Parts with undocumented geometry or procurement data

- `VC-ASM-0000` Vibrocore V1: Machine height is published as a range, 1.50-1.70 m, not a single value.
- `VC-ASM-0000` Vibrocore V1: UTV mount and tilt-lock dimensions are not specified.
- `VC-ASM-1000` Sonic head assembly: Motor centre distance is only a minimum of 170 mm. It is not a frozen pitch, so the motors are not placed in the 3D model.
- `VC-ASM-1000` Sonic head assembly: Isolator coordinates are not given.
- `VC-ASM-2000` Hub system assembly: Carriage plate length and width are not given, only the 10 mm thickness.
- `VC-ASM-2000` Hub system assembly: Drive-shaft length is not given. Diameter is published as a range, 25-30 mm.
- `VC-ASM-3000` Frame assembly: Profile connector types are not identified beyond mk standard corners or T-slot nuts.
- `VC-ASM-3000` Frame assembly: Tilt mechanism, gas strut and stabiliser feet have no selected order codes.
- `VC-ASM-4000` Power system assembly: no solid. Dimensions were not complete enough to model.
- `VC-ASM-5000` Control system assembly: no solid. Dimensions were not complete enough to model.
- `VC-CT-6100` WAGO PFC200 XTR: no solid. Dimensions were not complete enough to model.
- `VC-CT-6110` WAGO 750-430 XTR: no solid. Dimensions were not complete enough to model.
- `VC-CT-6120` WAGO 750-530 XTR: no solid. Dimensions were not complete enough to model.
- `VC-CT-6130` WAGO 750-637: no solid. Dimensions were not complete enough to model.
- `VC-CT-6140` WAGO 750-826: no solid. Dimensions were not complete enough to model.
- `VC-CT-6150` WAGO 750-600: no solid. Dimensions were not complete enough to model.
- `VC-CT-6200` Inductive limit switch: no solid. Dimensions were not complete enough to model.
- `VC-CT-6210` Emergency stop: no solid. Dimensions were not complete enough to model.
- `VC-CT-6220` Safety relay: no solid. Dimensions were not complete enough to model.
- `VC-CT-6300` Control enclosure: Confirm the enclosure actually fits the WAGO rack and the VFD. Do not treat 200 x 150 x 80 mm as a checked layout.
- `VC-CT-6400` RDDL trust wallet: no solid. Dimensions were not complete enough to model.
- `VC-CT-6410` SE050 breakout: no solid. Dimensions were not complete enough to model.
- `VC-CT-6500` GPS antenna u-blox ANN-MB: no solid. Dimensions were not complete enough to model.
- `VC-CT-6510` GPS receiver u-blox ZED-F9P: no solid. Dimensions were not complete enough to model.
- `VC-CT-6600` Teltonika RUT241: no solid. Dimensions were not complete enough to model.
- `VC-CT-6610` LTE SIM data plan: no solid. Dimensions were not complete enough to model.
- `VC-CT-6620` DC converter 24 V to 9 V: Confirm the router is not powered directly from 24 V.
- `VC-CT-6700` Wiring harness: no solid. Dimensions were not complete enough to model.
- `VC-FR-4100` Aluminium profile 50x100x1500: mk 2004 slot geometry is not in the repository. The solid is the outer envelope only and is not a machining model.
- `VC-FR-4100` Aluminium profile 50x100x1500: Alloy and the exact mk order code.
- `VC-FR-4200` Profile connector: Which mk connector.
- `VC-FR-4300` Bottom steel plate: Rod-guide bore position, NEMA 42 mount, profile feet and UTV holes.
- `VC-FR-4400` Top steel plate: Idle-sprocket mount and profile bolt pattern.
- `VC-FR-4500` Rod guide bushing: Length, flange and housing diameter.
- `VC-FR-4600` UTV mounting bracket: UTV interface dimensions.
- `VC-FR-4700` Tilt mechanism: Strut force, hinge pin and lock.
- `VC-FR-4800` Stabiliser foot: Selected jack and the pad size.
- `VC-FR-4900` Fastener kit, frame: no solid. Dimensions were not complete enough to model.
- `VC-GP-7100` DT325 probe rod pair: no solid. Dimensions were not complete enough to model.
- `VC-GP-7200` DT325 cutting shoe: no solid. Dimensions were not complete enough to model.
- `VC-GP-7300` Drive cap GH60: no solid. Dimensions were not complete enough to model.
- `VC-GP-7400` Core liner 3.25 inch: no solid. Dimensions were not complete enough to model.
- `VC-HB-2100` NEMA 42 closed-loop stepper: Exact catalogue number, body length and mass.
- `VC-HB-2200` Planetary gearbox PLPE120-040: Input flange code for the selected NEMA 42 motor.
- `VC-HB-2300` Closed-loop stepper driver: Final driver, and therefore the connector and the encoder interface.
- `VC-HB-2400` Elastomer coupling: Bore pair. Gearbox output is 32 mm; the drive shaft is not frozen.
- `VC-HB-2500` Hub drive shaft: Diameter inside the 25-30 mm range, length, key size and sprocket seat.
- `VC-HB-2600` Pillow block UCP 206: Confirm 30 mm bore against the final shaft diameter. HUB_SYSTEM.md also mentions UCP 205/206.
- `VC-HB-2700` Duplex chain 10B-2: no solid. Dimensions were not complete enough to model.
- `VC-HB-2800` Sprocket 10B-2 15T drive: no solid. Dimensions were not complete enough to model.
- `VC-HB-2810` Sprocket 10B-2 15T idle: no solid. Dimensions were not complete enough to model.
- `VC-HB-2900` Chain tensioner: Selected model.
- `VC-HB-3000` Power-off brake 24 V: Catalogue number and the matching shaft bore.
- `VC-HB-3100` Linear guide rail HGR20: no solid. Dimensions were not complete enough to model.
- `VC-HB-3110` Linear carriage HGH20: no solid. Dimensions were not complete enough to model.
- `VC-HB-3200` Carriage plate: Length, width, hole pattern and chain-pin position. Thickness alone is not enough to model a blank.
- `VC-HB-3300` Fastener kit, hub: no solid. Dimensions were not complete enough to model.
- `VC-KIT-6000` DT325 sampling kit: no solid. Dimensions were not complete enough to model.
- `VC-KIT-7000` Positioning kit: no solid. Dimensions were not complete enough to model.
- `VC-PS-8100` viDoc RTK Light: no solid. Dimensions were not complete enough to model.
- `VC-PS-8200` WLAN bridge: no solid. Dimensions were not complete enough to model.
- `VC-PW-5100` Instagrid ONE max: no solid. Dimensions were not complete enough to model.
- `VC-PW-5200` DIN-rail supply 48 V 10 A: no solid. Dimensions were not complete enough to model.
- `VC-PW-5300` DC converter 48 V to 24 V: no solid. Dimensions were not complete enough to model.
- `VC-PW-5400` DC converter 48 V to 12 V and 5 V: Whether this is one dual-output converter or two parts.
- `VC-PW-5500` Power distribution kit: no solid. Dimensions were not complete enough to model.
- `VC-PW-5600` Power cable set: no solid. Dimensions were not complete enough to model.
- `VC-SH-1100` OLI MVE 400/6-HF: Which motor axis is the 90 mm bolt pitch, and which is the 125 mm pitch, is not stated.
- `VC-SH-1100` OLI MVE 400/6-HF: The solid is the published envelope, not a manufacturer model.
- `VC-SH-1200` Frequency inverter 1.5 kW: Enclosure size, braking behaviour beyond the V20 parameter notes, and the final order code.
- `VC-SH-1300` Vibrating plate weldment: Rib spacing and weld details are not specified, so the ribs are separate blanks and are not positioned on the plate.
- `VC-SH-1301` Vibrating plate blank: 4x M12 isolator coordinates.
- `VC-SH-1301` Vibrating plate blank: Two times 4x M12 motor holes. Pitch is 90 x 125 mm, location on the plate is not fixed.
- `VC-SH-1301` Vibrating plate blank: Edge preparation, surface finish and whether the plate is 20 mm finished or stock.
- `VC-SH-1302` Stiffener rib: Weld position on the plate.
- `VC-SH-1400` Center column: Flange thickness, bolt-circle diameter and whether the 6x M10 holes are tapped or through.
- `VC-SH-1400` Center column: Flange diameter 80 mm is published, but it is not modelled until the thickness is known.
- `VC-SH-1500` DT325 adapter: Thread designation, engagement length and wrench flats. Do not model until the Geoprobe interface is confirmed.
- `VC-SH-1600` Rubber isolator M12: Catalogue number, free height and stud length.
- `VC-SH-1700` Motor cable shielded: Exact length and gland sizes.
- `VC-SH-1800` Fastener kit, sonic head: no solid. Dimensions were not complete enough to model.

## Modelled in this revision

- `VC-SH-1100` OLI MVE 400/6-HF: box, fidelity `envelope` (docs/design/SONIC_HEAD.md#2.2).
- `VC-SH-1301` Vibrating plate blank: box, fidelity `partial` (docs/engineering/DIMENSIONING.md#3.1).
- `VC-SH-1302` Stiffener rib: box, fidelity `solid` (docs/engineering/DIMENSIONING.md#3.1).
- `VC-SH-1400` Center column: cylinder, fidelity `partial` (docs/design/SONIC_HEAD.md#8).
- `VC-FR-4100` Aluminium profile 50x100x1500: box, fidelity `envelope` (docs/engineering/BOM.md#3).
- `VC-FR-4300` Bottom steel plate: box, fidelity `partial` (docs/engineering/BOM.md#3).
- `VC-FR-4400` Top steel plate: box, fidelity `partial` (docs/engineering/BOM.md#3).
