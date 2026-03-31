"""
Tests for FB_SonicHead — OLI motor state machine.

Covers: startup ramp, resonance band skip, fast stop (OFF3) vs normal stop (OFF1),
xConfirmedStopped timing, adaptive frequency, fault handling.
"""
import pytest
from sim import FB_SonicHead, SonicState, CYCLE_MS, P


@pytest.fixture
def sonic() -> FB_SonicHead:
    return FB_SonicHead()


def run(sonic: FB_SonicHead, cycles: int, **kw) -> None:
    defaults = dict(
        xEnable=True, xSafeState=False, xFastStop=False,
        rTargetFreq_Hz=P.VFD_FREQ_DEFAULT_HZ, xFaultReset=False,
    )
    defaults.update(kw)
    for _ in range(cycles):
        sonic.tick(**defaults)


class TestStartup:
    def test_starts_in_idle(self, sonic):
        assert sonic.eState == SonicState.IDLE

    def test_enable_transitions_to_starting(self, sonic):
        sonic.tick(xEnable=True, xSafeState=False, xFastStop=False,
                   rTargetFreq_Hz=100.0)
        assert sonic.eState == SonicState.STARTING

    def test_ramps_to_running(self, sonic):
        # At 1.5 Hz/step per 100ms tick, 100 Hz needs ~67 ticks × 10 cycles = ~670 cycles
        for i in range(2000):
            sonic.tick(xEnable=True, xSafeState=False, xFastStop=False,
                       rTargetFreq_Hz=100.0)
            if sonic.eState == SonicState.RUNNING:
                break
        assert sonic.eState == SonicState.RUNNING
        assert sonic.xRunning is True

    def test_resonance_band_skipped(self, sonic):
        """Frequency must never linger in 8–25 Hz band during ramp-up."""
        frequencies_seen = []
        for _ in range(5000):
            sonic.tick(xEnable=True, xSafeState=False, xFastStop=False,
                       rTargetFreq_Hz=100.0)
            frequencies_seen.append(sonic.rActualFreq_Hz)
            if sonic.eState == SonicState.RUNNING:
                break

        band_violations = [
            f for f in frequencies_seen
            if P.VFD_SKIP_BAND_LOW_HZ < f < P.VFD_SKIP_BAND_HIGH_HZ
        ]
        assert band_violations == [], (
            f"Frequency entered resonance band: {band_violations}"
        )


class TestNormalStop:
    def test_disable_transitions_to_stopping(self, sonic):
        run(sonic, 5000)   # reach RUNNING
        assert sonic.eState == SonicState.RUNNING
        sonic.tick(xEnable=False, xSafeState=False, xFastStop=False,
                   rTargetFreq_Hz=100.0)
        assert sonic.eState == SonicState.STOPPING

    def test_normal_stop_returns_to_idle(self, sonic):
        run(sonic, 5000)
        for _ in range(50000):
            sonic.tick(xEnable=False, xSafeState=False, xFastStop=False,
                       rTargetFreq_Hz=100.0)
            if sonic.eState == SonicState.IDLE:
                break
        assert sonic.eState == SonicState.IDLE

    def test_normal_stop_takes_time(self, sonic):
        """Normal OFF1 stop should take multiple seconds (not instant)."""
        run(sonic, 5000)
        cycles_to_stop = 0
        for _ in range(100000):
            sonic.tick(xEnable=False, xSafeState=False, xFastStop=False,
                       rTargetFreq_Hz=100.0)
            cycles_to_stop += 1
            if sonic.eState == SonicState.IDLE:
                break
        elapsed_ms = cycles_to_stop * CYCLE_MS
        assert elapsed_ms > 2000, (
            f"Normal stop too fast: {elapsed_ms}ms (should be >2000ms)"
        )


