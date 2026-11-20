# VC-HB-2400

Manufacturer: KTR.
Type code: ROTEX 28.
The coupling is three public STEP files.

| Piece | Type | File | Bytes | URL |
|---|---|---|---|---|
| Hub, 32H7, with keyway | 020285103200 | `020285103200.stp` | 65403 | https://wsp007.ktr.com/spacecenter/model/020285103200?model=S214&pack=false |
| Hub, unbored | 020285100040 | `020285100040.stp` | 51972 | https://wsp007.ktr.com/spacecenter/model/020285100040?model=S214&pack=false |
| Spider, 92 Sh-A | 020281000045 | `020281000045.stp` | 208992 | https://wsp007.ktr.com/spacecenter/model/020281000045?model=S214&pack=false |

Each file starts with `ISO-10303-21`.
Downloaded: 2026-11-19.
Terms: public direct download, no account.
Check the manufacturer's terms before redistributing these files.

`load_vendor_shape` on this part would keep only the first sorted file and would recenter it.
The assembly calls `load_vendor_shape` once per file with `recenter=False`.
The jaw face is the file origin, not the box centre.

Each hub is Ø65 × 52.5 mm.
The jaw band is Z = 0 to 17.5 mm in the file.
The unbored hub is yawed 45° about Z, turned 180° about Y, then shifted +17.5 mm on Z.
The spider is shifted +8.75 mm on Z so it sits on that band.
`Rot(-90, 0, 0)` then lays the axis on Y.
The 32H7 hub faces −Y, toward the gearbox.
The gearbox is outboard of the coupling. Its output points toward the mast.
The unbored hub faces +Y. The separate brake is not in the train.

The oriented coupling is 65 × 87.5 × 65 mm.
The 50 mm envelope is only the fallback.
The 32H7 face sits on the output journal. The shaft tip meets the jaw face.
The placed coupling is still outside the head sweep.
The jaws and the spider share about 39 mm³ inside this one part.
That is the elastomer fit.
A boolean fuse of the three solids is rejected, so they stay one compound.
The Neugart shaft is not in this batch.
The 32H7 bore is the gearbox-side hub only.
The chain-side hub is unbored in the file. The assembly cuts a Ø30.4 mm bore into that hub.
Purchase hubs are Ø25H7, article 020285102500, and Ø30, article 020285103000.
The placed STEP is not those two hubs. A sleeve inside the 32H7 bore leaves Ø25.4 mm for the Ø25 journal.
The specified spider is 64 Sh-D. KTR lists TKmax 400 Nm, which covers gearbox T2max 365 Nm.
The public file in this folder is still 92 Sh-A, article 020281000045. Size 28 uses one envelope.
