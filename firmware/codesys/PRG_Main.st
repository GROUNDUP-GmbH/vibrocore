(*
 * PRG_Main — Vibrocore Main Control Program
 *
 * Orchestrates all function blocks in the correct execution order:
 *   1. FB_Safety  — always first, evaluates all safety inputs
 *   2. FB_SonicHead — VFD / OLI motor control
 *   3. FB_HubControl — carriage position and chain drive
 *   4. FB_DataLogger — cycle data and MQTT/RDDL payload
 *
 * Physical I/O outputs (from GVL_IO) are assigned ONLY here,
 * never inside function blocks.
 *
 * Operating modes (eMode):
 *   0  MANUAL   — jog up/down via HMI buttons, sonic via HMI toggle
 *   1  DT325    — automatic sampling cycle with DT325 Geoprobe core barrel
 *   2  AUGER    — automatic sampling cycle with 30mm auger (future)
 *
 * Sampling cycle sequence (DT325_AUTO):
 *
 *   IDLE → [CycleStart]
 *   → SONIC_START   : enable sonic, wait xSonicRunning
 *   → DRILLING      : hub down at penetration speed
 *   → [xAtTarget OR xStoneDetected OR xLimitDown]
 *   → STOP_SONIC    : brake hub, sonic fast-stop, wait xSonicConfirmedStopped
 *   → RETRACT       : hub up at retract speed
 *   → [xAtHome]
 *   → LOG_CYCLE     : write data, signal SE050 signing
 *   → IDLE
 *
 * INTERLOCK: Hub retract BLOCKED until fbSonic.xConfirmedStopped = TRUE.
 *            No exception. Not for stone, not for normal stop.
 *)
PROGRAM PRG_Main
VAR
    fbSafety        : FB_Safety;
    fbSonic         : FB_SonicHead;
    fbHub           : FB_HubControl;
    fbLogger        : FB_DataLogger;

    (* Operating mode selection *)
    eMode           : INT := 0;   (* 0=MANUAL 1=DT325_AUTO 2=AUGER *)

    (* Sampling target (can be overridden from HMI / Modbus PLC register) *)
    rTargetDepth_mm : REAL := GVL_PARAMS.rTARGET_DEPTH_MM;
    rTargetFreq_Hz  : REAL := GVL_PARAMS.rVFD_FREQ_DEFAULT_HZ;

    (* HMI / operator inputs (write from HMI or Modbus PLC holding register) *)
    xHMI_CycleStart : BOOL;
    xHMI_JogDown    : BOOL;
    xHMI_JogUp      : BOOL;
    xHMI_SonicToggle: BOOL;
    xHMI_FaultReset : BOOL;

    (* Status outputs (readable from HMI / remote via WAGO REST API) *)
    eSystemState    : INT;    (* mirrors sampling state *)
    sSafetyStatus   : STRING[30];
    xSystemOK       : BOOL;
END_VAR

(* ================================================================
   1. SAFETY — always executed first, every scan cycle
   ================================================================ *)
fbSafety(
    xEStop_NC           := GVL_IO.xEStop_NC,
    xLimitUp_NC         := GVL_IO.xLimitUp,
    xLimitDown_NC       := GVL_IO.xLimitDown,
    xHubAlarm           := GVL_IO.xHubAlarm,
    xVFD_Fault          := fbSonic.xFault,
    rVFD_Current_pct    := fbSonic.rActualCurrent_pct,
    xHubMovingDown      := (fbHub.eState = 3),
    xHubMovingUp        := (fbHub.eState = 5) OR (fbHub.eState = 1)
);

(* ================================================================
   2. SONIC HEAD
   ================================================================ *)
fbSonic(
    xEnable         := (eMode = 1) AND (fbHub.eState = 3 OR fbHub.eState = 2)
                       OR (eMode = 0 AND xHMI_SonicToggle),
    xSafeState      := fbSafety.xSafeState,
    xFastStop       := fbHub.xNeedSonicStop OR fbSafety.xSafeState,
    rTargetFreq_Hz  := rTargetFreq_Hz,
    xFaultReset     := xHMI_FaultReset
);

(* ================================================================
   3. HUB CONTROL
   ================================================================ *)
fbHub(
    xEnable                 := NOT fbSafety.xSafeState,
    xSafeState              := fbSafety.xSafeState,
    xStoneDetected          := fbSafety.xStoneDetected,
    xSonicRunning           := fbSonic.xRunning,
    xSonicConfirmedStopped  := fbSonic.xConfirmedStopped,
    rTargetDepth_mm         := rTargetDepth_mm,
    xCmdJogDown             := xHMI_JogDown AND (eMode = 0),
    xCmdJogUp               := xHMI_JogUp   AND (eMode = 0),
    xCmdCycleStart          := xHMI_CycleStart AND (eMode = 1),
    xCmdReset               := xHMI_FaultReset
);

(* ================================================================
   4. PHYSICAL I/O ASSIGNMENT
   Write physical outputs ONLY here, never inside FBs
   ================================================================ *)
GVL_IO.xBrakeRelease := fbHub.xBrakeRelease_out AND NOT fbSafety.xSafeState;
GVL_IO.xHubEnable    := fbHub.xHubEnable_out    AND NOT fbSafety.xSafeState;
GVL_IO.xVFD_Reset    := xHMI_FaultReset;
GVL_IO.xAlarmBeacon  := fbSafety.xSafeState OR fbHub.xFault OR fbSonic.xFault;

(* ================================================================
   5. DATA LOGGER
   ================================================================ *)
fbLogger(
    xCycleTrigger   := fbHub.xCycleComplete,
    rDepth_mm       := fbHub.rPosition_mm,
    rFreq_Hz        := fbSonic.rActualFreq_Hz,
    rCurrent_A      := fbSonic.rActualCurrent_A,
    iSafetyReason   := fbSafety.eSafetyReason
);

(* ================================================================
   6. SYSTEM STATUS SUMMARY (for HMI / remote monitoring)
   ================================================================ *)
eSystemState := fbHub.eState;
xSystemOK    := NOT fbSafety.xSafeState
             AND NOT fbHub.xFault
             AND NOT fbSonic.xFault;

CASE fbSafety.eSafetyReason OF
    0: sSafetyStatus := 'OK';
    1: sSafetyStatus := 'E-STOP PRESSED';
    2: sSafetyStatus := 'HUB DRIVER ALARM';
    3: sSafetyStatus := 'VFD FAULT';
    4: sSafetyStatus := 'STONE DETECTED';
    5: sSafetyStatus := 'UPPER LIMIT HIT';
    6: sSafetyStatus := 'LOWER LIMIT HIT';
ELSE
    sSafetyStatus := 'UNKNOWN';
END_CASE;
