(*
 * FB_ModbusVFD — Siemens V20 VFD Communication via Modbus RTU
 *
 * Hardware: WAGO 750-826 RS-485 module, COM2 port
 * VFD: Siemens SINAMICS V20, Modbus slave address 1
 *
 * V20 pre-commissioning (set via BOP or STARTER):
 *   P0700 = 5     (command source: Modbus)
 *   P1000 = 5     (freq setpoint: Modbus)
 *   P2010[0] = 6  (Modbus baud: 9600)
 *   P2011[0] = 1  (slave address: 1)
 *   P2012[0] = 2  (PZD word count: 2)
 *   P1120 = 5.0   (ramp-up time, s)
 *   P1121 = 3.0   (ramp-down time OFF1, s)
 *   P1135 = 0.3   (ramp-down time OFF3 fast-stop, s)
 *   P1232 = 100   (DC braking current %)
 *   P1233 = 0.5   (DC braking duration, s)
 *
 * Control word bits (STW1):
 *   Bit 0: ON/OFF1  (0 = ramp to stop via P1121)
 *   Bit 1: no OFF2  (0 = coast to stop — keep 1)
 *   Bit 2: no OFF3  (0 = fast stop via P1135 — used for fast stop)
 *   Bit 3: enable operation
 *   Bit 6: setpoint enable
 *   Bit 7: fault acknowledge
 *
 * Note: Modbus library used is WagoAppModbusMasterRtu (WAGO CODESYS package).
 * Import via Library Manager: WagoAppModbusMasterRtu >= 1.1.0.0
 *)
FUNCTION_BLOCK FB_ModbusVFD
VAR_INPUT
    xEnable         : BOOL;   (* FALSE = VFD disabled, no communication *)
    xStart          : BOOL;   (* TRUE = run motor *)
    xFastStop       : BOOL;   (* TRUE = OFF3 immediately (stone / safety) *)
    xFaultReset     : BOOL;   (* rising edge = reset VFD fault *)
    rFreqSetpoint   : REAL;   (* Hz, clamped internally to MIN/MAX *)
END_VAR

VAR_OUTPUT
    xRunning        : BOOL;   (* TRUE = VFD reports motor running *)
    xReady          : BOOL;   (* TRUE = VFD ready for start command *)
    xFault          : BOOL;   (* TRUE = VFD in fault state *)
    rFreqActual     : REAL;   (* Hz — actual output frequency *)
    rCurrentActual  : REAL;   (* A  — actual output current *)
    rCurrent_pct    : REAL;   (* % of motor rated current (rated = 1.45A) *)
    xCommError      : BOOL;   (* TRUE = Modbus communication lost *)
END_VAR

VAR
    (* Modbus master FB — WagoAppModbusMasterRtu library *)
    fbMBWrite       : WagoModbusMasterRtu.MB_RTU_WRITE_REGS;
    fbMBRead        : WagoModbusMasterRtu.MB_RTU_READ_REGS;

    awWriteRegs     : ARRAY[0..1] OF WORD;   (* control + freq setpoint *)
    awReadRegs      : ARRAY[0..2] OF WORD;   (* status + freq actual + current *)

    wControlWord    : WORD;
    iFreqRaw        : INT;

    tCycle          : TON;     (* 20ms poll cycle *)
    tCommTimeout    : TON;     (* Modbus comms watchdog *)

    xResetEdge      : R_TRIG;
    xLastFaultReset : BOOL;

    (* Motor rated current for % calculation — OLI MVE 400/6-HF: 1.45A at 230V 3ph *)
    rRATED_CURRENT  : REAL := 1.45;
END_VAR

(* ---- Fault reset edge detection ---- *)
xResetEdge(CLK := xFaultReset);

(* ---- Build control word ---- *)
IF NOT xEnable THEN
    wControlWord := 16#0000;   (* fully disabled *)

ELSIF xFastStop THEN
    (* OFF3: bit 2 = 0 → VFD uses P1135 ramp + DC brake *)
    (* Achieves motor stop in ~200–400ms (vs 3+ s for normal ramp) *)
    wControlWord := GVL_PARAMS.wVFD_CW_STOP_FAST;

ELSIF xResetEdge.Q THEN
    wControlWord := GVL_PARAMS.wVFD_CW_FAULT_RESET;

ELSIF xStart THEN
    wControlWord := GVL_PARAMS.wVFD_CW_START;

ELSE
    (* Normal stop: OFF1, ramps down via P1121 *)
    wControlWord := GVL_PARAMS.wVFD_CW_STOP_NORMAL;
END_IF;

(* ---- Frequency setpoint (V20: value = Hz × 100) ---- *)
iFreqRaw := REAL_TO_INT(
    MAX(GVL_PARAMS.rVFD_FREQ_MIN_HZ,
        MIN(GVL_PARAMS.rVFD_FREQ_MAX_HZ, rFreqSetpoint)) * 100.0
);

(* ---- Pack write registers ---- *)
awWriteRegs[0] := wControlWord;
awWriteRegs[1] := INT_TO_WORD(iFreqRaw);

(* ---- 20ms poll cycle ---- *)
tCycle(IN := NOT tCycle.Q, PT := T#20MS);

IF tCycle.Q AND xEnable THEN

    (* Write: control word + freq setpoint *)
    fbMBWrite(
        bExecute     := TRUE,
        nSlaveAddress := BYTE#1,
        eFunction    := WagoModbusMasterRtu.eMBFC.WriteMultipleRegisters,
        nStartAddress := INT_TO_WORD(GVL_PARAMS.iVFD_REG_CONTROL),
        nQuantity    := 2,
        pData        := ADR(awWriteRegs),
        nDataLen     := SIZEOF(awWriteRegs)
    );

    (* Read: status word + actual freq + actual current *)
    fbMBRead(
        bExecute     := TRUE,
        nSlaveAddress := BYTE#1,
        eFunction    := WagoModbusMasterRtu.eMBFC.ReadHoldingRegisters,
        nStartAddress := INT_TO_WORD(GVL_PARAMS.iVFD_REG_STATUS),
        nQuantity    := 3,
        pData        := ADR(awReadRegs),
        nDataLen     := SIZEOF(awReadRegs)
    );

    IF fbMBRead.bDone AND NOT fbMBRead.bError THEN
        xCommError  := FALSE;
        (* ZSW1 status word bits *)
        xReady      := awReadRegs[0].1;   (* Bit 1: ready to switch on *)
        xRunning    := awReadRegs[0].2;   (* Bit 2: operation enabled / running *)
        xFault      := awReadRegs[0].3;   (* Bit 3: fault *)
        rFreqActual := WORD_TO_INT(awReadRegs[1]) / 100.0;
        rCurrentActual := WORD_TO_INT(awReadRegs[2]) / 10.0;
        rCurrent_pct   := (rCurrentActual / rRATED_CURRENT) * 100.0;
        tCommTimeout(IN := FALSE);
    ELSE
        tCommTimeout(IN := TRUE, PT := T#2S);
        xCommError := tCommTimeout.Q;
    END_IF;

END_IF;
