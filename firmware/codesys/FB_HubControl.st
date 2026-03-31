(*
 * FB_HubControl — Hub Lift/Lower State Machine
 *
 * Controls NEMA 42 stepper via Nanotec C5-E (Modbus RTU, CiA 402).
 * Drive train: NEMA42 → Neugart PLPE120-040 (40:1) → 10B-2 chain → carriage.
 *
 * CRITICAL INTERLOCK:
 *   Hub may ONLY move upward (retract) when xSonicConfirmedStopped = TRUE.
 *   This prevents soil sample falling out during extraction.
 *   Stone detection also requires sonic stop FIRST — never retract while vibrating.
 *
 * State machine:
 *   0 IDLE          — brake engaged, motor disabled
 *   1 HOMING        — move up until xLimitUp (establishes position zero)
 *   2 DRILL_WAIT    — waiting for sonic confirmed running before hub moves
 *   3 DRILLING      — hub moves down at penetration speed
 *   4 STOP_SONIC    — target/stone reached: brake hub, request sonic fast-stop
 *   5 RETRACT       — sonic confirmed stopped, hub moves up
 *   6 ESTOP_HOLD    — emergency stop: brake engaged, waiting for release
 *   7 FAULT         — driver alarm or timeout
 *)
FUNCTION_BLOCK FB_HubControl
VAR_INPUT
    xEnable                 : BOOL;
    xSafeState              : BOOL;   (* from FB_Safety: freeze all motion *)
    xStoneDetected          : BOOL;   (* from FB_Safety: obstacle detected *)
    xSonicRunning           : BOOL;   (* from FB_SonicHead: motors spinning *)
    xSonicConfirmedStopped  : BOOL;   (* from FB_SonicHead: motors confirmed at rest *)

    rTargetDepth_mm         : REAL;   (* sampling target depth (mm from home) *)

    (* Manual jog inputs (active only in IDLE state) *)
    xCmdJogDown             : BOOL;
    xCmdJogUp               : BOOL;

    (* Auto cycle start *)
    xCmdCycleStart          : BOOL;

    (* Fault reset *)
    xCmdReset               : BOOL;
END_VAR

VAR_OUTPUT
    rPosition_mm        : REAL;    (* current carriage position from home, mm *)
    xAtHome             : BOOL;    (* carriage at upper limit *)
    xAtTarget           : BOOL;    (* carriage within tolerance of target depth *)
    xNeedSonicStop      : BOOL;    (* TRUE = request sonic fast-stop *)
    xCycleComplete      : BOOL;    (* pulse: TRUE for one cycle after retract done *)
    xFault              : BOOL;
    eState              : INT;

    (* Physical outputs — mapped by PRG_Main to GVL_IO *)
    xBrakeRelease_out   : BOOL;
    xHubEnable_out      : BOOL;
END_VAR

VAR
    (* Modbus to Nanotec C5-E *)
    fbMBWrite           : WagoModbusMasterRtu.MB_RTU_WRITE_REGS;
    fbMBRead            : WagoModbusMasterRtu.MB_RTU_READ_REGS;
    awWriteRegs         : ARRAY[0..1] OF WORD;   (* controlword + target velocity *)
    awReadRegs          : ARRAY[0..2] OF WORD;   (* statusword + actual pos low/high *)

    tMBCycle            : TON;
    tSonicStopTimeout   : TON;
    tCyclePulse         : TON;

    iSpeedSetpoint_rpm  : INT;   (* speed sent to C5-E, signed: + = down, - = up *)
    wHubCtrlWord        : WORD;

    (* 32-bit encoder position from Modbus *)
    lActualPos          : LINT;
    iPosPrev            : INT;
END_VAR

