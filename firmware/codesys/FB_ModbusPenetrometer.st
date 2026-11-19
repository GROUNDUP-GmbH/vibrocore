(*
 * FB_ModbusPenetrometer — Force ADC via Modbus RTU (Slave 3)
 *
 * Hardware: WAGO 750-826 RS-485, Force ADC (4–20 mA → Modbus holding register)
 * Poll cycle: 50 ms. On timeout, set xFault and eFaultCode = 6 (VFD_COMM family
 * is reserved for Modbus loss on the VFD; penetrometer uses eFaultCode = 7 locally
 * and maps to GVL status only — see ADR-0001 for HMI presentation).
 *
 * Register map (device-specific — confirm at commissioning):
 *   Holding register 0: raw force counts (0..10000 → 0..5000 N)
 *)
FUNCTION_BLOCK FB_ModbusPenetrometer
VAR_INPUT
    xEnable             : BOOL;
    xFaultReset         : BOOL;
END_VAR

VAR_OUTPUT
    rForce_N            : REAL;
    rPeakForce_N        : REAL;
    xCommError          : BOOL;
    xFault              : BOOL;
    eFaultCode          : INT;    (* 0=OK  7=PENETROMETER_COMM *)
END_VAR

VAR
    fbMBRead            : WagoModbusMasterRtu.MB_RTU_READ_REGS;
    awReadRegs          : ARRAY[0..0] OF WORD;
    tCycle              : TON;
    tCommTimeout        : TON;
    rTrigReset          : R_TRIG;
    iRaw                : INT;
END_VAR

rTrigReset(CLK := xFaultReset);

IF rTrigReset.Q THEN
    xFault     := FALSE;
    xCommError := FALSE;
    eFaultCode := 0;
    tCommTimeout(IN := FALSE);
END_IF;

IF NOT xEnable THEN
    RETURN;
END_IF;

tCycle(IN := NOT tCycle.Q, PT := GVL_PARAMS.tPENETRO_POLL);

IF tCycle.Q THEN
    fbMBRead(
        bExecute      := TRUE,
        nSlaveAddress := BYTE#3,
        eFunction     := WagoModbusMasterRtu.eMBFC.ReadHoldingRegisters,
        nStartAddress := INT_TO_WORD(GVL_PARAMS.iPENETRO_REG_FORCE),
        nQuantity     := 1,
        pData         := ADR(awReadRegs),
        nDataLen      := SIZEOF(awReadRegs)
    );

    IF fbMBRead.bDone AND NOT fbMBRead.bError THEN
        tCommTimeout(IN := FALSE);
        xCommError := FALSE;
        iRaw := WORD_TO_INT(awReadRegs[0]);
        (* Scale: 0..10000 counts → 0..5000 N *)
        rForce_N := INT_TO_REAL(iRaw) * 0.5;
        IF rForce_N > rPeakForce_N THEN
            rPeakForce_N := rForce_N;
        END_IF;
        IF NOT xFault THEN
            eFaultCode := 0;
        END_IF;
    ELSE
        tCommTimeout(IN := TRUE, PT := GVL_PARAMS.tPENETRO_TIMEOUT);
        IF tCommTimeout.Q THEN
            xCommError := TRUE;
            xFault     := TRUE;
            eFaultCode := 7;   (* PENETROMETER_COMM — local; not in FB_Safety table *)
            rForce_N   := 0.0;
        END_IF;
    END_IF;
END_IF;
