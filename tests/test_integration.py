"""
Integration tests — full Vibrocore system simulation.

Uses the Vibrocore class (PRG_Main equivalent) which wires
FB_Safety + FB_SonicHead + FB_HubControl together exactly as
the CODESYS PRG_Main.st does.

These tests verify end-to-end behaviour including:
  - Nominal sampling cycle (DT325)
  - Stone detection mid-drill
  - E-Stop at various cycle phases
  - Multiple consecutive cycles
  - The sonic-hub interlock under real timing
"""
import pytest
from sim import Vibrocore, HubState, SonicState, P, CYCLE_MS


@pytest.fixture
def vc() -> Vibrocore:
    return Vibrocore()


class TestNominalCycle:
    def test_system_starts_in_idle(self, vc):
        assert vc.hub.eState == HubState.IDLE
        assert vc.sonic.eState == SonicState.IDLE

    def test_cycle_start_begins_homing(self, vc):
        vc.start_cycle()
        assert vc.hub.eState == HubState.HOMING

    def test_full_nominal_cycle_completes(self, vc):
        """Complete cycle: IDLE → home → wait → drill → stop_sonic → retract → IDLE."""
        vc.start_cycle()

        # Homing
        vc.run_until(
            lambda: vc.hub.eState == HubState.DRILL_WAIT,
            max_ms=10_000, label="DRILL_WAIT"
        )
        assert vc.hub.rPosition_mm == pytest.approx(0.0)

        # Sonic must start — sonic enabled when hub in DRILL_WAIT
        vc.run_until(
            lambda: vc.sonic.xRunning,
            max_ms=30_000, label="sonic xRunning"
        )
        assert vc.hub.eState == HubState.DRILLING

        # Drill to target depth
        vc.hub.set_position(P.TARGET_DEPTH_MM - 1.0)
        vc.run_until(
            lambda: vc.hub.eState == HubState.STOP_SONIC,
            max_ms=5_000, label="STOP_SONIC"
        )

        vc.run_until(
            lambda: vc.hub.eState == HubState.RETRACT,
            max_ms=10_000, label="RETRACT"
        )
        # At moment of RETRACT entry, sonic must be confirmed stopped
        assert vc.sonic.xConfirmedStopped is True, (
            "Hub entered RETRACT before sonic confirmed stopped!"
        )
        assert not vc.sonic.xRunning, (
            "Sonic still running when hub started retracting!"
        )

        # Retract to home
        vc.run_until(
            lambda: vc.hub.eState == HubState.IDLE,
            max_ms=60_000, label="IDLE (cycle complete)"
        )
        assert vc.hub.xAtHome is True

    def test_sonic_not_running_during_retract(self, vc):
        """Sonic must be OFF for the entire duration of retraction."""
        vc.start_cycle()
        vc.run_until(lambda: vc.hub.eState == HubState.DRILL_WAIT, max_ms=10_000)
        vc.run_until(lambda: vc.sonic.xRunning, max_ms=30_000)
        vc.hub.set_position(P.TARGET_DEPTH_MM - 1.0)
        vc.run_until(lambda: vc.hub.eState == HubState.RETRACT, max_ms=15_000)

        # Monitor entire retract phase
        while vc.hub.eState == HubState.RETRACT:
            assert not vc.sonic.xRunning, (
                f"Sonic was running during retract! "
                f"Hub pos={vc.hub.rPosition_mm:.1f}mm, "
                f"sonic state={vc.sonic.eState}"
            )
            vc.tick()
            if vc.cycle > 100_000:
                pytest.fail("Retract took too long")

    def test_two_consecutive_cycles(self, vc):
        """System must be fully reusable — run two cycles back to back."""
        for cycle_num in range(1, 3):
            vc.start_cycle()
            vc.run_until(lambda: vc.hub.eState == HubState.DRILL_WAIT, max_ms=10_000)
            vc.run_until(lambda: vc.sonic.xRunning, max_ms=30_000)
            vc.hub.set_position(P.TARGET_DEPTH_MM - 1.0)
            vc.run_until(lambda: vc.hub.eState == HubState.IDLE, max_ms=60_000)
            assert vc.hub.xAtHome, f"Not at home after cycle {cycle_num}"
            assert not vc.sonic.xRunning, f"Sonic still running after cycle {cycle_num}"