class TestFastStop:
    def _reach_running(self, sonic: FB_SonicHead) -> None:
        for _ in range(5000):
            sonic.tick(xEnable=True, xSafeState=False, xFastStop=False,
                       rTargetFreq_Hz=100.0)
            if sonic.eState == SonicState.RUNNING:
                return
        pytest.fail("Could not reach RUNNING state")

    def test_fast_stop_enters_fast_stop_state(self, sonic):
        self._reach_running(sonic)
        sonic.tick(xEnable=True, xSafeState=False, xFastStop=True,
                   rTargetFreq_Hz=100.0)
        assert sonic.eState == SonicState.FAST_STOP

    def test_fast_stop_faster_than_normal_stop(self, sonic):
        """OFF3 (fast stop) must complete faster than OFF1 (normal stop)."""
        # Measure fast stop time
        self._reach_running(sonic)
        fast_cycles = 0
        for _ in range(100000):
            sonic.tick(xEnable=True, xSafeState=False, xFastStop=True,
                       rTargetFreq_Hz=100.0)
            fast_cycles += 1
            if sonic.xConfirmedStopped:
                break
        fast_ms = fast_cycles * CYCLE_MS

        # Measure normal stop time with a fresh instance
        sonic2 = FB_SonicHead()
        for _ in range(5000):
            sonic2.tick(xEnable=True, xSafeState=False, xFastStop=False,
                        rTargetFreq_Hz=100.0)
            if sonic2.eState == SonicState.RUNNING:
                break
        normal_cycles = 0
        for _ in range(100000):
            sonic2.tick(xEnable=False, xSafeState=False, xFastStop=False,
                        rTargetFreq_Hz=100.0)
            normal_cycles += 1
            if sonic2.eState == SonicState.IDLE:
                break
        normal_ms = normal_cycles * CYCLE_MS

        assert fast_ms < normal_ms, (
            f"Fast stop ({fast_ms}ms) was not faster than normal stop ({normal_ms}ms)"
        )
        # Fast stop should be well under 2s
        assert fast_ms < 2000, f"Fast stop took {fast_ms}ms, expected < 2000ms"

    def test_confirmed_stopped_only_after_standstill_confirmed(self, sonic):
        """xConfirmedStopped must be FALSE until VFD stop + 200ms hold."""
        self._reach_running(sonic)
        sonic.tick(xEnable=True, xSafeState=False, xFastStop=True,
                   rTargetFreq_Hz=100.0)
        # Immediately after fast stop command: NOT yet confirmed
        assert sonic.xConfirmedStopped is False

    def test_safe_state_triggers_fast_stop(self, sonic):
        """xSafeState should have same effect as xFastStop."""
        self._reach_running(sonic)
        sonic.tick(xEnable=True, xSafeState=True, xFastStop=False,
                   rTargetFreq_Hz=100.0)
        assert sonic.eState == SonicState.FAST_STOP

    def test_stop_timeout_causes_fault(self, sonic):
        """If motor doesn't stop within SONIC_STOP_TIMEOUT_MS → FAULT."""
        self._reach_running(sonic)
        # Prevent VFD from ever stopping
        sonic._vfd.xRunning = True

        timeout_cycles = (P.SONIC_STOP_TIMEOUT_MS // CYCLE_MS) + 50
        for _ in range(timeout_cycles):
            sonic._vfd.xRunning = True   # force-keep running
            sonic.tick(xEnable=True, xSafeState=False, xFastStop=True,
                       rTargetFreq_Hz=100.0)
            if sonic.eState == SonicState.FAULT:
                break

        assert sonic.eState == SonicState.FAULT


class TestFaultReset:
    def test_fault_reset_clears_fault(self, sonic):
        sonic._vfd.inject_fault = True
        for _ in range(10):
            sonic.tick(xEnable=True, xSafeState=False, xFastStop=False,
                       rTargetFreq_Hz=100.0)

        sonic._vfd.xFault = False
        # Reset with xEnable=False — prevents immediate re-start after fault clear
        for _ in range(5):
            sonic.tick(xEnable=False, xSafeState=False, xFastStop=False,
                       rTargetFreq_Hz=100.0, xFaultReset=True)

        # Must have exited FAULT state
        assert sonic.eState == SonicState.IDLE, (
            f"Expected IDLE after fault reset, got state={sonic.eState}"
        )
        assert not sonic.xFault
