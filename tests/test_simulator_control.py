import pytest

from simulator.control import ControlError, apply_controls
from simulator.datapath import Datapath


def test_register_bus_transfer():
    dp = Datapath()
    dp.a.load(0x42)
    apply_controls(dp, ["A_OUT", "X_LOAD"])
    assert dp.x.value == 0x42
    assert dp.data_bus.driver == "A_OUT"


def test_pc_to_mar_is_direct_16_bit_path():
    dp = Datapath()
    dp.pc.load(0x8123)
    apply_controls(dp, ["PC_TO_MAR"])
    assert dp.mar.value == 0x8123
    assert dp.data_bus.value is None


def test_stack_address_transfer_uses_page_one():
    dp = Datapath()
    dp.sp.load(0xA5)
    apply_controls(dp, ["SP_TO_MAR"])
    assert dp.mar.value == 0x01A5


def test_pc_increment_wraps():
    dp = Datapath()
    dp.pc.load(0xFFFF)
    apply_controls(dp, ["PC_INC"])
    assert dp.pc.value == 0


def test_direct_flag_controls():
    dp = Datapath()
    apply_controls(dp, ["C_SET", "I_SET"])
    assert dp.flags.value & 0x11 == 0x11
    apply_controls(dp, ["C_CLEAR", "I_CLEAR"])
    assert dp.flags.value & 0x11 == 0


def test_load_without_bus_source_is_rejected():
    dp = Datapath()
    with pytest.raises(ControlError):
        apply_controls(dp, ["A_LOAD"])


def test_canonical_validator_rejects_bus_contention():
    dp = Datapath()
    with pytest.raises(ValueError, match="multiple DB sources"):
        apply_controls(dp, ["A_OUT", "X_OUT"])


def test_alu_result_can_drive_bus_and_load_register():
    dp = Datapath()
    dp.a.load(2)
    dp.tmp.load(3)
    apply_controls(dp, ["ALU_ADD", "ALU_OUT_ENABLE", "Y_LOAD"])
    assert dp.y.value == 5
    assert dp.data_bus.driver == "ALU_OUT_ENABLE"
