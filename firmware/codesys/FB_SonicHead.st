(*
 * FB_SonicHead — Sonic Head State Machine
 *
 * Controls 2× OLI MVE 400/6-HF via Siemens V20 VFD (Modbus RTU).
 * Provides adaptive frequency control based on VFD load current.
 *
 * CRITICAL STOP BEHAVIOUR:
 *   - xFastStop = TRUE  → OFF3 command to VFD immediately
 *                         VFD uses P1135 ramp (0.3s) + DC injection braking
 *                         Expected motor standstill: 200–400ms
 *   - xFastStop = FALSE → OFF1 normal ramp (P1121, 3s) for end-of-cycle stop
 *
 * State machine:
 *   0 IDLE       — VFD disabled, motors at rest
 *   1 STARTING   — VFD enabled, ramping up, skip resonance band
 *   2 RUNNING    — Full speed, adaptive freq control active
 *   3 STOPPING   — Normal OFF1 stop (end of cycle)
 *   4 FAST_STOP  — OFF3 stop (stone / safety / E-Stop)
 *   5 FAULT      — VFD or comms fault, waits for reset
 *
 * Output xConfirmedStopped = TRUE only when VFD reports NOT running
 * AND state machine is in IDLE. Hub retract must wait for this.
 *)
FUNCTION_BLOCK FB_SonicHead
VAR_INPUT
    xEnable         : BOOL;   (* Allow sonic head to run *)
    xSafeState      : BOOL;   (* Safety FB active → fast stop *)
    xFastStop       : BOOL;   (* External fast stop request (stone, end-of-cycle) *)
    rTargetFreq_Hz  : REAL;   (* Desired operating frequency 30–110 Hz *)
    xFaultReset     : BOOL;   (* Reset VFD fault *)
END_VAR

VAR_OUTPUT
    xRunning            : BOOL;   (* TRUE = OLI motors are rotating *)
    xConfirmedStopped   : BOOL;   (* TRUE = motors confirmed at standstill *)
    xFault              : BOOL;
    rActualFreq_Hz      : REAL;
    rActualCurrent_A    : REAL;
    rActualCurrent_pct  : REAL;
    eState              : INT;
END_VAR

VAR
    fbVFD               : FB_ModbusVFD;

    rCurrentFreq        : REAL  := 0.0;   (* tracked setpoint sent to VFD *)
    tRampTick           : TON;            (* 100ms ramp tick *)
    tFastStopTimeout    : TON;            (* watchdog: motor must stop within 5s *)
    tFastStopConfirm    : TON;            (* confirm standstill for 200ms *)

    xFastStopActive     : BOOL;
    xNormalStopActive   : BOOL;
END_VAR

(* ---- Resolve stop type ---- *)
xFastStopActive   := xFastStop OR xSafeState;
xNormalStopActive := (NOT xEnable) AND (NOT xFastStopActive);

