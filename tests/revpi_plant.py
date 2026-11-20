"""Integer plant model for the RevPi golden vectors.

Keep this file in step with ``firmware/revpi/crates/vc-core``.
The old ``tests/sim.py`` blocks stay the reference for the first 60 tests.
This model adds jog, park, tilt, rotation and the sonic interlocks.

SF3, Stefan, 2026-11-20: there is no second holding means.
The S200 motor holding brake is the only hold.
The brake test is optional.
"""

from __future__ import annotations

from sim import FB_Safety

CYCLE_MS = 10
STROKE_UM = 1_300_000
TARGET_UM = 1_200_000
HOME_UM = 2_000
LOWERED_UM = 50_000
HOMING_UM_S = 40_000
PENETRATE_UM_S = 15_000
RETRACT_UM_S = 50_000
JOG_UM_S = 10_000
BRAKE_TEST_CYCLES = 10
BRAKE_SLIP_LIMIT_UM = 2_000
TILT_ANGLE_LIMIT_MDEG = 5_000
SONIC_RAMP_CYCLES = 10
SONIC_RAMP_UP_MHZ = 1_500
SONIC_SKIP_LOW_MHZ = 8_000
SONIC_SKIP_HIGH_MHZ = 25_000
SONIC_TARGET_MHZ = 100_000
SONIC_STANDSTILL_CYCLES = 20
SONIC_STOP_TIMEOUT_CYCLES = 500
ROTATION_RPM = 60
ROTATION_TORQUE_LIMIT_PCT = 40
ROTATION_STALL_CYCLES = 20

SF3_SECOND_HOLD_FITTED = False

HUB_IDLE = 0
HUB_HOMING = 1
HUB_DRILL_WAIT = 2
HUB_DRILLING = 3
HUB_STOP_SONIC = 4
HUB_RETRACT = 5
HUB_ESTOP = 6
HUB_FAULT = 7
HUB_JOG = 8
HUB_PARK_MOVE = 9
HUB_BRAKE_TEST = 10
HUB_PARKED = 11

SONIC_IDLE = 0
SONIC_STARTING = 1
SONIC_RUNNING = 2
SONIC_STOPPING = 3
SONIC_FAST_STOP = 4
SONIC_FAULT = 5


def _step_um(speed_um_s: int) -> int:
    return speed_um_s * CYCLE_MS // 1000


