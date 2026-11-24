# VC-HB-3100

The manufacturer is HIWIN.
The type code is HGR20R1300H.
The rail length is 1300 mm.
The width is 20 mm.
The height is 17.5 mm from the mount face.
The URL is https://www.hiwin.de/en/configurator/newConfiguration/3PQ_GW

- The file is `HGR20R1300H.stp` (484365 bytes).
- The file starts with `ISO-10303-21`.
- The download date is 2026-11-19.
- The terms are the HIWIN CAD configurator and a free account.
- You must check the terms of the manufacturer before you send this file to other persons.

The file axes are X = width, Y = length and Z = height.
Z = 0 is the mount face.
The raceway is at Z = 17.5 mm.
The call to `load_vendor_shape` uses `recenter=False`, so that face stays put.
`Rot(90, 0, 0) * Rot(0, 90, 0)` maps the mount face to X = 0 and the length to Z.

- A shift of −650 mm then centres the length of 1300 mm.
- The assembly places X = 0 on the front face of the profile.
- Bolt centres are 20 mm from each end and then every 60 mm.
- The profile envelope has no holes that match.
- The solids meet on the face.
