(*
 * PRG_Main — Vibrocore Main Control Program
 *
 * Orchestrates all function blocks in the correct execution order:
 *   1. HMI / Modbus input conditioning (edge pulses, jog watchdog, mode)
 *   2. FB_Safety  — always first motion-critical, evaluates all safety inputs
 *   3. FB_SonicHead — VFD / OLI motor control
 *   4. FB_HubControl — carriage position and chain drive
 *   5. FB_LiftControl / FB_TiltControl — V1.1 actuators
 *   6. FB_ModbusPenetrometer — force ADC
 *   7. Physical I/O assignment
 *   8. FB_DataLogger + Modbus status write-back
 *
 * Physical I/O outputs (from GVL_IO) are assigned ONLY here,
 * never inside function blocks.
 *
 * Operating modes (eMode):
 *   0  MANUAL   — jog up/down via HMI buttons, sonic via HMI toggle
 *   1  DT325    — automatic sampling cycle with DT325 Geoprobe core barrel
 *   2  AUGER    — automatic sampling cycle with 30mm auger (future)
 *
 * Mode changes are accepted ONLY while the machine is idle
 * (hub IDLE, not safe-state, not fault).
 *
 * Fault-code table (canonical):
 *   0=OK 1=ESTOP 2=LIMIT_UP 3=LIMIT_DOWN 4=HUB_ALARM 5=STONE_DETECTED 6=VFD_COMM
 *
 * INTERLOCK: Hub retract BLOCKED until fbSonic.xConfirmedStopped = TRUE.
 *)
PROGRAM PRG_Main
VAR
    fbSafety        : FB_Safety;
    fbSonic         : FB_SonicHead;
    fbHub           : FB_HubControl;
    fbLogger        : FB_DataLogger;
    fbLift          : FB_LiftControl;
    fbTilt          : FB_TiltControl;
    fbPenetro       : FB_ModbusPenetrometer;

    (* Operating mode selection — driven from GVL_MODBUS when idle *)
    eMode           : INT := 0;   (* 0=MANUAL 1=DT325_AUTO 2=AUGER *)

    (* Sampling target (overridden from HMI / Modbus) *)
    rTargetDepth_mm : REAL := GVL_PARAMS.rTARGET_DEPTH_MM;
    rTargetFreq_Hz  : REAL := GVL_PARAMS.rVFD_FREQ_DEFAULT_HZ;

    (* Conditioned HMI commands (after edge / watchdog processing) *)
    xHMI_CycleStart : BOOL;
    xHMI_JogDown    : BOOL;
    xHMI_JogUp      : BOOL;
    xHMI_SonicToggle: BOOL;
    xHMI_FaultReset : BOOL;

    (* Edge / pulse helpers *)
    rTrigCycleStart : R_TRIG;
    rTrigFaultReset : R_TRIG;

    (* Jog heartbeat watchdog *)
    iJogHbPrev      : WORD;
    xJogHbAlive     : BOOL;
    tJogWatchdog    : TON;
    xJogHbInit      : BOOL;

    (* Status outputs *)
    eSystemState    : INT;
    sSafetyStatus   : STRING[30];
    xSystemOK       : BOOL;
    xMachineIdle    : BOOL;

    (* REAL ↔ 2× WORD overlay (IEEE 754, low word first — WAGO Modbus map) *)
    uDepth          : UNION
                          r : REAL;
                          w : ARRAY[0..1] OF WORD;
                      END_UNION;
    uTgtFreq        : UNION
                          r : REAL;
                          w : ARRAY[0..1] OF WORD;
                      END_UNION;
    uPos            : UNION
                          r : REAL;
                          w : ARRAY[0..1] OF WORD;
                      END_UNION;
    uFreq           : UNION
                          r : REAL;
                          w : ARRAY[0..1] OF WORD;
                      END_UNION;
    uCurrent        : UNION
                          r : REAL;
                          w : ARRAY[0..1] OF WORD;
                      END_UNION;
    uPeakForce      : UNION
                          r : REAL;
                          w : ARRAY[0..1] OF WORD;
                      END_UNION;
END_VAR

(* ================================================================
   0. HMI / MODBUS INPUT CONDITIONING
   ================================================================ *)

(* --- Mode switch: only while idle --- *)
xMachineIdle := (fbHub.eState = 0) AND NOT fbSafety.xSafeState
             AND NOT fbHub.xFault AND NOT fbSonic.xFault;