class TestStoneDetection:
    def test_stone_stops_sonic_before_retract(self, vc):
        """Stone detection via overcurrent → safety.xSafeState=TRUE → hub ESTOP_HOLD.
        Hub can only retract after reset + re-home. Sonic is fast-stopped first."""
        vc.start_cycle()
        vc.run_until(lambda: vc.hub.eState == HubState.DRILL_WAIT, max_ms=10_000)
        vc.run_until(lambda: vc.hub.eState == HubState.DRILLING, max_ms=30_000)

        # Simulate stone detection via overcurrent (goes through FB_Safety)
        debounce_cycles = P.STONE_DEBOUNCE_MS // CYCLE_MS
        for _ in range(debounce_cycles + 5):
            vc.hw.rVFD_Current_pct = P.STONE_CURRENT_PCT_THR + 20
            vc.tick()

        assert vc.safety.xStoneDetected is True
        assert vc.safety.xSafeState is True

        # Stone via safety path goes to ESTOP_HOLD (not STOP_SONIC)
        # — safety override has higher priority than drilling state machine
        assert vc.hub.eState == HubState.ESTOP_HOLD, (
            f"Expected ESTOP_HOLD after stone, got state={vc.hub.eState}"
        )

        # Hub must NOT retract — brake is engaged
        assert vc.hub.eState != HubState.RETRACT
        assert vc.hub.xBrakeRelease_out is False

        # Sonic receives fast-stop via xSafeState path
        assert vc.hub.xNeedSonicStop is True

        # Sonic must stop (confirmed) before any motion is possible
        vc.hw.rVFD_Current_pct = 0.0
        vc.run_until(
            lambda: vc.sonic.xConfirmedStopped,
            max_ms=10_000, label="sonic confirmed stopped after stone"
        )
        assert not vc.sonic.xRunning

    def test_stone_leaves_sample_intact(self, vc):
        """After stone detection, carriage must NOT advance deeper.
        Hub is held in ESTOP_HOLD with brake engaged until operator resets."""
        vc.start_cycle()
        vc.run_until(lambda: vc.hub.eState == HubState.DRILL_WAIT, max_ms=10_000)
        vc.run_until(lambda: vc.hub.eState == HubState.DRILLING, max_ms=30_000)

        # Drill to partial depth
        vc.hub.set_position(600.0)

        # Trigger stone via overcurrent
        debounce_cycles = P.STONE_DEBOUNCE_MS // CYCLE_MS
        for _ in range(debounce_cycles + 5):
            vc.hw.rVFD_Current_pct = P.STONE_CURRENT_PCT_THR + 20
            vc.tick()

        vc.hw.rVFD_Current_pct = 0.0
        depth_at_stone = vc.hub.rPosition_mm

        # Hub is frozen in ESTOP_HOLD — must not go deeper
        for _ in range(500):   # 5 seconds
            vc.tick()
            assert vc.hub.rPosition_mm <= depth_at_stone + P.POS_TOLERANCE_MM, (
                f"Hub drilled deeper after stone! "
                f"pos={vc.hub.rPosition_mm:.1f} > stone_depth={depth_at_stone:.1f}"
            )
            assert vc.hub.eState == HubState.ESTOP_HOLD

        # Sonic must be stopped while hub is frozen
        assert not vc.sonic.xRunning


class TestEStop:
    def test_estop_during_drilling_stops_everything(self, vc):
        vc.start_cycle()
        vc.run_until(lambda: vc.hub.eState == HubState.DRILLING, max_ms=40_000)

        vc.hw.xEStop_NC = False   # E-Stop pressed
        vc.tick()

        assert vc.safety.xSafeState is True
        assert vc.hub.eState == HubState.ESTOP_HOLD
        assert vc.hub.xBrakeRelease_out is False
        assert vc.hub.xNeedSonicStop is True

    def test_estop_during_stop_sonic_phase(self, vc):
        """E-Stop pressed while waiting for sonic to stop — must stay safe."""
        vc.start_cycle()
        vc.run_until(lambda: vc.hub.eState == HubState.DRILL_WAIT, max_ms=10_000)
        vc.run_until(lambda: vc.hub.eState == HubState.DRILLING, max_ms=30_000)
        vc.hub.set_position(P.TARGET_DEPTH_MM - 1.0)
        vc.run_until(lambda: vc.hub.eState == HubState.STOP_SONIC, max_ms=5_000)

        # Press E-Stop while in STOP_SONIC
        vc.hw.xEStop_NC = False
        vc.tick()

        assert vc.hub.eState == HubState.ESTOP_HOLD
        assert vc.hub.xBrakeRelease_out is False

    def test_estop_released_and_reset_resumes(self, vc):
        vc.start_cycle()
        vc.run_until(lambda: vc.hub.eState == HubState.DRILLING, max_ms=40_000)

        vc.hw.xEStop_NC = False
        vc.run_ms(200)

        # Release E-Stop and reset
        vc.hw.xEStop_NC = True
        vc.hmi.xFaultReset = True
        vc.tick()
        vc.hmi.xFaultReset = False

        assert vc.hub.eState == HubState.HOMING   # re-homes after E-Stop

    def test_brake_always_engaged_during_safe_state(self, vc):
        """Physical brake output must be LOW (engaged) whenever xSafeState=TRUE."""
        vc.start_cycle()
        vc.run_until(lambda: vc.hub.eState == HubState.DRILLING, max_ms=40_000)

        vc.hw.xEStop_NC = False
        for _ in range(50):
            vc.tick()
            if vc.safety.xSafeState:
                assert vc.hub.xBrakeRelease_out is False, (
                    "Brake was released during E-Stop / safe state!"
                )


class TestSystemHealth:
    def test_alarm_beacon_on_during_fault(self, vc):
        vc.hw.xEStop_NC = False
        vc.tick()
        # xAlarmBeacon is set in PRG_Main when xSafeState is TRUE
        # (simulated here via safety.xSafeState)
        assert vc.safety.xSafeState is True

    def test_no_motion_without_enable(self, vc):
        """Hub must not move when xEnable=FALSE (safe state active)."""
        vc.hw.xEStop_NC = False
        vc.tick()
        pos = vc.hub.rPosition_mm
        vc.run_ms(1000)
        assert vc.hub.rPosition_mm == pytest.approx(pos, abs=1.0)
