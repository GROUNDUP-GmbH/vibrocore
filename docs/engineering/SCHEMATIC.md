# Cabinet schematic

Drawing VC-SCH-5000 is the cabinet schematic.
The KiCad 8 project is `cad/kicad/vibrocore-control/`.
The PDF is `cad/export/kicad/vibrocore-control.pdf`.
The terminal list and the cable list are in that same directory.
A wire is a drawn segment.
A label names that wire.
A global label is used only when the net leaves the sheet.
The same global label on two sheets is one net.
The notes sheet lists every wire number that leaves its sheet.
Each circuit sheet keeps its notes in one band above the title block.
A marker such as (1) is the only note in the drawing area.
A note that does not fit in the band moves to the notes sheet.
Each symbol shows the reference, the maker and the short type, and the Ground UP article.
The title block revision is 0C.
Regenerate the sheets with `python3 cad/kicad/vibrocore-control/generate_schematic.py`.
Run ERC with `kicad-cli sch erc --severity-all --exit-code-violations`.

## Sheets

| Sheet | File | Content |
| --- | --- | --- |
| 1 | `vibrocore-control.kicad_sch` | Index |
| 2 | `01-power.kicad_sch` | Mains, isolator, RCD and the branch MCBs |
| 3 | `01b-supplies.kicad_sch` | Both 24 V supplies, 0 V and the PE bond |
| 4 | `02-safety.kicad_sch` | E-stop, PNOZ s4, STO, reset and feedback |
| 5 | `03-hub.kicad_sch` | S200, 1FL2104, encoder, brake, pulse and direction |
| 6 | `04-sonic.kicad_sch` | ATV320 and two OLI motors |
| 7 | `05-revpi.kicad_sch` | RevPi Connect 4 and one DIO |
| 8 | `06-field.kicad_sch` | Limits, enabling switch, index sensor and beacon |
| 9 | `06-tilt.kicad_sch` | Tilt contactors and the lift H-bridge |
| 10 | `07-rotation.kicad_sch` | Proposed rod-rotation drive |
| 11 | `08-network.kicad_sch` | RUT241, Ethernet and RS-485 |
| 12 | `09-terminals.kicad_sch` | Terminal strips X1 to X10, with the wire number and the section |
| 13 | `10-notes.kicad_sch` | Notes that do not fit on a sheet, and the net list |

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
No new EUR price is sourced.
Do not copy the old EUR 180-300 band onto the ATV320.
