# VC-HB-3100

Manufacturer: HIWIN.
Type code: HGR20R1300H.
Rail length 1300 mm. Width 20 mm. Height 17.5 mm from the mounting face.

URL: https://www.hiwin.de/en/configurator/newConfiguration/3PQ_GW
File: `HGR20R1300H.stp` (484365 bytes).
The file starts with `ISO-10303-21`.
Downloaded: 2026-11-19.
Terms: HIWIN CAD configurator, free account.
Check the manufacturer's terms before redistributing this file.

The file axes are X = width, Y = length, Z = height.
Z = 0 is the mounting face. The raceway is at Z = 17.5 mm.
`load_vendor_shape` is called with `recenter=False`, so that face stays put.
`Rot(90, 0, 0) * Rot(0, 90, 0)` maps the mounting face to X = 0 and the length to Z.
A shift of −650 mm then centres the 1300 mm length.
The assembly places X = 0 on the profile front face.
Bolt centres are 20 mm from each end and then every 60 mm.
The profile envelope has no matching holes. The solids meet on the face.
