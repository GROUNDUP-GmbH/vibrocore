# Cabinet schematic

Drawing VC-SCH-5000 is the cabinet schematic.
The KiCad 8 project is `cad/kicad/vibrocore-control/`.
The PDF is `cad/export/kicad/vibrocore-control.pdf`.
The terminal list and the cable list are in that same directory.
Wire numbers are the global labels.
The same label on two sheets is one net.
Sheet 1 lists every wire number that leaves its sheet.
Regenerate the sheets with `python3 cad/kicad/vibrocore-control/generate_schematic.py`.
Run ERC with `kicad-cli sch erc --severity-all --exit-code-violations`.

## Sheets

| Sheet | File | Content |
| --- | --- | --- |
| 1 | `vibrocore-control.kicad_sch` | Index and wire-number cross reference |
| 2 | `01-power.kicad_sch` | Mains, isolator, RCD, branch MCBs, both 24 V supplies, 0 V and PE |
| 3 | `02-safety.kicad_sch` | E-stop, PNOZ s4, STO, reset and feedback |
| 4 | `03-hub.kicad_sch` | S200, 1FL2104, encoder, brake, pulse and direction |
| 5 | `04-sonic.kicad_sch` | ATV320 and two OLI motors |
| 6 | `05-revpi.kicad_sch` | RevPi Connect 4, one DIO, limits, enabling switch and index |
| 7 | `06-tilt.kicad_sch` | Tilt contactors and the lift H-bridge |
| 8 | `07-rotation.kicad_sch` | Proposed rod-rotation drive |
| 9 | `08-network.kicad_sch` | RUT241, Ethernet and RS-485 |

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
The third contact is DIO input 2.
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
The general 24 V supply is an SDR-480-24-size slot, part VC-PW-5210.
Both 0 V rails meet at terminal X1 pin 4.
W1 is the only bond from 0 V to PE.
Confirm that bond in the S200 PTI manual.
Remove W1 if that manual forbids the bond.
VC-PW-5200, the 48 V supply, is not connected.
VC-PW-5400 is not connected.
The rotation drive has its own 2 A fuse on the general rail.

## Hub drive

Order the S200 as 6SL5510-1BB11-0AA0.
X131 and X108 are the terminals of the PTI standard drive.
The STO pin order on this drawing is taken from the S200 PN sheet.
Confirm that order on the PTI sheet.
U1 is the pulse and direction source.
U1 is not a DIO pin.
The pulse scale is TODO.

## Sonic motors

One ATV320 output feeds both OLI MVE 400/6-HF motors.
Motor A keeps the drive phase order.
Motor B swaps V and W at terminal X3.
F21 and F22 must tolerate a PWM output.
Do not link the ATV320 P24 terminal to the cabinet 24 V.
Assign the second STO channel in SoMove.
The parameter name is TODO.
Relay R1B opens on a fault and feeds DIO input 11.
Relay R2 is the STO monitor for DIO input 5.
The R2 parameter is TODO.

## Tilt and lift

Each tilt coil is in series with the NC contact of the other relay.
The off state puts both motor leads on 0 V.
Do not command both tilt directions.
Do not command both lift directions.
The lift power stage is the existing H-bridge VC-LT-9110.
The lift limit contacts are on sheet 6.
DI7 and DI8 are drawn as separate contacts.
Confirm the actuator terminal names.

## Rotation and network

The Nanotec PD2-C4118L1804-E-01 is a proposal.
It is not a released selection.
This order code speaks USB, not Modbus.
Clock and direction come from U2.
U2 is not a DIO pin.
The enable bit is DIO output 6.
The index sensor is B1 on sheet 6.
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
The cross-section is an assumption: 6 mm2 on the mains, 4 mm2 on the motor power, 2.5 mm2 on the 24 V rails.

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
The S200 X131 pin order is not confirmed on the PTI sheet.
The X130 STO-status pin name is TODO.
The PTI connector name and the pulse scale are TODO.
The RS-485 port on the PTI unit is TODO.
The Siemens order codes for the motor cable and the encoder cable are TODO.
The RevPi power and RS-485 housing pin numbers are TODO.
The ATV320 line current is not confirmed against the C16 breaker and the Instagrid current.
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
