# DT325 approximation solids

Geoprobe publishes no CAD for the DT325 tooling. These solids are envelopes.
Each one is marked as an approximation in the part name, the BOM spec and this file.
Do not manufacture from them.

The thread is a reduced band. It is not a helix.
Geoprobe does not state the thread form, the pitch or the engagement.
Those three values stay unknown.

## Sources

- DT325 SOP, MK3138, revised January 2011: https://geoprobe.com/sites/default/files/pdfs/dt325_sop_mk3138_0111-withmobilecode_0_0.pdf
- DT325 product sheet, 2013: https://geoprobe.com/sites/default/files/pdfs/ps_2013_dt325_0_0.pdf
- Tool string page: https://geoprobe.com/tooling/dt325-soil-sampling-system
- Liner dimensions page: https://geoprobe.com/tooling/liner-dimensions

The PDFs are not stored in this repository.

## What is placed

VC-GP-7200 is the cutting shoe already on the casing. The solid is now a tube with a thread band.
VC-GP-7330 is the 60 in sample sheath. The part solid is 1524 mm. The assembly seats only the free length below the split carrier.
VC-GP-7320 is SOP sheath drive head 10212, on top of that seated sheath.
VC-GP-7310 is catalog drive head 201385. It sits in the free bore above the split carrier. It stays obsolete and it is not a kit line.
The two heads are not joined. Center rods are not in this pose, because a rod would cross the split carrier.
The heads are not screwed into the sheath. Engagement is unknown, so the solids keep a gap.

## What is not placed

VC-GP-7410, retainer 208472, is not in the assembly. This machine does not use a liner. It stays obsolete and it has no solid.
Drive cap 9742 is the GH60 threadless cap. The current catalog number is 201275, already VC-GP-7300, and it is obsolete.
Drive cap 37708 is the 2011 SOP centering cap for 1.25 in rods. The current page lists a 1.25 in centering cap as MN 202145.
VC-SH-1500 is the sonic-head adapter on the 3.25 in casing. It is not 9742 and it is not 37708. Those caps are not modeled.
The liner, the 1.75 in shoe and the soil core are not solids.

## Dimensions

| Dimension | Value | Basis |
|---|---|---|
| Casing outside diameter, placed | 82.55 mm | Published 3.25 in. The SOP also writes 83 mm. The placed rod stays 82.55 mm so the 83 mm guide bore still fits. |
| Casing inside diameter | 66.675 mm | Published decision, 2.625 in. The SOP does not state the inside diameter. |
| Shoe outside diameter, placed | 87.63 mm | Published on the current tooling page for part 205449, 3.45 in. The 2011 SOP lists the same duty as 28508 and does not state this diameter. A stated 3.5 in (88.90 mm) is not used, so the existing envelope stays. |
| Shoe inside diameter | 46.99 mm | Published 1.85 in. SOP part 28508 and current part 205449. The SOP core diameter is written 47 mm. |
| Shoe length | 80 mm | Assumed. This is the existing placeholder. The SOP states no length. It is kept so the shoe tip and the machine height stay put. |
| Shoe thread band | 16 mm long, diameter 85.23 mm | Assumed visible band at the casing end. 2.4 mm less than the outside diameter. The thread form is unknown. |
| Sheath catalog length | 1524.0 mm | Published 60 in. SOP part 26719. The current catalog lists the 60 in sheath as MN 205099. |
| Sheath outside diameter | 60.0 mm | Assumed. It must pass the 66.675 mm bore and clear the 52.451 mm liner. No sheath diameter is published. |
| Sheath inside diameter | 53.0 mm | Assumed. About 0.27 mm of radial clearance on the liner outside diameter. |
| Sheath thread band | 16 mm at each end, bore 56.0 mm | Assumed. The SOP says both ends have the same internal thread. The form is unknown. |
| Placed sheath length | Free bore below the split carrier | Assumed fit. A 60 in sheath is longer than this 48 in rod, and the split carrier occupies the middle of the bore. The SOP says to match the sheath to the rod. |
| Drive-head body | 58 mm diameter, 44 mm long | Assumed. The body must fit the casing bore. No length is published. |
| Lower pin | 52 mm shoulder for 8 mm, then 49.6 mm for 14 mm | Assumed envelope that would enter the sheath. The solids are not mated, because the engagement is unknown. |
| Upper pin | 31.75 mm tip for 10 mm, then 29.35 mm for 26 mm | The 31.75 mm tip is the published 1.25 in pin. The band and both lengths are assumed. The form is unknown. |
| Drive-head length | 102 mm | Sum of the five assumed pieces. Parts 10212 and 201385 share this envelope, because no drawing separates them. |
| Liner | 52.451 mm outside, 49.911 mm inside | Published on the liner page, 2.065 in and 1.965 in. Not placed. The SOP rounds the outside to 2.1 in (53 mm). |
| Center rod | 31.75 mm outside | Published 1.25 in. Not placed. |
| Sample core | 47 mm by 1499 mm | Published in the SOP, 1.85 in by 59 in. It is the soil core, not a part. |
| Optional shoe inside diameter | 44.45 mm | Published 1.75 in. Not modeled. The placed shoe is the 1.85 in shoe. |
