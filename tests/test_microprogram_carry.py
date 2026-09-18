import json
from pathlib import Path
from tools.control_store import addr, build

ROOT=Path(__file__).resolve().parents[1]
BITS=json.loads((ROOT/"spec/control-word.json").read_text())["bits"]

def has(w,*ss): return all(w & (1<<BITS[s]) for s in ss)

def test_clc_sec_direct_c_latch_controls():
    words=build(json.loads((ROOT/"microcode/control-store.json").read_text()))
    for cond in range(4):
        assert has(words[addr(0x05,3,cond)],"C_CLEAR","INSTR_DONE","STEP_RESET")
        assert has(words[addr(0x06,3,cond)],"C_SET","INSTR_DONE","STEP_RESET")