(* ---- Position calculation (encoder → mm) ---- *)
(* Combine low and high words from C5-E position register *)
lActualPos   := SHL(LINT#0 + INT_TO_LINT(awReadRegs[2]), 16)
                + INT_TO_LINT(WORD_TO_INT(awReadRegs[1]));
rPosition_mm := LINT_TO_REAL(lActualPos) / GVL_PARAMS.rENCODER_PULSES_PER_MM;

(* ---- Derived position flags ---- *)
xAtHome   := NOT GVL_IO.xLimitUp_NC;   (* NC: FALSE = triggered = home *)
xAtTarget := (rPosition_mm >= rTargetDepth_mm - GVL_PARAMS.rPOS_TOLERANCE_MM)
          AND (rPosition_mm <= rTargetDepth_mm + GVL_PARAMS.rPOS_TOLERANCE_MM);

(* ---- Global E-Stop / Safety override ---- *)
IF xSafeState AND eState <> 6 AND eState <> 7 THEN
    wHubCtrlWord        := GVL_PARAMS.wHUB_CW_QUICKSTOP;
    iSpeedSetpoint_rpm  := 0;
    xBrakeRelease_out   := FALSE;   (* brake engages *)
    xHubEnable_out      := FALSE;
    xNeedSonicStop      := TRUE;
    eState              := 6;
END_IF;

(* ---- State machine ---- *)
CASE eState OF

    (* ============================================================ *)
    0: (* IDLE *)
    (* ============================================================ *)
        wHubCtrlWord       := GVL_PARAMS.wHUB_CW_SHUTDOWN;
        iSpeedSetpoint_rpm := 0;
        xBrakeRelease_out  := FALSE;
        xHubEnable_out     := FALSE;
        xNeedSonicStop     := FALSE;
        xFault             := FALSE;
        xCyclePulse(IN := FALSE);

        IF xCmdCycleStart AND xEnable AND NOT xSafeState THEN
            eState := 1;   (* Home first, then drill *)
        ELSIF xCmdJogDown AND xEnable AND NOT GVL_IO.xLimitDown AND NOT xSafeState THEN
            xBrakeRelease_out  := TRUE;
            xHubEnable_out     := TRUE;
            wHubCtrlWord       := GVL_PARAMS.wHUB_CW_ENABLE;
            iSpeedSetpoint_rpm := REAL_TO_INT(GVL_PARAMS.rSPEED_MANUAL_MMS
                                              * GVL_PARAMS.rENCODER_PULSES_PER_MM / 1000.0 * 60.0);
        ELSIF xCmdJogUp AND xEnable AND NOT GVL_IO.xLimitUp AND NOT xSafeState THEN
            xBrakeRelease_out  := TRUE;
            xHubEnable_out     := TRUE;
            wHubCtrlWord       := GVL_PARAMS.wHUB_CW_ENABLE;
            iSpeedSetpoint_rpm := -REAL_TO_INT(GVL_PARAMS.rSPEED_MANUAL_MMS
                                               * GVL_PARAMS.rENCODER_PULSES_PER_MM / 1000.0 * 60.0);
        END_IF;

    (* ============================================================ *)
    1: (* HOMING — move up to upper limit switch *)
    (* ============================================================ *)
        xBrakeRelease_out  := TRUE;
        xHubEnable_out     := TRUE;
        wHubCtrlWord       := GVL_PARAMS.wHUB_CW_ENABLE;
        iSpeedSetpoint_rpm := -REAL_TO_INT(GVL_PARAMS.rSPEED_HOMING_MMS
                                           * GVL_PARAMS.rENCODER_PULSES_PER_MM / 1000.0 * 60.0);

        IF xAtHome THEN
            (* Limit reached — stop motor, set position origin in C5-E *)
            wHubCtrlWord       := GVL_PARAMS.wHUB_CW_SHUTDOWN;
            iSpeedSetpoint_rpm := 0;
            xBrakeRelease_out  := FALSE;
            xHubEnable_out     := FALSE;
            eState             := 2;   (* → wait for sonic *)
        END_IF;

    (* ============================================================ *)
    2: (* DRILL_WAIT — wait for sonic confirmed running *)
    (* ============================================================ *)
        xBrakeRelease_out  := FALSE;
        xHubEnable_out     := FALSE;
        iSpeedSetpoint_rpm := 0;

        IF xSonicRunning THEN
            eState := 3;
        END_IF;

        IF NOT xEnable OR xSafeState THEN
            eState := 0;
        END_IF;

    (* ============================================================ *)
    3: (* DRILLING — hub moves down, sonic running *)
    (* ============================================================ *)
        xBrakeRelease_out  := TRUE;
        xHubEnable_out     := TRUE;
        wHubCtrlWord       := GVL_PARAMS.wHUB_CW_ENABLE;
        iSpeedSetpoint_rpm := REAL_TO_INT(GVL_PARAMS.rSPEED_PENETRATE_MMS
                                          * GVL_PARAMS.rENCODER_PULSES_PER_MM / 1000.0 * 60.0);

        (* Stop drilling on target OR stone *)
        IF xAtTarget OR xStoneDetected OR GVL_IO.xLimitDown THEN
            (* Engage brake, request sonic fast-stop *)
            wHubCtrlWord       := GVL_PARAMS.wHUB_CW_QUICKSTOP;
            iSpeedSetpoint_rpm := 0;
            xBrakeRelease_out  := FALSE;
            xHubEnable_out     := FALSE;
            xNeedSonicStop     := TRUE;
            eState             := 4;
        END_IF;

    (* ============================================================ *)
    4: (* STOP_SONIC — brake engaged, waiting for sonic to confirm stop *)
    (* Hub MUST NOT move. Retract only after xSonicConfirmedStopped. *)
    (* ============================================================ *)
        xBrakeRelease_out  := FALSE;
        xHubEnable_out     := FALSE;
        iSpeedSetpoint_rpm := 0;
        xNeedSonicStop     := TRUE;   (* keep requesting fast stop *)

        tSonicStopTimeout(
            IN := TRUE,
            PT := GVL_PARAMS.tSONIC_STOP_TIMEOUT
        );

        IF xSonicConfirmedStopped THEN
            tSonicStopTimeout(IN := FALSE);
            xNeedSonicStop := FALSE;
            eState := 5;   (* → now safe to retract *)
        END_IF;

        IF tSonicStopTimeout.Q THEN
            tSonicStopTimeout(IN := FALSE);
            xFault := TRUE;
            eState := 7;   (* timeout waiting for sonic → fault *)
        END_IF;

    (* ============================================================ *)
    5: (* RETRACT — sonic confirmed stopped, hub moves up *)
    (* ============================================================ *)
        xBrakeRelease_out  := TRUE;
        xHubEnable_out     := TRUE;
        wHubCtrlWord       := GVL_PARAMS.wHUB_CW_ENABLE;
        iSpeedSetpoint_rpm := -REAL_TO_INT(GVL_PARAMS.rSPEED_RETRACT_MMS
                                           * GVL_PARAMS.rENCODER_PULSES_PER_MM / 1000.0 * 60.0);

        IF xAtHome THEN
            wHubCtrlWord       := GVL_PARAMS.wHUB_CW_SHUTDOWN;
            iSpeedSetpoint_rpm := 0;
            xBrakeRelease_out  := FALSE;
            xHubEnable_out     := FALSE;
            (* Pulse xCycleComplete for one cycle *)
            tCyclePulse(IN := TRUE, PT := T#500MS);
            xCycleComplete     := tCyclePulse.Q;
            IF tCyclePulse.Q THEN
                tCyclePulse(IN := FALSE);
                xCycleComplete := FALSE;
                eState := 0;
            END_IF;
        END_IF;

    (* ============================================================ *)
    6: (* ESTOP_HOLD — hold until E-Stop released and reset *)
    (* ============================================================ *)
        wHubCtrlWord       := GVL_PARAMS.wHUB_CW_QUICKSTOP;
        iSpeedSetpoint_rpm := 0;
        xBrakeRelease_out  := FALSE;
        xHubEnable_out     := FALSE;
        xNeedSonicStop     := TRUE;

        IF NOT xSafeState AND xCmdReset THEN
            xNeedSonicStop := FALSE;
            eState := 1;   (* Re-home after E-Stop *)
        END_IF;

    (* ============================================================ *)
    7: (* FAULT — driver alarm or sonic stop timeout *)
    (* ============================================================ *)
        wHubCtrlWord       := GVL_PARAMS.wHUB_CW_QUICKSTOP;
        iSpeedSetpoint_rpm := 0;
        xBrakeRelease_out  := FALSE;
        xHubEnable_out     := FALSE;
        xFault             := TRUE;

        IF xCmdReset AND NOT xSafeState AND NOT GVL_IO.xHubAlarm THEN
            xFault := FALSE;
            eState := 0;
        END_IF;

END_CASE;

(* ---- Nanotec C5-E Modbus write (20ms cycle) ---- *)
tMBCycle(IN := NOT tMBCycle.Q, PT := T#20MS);
IF tMBCycle.Q THEN
    awWriteRegs[0] := wHubCtrlWord;
    awWriteRegs[1] := INT_TO_WORD(iSpeedSetpoint_rpm);

    fbMBWrite(
        bExecute      := TRUE,
        nSlaveAddress := BYTE#2,
        eFunction     := WagoModbusMasterRtu.eMBFC.WriteMultipleRegisters,
        nStartAddress := INT_TO_WORD(GVL_PARAMS.iHUB_REG_CONTROLWORD),
        nQuantity     := 2,
        pData         := ADR(awWriteRegs),
        nDataLen      := SIZEOF(awWriteRegs)
    );

    fbMBRead(
        bExecute      := TRUE,
        nSlaveAddress := BYTE#2,
        eFunction     := WagoModbusMasterRtu.eMBFC.ReadHoldingRegisters,
        nStartAddress := INT_TO_WORD(GVL_PARAMS.iHUB_REG_STATUSWORD),
        nQuantity     := 3,
        pData         := ADR(awReadRegs),
        nDataLen      := SIZEOF(awReadRegs)
    );
END_IF;
