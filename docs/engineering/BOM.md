# Bill of Materials (BOM)

Preliminary BOM for Vibrocore V1 prototype.
All prices are estimates; verify with suppliers before ordering.

## 1. Sonic Head (V2: 2× OLI MVE 400/6-HF)

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
| 1 | OLI MVE 400/6-HF       | HF vibration motor, 7.2 kg, 4 kN |   2 |  600–900 | OLI Vibrators (IT) / dealer|
| 2 | VFD                     | 1.5 kW, 230V 1ph in, 3ph out     |   1 |  180–300 | Siemens V20 / ABB ACS150   |
| 3 | Vibrating plate         | S355J2, 420×300×20 mm + ribs      |   1 |  200–350 | Custom fabrication (EU)    |
| 4 | Center column           | 42CrMo4, Ø50×200 mm + flange     |   1 |   80–120 | Custom machining (EU)      |
| 5 | DT325 adapter           | Steel, thread to Geoprobe spec    |   1 |   60–100 | Custom machining (EU)      |
| 6 | Rubber isolators M12    | 55–70 Shore A, cylindrical        |   4 |   30–60  | Schwingmetall / Paulstra   |
| 7 | Motor cable (shielded)  | 3×1.5 mm², < 5 m                 |   2 |   15–30  | Lapp (DE)                  |
| 8 | Fasteners (head)        | M12×40 (motors), M10 (column)    |   1 |   20–40  | Würth / Bossard (EU)       |

**Sonic Head Subtotal: ~1,185–1,900 €**

*Note: V2 eliminates custom eccentric shafts, discs, timing belts, and external
bearings — all handled internally by the OLI motors. Significant cost and
complexity reduction vs. V1 custom design.*

## 2. Hub System

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|17 | NEMA 42 stepper motor   | CL, 20 Nm, 6A, encoder           |   1 |  250–400 | Nanotec (DE) / Leadshine   |
|18 | Planetary gearbox       | PLPE120-040, 40:1                 |   1 |  600–900 | Neugart (DE)               |
|19 | Stepper driver          | CL86T-V4.1 or C5-E               |   1 |   80–150 | Nanotec / Leadshine (EU)   |
|20 | Elastomer coupling      | R+W EKH or KTR ROTEX 28          |   1 |   60–100 | R+W (DE) / KTR (DE)       |
|21 | Drive shaft             | Ø25–30 mm, keyed                  |   1 |   30–50  | Custom / standard (EU)     |
|22 | Pillow block UCP 206    | Self-aligning, Ø30 bore           |   2 |   30–50  | SKF / Schaeffler (EU)      |
|23 | Chain 10B-2 duplex      | 3.2 m, pre-greased                |   1 |   30–50  | iwis / Wippermann (DE)     |
|24 | Sprocket 10B-2 15T      | Taper-lock, drive                 |   1 |   25–40  | z24.de / ETKF (DE)         |
|25 | Sprocket 10B-2 15T      | Bearing-mounted, idle             |   1 |   30–50  | z24.de / ETKF (DE)         |
|26 | Chain tensioner          | Spring-type or adjustable         |   1 |   20–40  | Standard (EU)              |
|27 | Power-off brake         | 24V, 15 Nm, spring-applied        |   1 |  100–180 | Kendrion / Mayr (DE)       |
|28 | Linear guide rail HGR20 | 1,300 mm length                   |   2 |  100–180 | Hiwin / Bosch Rexroth      |
|29 | Linear slider HGH20     | Ball bearing type                  |   4 |   80–140 | Hiwin / Bosch Rexroth      |
|30 | Carriage plate          | 10 mm steel, machined             |   1 |   80–120 | Custom (EU)                |
|31 | Fasteners (hub)         | M6–M12, various                   |   1 |   20–40  | Würth / Bossard (EU)       |

**Hub System Subtotal: ~1,535–2,490 €**

## 3. Frame & Mounting

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|32 | Al profile 50×100       | mk 2004, 1,500 mm                 |   2 |  120–180 | mk Technology (DE)         |
|33 | Profile connectors      | mk standard corners/T-slot        |   8 |   40–80  | mk Technology (DE)         |
|34 | Bottom steel plate      | S355, 400×300×15 mm, machined     |   1 |   80–120 | Custom (EU)                |
|35 | Top steel plate         | S355, 300×200×12 mm, machined     |   1 |   50–80  | Custom (EU)                |
|36 | Rod guide bushing       | Bronze/PTFE, Ø83 bore             |   1 |   20–40  | Custom (EU)                |
|37 | UTV mounting brackets   | Steel, welded/bolted              |   4 |   60–100 | Custom (EU)                |
|38 | Tilt mechanism          | Hinge + gas strut + lock          |   1 |  100–180 | Standard parts (EU)        |
|39 | Stabiliser feet         | Adjustable screw jacks            |   4 |   40–80  | Standard (EU)              |
|40 | Fasteners (frame)       | M8–M16, various                   |   1 |   30–50  | Würth / Bossard (EU)       |

**Frame Subtotal: ~540–910 €**

