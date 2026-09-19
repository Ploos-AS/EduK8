import pytest

from simulator.datapath import ALU, Bus8, Datapath, Register8, Register16


def test_register_widths_and_partial_loads():
    r8 = Register8("R")
    r8.load(0x1AB)
    assert r8.output() == 0xAB

    r16 = Register16("R16", 0x1234)
    r16.load_low(0xAA)
    assert r16.output() == 0x12AA
    r16.load_high(0xBB)
    assert r16.output() == 0xBBAA


def test_bus_detects_multiple_drivers():
    bus = Bus8("DB")
    bus.drive("A", 0x12)
    with pytest.raises(ValueError, match="contention"):
        bus.drive("X", 0x34)
    bus.clear()
    bus.drive("X", 0x134)
    assert (bus.driver, bus.value) == ("X", 0x34)


def test_alu_basic_operations():
    alu = ALU(a=0x7F, b=0x01)
    assert alu.evaluate("ADD") == 0x80
    assert alu.overflow == 1

    alu.a, alu.b = 0xF0, 0x0F
    assert alu.evaluate("AND") == 0x00
    assert alu.evaluate("OR") == 0xFF
    assert alu.evaluate("XOR") == 0xFF


def test_datapath_snapshot_is_explicit_and_deterministic():
    dp = Datapath()
    dp.a.load(0x42)
    dp.pc.load(0x8000)
    dp.data_bus.drive("A", dp.a.output())
    dp.active_controls = ("A_OUT",)
    snap = dp.snapshot()

    assert snap["registers"]["A"] == 0x42
    assert snap["registers"]["PC"] == 0x8000
    assert snap["bus"] == {"DB": 0x42, "driver": "A"}
    assert snap["active_controls"] == ["A_OUT"]

    dp.begin_cycle()
    assert dp.data_bus.value is None
    assert dp.active_controls == ()
