# Electronics enclosure VC-ASM-5000

Study model. Do not manufacture from this note.
The solid is `cad/export/step/VC-ASM-5000.step`.
The box is not in the machine assembly.

## Box

Order Rittal AX 1181.000.
The box is sheet steel.
The rating is IP66.
The size is 800 x 1000 x 400 mm.
The mounting plate is included.
Installation depth T3 is 287.5 mm.
The S200 STEP depth is 214 mm.
The door clearance is 73.5 mm.
The price is unknown.
Source: https://www.rittal.com/pdf-creator/variant/com-en/1181000

The size 200 x 150 x 80 mm is withdrawn.
AX 1055.000 is not used.
Its T3 is 187.5 mm.
That depth is below the S200.

## Power

There is no 48 V rail.
Do not order SDR-480-48.
Do not order the 48 V to 12 V converter.
The S200 and the 1FL2 run on 230 V AC from the Instagrid.
Every other load is 24 V.

Two 24 V supplies sit on the DIN rail.

VC-PW-5310 is Mean Well SDR-120-24.
It is dedicated to the S200 control input and the motor brake.
The S200 control current is 2.2 A maximum.
The voltage window is 22.8 V to 28.8 V.
The brake current is below 1 A.
24 V is inside that window.
3.2 A is below the 5 A rating.
Nameplate heat at 120 W and 91 percent is 11.9 W.
The stated load is below that heat.

VC-PW-5320 is the supply for the rest of the machine.
The slot is the SDR-480-24 envelope.
That envelope is 85.5 x 125.2 x 128.5 mm.
The order is not frozen.
The current rating is open.
Actuator currents are not known.
Keep 40 mm above the supply, 20 mm below it, and 5 mm at each side.

## Heat

The check uses an IEC TR 60890 style area for one wall-mounted box.
A = 1.4 x W x (H + D) + 1.8 x H x D.
The area is 2.288 m2.
The steel factor is 5.5 W/m2K.
The sealed capacity at 10 K is 125.8 W.
Ambient temperature in the check is 40 C.
The internal limit in the check is 50 C.

Closed heat in the box is 118.7 W.
That figure gives about 49.4 C.
It includes the SDR-120-24 nameplate, the S200, a sonic-inverter candidate, the WAGO rack, the router bound, the PNOZ s4 supply, and small loads.
It does not include a 48 V supply.

A full SDR-480-24 at 94 percent loses about 30.6 W.
Add that ceiling and the total is 149.3 W.
That figure gives about 51.9 C.
The rating is not selected.
Do not treat 30.6 W as the installed loss.
The fan is not fitted.
Two door zones stay clear.
A later power budget decides if the fan is cut.
A cut drops the box from IP66 to IP54.

## Safety

Reserve DIN space for Pilz PNOZ s4, article 750104.
The size is 22.5 x 98 x 120 mm.
The DC supply is 2.5 W.
The safety assessment is open.
Do not state a performance level.

The E-stop is a 2-NC device.
One NC contact is hard-wired to the safety relay.
The PLC reads a monitor contact.
The PLC bit is not the only stop path.

The sonic inverter must have STO.
The order is not selected.
The enclosure holds a placeholder of 140 x 160 x 164.5 mm.

## Other layout

There is no chain-encoder gland.
Position comes from the 1FL2 absolute encoder through the S200.
The Option A rail is 150.6 mm.
Option B fits that rail.
Cable glands are on the bottom face.
The door faces the service side.
Mount the box on the idle-side mk 51.04 upright.
Do not place it in the tilt volume.

## Open points

The machine 24 V rating is open.
The sonic inverter order is open.
The safety assessment is open.
The box price is unknown.
The fan decision waits for the power budget.
