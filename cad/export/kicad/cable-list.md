# Cable list

The energy chain is VC-HB-3430.
A slip ring is not used.

| Cable | Part | From | To | Spec | In the chain | Note |
| --- | --- | --- | --- | --- | --- | --- |
| W-MAINS | VC-PW-5600 | Instagrid | X1 | 3G6, length TODO | no | Existing power cable set. |
| W-SON-A | VC-SH-1700 | X2 | M2 | 3x1.5 mm2 + PE, shielded | yes | Straight phases. |
| W-SON-B | VC-SH-1700 | X3 | M3 | 3x1.5 mm2 + PE, shielded | yes | V and W are swapped at X3. |
| W-HUB-P | VC-HB-3440 | X4 and X6 | M1 | Power and brake pair | no | Siemens order code TODO. Brake ends on X108. |
| W-HUB-E | VC-HB-3450 | X5 | M1 encoder | Catalogue encoder cable | no | Connector pinout is the Siemens cable. |
| W-STO | VC-CT-6730 | K1 | A2 and A3 | One twisted pair per STO channel | no | Do not mix the two channels in one pair. |
| W-IO | VC-CT-6740 | X7 and X8 | Field devices | 0.5 mm2 or 0.75 mm2 | part | Carriage limits and the head run in the energy chain. |
| W-ETH | VC-CT-6750 | A4 ETH0 | A7 LAN | Cat5e patch | no | Length assumed 0.5 m. |
| W-485 | VC-CT-6760 | A4 | A3 then A2 | Shielded twisted pair | no | 120 ohm at the S200. Shield to PE at the RevPi only. |
| W-ROT | VC-CT-6770 | X9 | A6 | 24 V plus clock, direction, enable | yes | Proposal. Not on the live BOM. |
| W-TILT | VC-CT-6740 | X8 | M4 | Two power cores and two limit cores | no | Actuator current is not confirmed. |
| W-LIFT | VC-LT-9120 | X10 and X7 | M5 and M6 | Power pair and series NC limits | no | Existing lift wiring line. |
| W-GNSS | VC-CT-6500 | Head | Receiver | Antenna cable | yes | Runs in VC-HB-3430. |
| W-CHAIN | VC-HB-3430 | Frame | Carriage | igus 2400.05.075.0 | yes | Bend radius 75 mm. Length for 1300 mm stroke is TODO. |
