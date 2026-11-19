# VC-HB-3000

Manufacturer: Kendrion INTORQ.
Type code: BFK457-10 Compact.
Holding torque: 16 Nm.
Bore: d10H7.

URL: https://www.kendrion.com/fileadmin/user_upload/Downloads/3D-Models_Step-Files/Industrial_Brakes_INTORQ/BFK457.zip
Zip size: 5156827 bytes, under 5 MB.
The zip is not in the repository.
File kept: `5028671_BFK457-10_Compact_d10H7.stp` (1080866 bytes).
This is size 10 Compact.
It is not Compact_HL and it is not another size.
The file starts with `ISO-10303-21`.
Downloaded: 2026-11-19.
Terms: public direct download, no account.
Check the manufacturer's terms before redistributing this file.

`load_vendor_shape` recenters the bounding box and does not rotate the file.
The cable pulls that centre off the shaft.
The assembly then moves the origin onto the rotor.
The file shaft is +X.
The cable runs toward −Y.
A lug reaches −Z.
`Rot(90, 270, 0)` maps the shaft onto Y, the cable onto −Z and the lug onto +X.
`Rot(0, -90, 0)` about the shaft then sends the cable forward and the lug up.
A cable on −Z would pass through the bottom plate.

The oriented bounding box is about 145.31 × 68.50 × 234.79 mm.
The magnet body is Ø130 mm.
The cable and the lug make the box larger than that body.
The body rear is 65 mm behind the shaft axis.
The axis is at X = 15 mm, so the body is flush with the profile rear face at X = −50 mm.
The axis height is Z = 82 mm.
The body bottom is then 2 mm above the bottom plate.
The cable runs forward, to about X = 185 mm.
The lug points up.
The train stands on the drive side of the head, outside the head's Y sweep.
A 2 mm gap stays between the brake and the gearbox, and between the motor shaft tip and the brake.
The bore is d10H7.
The stand-in motor shaft is Ø19 mm.
The two are not mated.
