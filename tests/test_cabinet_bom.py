"""Cabinet rows approved on 2026-11-20. Prices stay empty until a quote exists."""

from cad.tools.bom import load_bom

NEW_PARTS = (
    "VC-SH-1210",
    "VC-HB-3430",
    "VC-HB-3440",
    "VC-HB-3450",
    "VC-PW-5320",
    "VC-PW-5730",
    "VC-PW-5740",
    "VC-PW-5750",
    "VC-PW-5760",
    "VC-PW-5770",
    "VC-PW-5790",
    "VC-PW-5800",
    "VC-PW-5810",
    "VC-PW-5820",
    "VC-CT-6250",
    "VC-CT-6260",
    "VC-CT-6270",
    "VC-CT-6280",
    "VC-CT-6710",
    "VC-CT-6720",
    "VC-CT-6730",
    "VC-CT-6740",
    "VC-CT-6750",
    "VC-CT-6760",
    "VC-CT-6770",
    "VC-CT-6780",
    "VC-CT-6790",
    "VC-LT-9230",
)


def _qty(bom, assembly: str, part_number: str) -> float:
    return sum(line.qty for line in bom.children(assembly) if line.part_number == part_number)


def test_new_cabinet_parts_have_no_estimate():
    bom = load_bom()
    for number in NEW_PARTS:
        part = bom.part(number)
        assert part.estimate_eur_low is None, number
        assert part.estimate_eur_high is None, number


def test_named_hardware_is_on_the_agreed_bom():
    bom = load_bom()
    assert bom.part("VC-SH-1210").manufacturer_pn == "ATV320U15M2C"
    assert bom.part("VC-SH-1210").lifecycle == "active"
    assert _qty(bom, "VC-ASM-1000", "VC-SH-1210") == 1
    assert bom.part("VC-SH-1200").lifecycle == "superseded"
    assert bom.part("VC-SH-1200").superseded_by == "VC-SH-1210"
    assert _qty(bom, "VC-ASM-1000", "VC-SH-1200") == 0

    assert bom.part("VC-LT-9230").manufacturer_pn == "62.32.9.024.4000"
    assert _qty(bom, "VC-ASM-8200", "VC-LT-9230") == 2
    assert bom.part("VC-CT-6260").manufacturer_pn == "HE1B-M1"
    assert _qty(bom, "VC-ASM-5000", "VC-CT-6260") == 1
    assert bom.part("VC-HB-3430").manufacturer_pn == "2400.05.075.0"
    assert _qty(bom, "VC-ASM-2000", "VC-HB-3430") == 1
    assert bom.part("VC-CT-6220").manufacturer_pn == "750104"
    assert _qty(bom, "VC-ASM-5000", "VC-CT-6220") == 1

    assert bom.part("VC-CT-6280").lifecycle == "alternative"
    assert bom.part("VC-CT-6280").manufacturer_pn == "PD2-C4118L1804-E-01"
    assert _qty(bom, "VC-ASM-5000", "VC-CT-6280") == 0
    assert bom.part("VC-CT-6770").lifecycle == "alternative"
    assert _qty(bom, "VC-ASM-5000", "VC-CT-6770") == 0

    assert bom.part("VC-CT-6800").manufacturer_pn == "100378"
    assert bom.part("VC-CT-6800").lifecycle == "alternative"
    assert bom.part("VC-CT-6810").manufacturer_pn == "100197"
    assert bom.part("VC-CT-6810").lifecycle == "alternative"
    assert _qty(bom, "VC-ASM-5000", "VC-CT-6800") == 0
    assert _qty(bom, "VC-ASM-5000", "VC-CT-6810") == 0

    assert bom.part("VC-CT-6100").lifecycle == "active"
    assert bom.part("VC-CT-6100").manufacturer_pn == "750-8212/040-000"
    assert _qty(bom, "VC-ASM-5000", "VC-CT-6100") == 1

    assert _qty(bom, "VC-ASM-4000", "VC-PW-5310") == 1
    assert _qty(bom, "VC-ASM-4000", "VC-PW-5320") == 1
    assert _qty(bom, "VC-ASM-4000", "VC-PW-5200") == 0
    assert bom.part("VC-PW-5310").manufacturer_pn == "SDR-120-24"
    assert bom.part("VC-PW-5200").lifecycle == "obsolete"
    assert bom.part("VC-PW-5400").lifecycle == "obsolete"
