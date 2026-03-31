(*
 * GVL_PARAMS — Machine Parameters and Constants
 *
 * All physical machine constants. Verify against actual hardware
 * before commissioning. Speeds and thresholds are starting values
 * for field calibration.
 *)
VAR_GLOBAL CONSTANT

    (* =========================================================
       Hub Kinematics
       NEMA 42 + Neugart PLPE120-040 (40:1) + 10B-2 chain + 15T sprocket
       ========================================================= *)

    (* Encoder pulses per mm of carriage travel
       = (pulses/rev × gear_ratio) / (sprocket_teeth × chain_pitch)
       = (1000 × 4 × 40) / (15 × 15.875) = 160000 / 238.125 ≈ 671.9 *)
    rENCODER_PULSES_PER_MM  : REAL := 671.9;

    (* Maximum carriage travel (mm) — physical mast stroke *)
    rMAX_STROKE_MM          : REAL := 1300.0;

    (* Default sampling target depth (mm from home) *)
    rTARGET_DEPTH_MM        : REAL := 1200.0;

    (* Hub speed setpoints (mm/s) *)
    rSPEED_PENETRATE_MMS    : REAL := 15.0;   (* push-in with sonic active *)
    rSPEED_RETRACT_MMS      : REAL := 50.0;   (* pull-out after sonic stop *)
    rSPEED_MANUAL_MMS       : REAL := 30.0;   (* manual jog speed *)
    rSPEED_HOMING_MMS       : REAL := 40.0;   (* homing to upper limit *)

    (* Position tolerance for "at target" check (mm) *)
    rPOS_TOLERANCE_MM       : REAL := 5.0;

    (* =========================================================
       Hub Modbus (Nanotec C5-E — CiA 402 via Modbus RTU)
       ========================================================= *)

    iHUB_SLAVE_ADDR         : INT  := 2;

    (* Modbus register addresses (holding registers, 0-based Modbus) *)
    iHUB_REG_CONTROLWORD    : INT  := 16#6040;  (* CiA 402 control word *)
    iHUB_REG_STATUSWORD     : INT  := 16#6041;  (* CiA 402 status word *)
    iHUB_REG_TARGET_VEL     : INT  := 16#60FF;  (* target velocity, rpm *)
    iHUB_REG_ACTUAL_POS     : INT  := 16#6064;  (* position actual, encoder counts *)
    iHUB_REG_OPMODE         : INT  := 16#6060;  (* modes of operation: 3=Velocity *)

    (* CiA 402 control words *)
    wHUB_CW_SHUTDOWN        : WORD := 16#0006;  (* Shutdown *)
    wHUB_CW_ENABLE          : WORD := 16#000F;  (* Switch On + Enable Op *)
    wHUB_CW_QUICKSTOP       : WORD := 16#000B;  (* Quick stop *)
    wHUB_CW_FAULT_RESET     : WORD := 16#0080;  (* Fault reset *)

    (* =========================================================
       VFD Modbus (Siemens V20 — USS/Modbus profile)
       Standard parameter channel + process data (PKW + PZD)
       ========================================================= *)

    iVFD_SLAVE_ADDR         : INT  := 1;

    (* Process data input/output word addresses (0-based) *)
    iVFD_REG_CONTROL        : INT  := 100;   (* STW1: control word *)
    iVFD_REG_FREQ_SP        : INT  := 101;   (* HSW: freq setpoint ×100 Hz *)
    iVFD_REG_STATUS         : INT  := 110;   (* ZSW1: status word *)
    iVFD_REG_FREQ_ACT       : INT  := 111;   (* HIW: actual frequency ×100 Hz *)
    iVFD_REG_CURRENT        : INT  := 112;   (* actual current ×10 A *)

    (* V20 STW1 control words *)
    wVFD_CW_START           : WORD := 16#047F;  (* bits: ON + no OFF2 + no OFF3 + OpEnable *)
    wVFD_CW_STOP_NORMAL     : WORD := 16#047E;  (* OFF1: ramp down via P1121 *)
    wVFD_CW_STOP_FAST       : WORD := 16#047B;  (* OFF3: fast ramp via P1135 + DC brake *)
    wVFD_CW_FAULT_RESET     : WORD := 16#04FE;  (* fault acknowledgement *)

    (* Frequency limits (Hz) *)
    rVFD_FREQ_MIN_HZ        : REAL := 30.0;
    rVFD_FREQ_MAX_HZ        : REAL := 110.0;
    rVFD_FREQ_DEFAULT_HZ    : REAL := 100.0;

    (* Ramp rates for software-side tracking (Hz per 100ms cycle) *)
    rVFD_RAMP_UP_HZ_STEP    : REAL := 1.5;   (* ≈15 Hz/s -->  ~7s to 100 Hz *)
    rVFD_RAMP_DN_HZ_STEP    : REAL := 4.5;   (* ≈45 Hz/s --> normal stop *)

    (* Skip resonance band: avoid 8–25 Hz during run-up *)
    rVFD_SKIP_BAND_LOW_HZ   : REAL := 8.0;
    rVFD_SKIP_BAND_HIGH_HZ  : REAL := 25.0;

    (* =========================================================
       Safety / Stone Detection
       ========================================================= *)

    (* VFD output current threshold for stone detection (% of motor rated) *)
    rSTONE_CURRENT_PCT_THR  : REAL := 130.0;

    (* Debounce time before stone alarm is confirmed *)
    tSTONE_DEBOUNCE         : TIME := T#250MS;

    (* Hub retract distance after stone detection (mm) *)
    rSTONE_RETRACT_MM       : REAL := 50.0;

    (* Max wait time for Sonic head to confirm stop before fault *)
    tSONIC_STOP_TIMEOUT     : TIME := T#5S;

    (* =========================================================
       Data / Identity
       ========================================================= *)

    sMACHINE_ID             : STRING[20] := 'VIBROCORE-001';
    sHARDWARE_VERSION       : STRING[10] := 'V1.0';
    sFIRMWARE_VERSION       : STRING[10] := '1.0.0';

END_VAR
