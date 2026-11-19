"""Tests for the static ST GVL reference checker."""
from __future__ import annotations

from pathlib import Path

import pytest

from check_st_gvl_refs import (
    CODESYS,
    collect_declarations,
    find_undeclared,
    main,
    parse_gvl_declarations,
)


FIXTURES = Path(__file__).parent / "fixtures_st_gvl"


@pytest.fixture()
def fixture_dir(tmp_path: Path) -> Path:
    """Minimal ST tree: valid GVL + one bad reference file."""
    gvl = tmp_path / "GVL_IO.st"
    gvl.write_text(
        """\
VAR_GLOBAL
    xLimitUp        AT %IX0.0 : BOOL;
    xLimitDown      AT %IX0.1 : BOOL;
    xEStop_NC       AT %IX0.2 : BOOL;
END_VAR
""",
        encoding="utf-8",
    )
    bad = tmp_path / "FB_Bad.st"
    bad.write_text(
        """\
FUNCTION_BLOCK FB_Bad
(* comment with GVL_IO.xLimitUp_NC must be ignored *)
xAtHome := NOT GVL_IO.xLimitUp_NC;  // undeclared
xOk    := GVL_IO.xLimitUp;
END_VAR
""",
        encoding="utf-8",
    )
    return tmp_path


def test_parse_gvl_declarations_reads_at_addresses(tmp_path: Path):
    path = tmp_path / "GVL_IO.st"
    path.write_text(
        "VAR_GLOBAL\n    xLimitUp AT %IX0.0 : BOOL;\n    rForce_N : REAL;\nEND_VAR\n",
        encoding="utf-8",
    )
    names = parse_gvl_declarations(path)
    assert names == {"xLimitUp", "rForce_N"}


def test_fixture_detects_undeclared_limitup_nc(fixture_dir: Path):
    problems = find_undeclared(fixture_dir)
    refs = [p[2] for p in problems]
    assert any("xLimitUp_NC" in r for r in refs)
    assert not any(r.endswith(".xLimitUp") and "UNDECLARED" in str(p) for p in problems for r in [p[2]])


def test_repo_codesys_has_no_undeclared_gvl_refs():
    """CI gate: live firmware/codesys tree must be clean."""
    assert CODESYS.is_dir(), f"missing {CODESYS}"
    decls = collect_declarations(CODESYS)
    assert "GVL_IO" in decls
    assert "xLimitUp" in decls["GVL_IO"]
    assert "xLimitUp_NC" not in decls["GVL_IO"]
    problems = find_undeclared(CODESYS)
    assert problems == [], f"undeclared GVL refs: {problems}"


def test_main_returns_nonzero_on_bad_tree(fixture_dir: Path):
    assert main([str(fixture_dir)]) == 1


def test_main_returns_zero_on_repo():
    assert main([str(CODESYS)]) == 0