## 4. Power System (Phase 1 — PoC)

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|41 | Instagrid ONE max       | 230V AC, 3.6 kW, 2.1 kWh         |   1 | 2,500*   | instagrid.co (rental opt.) |
|42 | DC PSU 48V              | 230V AC → 48V/10A DC, DIN rail   |   1 |   80–140 | Mean Well (EU)             |
|43 | DC/DC 48V → 24V        | For brake, relays                 |   1 |   20–40  | Traco / Mean Well (EU)     |
|44 | DC/DC 48V → 12V/5V    | For PLC, sensors                  |   1 |   15–30  | Traco / Mean Well (EU)     |
|45 | Power distribution      | DIN rail, fuses, contactors       |   1 |   60–100 | Schneider / Eaton (EU)     |
|46 | Cable set               | Silicone, shielded, 2.5–6 mm²    |   1 |   40–80  | Lapp (DE)                  |

*Instagrid ONE typically rented (€95/week). Purchase ~€2,500.

**Power System Subtotal: ~2,715–2,890 € (with purchase) / ~310–490 € (with rental)**

## 5. Control & Electronics

| # | Component                   | Spec                                        | Qty | Est. €    | Supplier / Source            |
|---|-----------------------------|---------------------------------------------|-----|-----------|------------------------------|
|47 | WAGO PFC200 XTR             | 750-8212, −40..+70°C, 5g vib, 2×ETH, RS-485 |   1 |  600–900  | wago.com (DE)                |
|48 | WAGO 750-430 XTR            | 4× DI 24V DC, CAGE CLAMP                   |   1 |   60–90   | wago.com (DE)                |
|49 | WAGO 750-530 XTR            | 4× DO 24V DC, 0.5A, CAGE CLAMP             |   1 |   60–90   | wago.com (DE)                |
|50 | WAGO 750-637                | Incremental encoder interface               |   1 |  100–150  | wago.com (DE)                |
|51 | WAGO 750-826                | RS-485 Modbus RTU serial interface          |   1 |   80–120  | wago.com (DE)                |
|52 | WAGO 750-600                | End module                                  |   1 |   10–20   | wago.com (DE)                |
|53 | Limit switches              | Inductive, M12, NC, IP67                   |   2 |   30–60   | ifm / Sick (DE)              |
|54 | Emergency stop              | Mushroom NC, Category 3, IP65 enclosure    |   1 |   40–70   | Eaton / Schneider (EU)       |
|55 | Safety relay                | Pilz PNOZ m B0 or equivalent               |   1 |   80–130  | Pilz (DE)                   |
|56 | Control enclosure           | IP65, DIN rail, 200×150×80mm               |   1 |   40–80   | Rittal / Spelsberg (DE)      |
|57 | RDDL Trust Wallet           | Xiao ESP32-C3 + NXP SE050 breakout         |   1 |   25–50   | Seeed Studio / Mouser (EU)   |
|58 | SE050 breakout board        | NXP OM-SE050ARD or compatible              |   1 |   20–40   | NXP / Mouser (EU)            |
|59 | GPS antenna (drill head)    | u-blox ANN-MB, multi-band, SMA             |   1 |   50–80   | u-blox (CH)                  |
|60 | GPS receiver                | u-blox ZED-F9P, RTK capable                |   1 |  150–250  | u-blox / Mouser (EU)         |
|61 | Teltonika RUT241            | LTE Cat4 router, DIN-rail, −40..+75°C      |   1 |  100–160  | teltonika-networks.com (LT)  |
|62 | SIM card (data-only)        | LTE 1 GB/month, AT or HU carrier           |   1 |   10–20   | Any carrier                  |
|63 | DC step-down 24V→9V         | Power for RUT241 from 24V rail             |   1 |   10–20   | Traco / Mean Well (EU)       |
|64 | Wiring harness              | CAGE CLAMP terminals, shielded cables      |   1 |   50–90   | Weidmüller / Phoenix (DE)    |

**Control Subtotal: ~1,475–2,610 €**

> **Notes:**
> - CONTROLLINO / Arduino Opta removed — WAGO PFC200 XTR is the V1 production controller.
> - Teltonika RUT241: LTE for remote CODESYS debugging, OTA updates, MQTT to RDDL.
> - **No external braking resistor required.** The 80 J fast-stop energy is dissipated
>   as heat in the OLI motor windings via DC injection braking (P1232=100%).
>   Temperature rise: 0.012 °C per stop — negligible at 7.2 kg motor thermal mass.
>   V20 Vdc-max controller (P1240=1) prevents DC bus overvoltage during ramp.
>   If bus overvoltage fault occurs in field: increase P1135 from 0.3s → 0.5s.
>   See `docs/design/CONTROL_SYSTEM.md#braking-energy-analysis` for full calculation.

