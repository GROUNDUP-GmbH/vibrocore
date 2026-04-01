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

    // Register 1: Cycle start command (rising edge triggers cycle)
    xHMI_CycleStart         : WORD;    // %MW1  (treated as BOOL: 0/1)

    // Register 2: Jog down command (held = continuous jog in MANUAL mode)
    xHMI_JogDown            : WORD;    // %MW2

    // Register 3: Jog up command
    xHMI_JogUp              : WORD;    // %MW3

    // Register 4: Sonic toggle (starts/stops sonic head in MANUAL mode)
    xHMI_SonicToggle        : WORD;    // %MW4

    // Register 5: Fault reset (clears all quittable faults)
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

    // Register 19: Safety fault reason (FB_Safety.eSafetyReason)
    //   0=OK  1=ESTOP  2=LIMIT_UP  3=LIMIT_DOWN
    //   4=HUB_ALARM  5=STONE_DETECTED  6=VFD_COMM
    eStatus_SafetyReason    : INT;     // %MW19

    // Register 20: System OK flag (1 = safe, 0 = fault/safety active)
    xStatus_SystemOK        : WORD;    // %MW20

    // Register 21: Completed cycle counter (incremented per DT325 cycle)
    iStatus_CycleCount      : INT;     // %MW21

END_VAR


// ─── PRG_Main usage note ─────────────────────────────────────────────────────
//
// In PRG_Main, the PLC writes status to Modbus registers every scan cycle,
// and reads HMI commands with rising-edge detection. Example pattern:
//
//   // Write position to Modbus registers (REAL → 2× WORD)
//   LREALToWords(fbHub.rPosition_mm,
//                GVL_MODBUS.rStatus_Position_mm_LO,
//                GVL_MODBUS.rStatus_Position_mm_HI);
//
//   // Read HMI CycleStart with rising edge
//   IF GVL_MODBUS.xHMI_CycleStart <> 0 AND NOT xCycleStartPrev THEN
//       fbHub.xCmdCycleStart := TRUE;
//   END_IF
//   xCycleStartPrev := GVL_MODBUS.xHMI_CycleStart <> 0;
//   GVL_MODBUS.xHMI_CycleStart := 0;  // auto-clear after reading
//
// The WagoAppModbusSlaveTcp library maps %MW addresses automatically
// to Holding Register offsets when the Slave device is configured
// in the CODESYS device tree.
// ─────────────────────────────────────────────────────────────────────────────
