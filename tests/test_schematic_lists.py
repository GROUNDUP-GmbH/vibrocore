"""The cabinet schematic stays aligned with the I/O list and the generator."""

import csv
import subprocess
import sys
from pathlib import Path

from cad.tools.bom import ROOT

SCH = ROOT / "cad" / "kicad" / "vibrocore-control"
EXPORT = ROOT / "cad" / "export" / "kicad"

IO_NETS = (
    "460_LIM_UP",
    "461_LIM_DN",
    "420_ESTOP",
    "421_PNOZ",
    "440_S200FB",
    "452_SONSTO",
    "462_ENABLE",
    "470_TILT_V",
    "471_TILT_F",
    "472_LIFT_D",
    "473_LIFT_R",
    "451_FAULT",
    "480_INDEX",
    "490_EXT",
    "491_RET",
    "492_TILTV",
    "493_TILTF",
    "494_BEACON",
    "450_RESET",
    "495_ROT_EN",
    "431_STO1",
    "433_STO2",
    "201_24S",
    "211_24C",
    "001_0V",
)


def _rows(name: str) -> list[dict[str, str]]:
    with (EXPORT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_schematic_matches_the_generator():
    script = SCH / "generate_schematic.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_io_channels_and_sto_are_on_the_drawing():
    text = "\n".join(path.read_text(encoding="utf-8") for path in SCH.glob("*.kicad_sch"))
    for net in IO_NETS:
        assert f'"{net}"' in text, net
    assert "750-8212" not in text
    assert "ATV320" in text
    assert "100378" in text


def test_terminal_strips_and_cables():
    terminals = _rows("terminal-list.csv")
    strips = {row["strip"] for row in terminals}
    assert strips == {f"X{index}" for index in range(1, 11)}
    wires = {row["wire"] for row in terminals}
    assert {"100_L", "610_UA", "622_WB", "540_U", "480_INDEX", "498_ACT_A", "500_24R"} <= wires
    cables = {row["cable"]: row for row in _rows("cable-list.csv")}
    assert cables["W-SON-B"]["part"] == "VC-SH-1700"
    assert cables["W-CHAIN"]["part"] == "VC-HB-3430"
    assert cables["W-ROT"]["part"] == "VC-CT-6770"
    assert (EXPORT / "terminal-list.md").is_file()
    assert (EXPORT / "cable-list.md").is_file()


def test_erc_report_and_pdf():
    report = (EXPORT / "erc-report.txt").read_text(encoding="utf-8")
    assert "Errors 0" in report
    assert "Warnings 0" in report
    pdf = EXPORT / "vibrocore-control.pdf"
    assert pdf.is_file()
    assert pdf.stat().st_size > 10_000
