# I/O list

This file maps every control signal to one channel.
One RevPi DIO, part VC-CT-6810, has 14 inputs and 14 outputs.
This machine uses 13 inputs and 7 outputs on that module.
One input stays spare.
Seven outputs stay spare.
A second I/O module is not required.
There is no analogue input module.
Byte offsets come from PiCtory.
The numbers below are channel indexes, not byte offsets.

## Safety note for every function

The Pilz PNOZ s4 and the drive STO inputs are hard-wired.
The RevPi only reads feedback.
Do not credit this software in any ISO 13849 performance level.
A crash of this software must not be the only path that removes torque.

## SF3 hub hold

Stefan decided on 2026-11-20 that there is no second holding means.
The S200 motor holding brake is the only hold.
The brake coil stays on S200 terminal X108.
The RevPi does not drive that coil.
Nobody works under the raised head.
The chain drive is sized for the load.
The chain drive is inspected regularly.
This is a deliberate risk decision.
The brake test is optional.
The test only watches slip after the carriage is parked.
The test is not a safety function.
There is no bolt sensor and no bolt output.
There is no catch output and no second brake output.

## SF4 jog

Jog runs only while the enabling switch is held.
The speed is lower than the drill speed.
Release of the switch stops the jog command.
This gate is software.
It is not a performance level.

## SF5 sonic head

The sonic inverter STO input is hard-wired from the PNOZ.
The RevPi only reads the STO feedback.
Loss of that feedback commands the head off.
That monitor is not a performance level.

## SF6 tilt and lift

Stefan removed the tilt angle limit on 2026-11-20.
The machine works on hilly farmland.
A five degree lock is not used.
Tilt keeps two direction outputs.
Both outputs are never on together.
The actuators stop on their own end switches.
There is no tilt sensor.
Lift motion does not read a tilt angle.
This code is not a performance level.

## Soil sample

The carriage drives the sampler in with the sonic head.
Sonic and lift then stop.
The rod then turns one revolution to cut the core.
The carriage stops at each depth stage.
One to four stages are allowed.
At each stage the rod turns to that container angle.
Rotation stays blocked while the sonic head runs.
Rotation stays blocked while the lift moves.
A stall or a torque limit aborts the sequence.
The index input sets the angle to zero.
This sequence is not a performance level.

## Digital inputs

| Index | Signal | Type | Device | Role |
| --- | --- | --- | --- | --- |
| 0 | Limit up | 24 V DC, NC | Carriage upper limit | Hub overtravel monitor |
| 1 | Limit down | 24 V DC, NC | Carriage lower limit | Hub overtravel monitor |
| 2 | E-stop feedback | 24 V DC, NC | E-stop contact | Monitor only |
| 3 | Safety relay feedback | 24 V DC | PNOZ s4, article 750104 | Monitor only |
| 4 | S200 STO feedback | 24 V DC | S200 STO feedback | Hub drive STO monitor |
| 5 | Sonic STO feedback | 24 V DC | Sonic inverter STO feedback | SF5 monitor |
| 6 | Enabling held | 24 V DC, NO | IDEC HE1B-M1 | Closed only in position 2 |
| 7 | Tilt vertical | 24 V DC, NC | Tilt actuator limit | At vertical |
| 8 | Tilt folded | 24 V DC, NC | Tilt actuator limit | At folded |
| 9 | Lift deployed | 24 V DC, NC | Lift actuator limit | Tool lowered |
| 10 | Lift retracted | 24 V DC, NC | Lift actuator limit | Tool raised |
| 11 | Sonic fault | 24 V DC | Sonic inverter fault relay | Monitor |
| 12 | Rotation index | 24 V DC | Rotation index or marker | Sets angle zero |
| 13 | Spare |  |  |  |

## Digital outputs

| Index | Signal | Type | Device | Role |
| --- | --- | --- | --- | --- |
| 0 | Lift extend | 24 V DC | Existing lift H-bridge | Deploy the sampling lift |
| 1 | Lift retract | 24 V DC | Existing lift H-bridge | Raise the sampling lift |
| 2 | Tilt toward vertical | 24 V DC | Finder 62.32.9.024.4000 | One direction only |
| 3 | Tilt toward fold | 24 V DC | Finder 62.32.9.024.4000 | One direction only |
| 4 | Alarm beacon | 24 V DC | Beacon | Alarm lamp |
| 5 | Sonic fault reset | 24 V DC | Sonic inverter reset input | Reset pulse |
| 6 | Rotation enable | 24 V DC | Rotation drive enable | Not the step train |
| 7 to 13 | Spare |  |  |  |

Never energize lift extend and lift retract together.
Never energize both tilt directions together.

## Not on the DIO

The S200 pulse train is not a DIO output.
The S200 PTI accepts a fast pulse train.
A DIO output cannot source that train.
The pulse scale is TODO.
S200 fault status is Modbus.
Those registers are TODO.
Rod rotation step pulses are not a DIO output.
The rotation enable output is only the enable bit.
The rotation register map is TODO.
The S200 holding brake is not a DIO output.
