// GVL_MODBUS — Modbus TCP Slave Register Map
//
// This GVL documents the mapping between CODESYS variables and
// Modbus Holding Registers exposed by the WagoAppModbusSlaveTcp library.
// Node-RED reads/writes these registers for the HMI dashboard.
//
// WAGO CODESYS setup:
//   Device Tree → Add Device → "Modbus TCP Slave" (WagoAppModbusSlaveTcp)
//   Port: 502 (standard Modbus TCP)
//   Unit ID: 1
//
// Register type: Holding Registers (FC3 read / FC6+FC16 write)
// REAL encoding: IEEE 754 single precision, 2 consecutive registers, LOW WORD FIRST
//   → register[n] = low 16 bits, register[n+1] = high 16 bits
//
// See firmware/docker/nodered/flows.json for the matching Node-RED parser.

VAR_GLOBAL

    // ── R/W Registers: HMI → PLC (offset 0..9) ───────────────────

    // Register 0: Operating mode
    //   0 = MANUAL  (jog only)
    //   1 = DT325_AUTO (full automatic drilling cycle)
    eHMI_OperatingMode      : INT;     // %MW0

    // Register 1: Cycle start command — edge-triggered pulse; PLC auto-clears to 0
    xHMI_CycleStart         : WORD;    // %MW1  (treated as BOOL: 0/1)

    // Register 2: Jog down — momentary; must be refreshed with heartbeat (%MW33)
    // Never latch. PLC drops jog if heartbeat stalls > 300 ms.
    xHMI_JogDown            : WORD;    // %MW2

    // Register 3: Jog up — momentary (same heartbeat rule as jog down)
    xHMI_JogUp              : WORD;    // %MW3

    // Register 4: Sonic toggle (starts/stops sonic head in MANUAL mode)
    xHMI_SonicToggle        : WORD;    // %MW4

    // Register 5: Fault reset — edge-triggered pulse; PLC auto-clears to 0
    // After E-stop: only a rising edge that arrives while the circuit is healthy
    // is accepted (never auto-reset).
    xHMI_FaultReset         : WORD;    // %MW5

    // Registers 6–7: Target drilling depth [mm]  (REAL, lo/hi)
    rHMI_TargetDepth_mm_LO  : WORD;    // %MW6
    rHMI_TargetDepth_mm_HI  : WORD;    // %MW7

    // Registers 8–9: Target sonic frequency [Hz]  (REAL, lo/hi)
    rHMI_TargetFreq_Hz_LO   : WORD;    // %MW8
    rHMI_TargetFreq_Hz_HI   : WORD;    // %MW9

    // ── R/O Registers: PLC → HMI (offset 10..21) ─────────────────
    // (Also mapped as Holding Registers; HMI uses FC3 read only)

    // Register 10: System operating state
    //   0=IDLE  1=MANUAL  2=DT325_AUTO  3=FAULT  4=ESTOP
    eStatus_SystemState     : INT;     // %MW10

    // Register 11: Hub state machine state (FB_HubControl.eState)
    //   0=IDLE  1=HOMING  2=DRILL_WAIT  3=DRILLING  4=STOP_SONIC
    //   5=RETRACT  6=ESTOP_HOLD  7=FAULT
    eStatus_HubState        : INT;     // %MW11

    // Register 12: Sonic head state (FB_SonicHead.eState)
    //   0=IDLE  1=STARTING  2=RUNNING  3=STOPPING  4=FAST_STOP  5=FAULT
    eStatus_SonicState      : INT;     // %MW12

    // Registers 13–14: Actual carriage position [mm]  (REAL, lo/hi)
    rStatus_Position_mm_LO  : WORD;    // %MW13
    rStatus_Position_mm_HI  : WORD;    // %MW14

    // Registers 15–16: Actual VFD output frequency [Hz]  (REAL, lo/hi)
    rStatus_Freq_Hz_LO      : WORD;    // %MW15
    rStatus_Freq_Hz_HI      : WORD;    // %MW16

    // Registers 17–18: VFD output current [% of rated]  (REAL, lo/hi)
    rStatus_Current_pct_LO  : WORD;    // %MW17
    rStatus_Current_pct_HI  : WORD;    // %MW18

    // Register 19: Safety fault reason (canonical table — FB_Safety + Node-RED)
    //   0=OK  1=ESTOP  2=LIMIT_UP  3=LIMIT_DOWN
    //   4=HUB_ALARM  5=STONE_DETECTED  6=VFD_COMM
    eStatus_SafetyReason    : INT;     // %MW19

    // Register 20: System OK flag (1 = safe, 0 = fault/safety active)
    xStatus_SystemOK        : WORD;    // %MW20

    // Register 21: Completed cycle counter (incremented per DT325 cycle)
    iStatus_CycleCount      : INT;     // %MW21

    // ── V1.1 R/W Registers: Actuator HMI → PLC (offset 22..25) ──

    // Register 22: Deploy lift command (1 = extend, 0 = stop)
    xHMI_LiftExtend         : WORD;    // %MW22

    // Register 23: Retract lift command (1 = retract, 0 = stop)
    xHMI_LiftRetract        : WORD;    // %MW23

    // Register 24: Tilt to vertical command (1 = go vertical, 0 = stop)
    xHMI_TiltVertical       : WORD;    // %MW24

    // Register 25: Tilt to fold command (1 = go transport, 0 = stop)
    xHMI_TiltFold           : WORD;    // %MW25

    // ── V1.1 R/O Registers: Actuator + Penetrometer (offset 26..33) ─

    // Register 26: Deployment state
    //   0 = UNKNOWN  1 = DEPLOYING  2 = DEPLOYED  3 = RETRACTING  4 = RETRACTED
    eStatus_LiftState       : INT;     // %MW26

    // Register 27: Tilt state
    //   0 = UNKNOWN  1 = TILTING_VERT  2 = VERTICAL  3 = TILTING_FOLD  4 = FOLDED
    eStatus_TiltState       : INT;     // %MW27

    // Register 28: Current drill push force [N]  (INT, 0..5000)
    iStatus_Force_N         : INT;     // %MW28

    // Registers 29–30: Peak force this cycle [N]  (REAL, lo/hi)
    rStatus_PeakForce_LO    : WORD;    // %MW29
    rStatus_PeakForce_HI    : WORD;    // %MW30

    // Registers 31–32: Core image available flag + cycle ID reference
    // 0 = no image  1 = image published to MQTT (set by camera Pi via MQTT → CODESYS)
    xStatus_CoreImageReady  : WORD;    // %MW31
    iStatus_LastImageCycle  : INT;     // %MW32

    // Register 33: Jog heartbeat — HMI increments while any jog button is held
    // PLC accepts jog only while this value changes at least every 300 ms.
    iHMI_JogHeartbeat       : WORD;    // %MW33

END_VAR


// ─── PRG_Main usage note ─────────────────────────────────────────────────────
//
// PRG_Main wires GVL_MODBUS every scan:
//   - Mode change accepted only while hub is IDLE and not in safe/fault
//   - CycleStart / FaultReset are edge pulses; PLC writes the register back to 0
//   - JogDown / JogUp are momentary and gated by iHMI_JogHeartbeat watchdog
//
// See docs/adr/ADR-0001-HMI-PLC-INTERFACE.md for command semantics.
// The WagoAppModbusSlaveTcp library maps %MW addresses automatically
// to Holding Register offsets when the Slave device is configured
// in the CODESYS device tree.
// ─────────────────────────────────────────────────────────────────────────────