IF GVL_MODBUS.eHMI_OperatingMode <> eMode THEN
    IF xMachineIdle THEN
        eMode := GVL_MODBUS.eHMI_OperatingMode;
    ELSE
        (* Reject — write current mode back so HMI stays consistent *)
        GVL_MODBUS.eHMI_OperatingMode := eMode;
    END_IF;
END_IF;

(* --- Target depth / frequency from Modbus REAL words --- *)
uDepth.w[0] := GVL_MODBUS.rHMI_TargetDepth_mm_LO;
uDepth.w[1] := GVL_MODBUS.rHMI_TargetDepth_mm_HI;
IF uDepth.r > 0.0 THEN
    rTargetDepth_mm := uDepth.r;
END_IF;

uTgtFreq.w[0] := GVL_MODBUS.rHMI_TargetFreq_Hz_LO;
uTgtFreq.w[1] := GVL_MODBUS.rHMI_TargetFreq_Hz_HI;
IF uTgtFreq.r > 0.0 THEN
    rTargetFreq_Hz := uTgtFreq.r;
END_IF;

(* --- Start / reset: edge-triggered pulses; PLC auto-clears register --- *)
rTrigCycleStart(CLK := GVL_MODBUS.xHMI_CycleStart <> 0);
xHMI_CycleStart := rTrigCycleStart.Q;
IF GVL_MODBUS.xHMI_CycleStart <> 0 THEN
    GVL_MODBUS.xHMI_CycleStart := 0;
END_IF;

rTrigFaultReset(CLK := GVL_MODBUS.xHMI_FaultReset <> 0);
xHMI_FaultReset := rTrigFaultReset.Q;
IF GVL_MODBUS.xHMI_FaultReset <> 0 THEN
    GVL_MODBUS.xHMI_FaultReset := 0;
END_IF;

(* --- Jog: momentary + heartbeat watchdog (> 300 ms without change → stop) --- *)
IF NOT xJogHbInit THEN
    iJogHbPrev := GVL_MODBUS.iHMI_JogHeartbeat;
    xJogHbInit := TRUE;
    xJogHbAlive := FALSE;
END_IF;

IF GVL_MODBUS.iHMI_JogHeartbeat <> iJogHbPrev THEN
    iJogHbPrev := GVL_MODBUS.iHMI_JogHeartbeat;
    tJogWatchdog(IN := FALSE);
    xJogHbAlive := TRUE;
ELSE
    tJogWatchdog(IN := TRUE, PT := GVL_PARAMS.tJOG_HEARTBEAT_TIMEOUT);
    IF tJogWatchdog.Q THEN
        xJogHbAlive := FALSE;
    END_IF;
END_IF;

xHMI_JogDown := (GVL_MODBUS.xHMI_JogDown <> 0) AND xJogHbAlive;
xHMI_JogUp   := (GVL_MODBUS.xHMI_JogUp   <> 0) AND xJogHbAlive;
IF NOT xJogHbAlive THEN
    (* Never latch jog bits in the PLC image *)
    GVL_MODBUS.xHMI_JogDown := 0;
    GVL_MODBUS.xHMI_JogUp   := 0;
END_IF;

xHMI_SonicToggle := GVL_MODBUS.xHMI_SonicToggle <> 0;

(* ================================================================
   1. SAFETY — always executed first for motion interlocks
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
   4. LIFT / TILT (V1.1) — momentary commands, hub-idle interlock
   ================================================================ *)
fbLift(
    xSafeState         := fbSafety.xSafeState,
    xHubIdle           := (fbHub.eState = 0),
    xCmdExtend         := GVL_MODBUS.xHMI_LiftExtend <> 0,
    xCmdRetract        := GVL_MODBUS.xHMI_LiftRetract <> 0,
    xLimitDeployed_NC  := GVL_IO.xLiftDeployedLimit,
    xLimitRetracted_NC := GVL_IO.xLiftRetractedLimit
);

fbTilt(
    xSafeState        := fbSafety.xSafeState,
    xHubIdle          := (fbHub.eState = 0),
    xCmdVertical      := GVL_MODBUS.xHMI_TiltVertical <> 0,
    xCmdFold          := GVL_MODBUS.xHMI_TiltFold <> 0,
    xLimitVertical_NC := GVL_IO.xTiltVerticalLimit,
    xLimitFolded_NC   := GVL_IO.xTiltFoldedLimit
);

(* ================================================================
   5. PENETROMETER
   ================================================================ *)
fbPenetro(
    xEnable     := NOT fbSafety.xSafeState,
    xFaultReset := xHMI_FaultReset
);
GVL_IO.rForce_N := fbPenetro.rForce_N;

