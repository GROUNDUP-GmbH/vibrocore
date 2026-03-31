"""
pytest configuration for Vibrocore state machine tests.

No fixtures shared globally — each test file uses its own fixtures.
This file exists to make `tests/` a proper pytest root and to configure
test output formatting.
"""
import sys
import os

# Make sim module importable from any working directory
sys.path.insert(0, os.path.dirname(__file__))
