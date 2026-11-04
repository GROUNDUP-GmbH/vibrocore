"""
pytest configuration for Vibrocore state machine tests.

No fixtures shared globally — each test file uses its own fixtures.
This file exists to make `tests/` a proper pytest root and to configure
test output formatting.
"""
import sys
import os

# Make sim module importable from any working directory, and the cad package
# importable from the repository root.
_TESTS = os.path.dirname(__file__)
_ROOT = os.path.dirname(_TESTS)
sys.path.insert(0, _TESTS)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
