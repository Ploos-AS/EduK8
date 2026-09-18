import json
from pathlib import Path
from tools.control_store import addr, build

ROOT=Path(__file__).resolve().parents[1]

def test_nop_and_halt_microprograms_are_condition_independent():
    src=json.loads((ROOT/"microcode/control-store.json").read_text())
    words=build(src)
    for cond in range(4):
        assert words[addr(0x00,0,cond)] != 0
        assert words[addr(0x00,3,cond)] != 0
        assert words[addr(0x01,0,cond)] != 0
        assert words[addr(0x01,3,cond)] != 0

def test_unimplemented_opcode_remains_safe():
    src=json.loads((ROOT/"microcode/control-store.json").read_text())
    words=build(src)
    for cond in range(4):
        for step in range(32):
            assert words[addr(0xFF,step,cond)] == 0
