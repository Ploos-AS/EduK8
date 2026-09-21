from simulator.datapath import Datapath
from simulator.view import observable, render_text


def test_observable_exposes_flags_bus_alu_and_controls():
    dp = Datapath()
    dp.a.load(0x42)
    dp.pc.load(0x8123)
    dp.flags.load(0x15)
    dp.data_bus.drive("A", 0x42)
    dp.alu.a, dp.alu.b, dp.alu.result = 0x40, 0x02, 0x42
    dp.microstep = 7
    dp.clock = 12
    dp.active_controls = ("A_OUT", "TMP_LOAD")

    view = observable(dp.snapshot())
    assert view["flags"] == {"C": True, "Z": False, "N": True, "V": False, "I": True, "B": False}
    assert view["bus"] == {"DB": 0x42, "driver": "A"}
    assert view["alu"]["result"] == 0x42
    assert view["active_controls"] == ["A_OUT", "TMP_LOAD"]


def test_text_view_is_deterministic_and_human_readable():
    dp = Datapath()
    dp.a.load(0x42)
    dp.pc.load(0x8123)
    text = render_text(dp.snapshot())
    assert "A=42" in text
    assert "PC=8123" in text
    assert "DB=-- DRIVER=-" in text
    assert text.endswith("\n")
