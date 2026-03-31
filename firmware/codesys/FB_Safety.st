(*
 * FB_Safety — Safety Monitor Function Block
 *
 * Evaluates all safety-relevant inputs and sets xSafeState.
 * When xSafeState = TRUE, all motion must stop immediately.
 *
 * Safety categories addressed:
 *   - E-Stop: Category 3 (redundant NC wiring evaluated here)
 *   - Limit switches: NC wiring, software evaluation
 *   - Overcurrent / stone detection: software function
 *   - Hub driver fault: hardware alarm signal
 *   - VFD fault: reported by FB_ModbusVFD
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

    (* Limit switches — NC wiring, FALSE = triggered *)
    xLimitUp_NC         : BOOL;
    xLimitDown_NC       : BOOL;

    (* Hub driver alarm output (active HIGH) *)
    xHubAlarm           : BOOL;

    (* VFD fault flag from FB_ModbusVFD *)
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

    (* Reason code: 0=OK 1=EStop 2=HubAlarm 3=VFD 4=Stone *)
    eSafetyReason       : INT;
END_VAR

VAR
    tStoneDebounce      : TON;
END_VAR

(* ---- Limit switch evaluation (NC contacts: FALSE = triggered) ---- *)
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
    eSafetyReason := 1;

ELSIF xHubAlarm THEN
    (* Hub driver hardware fault *)
    xSafeState    := TRUE;
    eSafetyReason := 2;

ELSIF xVFD_Fault THEN
    (* VFD hardware fault *)
    xSafeState    := TRUE;
    eSafetyReason := 3;

ELSIF xStoneDetected THEN
    (* Overcurrent → stone/obstacle — handled by state machine,
       but also sets safe state to freeze motion *)
    xSafeState    := TRUE;
    eSafetyReason := 4;

ELSIF xLimitUpTriggered AND xHubMovingUp THEN
    (* Limit in direction of travel — stop motion *)
    xSafeState    := TRUE;
    eSafetyReason := 5;

ELSIF xLimitDownTriggered AND xHubMovingDown THEN
    (* Limit in direction of travel — stop motion *)
    xSafeState    := TRUE;
    eSafetyReason := 6;
END_IF;
