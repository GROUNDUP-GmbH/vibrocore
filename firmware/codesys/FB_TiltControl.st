(*
 * FB_TiltControl — Mast tilt actuator (%QX2.2 / %QX2.3)
 *
 * Safety rules:
 *   - Direction interlock: never assert vertical and fold together
 *   - End-limit stop: drop the active direction when its NC limit opens
 *   - E-stop / safe state: drop all outputs immediately
 *   - Drilling interlock: no tilt motion while hub is not IDLE
 *
 * Commands are momentary (hold-to-run) from the HMI / Modbus layer.
 *)
FUNCTION_BLOCK FB_TiltControl
VAR_INPUT
    xSafeState          : BOOL;
    xHubIdle            : BOOL;
    xCmdVertical        : BOOL;   (* momentary *)
    xCmdFold            : BOOL;   (* momentary *)
    xLimitVertical_NC   : BOOL;   (* TRUE = healthy / not at vertical end *)
    xLimitFolded_NC     : BOOL;   (* TRUE = healthy / not at folded end *)
END_VAR

VAR_OUTPUT
    xVertical_out       : BOOL;
    xFold_out           : BOOL;
    eState              : INT;    (* 0=UNKNOWN 1=TILTING_VERT 2=VERTICAL 3=TILTING_FOLD 4=FOLDED *)
    xFault              : BOOL;
END_VAR

VAR
    xAtVertical         : BOOL;
    xAtFolded           : BOOL;
END_VAR

xAtVertical := NOT xLimitVertical_NC;
xAtFolded   := NOT xLimitFolded_NC;

xVertical_out := FALSE;
xFold_out     := FALSE;
xFault        := FALSE;

IF xSafeState THEN
    eState := 0;
ELSIF NOT xHubIdle AND (xCmdVertical OR xCmdFold) THEN
    xFault := TRUE;
    eState := 0;
ELSIF xCmdVertical AND xCmdFold THEN
    xFault := TRUE;
    eState := 0;
ELSIF xCmdVertical AND NOT xAtVertical AND xHubIdle THEN
    xVertical_out := TRUE;
    eState := 1;
ELSIF xCmdFold AND NOT xAtFolded AND xHubIdle THEN
    xFold_out := TRUE;
    eState := 3;
ELSIF xAtVertical THEN
    eState := 2;
ELSIF xAtFolded THEN
    eState := 4;
ELSE
    eState := 0;
END_IF;