(* ---- State machine ---- *)
CASE eState OF

    (* ============================================================ *)
    0: (* IDLE — motors at rest *)
    (* ============================================================ *)
        rCurrentFreq  := 0.0;
        xConfirmedStopped := NOT fbVFD.xRunning;

        IF xEnable AND NOT xSafeState AND NOT xFastStopActive THEN
            tRampTick(IN := FALSE);
            eState := 1;
        END_IF;

        IF xFaultReset AND fbVFD.xFault THEN
            eState := 5;
        END_IF;

    (* ============================================================ *)
    1: (* STARTING — ramp up to target, skip resonance band *)
    (* ============================================================ *)
        xConfirmedStopped := FALSE;

        tRampTick(IN := NOT tRampTick.Q, PT := T#100MS);
        IF tRampTick.Q THEN
            rCurrentFreq := rCurrentFreq + GVL_PARAMS.rVFD_RAMP_UP_HZ_STEP;

            (* Skip over structural resonance band (8–25 Hz) *)
            IF rCurrentFreq > GVL_PARAMS.rVFD_SKIP_BAND_LOW_HZ
            AND rCurrentFreq < GVL_PARAMS.rVFD_SKIP_BAND_HIGH_HZ THEN
                rCurrentFreq := GVL_PARAMS.rVFD_SKIP_BAND_HIGH_HZ;
            END_IF;
        END_IF;

        IF rCurrentFreq >= rTargetFreq_Hz THEN
            rCurrentFreq := rTargetFreq_Hz;
            eState := 2;
        END_IF;

        (* Abort ramp-up if stop requested *)
        IF xFastStopActive THEN
            eState := 4;
        ELSIF xNormalStopActive THEN
            eState := 3;
        END_IF;

        IF fbVFD.xFault THEN
            eState := 5;
        END_IF;

    (* ============================================================ *)
    2: (* RUNNING — adaptive frequency control *)
    (* ============================================================ *)
        xConfirmedStopped := FALSE;

        (* Adaptive frequency: increase freq when soil resistance rises,
           decrease when soil is soft (VFD current as proxy for load) *)
        IF rActualCurrent_pct > 120.0 THEN
            (* High resistance: increase frequency towards max *)
            rCurrentFreq := MIN(GVL_PARAMS.rVFD_FREQ_MAX_HZ,
                                rCurrentFreq + 0.5);
        ELSIF rActualCurrent_pct < 50.0 THEN
            (* Low load: ease back towards min to save energy *)
            rCurrentFreq := MAX(GVL_PARAMS.rVFD_FREQ_MIN_HZ,
                                rCurrentFreq - 0.5);
        ELSE
            (* Within normal band: hold at target *)
            rCurrentFreq := rTargetFreq_Hz;
        END_IF;

        IF xFastStopActive THEN
            eState := 4;
        ELSIF xNormalStopActive THEN
            eState := 3;
        END_IF;

        IF fbVFD.xFault THEN
            eState := 5;
        END_IF;

    (* ============================================================ *)
    3: (* STOPPING — normal OFF1 ramp (end-of-cycle) *)
    (* ============================================================ *)
        (* VFD handles the ramp internally via P1121.
           We track frequency to zero for display only. *)
        tRampTick(IN := NOT tRampTick.Q, PT := T#100MS);
        IF tRampTick.Q THEN
            rCurrentFreq := MAX(0.0, rCurrentFreq - GVL_PARAMS.rVFD_RAMP_DN_HZ_STEP);
        END_IF;

        IF NOT fbVFD.xRunning AND rCurrentFreq <= 0.0 THEN
            tFastStopConfirm(IN := TRUE, PT := T#200MS);
            IF tFastStopConfirm.Q THEN
                tFastStopConfirm(IN := FALSE);
                eState := 0;
            END_IF;
        END_IF;

        (* Escalate to fast stop if safety triggers during normal stop *)
        IF xFastStopActive THEN
            eState := 4;
        END_IF;

    (* ============================================================ *)
    4: (* FAST_STOP — OFF3 immediately (stone / E-Stop / safety) *)
    (* CRITICAL: Hub must NOT retract until xConfirmedStopped = TRUE *)
    (* ============================================================ *)
        rCurrentFreq := 0.0;

        (* Watchdog: if motor does not stop within timeout → fault *)
        tFastStopTimeout(
            IN := TRUE,
            PT := GVL_PARAMS.tSONIC_STOP_TIMEOUT
        );

        IF NOT fbVFD.xRunning THEN
            (* Confirm standstill for 200ms before declaring stopped *)
            tFastStopConfirm(IN := TRUE, PT := T#200MS);
            tFastStopTimeout(IN := FALSE);

            IF tFastStopConfirm.Q THEN
                tFastStopConfirm(IN := FALSE);
                xConfirmedStopped := TRUE;

                IF NOT xFastStopActive THEN
                    eState := 0;   (* Fast stop cause cleared → back to IDLE *)
                END_IF;
            END_IF;
        ELSE
            tFastStopConfirm(IN := FALSE);
            xConfirmedStopped := FALSE;
        END_IF;

        IF tFastStopTimeout.Q THEN
            tFastStopTimeout(IN := FALSE);
            eState := 5;   (* Motor refuses to stop → fault *)
        END_IF;

    (* ============================================================ *)
    5: (* FAULT *)
    (* ============================================================ *)
        rCurrentFreq      := 0.0;
        xConfirmedStopped := FALSE;

        IF xFaultReset AND NOT fbVFD.xFault THEN
            eState := 0;
        END_IF;

END_CASE;

(* ---- Drive VFD FB ---- *)
fbVFD(
    xEnable       := xEnable OR (eState > 0),
    xStart        := (eState = 1) OR (eState = 2) OR (eState = 3),
    xFastStop     := (eState = 4),
    xFaultReset   := xFaultReset,
    rFreqSetpoint := rCurrentFreq
);

(* ---- Map outputs ---- *)
xRunning           := fbVFD.xRunning;
xFault             := fbVFD.xFault OR fbVFD.xCommError;
rActualFreq_Hz     := fbVFD.rFreqActual;
rActualCurrent_A   := fbVFD.rCurrentActual;
rActualCurrent_pct := fbVFD.rCurrent_pct;
