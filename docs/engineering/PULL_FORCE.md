# Allowable pull force

This note replaces the two hub-force figures in the older text.
The allowable pull force is **4.5 kN**.
Use this value in every document.
The inputs are the drive data already in this repository.

## Inputs

| Input | Value | Source |
|---|---|---|
| Chain pitch | 15.875 mm | ISO 606, size 10B |
| Sprocket teeth | 15 | HUB_SYSTEM.md and the BOM |
| Gear ratio | 40 | Neugart PLE120-040, article 100460948 |
| Gearbox efficiency used below | 0.90 | HUB_SYSTEM.md. This is not a measured Neugart value. |
| Gearbox nominal output torque | 220 Nm | HUB_SYSTEM.md |
| Gearbox emergency torque | 360 Nm | HUB_SYSTEM.md |
| Motor torque used as nominal | 15 Nm | HUB_SYSTEM.md. The range there is 12-20 Nm. |
| Motor torque on the BOM line | about 20 Nm | BOM. The catalogue number is not selected. |
| Chain working load | 4.5 kN | Design limit used by the bracket calculation. |
| Chain breaking load | not stated | G&G does not state a value for 600-302-0000. |
| Load cell rating | 5 kN | VC-PN-9300 |

The design working load is 4.5 kN.
It is not a G&G breaking load divided by ten.
G&G does not state a breaking load for chain 600-302-0000.
This note keeps 4.5 kN.

## Formulas

Pitch radius, same formula as HUB_SYSTEM.md:

```text
R = (pitch x teeth) / (2 x pi)
  = (15.875 x 15) / (2 x pi)
  = 37.899 mm
```

The exact pitch-circle radius is `pitch / (2 x sin(pi / teeth))` = 38.177 mm.
The force below uses 37.899 mm so it stays on the formula already in the design note.

Chain tension:

```text
F = T / R
```

Use metres for R when T is in newton-metres.

## Results

| Case | Torque at the sprocket | Tension |
|---|---|---|
| Gearbox nominal output | 220 Nm | 5805 N (5.80 kN) |
| Gearbox emergency output | 360 Nm | 9499 N (9.50 kN) |
| Motor 15 Nm x 40 x 0.90 | 540 Nm | 14248 N (14.25 kN) |
| Motor 20 Nm x 40 x 0.90 | 720 Nm | 18998 N (19.00 kN) |
| Chain working load | — | 4.5 kN |
| Chain breaking load | — | not stated by G&G |

540 Nm and 720 Nm are above the gearbox emergency torque of 360 Nm.
The gearbox cannot deliver the motor-times-ratio torque.
Do not call 14.3 kN an available pull force.

The gearbox nominal tension is 5.80 kN.
The chain working load is 4.5 kN.
The allowable continuous pull force is the lower value.

**Allowable pull force = 4.5 kN.**

## Withdrawn figures

The old 14.3 kN figure used 540 Nm at the sprocket.
That torque is above the gearbox rating.
Do not use it.

The README line "2.0-2.6 kN at 90 Nm" used 90 Nm at the sprocket and no 40:1 ratio.
90 Nm / 0.0379 m is about 2.4 kN.
No drive rating in this repository is 90 Nm at the sprocket.
Do not use that line.

## Required pull and margin

HUB_SYSTEM.md still lists a required pull of 2.0-4.0 kN with vibration off.
That figure is a process need.
It is not the drive capacity.

Margin of the allowable pull force on the upper required pull:

```text
4.5 kN / 4.0 kN = 1.13
```

The margin is small.
Do not invent a breaking load to enlarge that margin.
The working load is the limit used here.

## Load cell

VC-PN-9300 is an S-type cell rated 5 kN.
The cell sits in the pull path, between the carriage and the casing adapter.

The gearbox can put 5805 N into that path at nominal torque.
It can put 9499 N into that path at emergency torque.
The chain does not stop the rise at 4.5 kN.
G&G does not state the load at which this chain breaks.

5 kN is below both gearbox tensions.
A stall can overload the cell.

Decision:

- Keep the 5 kN cell. It matches the soil-force range.
- Add VC-PN-9340, a mechanical bypass in parallel with the cell.
- The bypass must close before 5 kN.
- The bypass must carry 9499 N.
- Do not select a higher-rated catalogue cell in this revision. No order code was verified.

The code that repeats these formulas is `cad/tools/pull_force.py`.
