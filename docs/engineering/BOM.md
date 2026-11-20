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
| 5 | Casing adapter          | Must push and pull. Do not use the GH60 cap. Thread TBD. | 1 | 60–100 | Custom machining (EU) |
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
|17 | Servo motor 1FL2104     | 3.2 Nm, 1 kW, brake, encoder |   1 |  250–400 | Siemens. Band is not a quote. |
|18 | Planetary gearbox       | PLE120-040, 7.65 kg, article 100460948 |   1 |  600–900 | Neugart. Band is not a quote. |
|19 | SINAMICS S200           | 6SL5510-1BB11-0AA0, cabinet      |   1 |   80–150 | Siemens. Band is not a quote. |
|20 | Elastomer coupling      | ROTEX 28, placed between gearbox and Ø30 shaft. |   1 |   60–100 | KTR. Band is not a quote. |
|21 | Chain bearing shaft     | Ø30 mm C45. Carries the sprocket between two SYJ 30 TF. |   1 |   30–50  | Custom (EU)                |
|22 | Pillow block SYJ 30 TF  | SKF, bore 30 mm, two M12, 1.1 kg |   2 |   30–50  | SKF. Band is not a quote. |
|23 | Chain 10B-2 duplex      | G&G 600-302-0000, 3.2 m placeholder |   1 |   30–50  | G&G                        |
|24 | Sprocket 10B-2 15T      | G&G 501-302-0515, drive           |   1 |   25–40  | G&G                        |
|25 | Sprocket 10B-2 15T      | Same solid, idle                  |   1 |   30–50  | G&G                        |
|26 | Chain tensioner          | G&G 681-302-1504, 36–57 mm        |   1 |   20–40  | G&G                        |
|27 | Power-off brake         | Obsolete. Motor brake is used.    |   0 |  100–180 | History only. Not in the rollup. |
|28 | Linear guide rail HGR20 | 1,300 mm length                   |   2 |  100–180 | Hiwin / Bosch Rexroth      |
|29 | Linear slider HGH20     | Ball bearing type                  |   4 |   80–140 | Hiwin / Bosch Rexroth      |
|30 | Carriage plate          | 10 mm steel, machined             |   1 |   80–120 | Custom (EU)                |
|31 | Fasteners (hub)         | M6–M12, various                   |   1 |   20–40  | Würth / Bossard (EU)       |

**Hub System Subtotal: ~1,435–2,310 €**

## 3. Frame & Mounting

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|32 | Al profile 50×100       | mk 2004, 51.04.2004, 1,500 mm, 7.275 kg |   2 |  120–180 | mk Technology (DE)         |
|33 | Profile connectors      | mk standard corners/T-slot        |   8 |   40–80  | mk Technology (DE)         |
|34 | Bottom steel plate      | S355, 400×300×15 mm, machined     |   1 |   80–120 | Custom (EU)                |
|35 | Top steel plate         | S355, 300×200×12 mm, machined     |   1 |   50–80  | Custom (EU)                |
|36 | Rod guide bushing       | Split bushing. Closed bore 83 mm. Open it to pass the 87.63 mm shoe. | 1 | 20–40 | Custom (EU) |
|37 | UTV mounting brackets   | Steel, welded/bolted              |   4 |   60–100 | Custom (EU)                |
|38 | Tilt mechanism (obsolete) | Hinge + gas strut + lock — **obsolete for V1.1**; use electric tilt §8b #73–75 | 0 |  100–180 | Alternative only (EU)   |
|39 | Stabiliser feet         | Adjustable screw jacks            |   4 |   40–80  | Standard (EU)              |
|40 | Fasteners (frame)       | M8–M16, various                   |   1 |   30–50  | Würth / Bossard (EU)       |

