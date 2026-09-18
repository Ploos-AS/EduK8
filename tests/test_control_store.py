import json, tempfile
from pathlib import Path
import pytest
from tools.control_store import addr, build, validate

def test_address_layout():
    assert addr(0x12,31,3)==(0x12<<7)|(31<<2)|3

def test_rejects_bus_contention():
    with pytest.raises(ValueError): validate(["A_OUT","X_OUT"])

def test_rejects_read_write():
    with pytest.raises(ValueError): validate(["MEM_READ","MEM_WRITE"])

def test_rejects_multiple_alu_ops():
    with pytest.raises(ValueError): validate(["ALU_ADD","ALU_SUB"])

def test_safe_unpopulated_words():
    words=build({"entries":[]})
    assert len(words)==32768 and not any(words)