## 6. Geoprobe DT325 Components

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|56 | Probe Rod 3.25″×48″   | PN: 201446 (pair, 35.4 kg)        |   2 |  800–1200| Geoprobe (US)              |
|57 | DT325 Cutting Shoe      | PN: 205449                        |   4 |  200–400 | Geoprobe (US)              |
|58 | Drive Cap GH60          | PN: 201275                        |   1 |  100–200 | Geoprobe (US)              |
|59 | Core liners             | 3.25″ Polycarbonate               |  50 |  150–300 | Geoprobe (US)              |

**Geoprobe Subtotal: ~1,250–2,100 €**

## 7. Positioning System

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|60 | viDoc RTK Light         | RTK rover, AR-capable             |   1 | ~2,000   | pix4d.com (existing)       |
|61 | GPS antenna (head)      | Multi-band GNSS, small form       |   1 |   50–100 | u-blox / Trimble           |
|62 | GPS receiver board      | u-blox ZED-F9P or similar         |   1 |  150–250 | u-blox (CH)                |
|63 | WLAN bridge             | For head GPS → tablet             |   1 |   20–40  | ESP32 module               |

**Positioning Subtotal: ~2,220–2,390 € (or ~220–390 € if viDoc existing)**

---

## Total Cost Summary

| Subsystem             | Low Est. (€) | High Est. (€) | Notes                              |
|-----------------------|-------------|---------------|------------------------------------|
| Sonic Head (2× OLI)   |       1,185 |         1,900 | 2× OLI MVE 400/6-HF               |
| Hub System            |       1,535 |         2,490 |                                    |
| Frame & Mounting      |         540 |           910 |                                    |
| Power System          |         310 |         2,890 | Range: Instagrid rental vs. buy    |
| Control & Electr.     |       1,345 |         2,220 | WAGO PFC200 XTR + SE050 + GPS      |
| Geoprobe DT325        |       1,250 |         2,100 | US import + shipping               |
| Positioning           |         220 |         2,390 | Range: existing vs. new viDoc      |
| **TOTAL**             |   **6,385** |    **14,900** |                                    |

### Realistic V1 Budget (Instagrid rental, existing viDoc)

| Item                      | Est. (€) |
|---------------------------|----------|
| Sonic Head (2× OLI)       |    1,500 |
| Hub System                |    2,000 |
| Frame                     |      700 |
| Power (Instagrid rental)  |      400 |
| WAGO PFC200 XTR system    |    1,200 |
| SE050 + ESP32-C3 wallet   |       80 |
| Geoprobe DT325 parts      |    1,700 |
| GPS head unit             |      300 |
| Misc / contingency        |      600 |
| **TOTAL**                 | **8,480** |

---

## Supplier Directory (EU Priority)

| Category          | Supplier                | Country | Website                      |
|-------------------|-------------------------|---------|------------------------------|
| Vibration motors  | OLI Vibrators           | IT      | olivibra.com                 |
| Motors (async)    | ABB                     | CH/EU   | new.abb.com                  |
| Motors (async)    | Siemens                 | DE      | siemens.com                  |
| Motors (stepper)  | Nanotec                 | DE      | nanotec.com                  |
| VFDs              | Siemens (SINAMICS V20)  | DE      | siemens.com                  |
| VFDs              | ABB (ACS150)            | CH/EU   | new.abb.com                  |
| Gearboxes         | Neugart                 | DE      | neugart.com                  |
| Bearings          | SKF                     | SE      | skf.com                      |
| Bearings          | Schaeffler/FAG/INA      | DE      | schaeffler.com               |
| Chains            | iwis                    | DE      | iwis.com                     |
| Chains            | Wippermann              | DE      | wippermann.com               |
| Sprockets/Chains  | z24.de                  | DE      | z24.de                       |
| Belts             | Gates                   | BE/EU   | gates.com                    |
| Belts             | Optibelt                | DE      | optibelt.com                 |
| Al Profiles       | mk Technology           | DE      | mk-group.com                 |
| Couplings         | R+W                     | DE      | rw-kupplungen.de             |
| Couplings         | KTR                     | DE      | ktr.com                      |
| Brakes            | Kendrion                | DE      | kendrion.com                 |
| Brakes            | Mayr                    | DE      | mayr.com                     |
| Linear guides     | Hiwin                   | TW/DE   | hiwin.de                     |
| Linear guides     | Bosch Rexroth           | DE      | boschrexroth.com             |
| Safety            | Pilz                    | DE      | pilz.com                     |
| PLC               | WAGO                    | DE      | wago.com                     |
| Secure element    | NXP (SE050)             | NL/EU   | nxp.com / mouser.com         |
| LTE Router        | Teltonika Networks      | LT/EU   | teltonika-networks.com       |
| Sensors           | ifm electronic          | DE      | ifm.com                      |
| Connectors        | Weidmüller              | DE      | weidmueller.com              |
| Connectors        | Phoenix Contact         | DE      | phoenixcontact.com           |
| Fasteners         | Würth                   | DE      | wuerth.de                    |
| Power supplies    | Mean Well               | TW/EU   | meanwell.com                 |
| Cables            | Lapp                    | DE      | lappkabel.de                 |

---

*Last updated: 2026-03-26*
*Status: PRELIMINARY — verify all prices and availability before ordering*
