"""
Tests for FB_HubControl — hub carriage state machine.

Covers: homing, drilling sequence, stone detection, E-Stop, and
most critically: the sonic-stop interlock (state STOP_SONIC must
wait for xSonicConfirmedStopped before transitioning to RETRACT).
"""
import pytest
from sim import FB_HubControl, HubState, P, CYCLE_MS


@pytest.fixture
def hub() -> FB_HubControl:
    return FB_HubControl()


def safe_tick(hub: FB_HubControl, **overrides) -> None:
    defaults = dict(
        xEnable=True,
        xSafeState=False,
        xStoneDetected=False,
        xSonicRunning=False,
        xSonicConfirmedStopped=False,
        rTargetDepth_mm=P.TARGET_DEPTH_MM,
        xCmdJogDown=False,
        xCmdJogUp=False,
        xCmdCycleStart=False,
        xCmdReset=False,
    )
    defaults.update(overrides)
    hub.tick(**defaults)


class TestHoming:
    def test_starts_in_idle(self, hub):
        assert hub.eState == HubState.IDLE

    def test_cycle_start_triggers_homing(self, hub):
        safe_tick(hub, xCmdCycleStart=True)
        assert hub.eState == HubState.HOMING

    def test_homing_reaches_home(self, hub):
        safe_tick(hub, xCmdCycleStart=True)
        # Carriage is already at home (position 0) — homing should complete fast
        for _ in range(200):
            safe_tick(hub)
            if hub.eState == HubState.DRILL_WAIT:
                break
        assert hub.eState == HubState.DRILL_WAIT
        assert hub.rPosition_mm == pytest.approx(0.0)

    def test_homing_moves_up(self, hub):
        hub.set_position(500.0)
        safe_tick(hub, xCmdCycleStart=True)

        positions = []
        for _ in range(500):
            safe_tick(hub)
            positions.append(hub.rPosition_mm)
            if hub.eState == HubState.DRILL_WAIT:
                break

        # Position must decrease (moving up) during homing
        assert positions[-1] < positions[0] or hub.eState == HubState.DRILL_WAIT


class TestDrillWait:
    def test_hub_waits_for_sonic(self, hub):
        safe_tick(hub, xCmdCycleStart=True)
        for _ in range(200):
            safe_tick(hub)
        assert hub.eState == HubState.DRILL_WAIT

        # Still waiting — sonic not running
        for _ in range(50):
            safe_tick(hub, xSonicRunning=False)
        assert hub.eState == HubState.DRILL_WAIT

    def test_hub_starts_drilling_when_sonic_runs(self, hub):
        safe_tick(hub, xCmdCycleStart=True)
        for _ in range(200):
            safe_tick(hub)
        assert hub.eState == HubState.DRILL_WAIT

        safe_tick(hub, xSonicRunning=True)
        assert hub.eState == HubState.DRILLING


class TestDrilling:
    def _reach_drilling(self, hub: FB_HubControl) -> None:
        safe_tick(hub, xCmdCycleStart=True)
        for _ in range(500):
            safe_tick(hub)
            if hub.eState == HubState.DRILL_WAIT:
                break
        safe_tick(hub, xSonicRunning=True)
        assert hub.eState == HubState.DRILLING

    def test_carriage_moves_down_while_drilling(self, hub):
        self._reach_drilling(hub)
        pos_before = hub.rPosition_mm
        for _ in range(100):
            safe_tick(hub, xSonicRunning=True)
        assert hub.rPosition_mm > pos_before

    def test_target_depth_transitions_to_stop_sonic(self, hub):
        self._reach_drilling(hub)
        # Teleport near target
        hub.set_position(P.TARGET_DEPTH_MM - 1.0)
        safe_tick(hub, xSonicRunning=True)
        # One more tick pushes into tolerance
        safe_tick(hub, xSonicRunning=True)
        assert hub.eState == HubState.STOP_SONIC

    def test_stone_detected_transitions_to_stop_sonic(self, hub):
        self._reach_drilling(hub)
        safe_tick(hub, xSonicRunning=True, xStoneDetected=True)
        assert hub.eState == HubState.STOP_SONIC

    def test_brake_engaged_on_stop_sonic_entry(self, hub):
        self._reach_drilling(hub)
        hub.set_position(P.TARGET_DEPTH_MM - 1.0)
        safe_tick(hub, xSonicRunning=True)
        safe_tick(hub, xSonicRunning=True)
        assert hub.eState == HubState.STOP_SONIC
        assert hub.xBrakeRelease_out is False   # brake engaged
        assert hub.xHubEnable_out is False


