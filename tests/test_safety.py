"""
Tests for FB_Safety — safety monitor function block.

Covers: E-Stop priority, limit switch NC logic, stone detection debounce,
VFD fault passthrough, and safety reason codes.
"""
import pytest
from sim import FB_Safety, CYCLE_MS, P


@pytest.fixture
def safety() -> FB_Safety:
    return FB_Safety()


def safe_defaults(safety: FB_Safety, **overrides) -> None:
    """Call safety.tick() with all-OK inputs, override selectively."""
    defaults = dict(
        xEStop_NC=True,
        xLimitUp_NC=True,
        xLimitDown_NC=True,
        xHubAlarm=False,
        xVFD_Fault=False,
        rVFD_Current_pct=0.0,
        xHubMovingDown=False,
        xHubMovingUp=False,
    )
    defaults.update(overrides)
    safety.tick(**defaults)


class TestEStop:
    def test_estop_pressed_sets_safe_state(self, safety):
        safe_defaults(safety, xEStop_NC=False)
        assert safety.xSafeState is True

    def test_estop_released_clears_safe_state(self, safety):
        safe_defaults(safety, xEStop_NC=False)
        safe_defaults(safety, xEStop_NC=True)
        assert safety.xSafeState is False

    def test_estop_has_highest_priority(self, safety):
        """E-Stop must override all other faults."""
        safe_defaults(
            safety,
            xEStop_NC=False,
            xHubAlarm=True,
            xVFD_Fault=True,
        )
        assert safety.eSafetyReason == 1

    def test_ok_state_reason_zero(self, safety):
        safe_defaults(safety)
        assert safety.xSafeState is False
        assert safety.eSafetyReason == 0


class TestLimitSwitches:
    def test_limit_up_triggered_when_nc_false(self, safety):
        safe_defaults(safety, xLimitUp_NC=False)
        assert safety.xLimitUpTriggered is True
        assert safety.xLimitDownTriggered is False

    def test_limit_down_triggered_when_nc_false(self, safety):
        safe_defaults(safety, xLimitDown_NC=False)
        assert safety.xLimitDownTriggered is True
        assert safety.xLimitUpTriggered is False

    def test_limit_up_causes_safe_state_only_when_moving_up(self, safety):
        safe_defaults(safety, xLimitUp_NC=False, xHubMovingUp=False)
        assert safety.xSafeState is False   # not moving up → no lockout

        safe_defaults(safety, xLimitUp_NC=False, xHubMovingUp=True)
        assert safety.xSafeState is True
        assert safety.eSafetyReason == 5

    def test_limit_down_causes_safe_state_only_when_moving_down(self, safety):
        safe_defaults(safety, xLimitDown_NC=False, xHubMovingDown=False)
        assert safety.xSafeState is False

        safe_defaults(safety, xLimitDown_NC=False, xHubMovingDown=True)
        assert safety.xSafeState is True
        assert safety.eSafetyReason == 6


class TestStoneDetection:
    def test_below_threshold_no_stone(self, safety):
        for _ in range(100):
            safe_defaults(safety, rVFD_Current_pct=100.0)
        assert safety.xStoneDetected is False

    def test_above_threshold_after_debounce(self, safety):
        debounce_cycles = P.STONE_DEBOUNCE_MS // CYCLE_MS
        for _ in range(debounce_cycles):
            safe_defaults(safety, rVFD_Current_pct=P.STONE_CURRENT_PCT_THR + 10)
        assert safety.xStoneDetected is True
        assert safety.eSafetyReason == 4

    def test_stone_clears_when_current_drops(self, safety):
        debounce_cycles = P.STONE_DEBOUNCE_MS // CYCLE_MS
        for _ in range(debounce_cycles):
            safe_defaults(safety, rVFD_Current_pct=P.STONE_CURRENT_PCT_THR + 10)
        assert safety.xStoneDetected is True

        safe_defaults(safety, rVFD_Current_pct=50.0)
        assert safety.xStoneDetected is False

    def test_intermittent_current_does_not_trigger(self, safety):
        """Spike shorter than debounce time must NOT trigger stone detection."""
        debounce_cycles = P.STONE_DEBOUNCE_MS // CYCLE_MS
        for i in range(debounce_cycles - 5):
            if i % 3 == 0:
                safe_defaults(safety, rVFD_Current_pct=P.STONE_CURRENT_PCT_THR + 10)
            else:
                safe_defaults(safety, rVFD_Current_pct=50.0)
        assert safety.xStoneDetected is False


class TestFaultPriority:
    def test_hub_alarm_priority_over_vfd(self, safety):
        safe_defaults(safety, xHubAlarm=True, xVFD_Fault=True)
        assert safety.eSafetyReason == 2   # HubAlarm beats VFD

    def test_vfd_fault_sets_safe_state(self, safety):
        safe_defaults(safety, xVFD_Fault=True)
        assert safety.xSafeState is True
        assert safety.eSafetyReason == 3
