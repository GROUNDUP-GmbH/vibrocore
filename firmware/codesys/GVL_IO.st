(*
 * GVL_IO — Global Variable List: Physical I/O Mapping
 *
 * WAGO PFC200 XTR (750-8212) + I/O Modules:
 *   Slot 1: 750-430 XTR  — 4× Digital Input  24V DC  → %IX0.0..%IX0.3
 *   Slot 2: 750-530 XTR  — 4× Digital Output 24V DC  → %QX0.0..%QX0.3
 *   Slot 3: 750-637      — Incremental Encoder        → %IW4 (32-bit via IW4+IW5)
 *   Slot 4: 750-826      — RS-485 Modbus RTU          → COM config in hardware tree
 *   Slot 5: 750-600      — End module
 *
 * RS-485 Slave Addresses:
 *   Addr 1: Siemens V20 VFD  (Sonic Head)
 *   Addr 2: Nanotec C5-E     (Hub stepper driver)
 *)
VAR_GLOBAL

    (* =========================================================
       Slot 1 — 750-430 XTR: 4x Digital Input 24V DC
       ========================================================= *)

    (* Upper limit switch (NC wiring — FALSE = triggered) *)
    xLimitUp        AT %IX0.0 : BOOL;

    (* Lower limit switch (NC wiring — FALSE = triggered) *)
    xLimitDown      AT %IX0.1 : BOOL;

    (* Emergency stop mushroom button (NC — FALSE = pressed) *)
    xEStop_NC       AT %IX0.2 : BOOL;

    (* Hub driver alarm output (Nanotec C5-E ALM pin, active HIGH) *)
    xHubAlarm       AT %IX0.3 : BOOL;

    (* =========================================================
       Slot 2 — 750-530 XTR: 4x Digital Output 24V DC
       ========================================================= *)

    (* Spring-applied brake: HIGH = 24V energised = brake RELEASED *)
    xBrakeRelease   AT %QX0.0 : BOOL;

    (* Hub driver enable (Nanotec C5-E ENA pin, active HIGH) *)
    xHubEnable      AT %QX0.1 : BOOL;

    (* VFD fault reset pulse (momentary, 200ms) *)
    xVFD_Reset      AT %QX0.2 : BOOL;

    (* Spare digital output — reserved for alarm beacon / HMI *)
    xAlarmBeacon    AT %QX0.3 : BOOL;

    (* =========================================================
       Slot 3 — 750-637: Incremental Encoder
       Encoder on hub chain shaft (1000 ppr, quadrature)
       Mapped as 32-bit signed integer (IW4 = low word, IW5 = high word)
       ========================================================= *)

    iEncoderLow     AT %IW4   : INT;
    iEncoderHigh    AT %IW5   : INT;

END_VAR