(* ================================================================
   6. PHYSICAL I/O ASSIGNMENT
   Write physical outputs ONLY here, never inside FBs
   ================================================================ *)
GVL_IO.xBrakeRelease := fbHub.xBrakeRelease_out AND NOT fbSafety.xSafeState;
GVL_IO.xHubEnable    := fbHub.xHubEnable_out    AND NOT fbSafety.xSafeState;
GVL_IO.xVFD_Reset    := xHMI_FaultReset;
GVL_IO.xAlarmBeacon  := fbSafety.xSafeState OR fbHub.xFault OR fbSonic.xFault
                     OR fbLift.xFault OR fbTilt.xFault OR fbPenetro.xFault;

(* Lift / tilt — E-stop drops all; FB already enforces direction + limit interlocks *)
IF fbSafety.xSafeState THEN
    GVL_IO.xLiftExtend   := FALSE;
    GVL_IO.xLiftRetract  := FALSE;
    GVL_IO.xTiltVertical := FALSE;
    GVL_IO.xTiltFold     := FALSE;
ELSE
    GVL_IO.xLiftExtend   := fbLift.xExtend_out;
    GVL_IO.xLiftRetract  := fbLift.xRetract_out;
    GVL_IO.xTiltVertical := fbTilt.xVertical_out;
    GVL_IO.xTiltFold     := fbTilt.xFold_out;
END_IF;

(* ================================================================
   7. DATA LOGGER
   ================================================================ *)
fbLogger(
    xCycleTrigger   := fbHub.xCycleComplete,
    rDepth_mm       := fbHub.rPosition_mm,
    rFreq_Hz        := fbSonic.rActualFreq_Hz,
    rCurrent_A      := fbSonic.rActualCurrent_A,
    iSafetyReason   := fbSafety.eSafetyReason
);

(* ================================================================
   8. SYSTEM STATUS + MODBUS WRITE-BACK
   ================================================================ *)
eSystemState := fbHub.eState;
xSystemOK    := NOT fbSafety.xSafeState
             AND NOT fbHub.xFault
             AND NOT fbSonic.xFault
             AND NOT fbPenetro.xFault;

CASE fbSafety.eSafetyReason OF
    0: sSafetyStatus := 'OK';
    1: sSafetyStatus := 'E-STOP PRESSED';
    2: sSafetyStatus := 'UPPER LIMIT HIT';
    3: sSafetyStatus := 'LOWER LIMIT HIT';
    4: sSafetyStatus := 'HUB DRIVER ALARM';
    5: sSafetyStatus := 'STONE DETECTED';
    6: sSafetyStatus := 'VFD COMM FAULT';
ELSE
    sSafetyStatus := 'UNKNOWN';
END_CASE;

(* Status registers for HMI *)
GVL_MODBUS.eStatus_SystemState  := eSystemState;
GVL_MODBUS.eStatus_HubState     := fbHub.eState;
GVL_MODBUS.eStatus_SonicState   := fbSonic.eState;
GVL_MODBUS.eStatus_SafetyReason := fbSafety.eSafetyReason;
IF xSystemOK THEN
    GVL_MODBUS.xStatus_SystemOK := 1;
ELSE
    GVL_MODBUS.xStatus_SystemOK := 0;
END_IF;
GVL_MODBUS.eStatus_LiftState    := fbLift.eState;
GVL_MODBUS.eStatus_TiltState    := fbTilt.eState;
GVL_MODBUS.iStatus_Force_N      := REAL_TO_INT(fbPenetro.rForce_N);

uPos.r := fbHub.rPosition_mm;
GVL_MODBUS.rStatus_Position_mm_LO := uPos.w[0];
GVL_MODBUS.rStatus_Position_mm_HI := uPos.w[1];

uFreq.r := fbSonic.rActualFreq_Hz;
GVL_MODBUS.rStatus_Freq_Hz_LO := uFreq.w[0];
GVL_MODBUS.rStatus_Freq_Hz_HI := uFreq.w[1];

uCurrent.r := fbSonic.rActualCurrent_pct;
GVL_MODBUS.rStatus_Current_pct_LO := uCurrent.w[0];
GVL_MODBUS.rStatus_Current_pct_HI := uCurrent.w[1];

uPeakForce.r := fbPenetro.rPeakForce_N;
GVL_MODBUS.rStatus_PeakForce_LO := uPeakForce.w[0];
GVL_MODBUS.rStatus_PeakForce_HI := uPeakForce.w[1];