class Plant:
    def __init__(self) -> None:
        self.hub_state = HUB_IDLE
        self.position_um = 0
        self._hub_fault = False
        self._test_ticks = 0
        self._stop_ticks = 0
        self._origin_um = 0
        self._prev_reset = False
        self.sonic_state = SONIC_IDLE
        self.freq_mhz = 0
        self._ramp_ticks = 0
        self._still_ticks = 0
        self._sonic_stop_ticks = 0
        self.tilt_state = 0
        self.lift_state = 0
        self.rotation_state = 0
        self._stall_ticks = 0
        self._safety = FB_Safety()
        self._last_down = False
        self._last_up = False
        self._sonic_running = False
        self._sonic_confirmed = True

    def set_position_um(self, position_um: int) -> None:
        self.position_um = max(0, min(STROKE_UM, position_um))

    def tick(self, **raw: object) -> dict[str, object]:
        inp = _defaults()
        inp.update(raw)
        self._safety.tick(
            xEStop_NC=bool(inp["estop_nc"]),
            xLimitUp_NC=bool(inp["limit_up_nc"]),
            xLimitDown_NC=bool(inp["limit_down_nc"]),
            xHubAlarm=bool(inp["hub_alarm"]),
            xVFD_Fault=bool(inp["sonic_drive_fault"]),
            rVFD_Current_pct=int(inp["sonic_current_pct_x10"]) / 10.0,
            xHubMovingDown=self._last_down,
            xHubMovingUp=self._last_up,
        )
        hub_idle = self.hub_state == HUB_IDLE
        tilt = self._tilt(inp, self._safety.xSafeState, hub_idle)
        hub = self._hub(inp, self._safety, tilt["lift_allowed"])
        lowered = hub["position_um"] > LOWERED_UM
        sonic = self._sonic(inp, self._safety.xSafeState, hub["need_sonic_stop"], lowered)
        hub_quiet = hub["state"] in (HUB_IDLE, HUB_PARKED)
        rotation = self._rotation(
            inp,
            hub_quiet and not sonic["run"] and not self._safety.xSafeState,
        )
        self._last_down = hub["speed_um_s"] > 0
        self._last_up = hub["speed_um_s"] < 0
        self._sonic_running = bool(sonic["run"])
        self._sonic_confirmed = bool(sonic["confirmed"])
        return {
            "hub_state": hub["state"],
            "position_um": hub["position_um"],
            "speed_um_s": hub["speed_um_s"],
            "pulse_enable": hub["pulse_enable"],
            "motion_blocked": hub["motion_blocked"],
            "hub_fault": hub["fault"],
            "sonic_state": sonic["state"],
            "sonic_freq_mhz": sonic["freq_mhz"],
            "sonic_run": sonic["run"],
            "sonic_fault": sonic["fault"],
            "sonic_sto_fault": sonic["sto_fault"],
            "tilt_state": tilt["tilt_state"],
            "tilt_vertical": tilt["vertical"],
            "tilt_fold": tilt["fold"],
            "lift_allowed": tilt["lift_allowed"],
            "lift_extend": tilt["extend"],
            "rotation_state": rotation["state"],
            "rotation_speed_rpm": rotation["speed_rpm"],
            "rotation_stalled": rotation["stalled"],
            "safe_state": self._safety.xSafeState,
            "safety_reason": self._safety.eSafetyReason,
        }

    def _hub(self, inp: dict[str, object], safety: FB_Safety, lift_allowed: bool) -> dict[str, object]:
        reset_edge = bool(inp["cmd_reset"]) and not self._prev_reset
        self._prev_reset = bool(inp["cmd_reset"])
        view = {
            "safe": safety.xSafeState,
            "stone": safety.xStoneDetected,
            "lift_allowed": lift_allowed,
            "enabling": bool(inp["enabling_held"]),
            "limit_up": safety.xLimitUpTriggered,
            "limit_down": safety.xLimitDownTriggered,
            "sonic_running": self._sonic_running,
            "sonic_stopped": self._sonic_confirmed,
            "cycle": bool(inp["cmd_cycle_start"]),
            "jog_down": bool(inp["cmd_jog_down"]),
            "jog_up": bool(inp["cmd_jog_up"]),
            "park": bool(inp["cmd_park"]),
            "unpark": bool(inp["cmd_unpark"]),
            "brake_test": bool(inp["brake_test_enable"]),
            "slip": int(inp["brake_slip_um"]),
        }
        if view["safe"] and self.hub_state != HUB_ESTOP:
            self.hub_state = HUB_ESTOP
            self._stop_ticks = 0
            return self._stopped(True, False)
        handler = {
            HUB_IDLE: self._idle,
            HUB_JOG: self._jog,
            HUB_HOMING: self._home,
            HUB_DRILL_WAIT: self._drill_wait,
            HUB_DRILLING: self._drill,
            HUB_STOP_SONIC: self._stop_sonic,
            HUB_RETRACT: self._retract,
            HUB_PARK_MOVE: self._park_move,
            HUB_BRAKE_TEST: self._brake_test,
            HUB_PARKED: self._parked,
            HUB_ESTOP: lambda item: self._estop(item, reset_edge),
            HUB_FAULT: lambda item: self._fault_state(item, reset_edge),
        }[self.hub_state]
        return handler(view)

    def _idle(self, item: dict[str, object]) -> dict[str, object]:
        self._hub_fault = False
        motion = item["jog_down"] or item["jog_up"] or item["cycle"] or item["park"]
        if not item["lift_allowed"] and motion:
            return self._stopped(False, True)
        if item["park"] and item["lift_allowed"]:
            self._origin_um = self.position_um
            self._test_ticks = 0
            if self.position_um <= HOME_UM:
                return self._enter_hold(item)
            self.hub_state = HUB_PARK_MOVE
            return self._park_move(item)
        if item["cycle"] and item["lift_allowed"]:
            self.hub_state = HUB_HOMING
            return self._home(item)
        if self._jog_allowed(item):
            self.hub_state = HUB_JOG
            return self._jog(item)
        return self._stopped(False, False)

    def _jog(self, item: dict[str, object]) -> dict[str, object]:
        if not self._jog_allowed(item):
            self.hub_state = HUB_IDLE
            return self._stopped(False, not item["lift_allowed"])
        down = item["jog_down"] and not item["limit_down"]
        up = item["jog_up"] and not down and not item["limit_up"]
        if down:
            self._move(JOG_UM_S)
            return self._motion(HUB_JOG, JOG_UM_S)
        if up:
            self._move(-JOG_UM_S)
            return self._motion(HUB_JOG, -JOG_UM_S)
        self.hub_state = HUB_IDLE
        return self._stopped(False, False)

    def _jog_allowed(self, item: dict[str, object]) -> bool:
        return bool(
            item["enabling"]
            and item["lift_allowed"]
            and not item["safe"]
            and (item["jog_down"] or item["jog_up"])
        )

    def _home(self, item: dict[str, object]) -> dict[str, object]:
        if not item["lift_allowed"]:
            self.hub_state = HUB_IDLE
            return self._stopped(False, True)
        if self.position_um <= HOME_UM or item["limit_up"]:
            self.position_um = 0
            self.hub_state = HUB_DRILL_WAIT
            return self._stopped(False, False)
        self._move(-HOMING_UM_S)
        return self._motion(HUB_HOMING, -HOMING_UM_S)

    def _drill_wait(self, item: dict[str, object]) -> dict[str, object]:
        if not item["lift_allowed"]:
            self.hub_state = HUB_IDLE
            return self._stopped(False, True)
        if self.position_um <= LOWERED_UM:
            self._move(PENETRATE_UM_S)
            return self._motion(HUB_DRILL_WAIT, PENETRATE_UM_S)
        if item["sonic_running"]:
            self.hub_state = HUB_DRILLING
        return self._stopped(False, False)

    def _drill(self, item: dict[str, object]) -> dict[str, object]:
        if self.position_um >= TARGET_UM or item["stone"] or item["limit_down"]:
            self.hub_state = HUB_STOP_SONIC
            self._stop_ticks = 0
            return self._stopped(True, False)
        self._move(PENETRATE_UM_S)
        return self._motion(HUB_DRILLING, PENETRATE_UM_S)

    def _stop_sonic(self, item: dict[str, object]) -> dict[str, object]:
        self._stop_ticks += 1
        if item["sonic_stopped"]:
            self._stop_ticks = 0
            self.hub_state = HUB_RETRACT
            return self._stopped(False, False)
        if self._stop_ticks >= SONIC_STOP_TIMEOUT_CYCLES:
            self._hub_fault = True
            self.hub_state = HUB_FAULT
        return self._stopped(True, False)

    def _retract(self, item: dict[str, object]) -> dict[str, object]:
        if not item["lift_allowed"]:
            return self._stopped(False, True)
        if self.position_um <= HOME_UM or item["limit_up"]:
            self.position_um = 0
            self.hub_state = HUB_IDLE
            return self._stopped(False, False)
        self._move(-RETRACT_UM_S)
        return self._motion(HUB_RETRACT, -RETRACT_UM_S)

    def _park_move(self, item: dict[str, object]) -> dict[str, object]:
        if not item["lift_allowed"]:
            self.hub_state = HUB_IDLE
            return self._stopped(False, True)
        if self.position_um <= HOME_UM or item["limit_up"]:
            return self._enter_hold(item)
        self._move(-HOMING_UM_S)
        return self._motion(HUB_PARK_MOVE, -HOMING_UM_S)

    def _enter_hold(self, item: dict[str, object]) -> dict[str, object]:
        self.position_um = 0
        self._origin_um = 0
        self._test_ticks = 0
        if item["brake_test"]:
            self.hub_state = HUB_BRAKE_TEST
            return self._brake_test(item)
        self.hub_state = HUB_PARKED
        return self._stopped(False, False)

    def _brake_test(self, item: dict[str, object]) -> dict[str, object]:
        self.position_um = max(0, min(STROKE_UM, self.position_um + int(item["slip"])))
        self._test_ticks += 1
        if abs(self.position_um - self._origin_um) > BRAKE_SLIP_LIMIT_UM:
            self._hub_fault = True
            self.hub_state = HUB_FAULT
            return self._stopped(False, False)
        if self._test_ticks >= BRAKE_TEST_CYCLES:
            self.hub_state = HUB_PARKED
        return self._stopped(False, False)

    def _parked(self, item: dict[str, object]) -> dict[str, object]:
        if item["unpark"] and not item["safe"]:
            self.hub_state = HUB_IDLE
            return self._stopped(False, False)
        requested = item["jog_down"] or item["jog_up"] or item["cycle"] or item["park"]
        return self._stopped(False, bool(requested))

    def _estop(self, item: dict[str, object], reset_edge: bool) -> dict[str, object]:
        if not item["safe"] and reset_edge:
            self.hub_state = HUB_HOMING
        return self._stopped(True, False)

    def _fault_state(self, item: dict[str, object], reset_edge: bool) -> dict[str, object]:
        if reset_edge and not item["safe"]:
            self._hub_fault = False
            self.hub_state = HUB_IDLE
        output = self._stopped(False, False)
        output["fault"] = True
        return output

    def _move(self, speed_um_s: int) -> None:
        self.position_um = max(0, min(STROKE_UM, self.position_um + _step_um(speed_um_s)))

    def _motion(self, state: int, speed_um_s: int) -> dict[str, object]:
        return {
            "state": state,
            "position_um": self.position_um,
            "speed_um_s": speed_um_s,
            "pulse_enable": speed_um_s != 0,
            "need_sonic_stop": False,
            "motion_blocked": False,
            "fault": self._hub_fault,
        }

    def _stopped(self, need_stop: bool, blocked: bool) -> dict[str, object]:
        return {
            "state": self.hub_state,
            "position_um": self.position_um,
            "speed_um_s": 0,
            "pulse_enable": False,
            "need_sonic_stop": need_stop,
            "motion_blocked": blocked,
            "fault": self._hub_fault,
        }

    def _sonic(
        self,
        inp: dict[str, object],
        safe: bool,
        fast_stop: bool,
        lowered: bool,
    ) -> dict[str, object]:
        sto = bool(inp["sonic_sto_healthy"])
        drive_fault = bool(inp["sonic_drive_fault"])
        actual = bool(inp["sonic_actual_running"])
        unexpected = (not sto) and (not safe)
        permit = (
            lowered
            and bool(inp["tool_engaged"])
            and sto
            and not drive_fault
            and not safe
            and not fast_stop
        )
        if drive_fault or unexpected:
            self.sonic_state = SONIC_FAULT
            self.freq_mhz = 0
        elif safe or fast_stop:
            if self.sonic_state not in (SONIC_IDLE, SONIC_FAULT):
                self.sonic_state = SONIC_FAST_STOP
            self.freq_mhz = 0
        if self.sonic_state == SONIC_IDLE:
            self.freq_mhz = 0
            self._still_ticks = 0
            if permit:
                self.sonic_state = SONIC_STARTING
                self._ramp_ticks = 0
        elif self.sonic_state == SONIC_STARTING:
            self._ramp(int(inp["sonic_target_mhz"]))
            if self.freq_mhz >= int(inp["sonic_target_mhz"]):
                self.freq_mhz = int(inp["sonic_target_mhz"])
                self.sonic_state = SONIC_RUNNING
            if not permit and not fast_stop and not safe:
                self.sonic_state = SONIC_STOPPING
        elif self.sonic_state == SONIC_RUNNING:
            self.freq_mhz = int(inp["sonic_target_mhz"])
            if not permit and not fast_stop and not safe:
                self.sonic_state = SONIC_STOPPING
        elif self.sonic_state == SONIC_STOPPING:
            self._ramp_down()
            if self._at_rest(actual):
                self.sonic_state = SONIC_IDLE
                self.freq_mhz = 0
        elif self.sonic_state == SONIC_FAST_STOP:
            self.freq_mhz = 0
            self._sonic_stop_ticks += 1
            if self._at_rest(actual):
                self._sonic_stop_ticks = 0
                if not fast_stop and not safe:
                    self.sonic_state = SONIC_IDLE
            elif self._sonic_stop_ticks >= SONIC_STOP_TIMEOUT_CYCLES:
                self.sonic_state = SONIC_FAULT
        elif self.sonic_state == SONIC_FAULT:
            self.freq_mhz = 0
            if bool(inp["cmd_reset"]) and not drive_fault and not unexpected:
                self.sonic_state = SONIC_IDLE
        confirmed = self.sonic_state in (SONIC_IDLE, SONIC_FAST_STOP) and not actual and self.freq_mhz == 0
        if self.sonic_state != SONIC_IDLE:
            confirmed = confirmed and self._still_ticks >= SONIC_STANDSTILL_CYCLES
        return {
            "state": self.sonic_state,
            "freq_mhz": self.freq_mhz,
            "run": self.sonic_state in (SONIC_STARTING, SONIC_RUNNING),
            "confirmed": confirmed,
            "sto_fault": unexpected,
            "fault": self.sonic_state == SONIC_FAULT,
        }

    def _ramp(self, target_mhz: int) -> None:
        self._ramp_ticks += 1
        if self._ramp_ticks < SONIC_RAMP_CYCLES:
            return
        self._ramp_ticks = 0
        self.freq_mhz += SONIC_RAMP_UP_MHZ
        if SONIC_SKIP_LOW_MHZ < self.freq_mhz < SONIC_SKIP_HIGH_MHZ:
            self.freq_mhz = SONIC_SKIP_HIGH_MHZ
        if self.freq_mhz > target_mhz:
            self.freq_mhz = target_mhz

    def _ramp_down(self) -> None:
        self._ramp_ticks += 1
        if self._ramp_ticks < SONIC_RAMP_CYCLES:
            return
        self._ramp_ticks = 0
        self.freq_mhz = max(0, self.freq_mhz - SONIC_RAMP_UP_MHZ * 3)

    def _at_rest(self, actual_running: bool) -> bool:
        if actual_running or self.freq_mhz > 0:
            self._still_ticks = 0
            return False
        self._still_ticks += 1
        return self._still_ticks >= SONIC_STANDSTILL_CYCLES

    def _tilt(self, inp: dict[str, object], safe: bool, hub_idle: bool) -> dict[str, object]:
        angle = int(inp["angle_mdeg"])
        valid = bool(inp["sensor_valid"])
        lift_allowed = valid and angle <= TILT_ANGLE_LIMIT_MDEG
        vertical = False
        fold = False
        extend = False
        retract = False
        fault = False
        if safe or not valid:
            self.tilt_state = 5
            self.lift_state = 0
        else:
            both_tilt = bool(inp["cmd_vertical"]) and bool(inp["cmd_fold"])
            both_lift = bool(inp["cmd_extend"]) and bool(inp["cmd_retract"])
            moving = bool(inp["cmd_extend"]) or bool(inp["cmd_retract"])
            fault = both_tilt or both_lift or ((not hub_idle) and (both_lift or moving))
            if not both_tilt and inp["cmd_vertical"] and not inp["limit_vertical_reached"]:
                vertical = True
                self.tilt_state = 1
            elif (
                not both_tilt
                and inp["cmd_fold"]
                and lift_allowed
                and not inp["limit_folded_reached"]
            ):
                fold = True
                self.tilt_state = 3
            elif inp["limit_vertical_reached"]:
                self.tilt_state = 2
            elif inp["limit_folded_reached"]:
                self.tilt_state = 4
            elif not lift_allowed:
                self.tilt_state = 5
            else:
                self.tilt_state = 0
            if fault or not hub_idle or not lift_allowed:
                self.lift_state = 0
            elif inp["cmd_extend"] and not inp["limit_deployed_reached"]:
                extend = True
                self.lift_state = 1
            elif inp["cmd_retract"] and not inp["limit_retracted_reached"]:
                retract = True
                self.lift_state = 3
            elif inp["limit_deployed_reached"]:
                self.lift_state = 2
            elif inp["limit_retracted_reached"]:
                self.lift_state = 4
            else:
                self.lift_state = 0
        if fault:
            vertical = False
            fold = False
            extend = False
            retract = False
        return {
            "tilt_state": self.tilt_state,
            "lift_state": self.lift_state,
            "vertical": vertical,
            "fold": fold,
            "extend": extend,
            "retract": retract,
            "lift_allowed": lift_allowed,
            "fault": fault,
        }

    def _rotation(self, inp: dict[str, object], permit: bool) -> dict[str, object]:
        if bool(inp["rotation_fault"]):
            self.rotation_state = 3
            self._stall_ticks = 0
            return self._rotation_stop(True, False)
        if not permit:
            self.rotation_state = 4
            self._stall_ticks = 0
            return self._rotation_stop(False, False)
        if not bool(inp["cmd_rotate"]):
            self.rotation_state = 0
            self._stall_ticks = 0
            return self._rotation_stop(False, False)
        speed = -ROTATION_RPM if inp["rotate_reverse"] else ROTATION_RPM
        loaded = int(inp["rotation_actual_rpm"]) == 0 and int(inp["rotation_torque_pct"]) >= ROTATION_TORQUE_LIMIT_PCT
        if loaded:
            self._stall_ticks += 1
        else:
            self._stall_ticks = 0
        if self._stall_ticks >= ROTATION_STALL_CYCLES:
            self.rotation_state = 2
            return self._rotation_stop(False, True)
        self.rotation_state = 1
        return {"state": 1, "speed_rpm": speed, "stalled": False, "fault": False}

    def _rotation_stop(self, fault: bool, stalled: bool) -> dict[str, object]:
        return {
            "state": self.rotation_state,
            "speed_rpm": 0,
            "stalled": stalled,
            "fault": fault,
        }


def _defaults() -> dict[str, object]:
    return {
        "estop_nc": True,
        "limit_up_nc": True,
        "limit_down_nc": True,
        "hub_alarm": False,
        "sonic_drive_fault": False,
        "sonic_current_pct_x10": 0,
        "sonic_sto_healthy": True,
        "sonic_actual_running": False,
        "tool_engaged": False,
        "enabling_held": False,
        "sensor_valid": True,
        "angle_mdeg": 0,
        "limit_vertical_reached": False,
        "limit_folded_reached": False,
        "limit_deployed_reached": False,
        "limit_retracted_reached": False,
        "cmd_vertical": False,
        "cmd_fold": False,
        "cmd_extend": False,
        "cmd_retract": False,
        "cmd_cycle_start": False,
        "cmd_jog_down": False,
        "cmd_jog_up": False,
        "cmd_park": False,
        "cmd_unpark": False,
        "cmd_reset": False,
        "brake_test_enable": False,
        "brake_slip_um": 0,
        "cmd_rotate": False,
        "rotate_reverse": False,
        "rotation_actual_rpm": 0,
        "rotation_torque_pct": 0,
        "rotation_fault": False,
        "sonic_target_mhz": SONIC_TARGET_MHZ,
    }
