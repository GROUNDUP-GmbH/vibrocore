(*
 * FB_LiftControl — Deploy / retract lift actuators (%QX2.0 / %QX2.1)
 *
 * Safety rules:
 *   - Direction interlock: never assert extend and retract together
 *   - End-limit stop: drop the active direction when its NC limit opens
 *   - E-stop / safe state: drop all outputs immediately
 *   - Drilling interlock: no lift motion while hub is not IDLE
 *
 * Commands are momentary (hold-to-run) from the HMI / Modbus layer.
 *)
FUNCTION_BLOCK FB_LiftControl
VAR_INPUT
    xSafeState          : BOOL;
    xHubIdle            : BOOL;   (* TRUE only when FB_HubControl.eState = IDLE *)
    xCmdExtend          : BOOL;   (* momentary *)
    xCmdRetract         : BOOL;   (* momentary *)
    xLimitDeployed_NC   : BOOL;   (* TRUE = healthy / not at deployed end *)
    xLimitRetracted_NC  : BOOL;   (* TRUE = healthy / not at retracted end *)
END_VAR

VAR_OUTPUT
    xExtend_out         : BOOL;
    xRetract_out        : BOOL;
    eState              : INT;    (* 0=UNKNOWN 1=DEPLOYING 2=DEPLOYED 3=RETRACTING 4=RETRACTED *)
    xFault              : BOOL;
END_VAR

VAR
    xAtDeployed         : BOOL;
    xAtRetracted        : BOOL;
END_VAR

xAtDeployed  := NOT xLimitDeployed_NC;
xAtRetracted := NOT xLimitRetracted_NC;

xExtend_out  := FALSE;
xRetract_out := FALSE;
xFault       := FALSE;

IF xSafeState THEN
    eState := 0;
ELSIF NOT xHubIdle AND (xCmdExtend OR xCmdRetract) THEN
    (* Mutual interlock with drilling / hub motion *)
    xFault := TRUE;
    eState := 0;
ELSIF xCmdExtend AND xCmdRetract THEN
    (* Both directions commanded — reject *)
    xFault := TRUE;
    eState := 0;
ELSIF xCmdExtend AND NOT xAtDeployed AND xHubIdle THEN
    xExtend_out := TRUE;
    eState := 1;
ELSIF xCmdRetract AND NOT xAtRetracted AND xHubIdle THEN
    xRetract_out := TRUE;
    eState := 3;
ELSIF xAtDeployed THEN
    eState := 2;
ELSIF xAtRetracted THEN
    eState := 4;
ELSE
    eState := 0;
END_IF;
