(*
 * GVL_IO — Global Variable List: Physical I/O Mapping
 *
 * WAGO PFC200 XTR (750-8212) + I/O Modules:
 *
 * V1 (Base):
 *   Slot 1: 750-430/040-000 — 8× DI 24V DC   → %IX0.0..%IX0.3  (hub/safety)
 *   Slot 2: 750-537/040-000 — 8× DO 24V DC → %QX0.0..%QX0.3  (hub/safety)
 *   No encoder slot. VC-HB-3410 and 750-637 are obsolete.
 *   Position comes from the 1FL2 absolute encoder through the S200.
 *   Slot 3: 750-652 candidate — RS-485 Modbus → Slave 1: V20, Slave 2: S200
 *   Slot 4: 750-600      — End module
 *
 * V1.1 (+ Lift, Tilt, Penetrometer — see docs/engineering/BOM.md §8):
 *   Slot 5: 750-430/040-000 — 8× DI 24V DC → %IX2.0..%IX2.3  (actuator limits)
 *   Slot 6: 750-537/040-000 — 8× DO 24V DC → %QX2.0..%QX2.3  (actuator control)
 *   Slot 7: 750-600      — End module
 *   RS-485 Slave 3: Force ADC (4-20mA → Modbus RTU)
 *
 * RevPi Option B: All signals below map to RevPi DIO channels instead.
 *   RevPi DIO: 14 DI (channels 0-13) + 14 DO (channels 0-13)
 *   Built-in RS-485: same Slave addresses 1-3
 *)
VAR_GLOBAL

    (* =========================================================
       Slot 1 — 750-430/040-000: 8x Digital Input 24V DC
       ========================================================= *)

    (* Upper limit switch (NC wiring — FALSE = triggered) *)
    xLimitUp        AT %IX0.0 : BOOL;

    (* Lower limit switch (NC wiring — FALSE = triggered) *)
    xLimitDown      AT %IX0.1 : BOOL;

    (* Emergency stop monitor contact (NC — FALSE = pressed).
       The device is 2-NC. The second NC contact is hard-wired to the safety relay.
       This PLC bit is not the only stop path. *)
    xEStop_NC       AT %IX0.2 : BOOL;

    (* Hub driver alarm output (SINAMICS S200, active HIGH) *)
    xHubAlarm       AT %IX0.3 : BOOL;

    (* =========================================================
       Slot 2 — 750-537/040-000: 8x Digital Output 24V DC
       ========================================================= *)

    (* Spring-applied brake: HIGH = 24V energised = brake RELEASED *)
    xBrakeRelease   AT %QX0.0 : BOOL;

    (* Hub driver enable (SINAMICS S200, active HIGH) *)
    xHubEnable      AT %QX0.1 : BOOL;

    (* VFD fault reset pulse (momentary, 200ms) *)
    xVFD_Reset      AT %QX0.2 : BOOL;

    (* Spare digital output — reserved for alarm beacon / HMI *)
    xAlarmBeacon    AT %QX0.3 : BOOL;

    (* Chain-shaft encoder words are removed.
       VC-HB-3410 and 750-637 are obsolete.
       Position comes from the 1FL2 absolute encoder through the S200. *)

    (* =========================================================
       Slot 5 — 750-430/040-000 (2nd): 8x DI 24V DC  [V1.1]
       Actuator limit switches, NC wiring
       ========================================================= *)

    (* Lift actuators fully deployed — device in drilling position *)
    xLiftDeployedLimit  AT %IX2.0 : BOOL;

    (* Lift actuators fully retracted — device in transport position *)
    xLiftRetractedLimit AT %IX2.1 : BOOL;

    (* Mast tilt actuator at vertical/drilling position *)
    xTiltVerticalLimit  AT %IX2.2 : BOOL;

    (* Mast tilt actuator at folded/transport position *)
    xTiltFoldedLimit    AT %IX2.3 : BOOL;

    (* =========================================================
       Slot 6 — 750-537/040-000 (2nd): 8x DO 24V DC  [V1.1]
       Actuator direction control via H-bridge relay modules
       SAFETY: xLiftExtend / xLiftRetract mutually exclusive.
               xTiltVertical / xTiltFold mutually exclusive.
       ========================================================= *)

    (* Extend lift actuators — move device down to drilling position *)
    xLiftExtend     AT %QX2.0 : BOOL;

    (* Retract lift actuators — raise device to transport position *)
    xLiftRetract    AT %QX2.1 : BOOL;

    (* Drive tilt actuator toward vertical drilling position *)
    xTiltVertical   AT %QX2.2 : BOOL;

    (* Drive tilt actuator toward folded transport position *)
    xTiltFold       AT %QX2.3 : BOOL;

    (* =========================================================
       RS-485 Slave 3 — Force ADC (Penetrometer)  [V1.1]
       Not a physical %I/%Q address.
       Populated by FB_ModbusPenetrometer in PRG_Main via
       WagoAppModbusMasterRtu read request to Slave addr 3.
       ========================================================= *)

    (* Drill push force in Newtons — updated every 50 ms *)
    rForce_N        : REAL;

END_VAR
