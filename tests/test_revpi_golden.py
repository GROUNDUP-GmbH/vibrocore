"""Parity harness for the RevPi safety monitor.

The golden file is the shared vector set. This test plays each vector on
``tests/sim.py``. The Rust test ``safety_parity`` plays the same file on
``vc-core``. Both sides must agree while the state machines are ported.
"""

from __future__ import annotations

import json
from pathlib import Path

from sim import CYCLE_MS, FB_Safety

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "firmware" / "revpi" / "golden" / "safety-vectors.json"


def _play(safety: FB_Safety, case: dict) -> None:
    for step in case["steps"]:
        expect = step["expect"]
        output = None
        for _ in range(step["cycles"]):
            safety.tick(**step["input"])
            output = safety
        assert output is not None
        assert output.xSafeState is expect["safe_state"]
        assert output.xStoneDetected is expect["stone_detected"]
        assert output.xLimitUpTriggered is expect["limit_up_triggered"]
        assert output.xLimitDownTriggered is expect["limit_down_triggered"]
        assert output.eSafetyReason == expect["reason"]


def test_golden_vectors_match_python_safety_monitor():
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    assert data["source"] == "tests/sim.py FB_Safety"
    assert data["cycle_ms"] == CYCLE_MS
    cases = data["cases"]
    assert [case["name"] for case in cases] == [
        "estop_has_highest_priority",
        "limit_up_causes_safe_state_only_when_moving_up",
        "above_threshold_after_debounce",
    ]
    for case in cases:
        _play(FB_Safety(), case)
