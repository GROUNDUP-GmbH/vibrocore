# Cabinet schematic

Drawing VC-SCH-5000 revision 0D is the cabinet schematic.
The drawing of record is the QElectroTech project `cad/electrical/VC-SCH-5000/VC-SCH-5000.qet`.
The PDF is `cad/export/qet/VC-SCH-5000.pdf`.
One PNG per folio is in `cad/export/qet/png/`.
The title block reads Ground UP GmbH, file VC-SCH-5000, revision 0D, date 2026-11-20.
Regenerate the project with `python3 cad/electrical/VC-SCH-5000/generate_qet.py`.
The generator reads the component names, the article numbers, the terminal list and the cable list from the KiCad generator.
It does not add a part.

The KiCad 8 project `cad/kicad/vibrocore-control/` is a superseded reference.
Its revision is 0C.
Keep the files.
Do not treat the KiCad PDF as the drawing of record.
The KiCad ERC job still checks that reference.

Each folio has a column and row grid.
That grid is the current-path reference.
Power is at the top.
Control is below.
The flow is left to right.
A wire is orthogonal.
A wire shorter than one grid step is rejected.
Text that overlaps text, a symbol, a wire, a device border, the ruler or the title block is rejected.
A junction dot is a connection.
A crossing without a dot is not a connection.
Notes sit in the numbered notes field.
A marker such as (1) is the only note mark in the drawing area.
The terminal plan is folio 19.
The cable list is folio 20.
QElectroTech writes the component list, the wire list, the net list and the conductor list into `cad/export/qet/`.
The terminal-strip editor did not write a separate file.
Folio 19 is the terminal plan.
The conductor export carries the section and the colour.
It does not name the harness cables.
Folio 20 names those cables.

## Folios

| Folio | Title | Content |
| --- | --- | --- |
| 1 | Cover and folio index | Drawing index |
| 2 | Mains incoming | Instagrid, isolator Q1, RCD QF1, breaker F1, PE |
| 3 | Branch feeders | F2 is one three-pole GV2L20. Pole 3 is open. F3, F4 and F5 |
| 4 | 24 V supplies | G1 and G2 device boxes, F14, F24, 0 V and bond W1 |
| 5 | E-stop and PNOZ inputs | Mushroom E-stop, reset, and the PNOZ s4 device box |
| 6 | PNOZ outputs | PNOZ s4 output terminals, STO channels and the monitor contact |
| 7 | S200 power and motor | 6SL5510 and the 1FL2104 as device boxes |
| 8 | S200 control | S200 control terminals, encoder, pulse and RS-485 |
| 9 | ATV320 motor A | ATV320, F21 and motor A as device boxes |
| 10 | ATV320 motor B | ATV320, F22 and motor B. V and W swap at X3 |
| 11 | ATV320 control | ATV320 control terminals |
| 12 | RevPi supply | RevPi Connect 4 device, order 100378 |
| 13 | DIO channels | RevPi DIO device, order 100197 |
| 14 | Field devices | Limits, enabling switch, index sensor and beacon |
| 15 | Tilt | Finder 62.32 contactors and the tilt actuator |
| 16 | Lift | H-bridge and the lift actuators |
| 17 | Rotation proposal | Nanotec proposal, not released |
| 18 | Network | RUT241 device, Ethernet and RS-485 |
| 19 | Terminal plan | Strips X1 to X10 |
| 20 | Cable list | Harness cables |
| 21 | Notes | Points that apply to the whole drawing |

## Controller

The controller on this drawing is RevPi Connect 4, order 100378, part VC-CT-6800.
The I/O module is RevPi DIO, order 100197, part VC-CT-6810.
DIO input I1 is I/O-list index 0.
The channel table in `IO-LIST.md` is the source.
The WAGO PFC200 is not on this drawing.
VC-CT-6100 stays on the control BOM.
That BOM status is a separate decision.
There is no CODESYS target on this drawing.

## Safety

The E-stop has three NC contacts.
Two contacts go to the PNOZ s4, article 750104, part VC-CT-6220.
The third contact is DIO input index 2.
Set the PNOZ for two channels, short detection and a monitored manual reset.
Confirm the rotary-switch mark in the PNOZ s4 manual before you commission the relay.
PNOZ contact 13-14 is STO channel 1 for the S200 and for the ATV320.
PNOZ contact 23-24 is STO channel 2 for both drives.
The auxiliary contact 41-42 is DIO input 3.
Do not use that auxiliary contact in the safety path.
Do not use contact 33-34 for a normal load.
The reset button sits between S12 and S34.
The enabling switch is DIO input 6 only.
The enabling switch is not in the PNOZ.
The RevPi only reads feedback.
Do not claim an ISO 13849 performance level for this drawing.

## Power and 0 V

The AC source is the Instagrid ONE max, part VC-PW-5100.
The isolator Q1 does not switch PE.
The RCD QF1 is type B, 30 mA.
The SDR-120-24, part VC-PW-5310, feeds only S200 terminal X124.
The brake driver is inside the S200.
The brake coil stays on X108.
There is no second holding means.
The general 24 V supply is an SDR-480-24-size slot, part VC-PW-5320.
Both 0 V rails meet at terminal X1 pin 4.
W1 is the only bond from 0 V to PE.
Confirm that bond in the S200 PTI manual.
Remove W1 if that manual forbids the bond.
There is no 48 V rail.
VC-PW-5200 and VC-PW-5400 are obsolete.
The rotation drive has its own 2 A fuse on the general rail.

## Hub drive

