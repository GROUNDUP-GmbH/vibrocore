"""Enclosure layout, obsolete 48 V rail, and the sealed heat check."""

from cad.models.electronics_enclosure import (
    HEAT_W,
    heat_total_w,
    internal_c,
    layout_items,
    passive_watts,
    rack_width_mm,
    validate_layout,
)
from cad.tools.bom import load_bom


def test_no_48v_parts_on_a_live_bom():
    bom = load_bom()
    assert bom.part("VC-PW-5200").lifecycle == "obsolete"
    assert bom.part("VC-PW-5400").lifecycle == "obsolete"
    live = set()
    for assembly in bom.assemblies:
        live.update(line.part_number for line in bom.children(assembly))
    assert "VC-PW-5200" not in live
    assert "VC-PW-5400" not in live
    assert "VC-HB-3410" not in live
    assert "VC-CT-6130" not in live
    power = {line.part_number for line in bom.children("VC-ASM-4000")}
    assert power >= {"VC-PW-5310", "VC-PW-5320"}
    assert bom.part("VC-PW-5320").estimate_eur_low is None
    assert bom.part("VC-PW-5310").manufacturer_pn == "SDR-120-24"
    assert "2.2 A" in bom.part("VC-PW-5310").spec
    assert bom.part("VC-CT-6220").manufacturer_pn == "750104"
    assert "two NC" in bom.part("VC-CT-6210").spec
    assert "STO" in bom.part("VC-SH-1200").spec


def test_heat_check_drops_the_48v_supply():
    closed = heat_total_w(include_machine_psu=False)
    ceiling = heat_total_w(include_machine_psu=True)
    assert "sdr480_nameplate" not in HEAT_W
    assert "dc_converters" not in HEAT_W
    assert HEAT_W["sdr120_dedicated"] == 11.9
    assert HEAT_W["machine_sdr480_24_nameplate"] == 30.6
    assert HEAT_W["safety_relay"] == 2.5
    assert abs(closed - 118.7) < 1e-9
    assert abs(ceiling - closed - 30.6) < 1e-9
    assert internal_c(closed) < 50.0
    assert internal_c(ceiling) > 50.0
    assert closed < passive_watts(10) < ceiling


def test_layout_reserves_the_open_slots():
    validate_layout()
    names = {item.name for item in layout_items()}
    assert "VC-PW-5310" in names
    assert "VC-PW-5320-PLACEHOLDER" in names
    assert "VC-CT-6220-RESERVE" in names
    assert "VC-SH-1200-STO" in names
    assert "VC-PW-5200-PLACEHOLDER" not in names
    assert "VC-PW-5400" not in names
    assert not any("chain" in name.lower() for name in names)
    relay = next(item for item in layout_items() if item.name == "VC-CT-6220-RESERVE")
    assert relay.sx == 22.5
    assert relay.sz == 98.0
    slot = next(item for item in layout_items() if item.name == "VC-PW-5320-PLACEHOLDER")
    assert slot.sx == 85.5
    assert rack_width_mm() == 150.6
