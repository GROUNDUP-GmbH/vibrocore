#!/usr/bin/env python3
"""
Static check: every GVL_*.var reference in CODESYS ST sources must be declared.

Parses firmware/codesys/*.st for:
  - Declarations inside VAR_GLOBAL ... END_VAR in GVL_*.st
  - References of the form GVL_NAME.identifier elsewhere

Exit codes:
  0 — all references resolve
  1 — one or more undeclared references (or parse/IO error)

Usage:
  python3 tests/check_st_gvl_refs.py
  python3 -m pytest tests/test_st_gvl_refs.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODESYS = ROOT / "firmware" / "codesys"

# VAR_GLOBAL body: capture declared identifiers (ignore AT %.. and types)
DECL_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:AT\s+%[A-Z0-9.]+\s*)?:\s*",
    re.MULTILINE,
)
# Reference: GVL_FOO.bar (not inside comments ideally — strip comments first)
REF_RE = re.compile(r"\b(GVL_[A-Za-z0-9_]+)\.([A-Za-z_][A-Za-z0-9_]*)\b")

COMMENT_BLOCK_RE = re.compile(r"\(\*.*?\*\)", re.DOTALL)
COMMENT_LINE_RE = re.compile(r"//.*?$", re.MULTILINE)


def strip_comments(text: str) -> str:
    text = COMMENT_BLOCK_RE.sub(" ", text)
    text = COMMENT_LINE_RE.sub(" ", text)
    return text


def parse_gvl_declarations(path: Path) -> set[str]:
    """Return set of variable names declared in a GVL_*.st file."""
    raw = path.read_text(encoding="utf-8")
    text = strip_comments(raw)
    names: set[str] = set()
    # Walk VAR_GLOBAL ... END_VAR blocks
    for block in re.finditer(
        r"VAR_GLOBAL(?:\s+CONSTANT)?\s+(.*?)\s*END_VAR",
        text,
        re.DOTALL | re.IGNORECASE,
    ):
        body = block.group(1)
        for match in DECL_RE.finditer(body):
            names.add(match.group(1))
    return names


def collect_declarations(codesys_dir: Path) -> dict[str, set[str]]:
    decls: dict[str, set[str]] = {}
    for path in sorted(codesys_dir.glob("GVL_*.st")):
        gvl_name = path.stem  # e.g. GVL_IO
        decls[gvl_name] = parse_gvl_declarations(path)
    return decls


def collect_references(codesys_dir: Path) -> list[tuple[Path, int, str, str]]:
    """Return list of (file, line, gvl_name, var_name)."""
    refs: list[tuple[Path, int, str, str]] = []
    for path in sorted(codesys_dir.glob("*.st")):
        raw = path.read_text(encoding="utf-8")
        # Strip comments per-line for line numbers that still match reasonably
        lines = raw.splitlines()
        in_block = False
        for lineno, line in enumerate(lines, start=1):
            work = line
            if in_block:
                end = work.find("*)")
                if end >= 0:
                    work = work[end + 2 :]
                    in_block = False
                else:
                    continue
            while True:
                start = work.find("(*")
                if start < 0:
                    break
                end = work.find("*)", start + 2)
                if end < 0:
                    work = work[:start]
                    in_block = True
                    break
                work = work[:start] + " " + work[end + 2 :]
            # Line comments
            if "//" in work:
                work = work[: work.index("//")]
            for match in REF_RE.finditer(work):
                refs.append((path, lineno, match.group(1), match.group(2)))
    return refs


def find_undeclared(
    codesys_dir: Path | None = None,
) -> list[tuple[str, int, str, str]]:
    codesys_dir = codesys_dir or CODESYS
    decls = collect_declarations(codesys_dir)
    problems: list[tuple[str, int, str, str]] = []
    for path, lineno, gvl, var in collect_references(codesys_dir):
        declared = decls.get(gvl)
        if declared is None:
            problems.append((str(path), lineno, gvl, var))
            continue
        if var not in declared:
            problems.append((str(path), lineno, f"{gvl}.{var}", "UNDECLARED"))
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    codesys = Path(argv[0]) if argv else CODESYS
    if not codesys.is_dir():
        print(f"ERROR: codesys directory not found: {codesys}", file=sys.stderr)
        return 1

    decls = collect_declarations(codesys)
    if not decls:
        print(f"ERROR: no GVL_*.st files in {codesys}", file=sys.stderr)
        return 1

    print("Declared GVL symbols:")
    for name, vars_ in decls.items():
        print(f"  {name}: {len(vars_)} symbols")

    problems = find_undeclared(codesys)
    if problems:
        print("\nUNDECLARED GVL references:", file=sys.stderr)
        for path, lineno, ref, _ in problems:
            print(f"  {path}:{lineno}: {ref}", file=sys.stderr)
        print(f"\n{len(problems)} undeclared reference(s)", file=sys.stderr)
        return 1

    print("OK — all GVL references are declared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