Order the S200 as 6SL5510-1BB11-0AA0.
This is the PTI standard drive.
X131 pins are 1 STO1+, 2 STO1-, 3 STO-VS, 4 STO-M, 5 STO2+ and 6 STO2-.
STO1+ and STO2+ come from the PNOZ.
STO1- and STO2- go to 0 V.
STO-VS and STO-M are TBC.
Do not land 24 V on STO-VS until the figure is confirmed.
X130 is not on this PTI drive.
STO status is status word bit STO_EP.
Do not land 440_S200FB until a digital output is assigned.
U1 is the pulse and direction source.
U1 is not a DIO pin.
The pulse scale is TODO.

## Sonic motors

One ATV320 output feeds both OLI MVE 400/6-HF motors.
Motor A keeps the drive phase order.
Motor B swaps V and W at terminal X3.
F21 and F22 must tolerate a PWM output.
R1C is the fault-relay common and sits on the general 24 V rail.
R1B is the NC contact and feeds DIO input index 11.
R1A stays open.
Do not link the ATV320 P24 terminal to the cabinet 24 V.
F2 is a TeSys GV2L20.
NVE41289.09 lists it for ATV320U15M2 in an enclosure on 240 V one phase.
The line current is 17.8 A at 200 V.
The magnetic trip is 223 A.
Pole 3 is open.
The supply wire is 6 mm2.
Assign the second STO channel in SoMove.
The parameter name is TODO.
Relay R2 is the STO monitor for DIO input index 5.
The R2 parameter is TODO.

## Tilt and lift

Each tilt coil is in series with the NC contact of the other relay.
The off state puts both motor leads on 0 V.
Do not command both tilt directions.
Do not command both lift directions.
The lift power stage is the existing H-bridge VC-LT-9110.
The lift limit contacts are on the field-device sheet.
DI7 and DI8 are drawn as separate contacts.
Confirm the actuator terminal names.

## Rotation and network

The Nanotec PD2-C4118L1804-E-01 is a proposal.
It is not a released selection.
This order code speaks USB, not Modbus.
Clock and direction come from U2.
U2 is not a DIO pin.
The enable bit is DIO output 6.
The index sensor is B1 on the field-device sheet.
The RUT241 runs from the general 24 V rail.
RevPi ETH0 goes to the router LAN port.
Modbus slave 1 is the ATV320.
Modbus slave 2 is the S200.
The 120 ohm resistor is drawn at the S200.
Move it if the bus order changes.
The rotation drive is not on this bus.

## Terminals

Strips X1 to X10 are the names on this drawing.
The purchased terminal block is not chosen.
The mains cable is 3G6.
PE on that cable is 6 mm2.
The sonic feeder is 6 mm2.
The S200 feeder is 2.5 mm2.
Servo power and each vibrator output are 4G1.5 shielded.
The drive-to-protector wires 600_U, 600_V and 600_W are 1.5 mm2.
They are the same motor feed as that cable.
The harness cores stay 610_UA, 611_VA, 612_WA, 620_UB, 621_VB and 622_WB.
The servo brake pair is 2x0.75 mm2.
The general 24 V rail is 2.5 mm2.
The S200 24 V feed is 1.0 mm2.
STO, field signals and the rotation cable are 0.75 mm2.
The field 24 V feed is 1.0 mm2.
Tilt power is 1.5 mm2 and the current is TBC.
The lift section is TBC.

| Strip | Function |
| --- | --- |
| X1 | Mains L, N, PE and the 0 V star point |
| X2 | Sonic motor A, straight phase order |
| X3 | Sonic motor B, V and W swapped |
| X4 | Hub motor power |
| X5 | Hub encoder cable |
| X6 | Hub brake pair to S200 X108 |
| X7 | Field signals, beacon, limits and the index |
| X8 | Tilt actuator and its limit monitors |
| X9 | Proposed rotation drive |
| X10 | Lift actuator pair |

## Open points

The E-stop contact block is not chosen.
The reset-button order code and colour are not chosen.
The PNOZ rotary-switch detent text is not confirmed on the unit.
The state of auxiliary contact 41-42 is not confirmed.
X131 is confirmed.
X130 is absent on this drive.
STO-VS and STO-M are still TBC.
The STO status wire 440_S200FB is not landed.
The PTI connector name and the pulse scale are TODO.
The RS-485 port on the PTI unit is TODO.
The Siemens order codes for the motor cable and the encoder cable are TODO.
The RevPi power and RS-485 housing pin numbers are TODO.
The Instagrid source is 15.7 A continuous.
The drive rated input is 17.8 A at 200 V.
The drive does not run at rated input on this source.
The SoMove STO parameter and the RJ45 pin numbers are TODO.
The Modbus baud and parity are TODO.
F21 and F22 have no PWM-rated order code.
The index sensor order code is not chosen.
The drawing shows a PNP output.
The tilt actuator current and the internal limit names are TODO.
Confirm that the actuator allows both leads on 0 V.
Confirm that the Finder suffix .4000 has no internal diode.
Do not release the SDR-480-24 order until the actuator currents are known.
The energy-chain length for a 1300 mm stroke is TODO.
There is no slip ring.
The rotation cable is not released.
The feeder and the Instagrid may trip on the combined inrush.
The terminal list gives 211_24C as 1.0 mm2.
The supplies note calls the general 24 V rail 2.5 mm2.
Both statements are on revision 0C.
This drawing keeps both.
No new EUR price is sourced.
Do not copy the old EUR 180-300 band onto the ATV320.
