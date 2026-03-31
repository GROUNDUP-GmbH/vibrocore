"""
Vibrocore — IEC 61131-3 State Machine Simulator

Faithful Python translation of the CODESYS Structured Text state machines.
Used exclusively for unit and integration testing without hardware.

Conventions mirroring the ST code:
  - Each class represents one Function Block (FB_*)
  - `.tick()` = one PLC scan cycle (default: CYCLE_MS = 10ms)
  - Timer classes replicate IEC 61131-3 TON behaviour exactly
  - State integer codes match the CASE constants in the ST files
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# PLC cycle time — every .tick() call advances time by this amount
# ---------------------------------------------------------------------------
CYCLE_MS: int = 10


# ---------------------------------------------------------------------------
# IEC 61131-3 Timer: TON
# ---------------------------------------------------------------------------
class TON:
    """On-delay timer. Q becomes TRUE after IN held TRUE for >= PT_ms."""

    def __init__(self) -> None:
        self._cycles: int = 0
        self.Q: bool = False
        self.ET_ms: int = 0

    def __call__(self, IN: bool, PT_ms: int) -> None:
        PT_cycles = max(1, PT_ms // CYCLE_MS)
        if IN:
            if self._cycles < PT_cycles:
                self._cycles += 1
            self.Q = self._cycles >= PT_cycles
        else:
            self._cycles = 0
            self.Q = False
        self.ET_ms = self._cycles * CYCLE_MS

    def reset(self) -> None:
        self._cycles = 0
        self.Q = False
        self.ET_ms = 0


# ---------------------------------------------------------------------------
# Rising edge detector: R_TRIG
# ---------------------------------------------------------------------------
class R_TRIG:
    def __init__(self) -> None:
        self._prev: bool = False
        self.Q: bool = False

    def __call__(self, CLK: bool) -> None:
        self.Q = CLK and not self._prev
        self._prev = CLK


# ---------------------------------------------------------------------------
# Machine constants (mirrors GVL_PARAMS.st)
# ---------------------------------------------------------------------------
@dataclass
class Params:
    ENCODER_PULSES_PER_MM: float = 671.9
    MAX_STROKE_MM: float = 1300.0
    TARGET_DEPTH_MM: float = 1200.0
    SPEED_PENETRATE_MMS: float = 15.0
    SPEED_RETRACT_MMS: float = 50.0
    SPEED_HOMING_MMS: float = 40.0
    POS_TOLERANCE_MM: float = 5.0

    VFD_FREQ_MIN_HZ: float = 30.0
    VFD_FREQ_MAX_HZ: float = 110.0
    VFD_FREQ_DEFAULT_HZ: float = 100.0
    VFD_RAMP_UP_HZ_STEP: float = 1.5      # per 100ms tick
    VFD_RAMP_DN_HZ_STEP: float = 4.5      # per 100ms tick
    VFD_SKIP_BAND_LOW_HZ: float = 8.0
    VFD_SKIP_BAND_HIGH_HZ: float = 25.0

    STONE_CURRENT_PCT_THR: float = 130.0
    STONE_DEBOUNCE_MS: int = 250
    SONIC_STOP_TIMEOUT_MS: int = 5000

    # Simulated VFD motor stop delays
    VFD_FAST_STOP_MS: int = 300    # OFF3: P1135 (0.3s) + DC brake
    VFD_NORMAL_STOP_MS: int = 3000  # OFF1: P1121 (3s)


P = Params()


# ---------------------------------------------------------------------------
# Mock VFD (Siemens V20) — replaces FB_ModbusVFD for simulation
# ---------------------------------------------------------------------------
class MockVFD:
    """
    Simulates V20 motor behaviour:
      - Motor spins up instantly when start commanded (conservative)
      - OFF3 (fast stop): motor stops after VFD_FAST_STOP_MS
      - OFF1 (normal stop): motor stops after VFD_NORMAL_STOP_MS
    """

    def __init__(self) -> None:
        self.xRunning: bool = False
        self.xReady: bool = True
        self.xFault: bool = False
        self.xCommError: bool = False
        self.rFreqActual: float = 0.0
        self.rCurrentActual: float = 0.0
        self.rCurrent_pct: float = 0.0

        self._stop_countdown: int = 0
        self._target_freq: float = 0.0

        # Inject fault on next tick for fault-path testing
        self.inject_fault: bool = False

    def command(
        self,
        xEnable: bool,
        xStart: bool,
        xFastStop: bool,
        rFreqSetpoint: float,
    ) -> None:
        if self.inject_fault:
            self.xFault = True
            self.inject_fault = False

        if not xEnable or self.xFault:
            self._target_freq = 0.0
            self._stop_countdown = 1
            return

        if xFastStop:
            self._target_freq = 0.0
            if self._stop_countdown == 0 and self.xRunning:
                self._stop_countdown = P.VFD_FAST_STOP_MS // CYCLE_MS
        elif xStart and rFreqSetpoint > 0.0:
            # Running at non-zero frequency: start/keep running, clear stop countdown
            self._target_freq = rFreqSetpoint
            if not self.xRunning:
                self.xRunning = True
                self.rFreqActual = rFreqSetpoint
            self._stop_countdown = 0
        elif xStart and rFreqSetpoint <= 0.0:
            # xStart=TRUE but freq ramped to zero (STOPPING state):
            # treat as normal stop — tick() will trigger the countdown
            self._target_freq = 0.0
        else:
            self._target_freq = 0.0
            if self._stop_countdown == 0 and self.xRunning:
                self._stop_countdown = P.VFD_NORMAL_STOP_MS // CYCLE_MS

    def tick(self) -> None:
        if self._stop_countdown > 0:
            self._stop_countdown -= 1
            if self._stop_countdown == 0:
                self.xRunning = False
                self.rFreqActual = 0.0
        elif self.xRunning and self._target_freq <= 0.0:
            # Frequency setpoint has been ramped to zero → start normal stop countdown
            if self._stop_countdown == 0:
                self._stop_countdown = P.VFD_NORMAL_STOP_MS // CYCLE_MS
        elif self.xRunning:
            self.rFreqActual = self._target_freq

    def reset_fault(self) -> None:
        self.xFault = False


# ---------------------------------------------------------------------------
# FB_Safety
# ---------------------------------------------------------------------------
class FB_Safety:
    """
    Mirrors firmware/codesys/FB_Safety.st

    Outputs:
      xSafeState       — TRUE: all motion must stop
      xStoneDetected   — TRUE: debounced overcurrent → obstacle
      xLimitUpTriggered
      xLimitDownTriggered
      eSafetyReason    — 0=OK 1=EStop 2=HubAlarm 3=VFD 4=Stone 5=LimitUp 6=LimitDn
    """

    def __init__(self) -> None:
        self.xSafeState: bool = False
        self.xStoneDetected: bool = False
        self.xLimitUpTriggered: bool = False
        self.xLimitDownTriggered: bool = False
        self.eSafetyReason: int = 0

        self._tStoneDebounce: TON = TON()

    def tick(
        self,
        xEStop_NC: bool,        # NC contact — FALSE = E-Stop pressed
        xLimitUp_NC: bool,      # NC contact — FALSE = triggered
        xLimitDown_NC: bool,    # NC contact — FALSE = triggered
        xHubAlarm: bool,
        xVFD_Fault: bool,
        rVFD_Current_pct: float,
        xHubMovingDown: bool = False,
        xHubMovingUp: bool = False,
    ) -> None:

        self.xLimitUpTriggered   = not xLimitUp_NC
        self.xLimitDownTriggered = not xLimitDown_NC

        self._tStoneDebounce(
            IN=rVFD_Current_pct > P.STONE_CURRENT_PCT_THR,
            PT_ms=P.STONE_DEBOUNCE_MS,
        )
        self.xStoneDetected = self._tStoneDebounce.Q

        self.xSafeState = False
        self.eSafetyReason = 0

        if not xEStop_NC:
            self.xSafeState = True
            self.eSafetyReason = 1
        elif xHubAlarm:
            self.xSafeState = True
            self.eSafetyReason = 2
        elif xVFD_Fault:
            self.xSafeState = True
            self.eSafetyReason = 3
        elif self.xStoneDetected:
            self.xSafeState = True
            self.eSafetyReason = 4
        elif self.xLimitUpTriggered and xHubMovingUp:
            self.xSafeState = True
            self.eSafetyReason = 5
        elif self.xLimitDownTriggered and xHubMovingDown:
            self.xSafeState = True
            self.eSafetyReason = 6


# ---------------------------------------------------------------------------
# FB_SonicHead
# ---------------------------------------------------------------------------

# State codes (mirror ST CASE values)
class SonicState:
    IDLE      = 0
    STARTING  = 1
    RUNNING   = 2
    STOPPING  = 3
    FAST_STOP = 4
    FAULT     = 5


class FB_SonicHead:
    """
    Mirrors firmware/codesys/FB_SonicHead.st

    Key output: xConfirmedStopped — TRUE only when motors are verified at
    standstill for 200ms. Hub retract must wait for this.
    """

    def __init__(self) -> None:
        self.xRunning: bool = False
        self.xConfirmedStopped: bool = False
        self.xFault: bool = False
        self.rActualFreq_Hz: float = 0.0
        self.rActualCurrent_A: float = 0.0
        self.rActualCurrent_pct: float = 0.0
        self.eState: int = SonicState.IDLE

        self._vfd: MockVFD = MockVFD()
        self._tRampTick: TON = TON()
        self._tFastStopTimeout: TON = TON()
        self._tFastStopConfirm: TON = TON()

        self._rCurrentFreq: float = 0.0
        self._xFastStopActive: bool = False
        self._xNormalStopActive: bool = False

    @property
    def vfd(self) -> MockVFD:
        return self._vfd

    def tick(
        self,
        xEnable: bool,
        xSafeState: bool,
        xFastStop: bool,
        rTargetFreq_Hz: float = P.VFD_FREQ_DEFAULT_HZ,
        xFaultReset: bool = False,
    ) -> None:

        self._xFastStopActive   = xFastStop or xSafeState
        self._xNormalStopActive = (not xEnable) and not self._xFastStopActive

        prev_state = self.eState

        if self.eState == SonicState.IDLE:
            self._rCurrentFreq = 0.0
            self.xConfirmedStopped = not self._vfd.xRunning

            if xEnable and not xSafeState and not self._xFastStopActive:
                self._tRampTick.reset()
                self.eState = SonicState.STARTING

        elif self.eState == SonicState.STARTING:
            self.xConfirmedStopped = False
            self._tRampTick(IN=True, PT_ms=100)
            if self._tRampTick.Q:
                self._tRampTick.reset()
                self._rCurrentFreq += P.VFD_RAMP_UP_HZ_STEP
                # Skip resonance band
                if (P.VFD_SKIP_BAND_LOW_HZ < self._rCurrentFreq
                        < P.VFD_SKIP_BAND_HIGH_HZ):
                    self._rCurrentFreq = P.VFD_SKIP_BAND_HIGH_HZ

            if self._rCurrentFreq >= rTargetFreq_Hz:
                self._rCurrentFreq = rTargetFreq_Hz
                self.eState = SonicState.RUNNING

            if self._xFastStopActive:
                self.eState = SonicState.FAST_STOP
            elif self._xNormalStopActive:
                self.eState = SonicState.STOPPING

            if self._vfd.xFault:
                self.eState = SonicState.FAULT

        elif self.eState == SonicState.RUNNING:
            self.xConfirmedStopped = False
            # Adaptive frequency (simplified — no load feedback in sim)
            self._rCurrentFreq = rTargetFreq_Hz

            if self._xFastStopActive:
                self.eState = SonicState.FAST_STOP
            elif self._xNormalStopActive:
                self.eState = SonicState.STOPPING

            if self._vfd.xFault:
                self.eState = SonicState.FAULT

        elif self.eState == SonicState.STOPPING:
            self._tRampTick(IN=True, PT_ms=100)
            if self._tRampTick.Q:
                self._tRampTick.reset()
                self._rCurrentFreq = max(
                    0.0, self._rCurrentFreq - P.VFD_RAMP_DN_HZ_STEP
                )

            if not self._vfd.xRunning and self._rCurrentFreq <= 0.0:
                self._tFastStopConfirm(IN=True, PT_ms=200)
                if self._tFastStopConfirm.Q:
                    self._tFastStopConfirm.reset()
                    self.eState = SonicState.IDLE
            else:
                self._tFastStopConfirm.reset()

            if self._xFastStopActive:
                self.eState = SonicState.FAST_STOP

        elif self.eState == SonicState.FAST_STOP:
            self._rCurrentFreq = 0.0

            self._tFastStopTimeout(
                IN=True, PT_ms=P.SONIC_STOP_TIMEOUT_MS
            )

            if not self._vfd.xRunning:
                self._tFastStopConfirm(IN=True, PT_ms=200)
                self._tFastStopTimeout.reset()

                if self._tFastStopConfirm.Q:
                    self._tFastStopConfirm.reset()
                    self.xConfirmedStopped = True
                    if not self._xFastStopActive:
                        self.eState = SonicState.IDLE
            else:
                self._tFastStopConfirm.reset()
                self.xConfirmedStopped = False

            if self._tFastStopTimeout.Q:
                self._tFastStopTimeout.reset()
                self.eState = SonicState.FAULT

        elif self.eState == SonicState.FAULT:
            self._rCurrentFreq = 0.0
            self.xConfirmedStopped = False
            if xFaultReset and not self._vfd.xFault:
                self.eState = SonicState.IDLE

        # Drive the mock VFD
        xStart = self.eState in (SonicState.STARTING, SonicState.RUNNING,
                                  SonicState.STOPPING)
        self._vfd.command(
            xEnable    = xEnable or self.eState > 0,
            xStart     = xStart,
            xFastStop  = self.eState == SonicState.FAST_STOP,
            rFreqSetpoint = self._rCurrentFreq,
        )
        self._vfd.tick()

        # Map outputs
        self.xRunning           = self._vfd.xRunning
        self.xFault             = self._vfd.xFault or self._vfd.xCommError
        self.rActualFreq_Hz     = self._vfd.rFreqActual
        self.rActualCurrent_A   = self._vfd.rCurrentActual
        self.rActualCurrent_pct = self._vfd.rCurrent_pct


# ---------------------------------------------------------------------------
# FB_HubControl (simplified — position tracked analytically)
# ---------------------------------------------------------------------------

class HubState:
    IDLE        = 0
    HOMING      = 1
    DRILL_WAIT  = 2
    DRILLING    = 3
    STOP_SONIC  = 4
    RETRACT     = 5
    ESTOP_HOLD  = 6
    FAULT       = 7


class FB_HubControl:
    """
    Mirrors firmware/codesys/FB_HubControl.st

    Position is tracked analytically (speed × time) rather than
    via Modbus registers — sufficient for state-machine testing.
    """

    def __init__(self) -> None:
        self.rPosition_mm: float = 0.0       # 0 = home (upper limit)
        self.xAtHome: bool = True
        self.xAtTarget: bool = False
        self.xNeedSonicStop: bool = False
        self.xCycleComplete: bool = False
        self.xFault: bool = False
        self.eState: int = HubState.IDLE

        self.xBrakeRelease_out: bool = False
        self.xHubEnable_out: bool = False

        self._tSonicStopTimeout: TON = TON()
        self._tCyclePulse: TON = TON()

        # Hardware mock: limit switches (NC)
        self._xLimitUp_NC: bool = True    # TRUE = not triggered
        self._xLimitDown_NC: bool = True

    def set_position(self, pos_mm: float) -> None:
        """Test helper: teleport carriage to position."""
        self.rPosition_mm = pos_mm
        self._update_limits()

    def _update_limits(self) -> None:
        self._xLimitUp_NC   = self.rPosition_mm > 2.0
        self._xLimitDown_NC = self.rPosition_mm < P.MAX_STROKE_MM - 2.0
        self.xAtHome        = not self._xLimitUp_NC
        self.xAtTarget      = abs(self.rPosition_mm - P.TARGET_DEPTH_MM) <= P.POS_TOLERANCE_MM

    def _move(self, speed_mms: float) -> None:
        """Advance position by one cycle at given speed (+ = down, - = up)."""
        self.rPosition_mm += speed_mms * (CYCLE_MS / 1000.0)
        self.rPosition_mm  = max(0.0, min(P.MAX_STROKE_MM, self.rPosition_mm))
        self._update_limits()

    def tick(
        self,
        xEnable: bool,
        xSafeState: bool,
        xStoneDetected: bool,
        xSonicRunning: bool,
        xSonicConfirmedStopped: bool,
        rTargetDepth_mm: float = P.TARGET_DEPTH_MM,
        xCmdJogDown: bool = False,
        xCmdJogUp: bool = False,
        xCmdCycleStart: bool = False,
        xCmdReset: bool = False,
    ) -> None:

        self.xCycleComplete = False

        # Safety override — interrupt any state immediately
        if xSafeState and self.eState not in (HubState.ESTOP_HOLD, HubState.FAULT):
            self.xBrakeRelease_out  = False
            self.xHubEnable_out     = False
            self.xNeedSonicStop     = True
            self.eState             = HubState.ESTOP_HOLD
            return

        if self.eState == HubState.IDLE:
            self.xBrakeRelease_out  = False
            self.xHubEnable_out     = False
            self.xNeedSonicStop     = False
            self.xFault             = False

            if xCmdCycleStart and xEnable and not xSafeState:
                self.eState = HubState.HOMING
            elif xCmdJogDown and xEnable and self._xLimitDown_NC and not xSafeState:
                self.xBrakeRelease_out = True
                self.xHubEnable_out    = True
                self._move(+P.SPEED_PENETRATE_MMS)
            elif xCmdJogUp and xEnable and self._xLimitUp_NC and not xSafeState:
                self.xBrakeRelease_out = True
                self.xHubEnable_out    = True
                self._move(-P.SPEED_RETRACT_MMS)

        elif self.eState == HubState.HOMING:
            self.xBrakeRelease_out = True
            self.xHubEnable_out    = True
            self._move(-P.SPEED_HOMING_MMS)

            if self.xAtHome:
                self.rPosition_mm      = 0.0
                self.xBrakeRelease_out = False
                self.xHubEnable_out    = False
                self.eState            = HubState.DRILL_WAIT

        elif self.eState == HubState.DRILL_WAIT:
            self.xBrakeRelease_out = False
            self.xHubEnable_out    = False

            if xSonicRunning:
                self.eState = HubState.DRILLING
            if not xEnable or xSafeState:
                self.eState = HubState.IDLE

        elif self.eState == HubState.DRILLING:
            self.xBrakeRelease_out = True
            self.xHubEnable_out    = True
            self._move(+P.SPEED_PENETRATE_MMS)

            if self.xAtTarget or xStoneDetected or not self._xLimitDown_NC:
                self.xBrakeRelease_out = False
                self.xHubEnable_out    = False
                self.xNeedSonicStop    = True
                self.eState            = HubState.STOP_SONIC

        elif self.eState == HubState.STOP_SONIC:
            # ---------------------------------------------------------------
            # CRITICAL INTERLOCK: Hub is braked. Hub will NOT retract until
            # xSonicConfirmedStopped = TRUE. No bypass, no exception.
            # ---------------------------------------------------------------
            self.xBrakeRelease_out = False
            self.xHubEnable_out    = False
            self.xNeedSonicStop    = True   # keep requesting fast stop

            self._tSonicStopTimeout(IN=True, PT_ms=P.SONIC_STOP_TIMEOUT_MS)

            if xSonicConfirmedStopped:
                self._tSonicStopTimeout.reset()
                self.xNeedSonicStop = False
                self.eState         = HubState.RETRACT

            elif self._tSonicStopTimeout.Q:
                self._tSonicStopTimeout.reset()
                self.xFault = True
                self.eState = HubState.FAULT

        elif self.eState == HubState.RETRACT:
            self.xBrakeRelease_out = True
            self.xHubEnable_out    = True
            self._move(-P.SPEED_RETRACT_MMS)

            if self.xAtHome:
                self.xBrakeRelease_out = False
                self.xHubEnable_out    = False
                self._tCyclePulse(IN=True, PT_ms=500)
                self.xCycleComplete = self._tCyclePulse.Q
                if self._tCyclePulse.Q:
                    self._tCyclePulse.reset()
                    self.xCycleComplete = False
                    self.eState = HubState.IDLE

        elif self.eState == HubState.ESTOP_HOLD:
            self.xBrakeRelease_out = False
            self.xHubEnable_out    = False
            self.xNeedSonicStop    = True

            if not xSafeState and xCmdReset:
                self.xNeedSonicStop = False
                self.eState         = HubState.HOMING

        elif self.eState == HubState.FAULT:
            self.xBrakeRelease_out = False
            self.xHubEnable_out    = False
            self.xFault            = True

            if xCmdReset and not xSafeState:
                self.xFault = False
                self.eState = HubState.IDLE


# ---------------------------------------------------------------------------
# PRG_Main simulator — wires all FBs together for integration tests
# ---------------------------------------------------------------------------

@dataclass
class HMI:
    """Operator inputs — write from tests to simulate button presses."""
    xCycleStart:  bool = False
    xJogDown:     bool = False
    xJogUp:       bool = False
    xSonicToggle: bool = False
    xFaultReset:  bool = False
    rTargetDepth: float = P.TARGET_DEPTH_MM
    rTargetFreq:  float = P.VFD_FREQ_DEFAULT_HZ


@dataclass
class HardwareMock:
    """Simulated physical hardware state — write from tests."""
    xEStop_NC:    bool = True    # TRUE = not pressed
    xLimitUp_NC:  bool = True    # TRUE = not triggered (NC)
    xLimitDown_NC: bool = True
    xHubAlarm:    bool = False
    rVFD_Current_pct: float = 0.0


class Vibrocore:
    """
    Full system simulation.

    Usage:
        vc = Vibrocore()
        vc.hmi.xCycleStart = True
        vc.run_cycles(10)
        assert vc.hub.eState == HubState.DRILL_WAIT
    """

    def __init__(self) -> None:
        self.safety  = FB_Safety()
        self.sonic   = FB_SonicHead()
        self.hub     = FB_HubControl()
        self.hmi     = HMI()
        self.hw      = HardwareMock()
        self.cycle   = 0

    def tick(self) -> None:
        """Execute one PLC scan cycle (10ms)."""
        self.cycle += 1

        # 1. Safety
        self.safety.tick(
            xEStop_NC          = self.hw.xEStop_NC,
            xLimitUp_NC        = self.hw.xLimitUp_NC,
            xLimitDown_NC      = self.hw.xLimitDown_NC,
            xHubAlarm          = self.hw.xHubAlarm,
            xVFD_Fault         = self.sonic.xFault,
            rVFD_Current_pct   = self.hw.rVFD_Current_pct,
            xHubMovingDown     = (self.hub.eState == HubState.DRILLING),
            xHubMovingUp       = self.hub.eState in (HubState.HOMING,
                                                      HubState.RETRACT),
        )

        # 2. Sonic
        sonic_enable = (
            (self.hub.eState in (HubState.DRILL_WAIT, HubState.DRILLING))
            or (self.hmi.xSonicToggle)
        )
        self.sonic.tick(
            xEnable        = sonic_enable,
            xSafeState     = self.safety.xSafeState,
            xFastStop      = self.hub.xNeedSonicStop or self.safety.xSafeState,
            rTargetFreq_Hz = self.hmi.rTargetFreq,
            xFaultReset    = self.hmi.xFaultReset,
        )

        # 3. Hub
        self.hub.tick(
            xEnable                = not self.safety.xSafeState,
            xSafeState             = self.safety.xSafeState,
            xStoneDetected         = self.safety.xStoneDetected,
            xSonicRunning          = self.sonic.xRunning,
            xSonicConfirmedStopped = self.sonic.xConfirmedStopped,
            rTargetDepth_mm        = self.hmi.rTargetDepth,
            xCmdJogDown            = self.hmi.xJogDown,
            xCmdJogUp              = self.hmi.xJogUp,
            xCmdCycleStart         = self.hmi.xCycleStart,
            xCmdReset              = self.hmi.xFaultReset,
        )

    def run_cycles(self, n: int) -> None:
        """Advance simulation by n PLC cycles."""
        for _ in range(n):
            self.tick()

    def run_ms(self, ms: int) -> None:
        """Advance simulation by ms milliseconds."""
        self.run_cycles(ms // CYCLE_MS)

    def run_until(
        self,
        condition,
        max_ms: int = 30_000,
        label: str = "condition",
    ) -> int:
        """
        Run until condition() returns True or max_ms exceeded.
        Returns elapsed ms. Raises TimeoutError on timeout.
        """
        max_cycles = max_ms // CYCLE_MS
        for i in range(max_cycles):
            self.tick()
            if condition():
                return (i + 1) * CYCLE_MS
        raise TimeoutError(
            f"Timed out waiting for {label} after {max_ms}ms "
            f"(hub={self.hub.eState}, sonic={self.sonic.eState})"
        )

    def start_cycle(self) -> None:
        """Convenience: pulse CycleStart for one tick."""
        self.hmi.xCycleStart = True
        self.tick()
        self.hmi.xCycleStart = False
