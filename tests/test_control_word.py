import pytest
from tools.control_word import encode

def test_encode_single_signal():
    assert encode(["A_OUT"]) == 1

def test_encode_multiple_signals():
    assert encode(["A_OUT","A_IN"]) == 3

def test_reject_multiple_bus_drivers():
    with pytest.raises(ValueError, match="multiple DB sources"):
        encode(["A_OUT","X_OUT"])

def test_reject_memory_conflict():
    with pytest.raises(ValueError, match="MEM_READ and MEM_WRITE"):
        encode(["MEM_READ","MEM_WRITE"])

def test_reject_alu_conflict():
    with pytest.raises(ValueError, match="multiple ALU"):
        encode(["ALU_ADD","ALU_SUB"])

def test_reject_unknown_signal():
    with pytest.raises(ValueError, match="unknown"):
        encode(["MAGIC"])