**Frame Subtotal (V1.1 live lines, without #38): ~497–808 €.** The mk Lasche, M8 screws and Winkel 40 are in this rollup. The three gussets and the drive crossbar are obsolete and are not included.

> **#38 vs §8b:** V1.1 firmware drives the electric tilt actuator (`FB_TiltControl`).
> The gas-spring / hinge line #38 is retained as an obsolete alternative only and is
> **not** on the live manufacturing BOM (`VC-FR-4700` lifecycle `obsolete`).

## 4. Power System (Phase 1 — PoC)

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|41 | Instagrid ONE max       | 230V AC, 3.6 kW, 2.1 kWh         |   1 | 2,500*   | instagrid.co (rental opt.) |
|42 | DC PSU 48V              | Mean Well SDR-480-48, 48 V / 10 A / 480 W. Price unknown. Do not order SDR-75-48. | 1 | unknown | Mean Well |
|43 | DC/DC 48V → 24V        | For brake, relays. V1.1 live PN: Mean Well **SDR-120-24** (supersedes DDR-60D-24) | 1 | 40–70 | Mean Well (EU) |
|44 | DC/DC 48V → 12V/5V    | For PLC, sensors                  |   1 |   15–30  | Traco / Mean Well (EU)     |
|45 | Power distribution      | DIN rail, fuses, contactors       |   1 |   60–100 | Schneider / Eaton (EU)     |
|46 | Cable set               | Silicone, shielded, 2.5–6 mm²    |   1 |   40–80  | Lapp (DE)                  |

*Instagrid ONE typically rented (€95/week). Purchase ~€2,500.

**Power System Subtotal (YAML rollup, Instagrid purchase included): EUR 2,655–2,780.** A rental is not a stock line. The old EUR 80–140 supply range is withdrawn.

## 5. Control & Electronics

| # | Component                   | Spec                                                      | Qty | Est. €    | Supplier / Source            |
|---|-----------------------------|-----------------------------------------------------------|-----|-----------|------------------------------|
|47 | WAGO PFC200 XTR             | 750-8212, 1 GHz Cortex-A8, 512 MB RAM, 4 GB Flash, −40..+70°C, 5g vib, 2×ETH, RS-485, Docker built-in (FW ≥ 23) | 1 | 600–900 | wago.com (DE) |
|48 | WAGO 750-430 XTR            | 4× DI 24V DC, CAGE CLAMP                                 |   1 |   60–90   | wago.com (DE)                |
|49 | WAGO 750-530 XTR            | 4× DO 24V DC, 0.5A, CAGE CLAMP                           |   1 |   60–90   | wago.com (DE)                |
|50 | WAGO 750-637                | Incremental encoder interface                             |   1 |  100–150  | wago.com (DE)                |
|51 | WAGO 750-826                | RS-485 Modbus RTU serial interface                        |   1 |   80–120  | wago.com (DE)                |
|52 | WAGO 750-600                | End module                                                |   1 |   10–20   | wago.com (DE)                |
|53 | Limit switches              | Inductive, M12, NC, IP67                                 |   2 |   30–60   | ifm / Sick (DE)              |
|54 | Emergency stop              | Mushroom NC, Category 3, IP65 enclosure                  |   1 |   40–70   | Eaton / Schneider (EU)       |
|55 | Safety relay                | Pilz PNOZ m B0 or equivalent                             |   1 |   80–130  | Pilz (DE)                   |
|56 | Control enclosure           | IP65. Size 200×150×80 mm is withdrawn. Order code and price unknown. | 1 | unknown | TBD |
|57 | RDDL Trust Wallet           | Xiao ESP32-C3 + NXP SE050 breakout                       |   1 |   25–50   | Seeed Studio / Mouser (EU)   |
|58 | SE050 breakout board        | Included in row 57. Do not buy a second board.           |   0 |   20–40   | History only                 |
|59 | GPS antenna (drill head)    | u-blox ANN-MB, multi-band, SMA                           |   1 |   50–80   | u-blox (CH)                  |
|60 | GPS receiver                | u-blox ZED-F9P, RTK capable                              |   1 |  150–250  | u-blox / Mouser (EU)         |
|61 | Teltonika RUT241            | LTE Cat4 router, DIN-rail, −40..+75°C                    |   1 |  100–160  | teltonika-networks.com (LT)  |
|62 | SIM card (data-only)        | LTE 1 GB/month, AT or HU carrier                         |   1 |   10–20   | Any carrier                  |
|63 | DC step-down 24V→9V         | Not required. RUT241 accepts 9–30 V DC.                  |   0 |   10–20   | History only                 |
|64 | Wiring harness              | CAGE CLAMP terminals, shielded cables                    |   1 |   50–90   | Weidmüller / Phoenix (DE)    |

**Software (no additional cost — runs on PFC200 Docker):**

| Component | License | Notes |
|-----------|---------|-------|
| Node-RED (wagoautomation/node-red-iot) | Apache 2.0 | Official WAGO ARM image, includes dashboard + Modbus |
| Mosquitto MQTT Broker | EPL 2.0 | Eclipse; Docker Hub official ARM image |
| CODESYS V3.5 Runtime | Included with WAGO PFC | Licensed per hardware |
| CODESYS Go | Free tier (500h/year) | Browser-based IDE, no Windows needed |

**Control Subtotal Option A (WAGO): EUR 1,565–2,460 (YAML rollup of VC-ASM-5000).**

---

### 5b. Control & Electronics — Option B: Revolution Pi Connect 4

*Alternative to WAGO PFC200 XTR — lower cost, more RAM/CPU, full Linux.
Recommended for V1 prototype / cost-sensitive builds.*

| # | Component | Spec | Qty | Est. € | Supplier |
|---|-----------|------|-----|--------|----------|
|47b| RevPi Connect 4 | CM4 Quad-Core A72 1.5 GHz, 4 GB RAM, 32 GB eMMC, 2× GbE, RS-485 built-in, Docker-native, −25..+55 °C, DIN rail | 1 | 450–520 | [revolutionpi.com](https://revolutionpi.com/shop/en/revpi-connect4) (DE) |
|48b| RevPi DIO module | 14× DI 24V + 14× DO 24V; DI configurable as quadrature encoder/counter — replaces WAGO 750-430 + 750-530 + 750-637 in one unit | 1 | 196–220 | revolutionpi.com (DE) |
|49b| *(RS-485 built-in)* | Modbus RTU to Siemens V20 + Nanotec C5-E — no separate module needed | — | 0 | — |
|50b–64b| Shared Option A lines, without the WAGO rack and without the obsolete SE050 and 9 V lines | | | inside the total below | same as §5 |

**Control Subtotal Option B:** EUR 1,181–1,650.
Arithmetic: Option A rollup EUR 1,565–2,460, minus the WAGO rack EUR 1,030–1,550, plus RevPi Connect 4 EUR 450–520 and RevPi DIO EUR 196–220.

**Software (RevPi — zero additional cost, full open source):**

| Component | Notes |
|-----------|-------|
| Raspberry Pi OS (Debian) | Pre-installed, full Linux, no license fees |
| Node-RED (official Docker image) | `platform: linux/arm/v8` in docker-compose.yml |
| Mosquitto | Same Docker stack as Option A |
| CODESYS SL for Raspberry Pi | Soft PLC from CODESYS Store (runtime license required) |
| Python / pymodbus | Full alternative to CODESYS — no Windows ever |

**Control Subtotal Option B (RevPi): ~1,521–2,430 € (hardware only; software €0)**

> **Option B savings vs. Option A: ~€300–600 less for the controller sub-system**
> (RevPi base €646 vs. WAGO system €910–1,370)

> **Key tradeoffs:**
> - Temperature: RevPi −25 °C vs. WAGO −40 °C. For EU field use (March–November) this
>   is acceptable; add enclosure heater strip (~€15) for cold-storage overnight.
> - Vibration: WAGO is explicitly 5g rated. The drill enclosure isolates the controller
>   from drilling vibrations via rubber mounts — in practice both are adequate.
> - CODESYS real-time: RevPi uses PREEMPT_RT Linux (soft PLC). For Vibrocore's
>   500ms Modbus polling cycles this is more than sufficient.
> - Encoder: RevPi DIO quadrature encoder mode handles 10 kHz count rate comfortably
>   (1000ppr × 10 mm/s = ~6.7 kHz max at drilling speed).
> - I/O advantage: 1 RevPi DIO replaces 3 WAGO modules — simpler wiring.
>
> See `docs/design/CONTROL_SYSTEM.md#controller-comparison` for full analysis.

> **Notes (Option A — WAGO):**
> - WAGO PFC200 XTR specs: **1 GHz ARM Cortex-A8, 512 MB RAM, 4 GB Flash** (G2).
>   Docker built-in from Firmware 23. Setup guide: `firmware/docker/README.md`.
> - CONTROLLINO / Arduino Opta removed — WAGO PFC200 XTR is the V1 production controller.
> - Teltonika RUT241: LTE for remote CODESYS debugging, OTA updates, MQTT to RDDL.
> - **No external braking resistor required.** The 80 J fast-stop energy is dissipated
>   as heat in the OLI motor windings via DC injection braking (P1232=100%).
>   Temperature rise: 0.012 °C per stop — negligible at 7.2 kg motor thermal mass.
>   V20 Vdc-max controller (P1240=1) prevents DC bus overvoltage during ramp.
>   If bus overvoltage fault occurs in field: increase P1135 from 0.3s → 0.5s.
>   See `docs/design/CONTROL_SYSTEM.md#braking-energy-analysis` for full calculation.

## 6. Casing and split carrier

The sampling string is the 3.25 in outer casing and the cutting shoe at the bottom.
Open lab tubes sit inside the casing.
The split carrier holds those tubes.
Sample tubes and push-on caps are lab consumables.
They are not lines in this table.
See `docs/engineering/SAMPLING.md`.

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|56 | Probe rod 3.25 in x 48 in | PN 201446, one rod, 17.7 kg    |   2 | 779.98   | Offer 26100096, EUR 389.99 each |
|57 | Cutting shoe            | PN 205449, OD 3.45 in             |   4 | 1203.12  | Offer 26100096, EUR 300.78 each |
|58 | Drive cap GH60          | PN 201275. Obsolete. Not on the kit. | 0 | 586.47 | History only. Do not buy. |
|59 | Core liner              | Withdrawn. Do not buy.            |   0 | unknown  | Not used                   |

The kit lines are two outer rods, one O-ring pack, four cutting shoes and the two half-shells with their fasteners.
The O-ring pack stays. It seals the 3.25 in casing joints.
The kit rollup is EUR 2,007.85.
That sum is two rods, four shoes and one O-ring pack.
The half-shells have no price yet.
Drive head 201385 and retainer HD 208472 are obsolete history. They are not kit lines.

## 7. Positioning System

| # | Component               | Spec                              | Qty | Est. €   | Supplier / Source          |
|---|-------------------------|-----------------------------------|-----|----------|----------------------------|
|60 | viDoc RTK Light         | RTK rover, AR-capable             |   1 | ~2,000   | pix4d.com (existing)       |
|63 | WLAN bridge             | For head GPS to the tablet        |   1 |   20–40  | ESP32 module               |

The GPS antenna and the ZED-F9P are on the control BOM only. Do not buy them again here.

**Positioning kit rollup: EUR 2,020–2,040.** If the viDoc is already owned, the added purchase is the WLAN bridge, EUR 20–40.

## 8. Deployment, Penetrometry & Core Imaging

*Optional subsystems for V1.1 / field-ready version.
Can be added incrementally without hardware changes to the base controller I/O.*

---

### 8a. Lift Actuator System (~40 cm deployment travel)

**Function:** Raises/lowers the entire drill mast ~400 mm between transport position
(mast raised, clears ground obstacles) and drilling position (mast deployed, weight
resting on stabiliser feet). Two parallel actuators ensure stable, torsion-free deployment.

**Design:** 2× electric linear actuator (one per frame side) + shared H-bridge relay direction control.
Each actuator has integrated mechanical end stops. CODESYS reads the 4 limit switches and
controls extend/retract via 2 DO channels (shared for both actuators in parallel).

| # | Component | Spec | Qty | Est. € | Supplier |
|---|-----------|------|-----|--------|----------|
|70 | Electric linear actuator (lift) | 24V DC, 400mm stroke, ≥1.5 kN push/pull, ≥8 mm/s, IP65, with integrated limit switch, DIN-rail PSU-powered | 2 | 150–280 ea. | Thomson PA, Ewellix CASM, Linak LA23 or equiv. |
|71 | H-bridge relay module | 24V coil, 10A contacts, DIN-rail, direction control | 1 | 20–40 | Phoenix Contact / Finder |
|72 | Limit switch wiring | 4-core cable, 2× NC sensors per actuator → 2 DI signals (deployed + retracted) | 1 | 10–20 | Lapp |

**Lift Subtotal: EUR 330–620 (YAML rollup of VC-ASM-8100).**

> **I/O impact:** +2 DI (xLiftDeployedLimit, xLiftRetractedLimit) + 2 DO (xLiftExtend, xLiftRetract).
> WAGO: requires 2nd 750-430 XTR and 2nd 750-530 XTR (see §5 I/O expansion below).
> RevPi: fits within existing RevPi DIO headroom (10/14 DI, 6/14 DO used after this addition).

---

### 8b. Tilt Actuator (0°–90° mast fold)

**Function:** Folds the drill mast from vertical (drilling) to horizontal (road transport),
and back. The pivot is at the base of the mast. In vertical position, the tilt actuator
is locked by motor-hold and a mechanical detent pin.

**Design:** Single electric linear actuator on a pivot bracket, 600 mm from mast pivot.
Stroke needed for 90°: ≈ 600 mm × sin(45°) × 2 ≈ 200 mm stroke is sufficient for
a carefully positioned pivot-to-attachment geometry. Verify with final mechanical design.

| # | Component | Spec | Qty | Est. € | Supplier |
|---|-----------|------|-----|--------|----------|
|73 | Electric linear actuator (tilt) | 24V DC, 200mm stroke, ≥2 kN, IP65, integrated limit switch, ≤10 mm/s (slow for safety) | 1 | 150–250 | Thomson PA, Linak LA36 or equiv. |
|74 | Pivot bracket | Welded steel, Ø30 pin, self-aligning | 1 | 40–80 | Custom (EU) |
|75 | Detent pin + spring | Positive lock in vertical position | 1 | 20–40 | Standard (EU) |

**Tilt Subtotal: ~210–370 €**

> **I/O impact:** +2 DI (xTiltVerticalLimit, xTiltFoldedLimit) + 2 DO (xTiltVertical, xTiltFold).
> Total new I/O for lift + tilt: 4 DI + 4 DO.
> WAGO: 1× additional 750-430 XTR + 1× additional 750-530 XTR handles all 4+4.
> RevPi: still within single DIO module capacity (10/14 DI, 8/14 DO).

> **PSU upgrade required:** Lift + Tilt actuators simultaneously draw up to 4× 2A = 8A @ 24V
> (unlikely all running at once, but spec for peak). Upgrade 24V PSU from
> Mean Well DDR-60D-24 (60W/2.5A) → **Mean Well SDR-120-24 (120W/5A)** (~€40–70). See §4.

---

### 8c. Integrated Penetrometer (Force-Displacement Measurement)

**Function:** Measures drilling resistance (push force) as a function of depth throughout
the entire penetration cycle. Combined with the existing position encoder this produces
a **drilling penetrogram** (force vs. depth curve) — functionally equivalent to a
lightweight Cone Penetration Test (CPT) at the sample point.

**Design:** S-type load cell mounted in-line between the hub carriage adapter plate and
the casing adapter. Output: 4–20 mA via signal conditioner to RS-485 Modbus RTU
converter (Slave address 3 on the existing bus). No additional PLC I/O module needed.

```
Hub carriage plate
        │
   ┌────┴────┐
   │ S-type  │  0–5 kN
   │ Load    │  ±0.1% accuracy
   │ Cell    │
   └────┬────┘
        │  mV/V bridge output
   ┌────▼────────────┐
   │ 4-20mA          │  (loop-powered, 24V from rail)
   │ Transmitter     │
   └────┬────────────┘
        │  4–20 mA current loop
   ┌────▼─────────────────────────┐
   │ Modbus RTU ADC Converter     │  RS-485 Slave addr 3
   │ (e.g. Datexel DAT8017-A,    │  Register 0: force [N]
   │  Weidmüller ACT20X, or      │  Updates at 50 ms
   │  equivalent 1-ch 4-20mA    │
   │  → RS-485 Modbus module)    │
   └────┬─────────────────────────┘
        │  RS-485 (existing Modbus RTU bus)
        ▼
   WAGO 750-826 / RevPi RS-485 (Slave 3, after Slave 2 Nanotec C5-E)
```

| # | Component | Spec | Qty | Est. € | Supplier |
|---|-----------|------|-----|--------|----------|
|76 | Load cell (S-type) | 0–5 kN, ≤0.1% non-linearity, IP67, thread M12 or Ø 22 mm inline, stainless | 1 | 100–200 | HBK S9M, Burster 8417, Bosche S2 or equiv. |
|77 | 4-20mA transmitter | Matches load cell bridge (mV/V), loop-powered 24V DC, DIN rail | 1 | 50–100 | Weidmüller ACT20C, HBK AD105E or equiv. |
|78 | Modbus RTU ADC | 1-ch 4-20mA → RS-485 Modbus RTU, 16-bit, Slave addr configurable | 1 | 80–130 | Datexel DAT8017-A, Procon RS-485 ADC or equiv. |
|79 | Inline adapter | CNC insert in the pull path. The load cell and the bypass mount here. | 1 | 60–100 | Custom (EU) |

**Penetrometer Subtotal: EUR 290–530.** The bypass VC-PN-9340 is in section 9. It has no price yet, so the rollup does not change.

> **No new PLC I/O module required** — uses existing RS-485 bus (Slave 3).
> `FB_DataLogger` reads Object Register 0 from Slave 3 and includes force array in JSON payload.
> Output data: `"force_n": [...]` array sampled at 50ms intervals → penetrogram per cycle.

---

### 8d. Core Scanner

The old through-liner procedure is withdrawn.
Do not scan a polycarbonate liner. The machine does not use that liner.
The cradle must fit one sample tube. The tube outside diameter is TBD.
The tube is a lab consumable and is not a BOM line.
Do not assume the tube wall is clear. See `docs/engineering/SAMPLING.md`.

The sled hardware below is unchanged. The cradle opening is not.

The sled still uses the Raspberry Pi 4, the HQ camera and the rail.
Do not apply a polycarbonate colour correction.
Do not crop to 82.6 mm.
The scan length follows the tube length. That length is TBD.
The previous 1300 mm cradle length was the transport length of the old liner.
Confirm it against the real tube.

**Field sequence after extraction:**
1. The hub retracts the casing.
2. The operator removes the open tubes from the half-shells.
3. The operator fits the push-on caps after the tubes are out of the casing.
4. One tube goes into the cradle for the scan.
5. The tubes stay a lab consumable. They are not packed as a Vibrocore part.

| # | Component | Spec | Qty | Est. € | Supplier |
|---|-----------|------|-----|--------|----------|
|80 | Raspberry Pi 4 (2 GB) | Quad-core Cortex-A72, 2 GB RAM, USB 3, CSI, WiFi — OpenCV host | 1 | 50–70 | raspberrypi.com / Mouser (EU) |
|81 | RPi HQ Camera (IMX477) | 12.3 MP, CSI-2. Through-wall colour is not confirmed. | 1 | 50–65 | raspberrypi.com / Mouser (EU) |
|82 | C-mount lens 8mm | Low distortion, manual focus-lock, suited for 28cm WD / 95mm FOV | 1 | 25–50 | Arducam / Computar (EU) |
|83 | NEMA 17 stepper | 48mm, 45 N·cm, sled drive | 1 | 12–20 | Stepperonline / Reichelt |
|84 | A4988 stepper driver | 12–24V, microstepping, controlled from RPi GPIO | 1 | 5–15 | Pololu / Amazon (EU) |
|85 | GT2 belt + pulleys | 6mm wide, 1,400mm loop, 16T pulley + idler | 1 | 10–20 | 3D printer suppliers (EU) |
|86 | mk 2004 Al-rail | 40×40mm profile, 1,450mm, matte black | 1 | 40–70 | mk Technology (DE) |
|87 | Camera sled carriage | mk connector + bracket + MGN12 miniature guide rail | 1 | 40–80 | Custom (mk + Hiwin) |
|88 | HDPE V-cradle | Opening follows the tube OD. Tube OD is TBD. Do not use 82.6 mm. | 1 | 25–50 | Custom CNC (HDPE) |
|89 | LED strip (daylight) | CRI ≥ 97, 5000K, 24V, 1.25m × 2, 45° angled mounts | 2 | 20–40 ea. | Waveform Lighting / RS Components |
|90 | LED driver | 24V → constant current, PWM dimmable | 1 | 20–40 | Mean Well LDD-1000H |
|91 | Light-tight cover | Al sheet + brush seals along sled rail, fold-down lid | 1 | 40–80 | Custom sheet metal (EU) |
|92 | Munsell reference tile | 3× chips (10YR 3/2, 5/4, 7/4) in fixed end-of-cradle holder | 1 | 20–40 | X-Rite / GretagMacbeth (EU) |
|93 | Home / end switches | Inductive, M8, for sled homing | 2 | 6–15 ea. | ifm / Conrad (EU) |
|94 | 5V + 12V PSU | 24V → 5V/5A (RPi + camera) + 12V/1A (stepper), DIN rail | 1 | 20–35 | Traco / Mean Well (EU) |
|95 | USB stick | 128 GB, USB 3.0, industrial (raw frames + stitched output) | 1 | 20–35 | Transcend Industrial |

**Core Scanner Subtotal: EUR 429–780 (YAML rollup of VC-ASM-8400).**

> **No liner splitting. No on-site storage. Sample integrity is absolute.**
> The scan adds ~4 minutes to the field workflow and zero risk to the sample.
> After scanning, the capped, labelled liner goes directly into the courier box for the lab.
>
> **Lab measures:** wet weight (field) + dry weight (105°C oven) + liner volume → bulk density.
> **Scanner measures:** color profile + horizon boundaries → pedological characterisation.
> These are orthogonal — the same sample delivers both without any conflict.

---

### 8e. I/O Expansion — Controller Impact Summary

New signals introduced by subsystems 8a–8c:

| Signal | Direction | Source | Count |
|--------|-----------|--------|-------|
| xLiftExtend | DO | PLC → Lift relay | 1 |
| xLiftRetract | DO | PLC → Lift relay | 1 |
| xLiftDeployedLimit | DI | Limit switch → PLC | 1 |
| xLiftRetractedLimit | DI | Limit switch → PLC | 1 |
| xTiltVertical | DO | PLC → Tilt relay | 1 |
| xTiltFold | DO | PLC → Tilt relay | 1 |
| xTiltVerticalLimit | DI | Limit switch → PLC | 1 |
| xTiltFoldedLimit | DI | Limit switch → PLC | 1 |
| rForce_N (via Modbus) | RS-485 | Load cell ADC Slave 3 | — |
| Core image (via MQTT) | MQTT | Raspberry Pi 4 (2 GB) | — |
| **Total new hard-wired** | | | **4 DI + 4 DO** |

**WAGO Option A — additional modules required:**

| Module | Function | Est. € |
|--------|----------|--------|
| WAGO 750-430 XTR (2nd) | 4× DI for lift + tilt limits | 60–90 |
| WAGO 750-530 XTR (2nd) | 4× DO for lift + tilt control | 60–90 |
| Mean Well SDR-120-24 | 24V/5A PSU upgrade (replaces DDR-60D-24) | 40–70 |
| **Additional cost Option A** | | **€160–250** |

**RevPi Option B — additional modules required:**

| Module | Function | Est. € |
|--------|----------|--------|
| RevPi DIO (existing) | 4 new DI + 4 new DO fit in remaining headroom (14 per direction) | 0 |
| Mean Well SDR-120-24 | 24V/5A PSU upgrade (same as Option A) | 40–70 |
| **Additional cost Option B** | | **€40–70** |

**Total Section 8 (Lift + Tilt + Penetrometer + Core Camera):**

| Sub-section | Low (€) | High (€) |
|-------------|---------|---------|
| 8a Lift actuators | 330 | 620 |
| 8b Tilt actuator | 210 | 370 |
| 8c Penetrometer | 290 | 530 |
| 8d Core Scanner (sled) | 429 | 780 |
| 8e I/O (WAGO) | 160 | 250 |
| 8e I/O (RevPi) | 40 | 70 |
| **Total §8 (Option A)** | **1,419** | **2,550** |
| **Total §8 (Option B)** | **1,299** | **2,370** |

VC-ASM-8000 is lift + tilt + penetrometer + scanner only: EUR 1,259–2,300.
Do not add the §8e I/O cost again. Those modules are already inside VC-ASM-5000 and VC-ASM-4000.

---

| Subsystem             | Low Est. (€) | High Est. (€) | Notes                              |
|-----------------------|-------------|---------------|------------------------------------|
| Sonic head VC-ASM-1000 | 1,185 | 1,900 | YAML rollup |
| Hub VC-ASM-2000 | 1,435 | 2,310 | YAML rollup. The ROTEX coupling is included. The obsolete brake is not. |
| Frame VC-ASM-3000 | 497 | 808 | Live lines. Gussets, the crossbar and the gas spring are not included. |
| Power VC-ASM-4000 | 2,655 | 2,780 | Includes Instagrid at EUR 2,500. Supply price is unknown. |
| Control VC-ASM-5000 | 1,565 | 2,460 | Option A. SE050 and the 9 V converter are not included. |
| Field VC-ASM-8000 | 1,259 | 2,300 | Lift, tilt, penetrometer, scanner. |
| **Machine VC-ASM-0000** | **8,596** | **12,558** | Sum of the six rollups above. |
| Casing kit VC-KIT-6000 | 2,007.85 | 2,007.85 | Offer prices. Half-shell price is unknown. |
| Positioning kit VC-KIT-7000 | 2,020 | 2,040 | viDoc plus WLAN bridge. |

The machine total does not include the two kits.

### Realistic V1 Budget (Instagrid rental, existing viDoc)

**Option A — WAGO PFC200 XTR (production recommended):**

| Item                        | V1 (€)  | V1.1 + §8 (€) | Notes |
|-----------------------------|---------|----------------|-------|
| Sonic Head (2× OLI)         |   1,500 |          1,500 | |
| Hub System                  |   2,000 |          2,000 | |
| Frame                       |     700 |            700 | |
| Power (Instagrid rental)    |     400 |            450 | SDR-120-24 PSU upgrade +€50 in V1.1 |
| WAGO PFC200 XTR system      |   1,200 |          1,400 | +2nd DI + DO module in V1.1 |
| SE050 + ESP32-C3 wallet     |      80 |             80 | |
| Teltonika RUT241 + SIM      |     180 |            180 | |
| Casing kit (offer prices)   |   2,008 |          2,008 | |
| GPS head unit               |     300 |            300 | |
| HMI Software (Docker)       |       0 |              0 | |
| Lift + Tilt actuators       |     — |            500 | §8a + §8b |
| Penetrometer (load cell)    |     — |            400 | §8c |
| Core scanner (sled)         |     — |            550 | §8d: RPi4 + HQ cam + sled + OpenCV |
| Misc / contingency          |     600 |            700 | |
| **TOTAL Option A**          | **8,968** | **10,718** | Rounded scenario. Not the YAML rollup. |

**Option B — RevPi Connect 4 (V1 prototype / cost-sensitive):**

| Item                        | V1 (€)  | V1.1 + §8 (€) | Notes |
|-----------------------------|---------|----------------|-------|
| Sonic Head (2× OLI)         |   1,500 |          1,500 | |
| Hub System                  |   2,000 |          2,000 | |
| Frame                       |     700 |            700 | |
| Power (Instagrid rental)    |     400 |            450 | SDR-120-24 PSU upgrade +€50 |
| RevPi Connect 4 (4 GB)      |     470 |            470 | |
| RevPi DIO module            |     200 |            200 | absorbs all new DI/DO with headroom |
| SE050 + ESP32-C3 wallet     |      80 |             80 | |
| Teltonika RUT241 + SIM      |     180 |            180 | |
| Casing kit (offer prices)   |    2,008 |          2,008 | |
| GPS head unit               |     300 |            300 | |
| HMI Software (Docker)       |       0 |              0 | |
| Lift + Tilt actuators       |     — |            500 | §8a + §8b |
| Penetrometer (load cell)    |     — |            400 | §8c |
| Core scanner (sled)         |     — |            550 | §8d: sled + RPi4 + stitching |
| Misc / contingency          |     600 |            700 | |
| **TOTAL Option B**          | **8,438** | **10,038** | Rounded scenario. Not the YAML rollup. |

> **Option B savings (arithmetic, not a third estimate):**
> - **V1:** EUR 8 968 − EUR 8 438 = **EUR 530** less than Option A.
> - **V1.1:** EUR 10 718 − EUR 10 038 = **EUR 680** less than Option A.
> Both figures are correct for their column. Do not mix them.

---

## 9. Parts added on 2026-11-19

Prices below are unknown unless the offer states them.
Do not invent an order code.

| # | Component | Spec | Qty | Est. € | Supplier |
|---|-----------|------|-----|--------|----------|
| 96 | Drag chain | Travel 1300 mm. Inner size TBD until cable diameters are known. | 1 | unknown | TBD |
| 97 | Chain-shaft encoder | 1000 ppr, quadrature, on the chain shaft, into WAGO 750-637. Bore TBD. | 1 | unknown | TBD |
| 98 | Chain drive guard | Fixed guard for the chain and the sprockets. Size TBD. | 1 | unknown | Custom (EU) |
| 99 | Vibro head guard | Fixed guard for the vibro head. Size TBD. | 1 | unknown | Custom (EU) |
| 100 | Main isolator | Lockable, 230 V, at least 20 A, between Instagrid and the machine. | 1 | unknown | TBD |
| 101 | Line circuit breaker | 230 V feed, 20 A unless the VFD manual says otherwise. Curve TBD. | 1 | unknown | TBD |
| 102 | Residual current device | Type B, 30 mA, at least 20 A. Do not use type A ahead of the VFD. | 1 | unknown | TBD |
| 103 | Warning beacon | 24 V DC. Output xAlarmBeacon at %QX0.3. Current at or below 0.5 A. | 1 | unknown | TBD |
| 104 | Operator tablet | WLAN client of the RUT241. Screen size TBD. | 1 | unknown | TBD |
| 105 | Split carrier half A | Draft. Holds open tubes. Tube OD and length TBD. | 1 | unknown | Custom (EU) |
| 106 | Split carrier half B | Draft mirror of half A. | 1 | unknown | Custom (EU) |
| 107 | Split carrier fasteners | Clamp the two halves. Size TBD. | 1 | unknown | TBD |
| 108 | Probe rod O-ring pack | PN 201325, 25 rings. Seals the 3.25 in casing joints. | 1 | 24.75 | Offer 26100096 |
| 110 | DT325 drive head | PN 201385, 1.25 in pin. Obsolete. Not on the kit. | 0 | 171.34 | History only |
| 111 | DT325 liner retainer HD | PN 208472. Obsolete. Not on the kit. | 0 | 161.93 | History only |
| 109 | Load-cell overload bypass | Closes before 5 kN. Must carry 9499 N. | 1 | unknown | Custom (EU) |

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

| Node-RED (HMI)    | WAGO (wagoautomation) | DE/INT  | hub.docker.com/r/wagoautomation |
| MQTT Broker       | Eclipse Mosquitto     | INT     | mosquitto.org                |

---

*Last updated: 2026-11-19*
*Status: PRELIMINARY — verify all prices and availability before ordering*
*Single-source YAML: `cad/bom/vibrocore.bom.yaml` (V1.1 baseline)*