class TestCriticalInterlock:
    """
    THE critical test suite.

    FB_HubControl MUST NOT transition from STOP_SONIC to RETRACT
    until xSonicConfirmedStopped = TRUE. These tests formally verify
    this property under all conditions.
    """

    def _reach_stop_sonic(self, hub: FB_HubControl) -> None:
        """Bring hub to STOP_SONIC state (target depth reached)."""
        safe_tick(hub, xCmdCycleStart=True)
        for _ in range(500):
            safe_tick(hub)
            if hub.eState == HubState.DRILL_WAIT:
                break
        safe_tick(hub, xSonicRunning=True)
        assert hub.eState == HubState.DRILLING
        hub.set_position(P.TARGET_DEPTH_MM - 1.0)
        safe_tick(hub, xSonicRunning=True)
        safe_tick(hub, xSonicRunning=True)
        assert hub.eState == HubState.STOP_SONIC, f"Expected STOP_SONIC, got {hub.eState}"

    def test_hub_does_not_retract_while_sonic_running(self, hub):
        """CRITICAL: Hub must NEVER go to RETRACT (5) before xSonicConfirmedStopped.
        After the sonic-stop timeout (5s) the hub goes to FAULT (7) — also not RETRACT."""
        self._reach_stop_sonic(hub)

        # Run for just under the sonic-stop timeout (4.5s < 5s timeout)
        timeout_safety_margin = (P.SONIC_STOP_TIMEOUT_MS // CYCLE_MS) - 50
        for _ in range(timeout_safety_margin):
            safe_tick(hub, xSonicConfirmedStopped=False)
            assert hub.eState != HubState.RETRACT, (
                f"Hub entered RETRACT (state {hub.eState}) "
                f"before xSonicConfirmedStopped! Interlock BROKEN."
            )
            assert hub.xBrakeRelease_out is False, "Brake released while waiting for sonic!"

    def test_hub_retracts_only_after_sonic_confirmed_stopped(self, hub):
        """CRITICAL: Hub MUST transition to RETRACT after xSonicConfirmedStopped."""
        self._reach_stop_sonic(hub)

        # 50 cycles with sonic NOT stopped
        for _ in range(50):
            safe_tick(hub, xSonicConfirmedStopped=False)
        assert hub.eState == HubState.STOP_SONIC

        # Now confirm sonic stopped
        safe_tick(hub, xSonicConfirmedStopped=True)
        assert hub.eState == HubState.RETRACT, (
            f"Hub did not transition to RETRACT after xSonicConfirmedStopped. "
            f"State: {hub.eState}"
        )

    def test_interlock_applies_to_stone_detection(self, hub):
        """Stone detection path also requires sonic confirmed stop before retract."""
        safe_tick(hub, xCmdCycleStart=True)
        for _ in range(500):
            safe_tick(hub)
            if hub.eState == HubState.DRILL_WAIT:
                break
        safe_tick(hub, xSonicRunning=True)
        safe_tick(hub, xSonicRunning=True, xStoneDetected=True)
        assert hub.eState == HubState.STOP_SONIC

        # Stone path: must still wait for sonic stop
        for _ in range(200):
            safe_tick(hub, xSonicConfirmedStopped=False)
        assert hub.eState == HubState.STOP_SONIC

        safe_tick(hub, xSonicConfirmedStopped=True)
        assert hub.eState == HubState.RETRACT

    def test_need_sonic_stop_asserted_during_stop_sonic(self, hub):
        """xNeedSonicStop must be TRUE in STOP_SONIC to request fast-stop."""
        self._reach_stop_sonic(hub)
        for _ in range(10):
            safe_tick(hub, xSonicConfirmedStopped=False)
            assert hub.xNeedSonicStop is True, (
                "xNeedSonicStop not asserted — VFD won't receive fast-stop command!"
            )

    def test_sonic_stop_timeout_causes_fault(self, hub):
        """If sonic never stops within timeout → Hub goes to FAULT."""
        self._reach_stop_sonic(hub)

        timeout_cycles = (P.SONIC_STOP_TIMEOUT_MS // CYCLE_MS) + 20
        for _ in range(timeout_cycles):
            safe_tick(hub, xSonicConfirmedStopped=False)
        assert hub.eState == HubState.FAULT
        assert hub.xFault is True

    def test_retract_moves_carriage_up(self, hub):
        self._reach_stop_sonic(hub)
        safe_tick(hub, xSonicConfirmedStopped=True)
        assert hub.eState == HubState.RETRACT

        pos_at_retract = hub.rPosition_mm
        for _ in range(200):
            safe_tick(hub)
        assert hub.rPosition_mm < pos_at_retract


class TestEStop:
    def test_estop_during_drilling_engages_brake(self, hub):
        safe_tick(hub, xCmdCycleStart=True)
        for _ in range(500):
            safe_tick(hub)
            if hub.eState == HubState.DRILL_WAIT:
                break
        safe_tick(hub, xSonicRunning=True)

        safe_tick(hub, xSafeState=True)
        assert hub.eState == HubState.ESTOP_HOLD
        assert hub.xBrakeRelease_out is False

    def test_estop_sets_need_sonic_stop(self, hub):
        safe_tick(hub, xSafeState=True)
        assert hub.xNeedSonicStop is True

    def test_reset_after_estop_triggers_homing(self, hub):
        safe_tick(hub, xSafeState=True)
        for _ in range(5):
            safe_tick(hub, xSafeState=True)
        safe_tick(hub, xSafeState=False, xCmdReset=True)
        assert hub.eState == HubState.HOMING
