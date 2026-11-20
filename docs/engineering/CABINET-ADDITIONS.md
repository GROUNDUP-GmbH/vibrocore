# Cabinet additions

These parts are proposed purchases.
Do not edit the BOM in this change.
Order codes below are the proposed buy list.
Prices are not quotes.

## Do not buy a second hold

Stefan decided on 2026-11-20 that there is no second holding means.
The S200 motor holding brake is the only hold.
Nobody works under the raised head.
The chain drive is sized for the load.
The chain drive is inspected regularly.
This is a deliberate risk decision.
Do not buy a locking bolt for this function.
Do not buy a chain-break catch for this function.
Do not buy a second brake for this function.

## Sonic inverter

Buy Schneider Electric ATV320U15M2C.
The rating is 1.5 kW, 200-240 V, one phase in.
Heavy duty output current is 8.0 A.
Output frequency is 0.1 Hz to 599 Hz.
The drive has an STO input.
Each OLI MVE 400/6-HF draws about 1.45 A.
Two motors draw about 2.9 A together.
A 6-pole motor at 6000 rpm needs about 300 Hz.
8.0 A covers 2.9 A.
599 Hz covers 300 Hz.
The drive STO is a drive function.
Do not claim a machine performance level from it.
Data sheet: https://iportal.se.com/Contents/docs/SQD-ATV320U15M2C_DATASHEET.PDF
Product page: https://www.se.com/us/en/product/ATV320U15M2C/variable-speed-drive-altivar-machine-atv320-1-5kw-200-to-240v-1-phase-compact/

## Enabling switch

Buy IDEC HE1B-M1.
It is a 3-position enabling switch.
The positions are off, on, off.
One contact closes only in the middle position.
The contact is SPST-NO.
The rating on the body is IP40.
Mount it inside a housing.
Data sheet: https://www.mouser.com/catalog/specsheets/IDEC_HE1BSeries.pdf
Product page: https://www.idec.com/en-us/safety-explosion-protection/safety-components/enabling-switches/he1b-series/he1b-m1

## Tilt sensor

Buy ifm JN2200.
The type code is INC-M2M360ABIAKG/US.
The range is plus or minus 180 degrees.
The signal is 4-20 mA.
A fault current is about 2 mA.
This signal is why the RevPi AIO is required.
Data sheet: https://media.ifm.com/dam/5bb1f070-ef83-490a-b8e0-67515ba7967e/Original/JN2200-02_EN-US.pdf
Product page: https://www.ifm.com/us/en/product/JN2200

## Tilt contactors

Buy Finder 62.32.9.024.4000.
The contact set is two changeover contacts.
The contact rating is 16 A.
The coil is 24 V DC.
Use two contactors for the two tilt directions.
Never energize both contactors together.
The tilt actuator current is not on a nameplate here.
The present H-bridge note assumes 10 A.
A 16 A contact covers that assumption.
Confirm the current on the chosen actuator before you order.
Data sheet: https://www.relayspec.com/specs/175/S62EN.pdf

## Rotation drive

The drive type is not frozen.
The software command is a trait.
The default adapter is step and direction.
Buy Nanotec PD2-C4118L1804-E-01 as the proposed unit.
The supply is 12 V DC to 48 V DC.
The unit is a NEMA 17 motor with an integrated controller.
This order code speaks USB, not Modbus RTU.
Clock-direction mode is in the manual.
A Modbus RTU order code in the same family is TODO.
Do not treat this row as a released selection.
Manual: https://www.nanotec.com/fileadmin/files/Handbuecher/Handbuecher_Archiv/Plug_Drive/PD2-C/fir-v2139/PD2C_USB_Technical-Manual_V3.2.0.pdf
Product page: https://www.nanotec.com/eu/en/products/1892-pd2-c4118l1804-e-01

## Cable carrier

Buy igus e-chain 2400.05.075.0.
The series is 2400.
The bend radius on this length is 75 mm.
Use a drag chain, not a slip ring.
The head cables travel with the carriage.
The rod turns inside the head.
Motor power does not cross that rotating joint.
Buy a slip ring only if a later design routes power through the joint.
No slip ring order code is assigned.
Series page: https://www.igus.com/product/series-2400

## Analogue module

Buy Kunbus RevPi AIO item 100250.
It has current inputs for 4-20 mA.
The ifm JN2200 uses that range.
One DIO cannot read this sensor.
Data sheet: https://revolutionpi.com/fileadmin/downloads/datasheets/Datasheet_RevPi_AIO.pdf
