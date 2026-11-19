(*
 * FB_Safety — Safety Monitor Function Block
 *
 * Evaluates all safety-relevant inputs and sets xSafeState.
 * When xSafeState = TRUE, all motion must stop immediately.
 *
 * Fault-code table (canonical — must match GVL_MODBUS and Node-RED):
 *   0 = OK
 *   1 = ESTOP
 *   2 = LIMIT_UP
 *   3 = LIMIT_DOWN
 *   4 = HUB_ALARM
 *   5 = STONE_DETECTED
 *   6 = VFD_COMM
 *
 * Safety categories addressed:
 *   - E-Stop: Category 3 (redundant NC wiring evaluated here)
 *   - Limit switches: NC wiring, software evaluation
 *   - Overcurrent / stone detection: software function
 *   - Hub driver fault: hardware alarm signal
 *   - VFD fault / Modbus loss: reported by FB_ModbusVFD
 *
 * IMPORTANT: This FB does NOT directly cut power. Physical power cut
 * is handled by the safety relay (Pilz PNOZ or equivalent) wired in
 * series with the 24V supply to the VFD enable and brake circuit.
 * This FB provides the software-level interlock for the state machines.
 *)
FUNCTION_BLOCK FB_Safety
VAR_INPUT
    (* E-Stop NC contact — FALSE when button pressed *)
    xEStop_NC           : BOOL;

    (* Limit switches — NC wiring: TRUE = healthy, FALSE = limit or wire break *)
    xLimitUp_NC         : BOOL;
    xLimitDown_NC       : BOOL;

    (* Hub driver alarm output (active HIGH) *)
    xHubAlarm           : BOOL;

    (* VFD fault or Modbus communication loss from FB_ModbusVFD *)
    xVFD_Fault          : BOOL;

    (* VFD output current as percentage of motor rated current
       Provided by FB_ModbusVFD after scaling *)
    rVFD_Current_pct    : REAL;

    (* Current hub movement direction (TRUE = moving down) *)
    xHubMovingDown      : BOOL;

    (* Current hub movement direction (TRUE = moving up) *)
    xHubMovingUp        : BOOL;
END_VAR

VAR_OUTPUT
    (* TRUE = safe state active — all motion must stop *)
    xSafeState          : BOOL;

    (* TRUE = stone/obstacle detected during penetration *)
    xStoneDetected      : BOOL;

    (* Upper limit triggered (only blocks upward movement) *)
    xLimitUpTriggered   : BOOL;

    (* Lower limit triggered (only blocks downward movement) *)
    xLimitDownTriggered : BOOL;

    (* Reason code — see header table *)
    eSafetyReason       : INT;
END_VAR

VAR
    tStoneDebounce      : TON;
END_VAR

(* ---- Limit switch evaluation (NC: FALSE = triggered or wire break) ---- *)
xLimitUpTriggered   := NOT xLimitUp_NC;
xLimitDownTriggered := NOT xLimitDown_NC;

(* ---- Stone detection with debounce ---- *)
tStoneDebounce(
    IN := rVFD_Current_pct > GVL_PARAMS.rSTONE_CURRENT_PCT_THR,
    PT := GVL_PARAMS.tSTONE_DEBOUNCE
);
xStoneDetected := tStoneDebounce.Q;

(* ---- Safe state evaluation (priority order) ---- *)
xSafeState    := FALSE;
eSafetyReason := 0;

IF NOT xEStop_NC THEN
    (* E-Stop has highest priority — hard stop *)
    xSafeState    := TRUE;
    eSafetyReason := 1;   (* ESTOP *)

ELSIF xHubAlarm THEN
    xSafeState    := TRUE;
    eSafetyReason := 4;   (* HUB_ALARM *)

ELSIF xVFD_Fault THEN
    xSafeState    := TRUE;
    eSafetyReason := 6;   (* VFD_COMM *)

ELSIF xStoneDetected THEN
    xSafeState    := TRUE;
    eSafetyReason := 5;   (* STONE_DETECTED *)

ELSIF xLimitUpTriggered AND xHubMovingUp THEN
    xSafeState    := TRUE;
    eSafetyReason := 2;   (* LIMIT_UP *)

ELSIF xLimitDownTriggered AND xHubMovingDown THEN
    xSafeState    := TRUE;
    eSafetyReason := 3;   (* LIMIT_DOWN *)
END_IF;
