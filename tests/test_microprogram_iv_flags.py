import json
from pathlib import Path
from tools.control_store import addr, build
ROOT=Path(__file__).resolve().parents[1]
BITS=json.loads((ROOT/"spec/control-word.json").read_text())["bits"]
def has(w,*ss): return all(w & (1<<BITS[s]) for s in ss)
def test_direct_i_v_controls():
    words=build(json.loads((ROOT/"microcode/control-store.json").read_text()))
    for c in range(4):
        assert has(words[addr(0x07,3,c)],"I_CLEAR","INSTR_DONE","STEP_RESET")
        assert has(words[addr(0x08,3,c)],"I_SET","INSTR_DONE","STEP_RESET")
        assert has(words[addr(0x09,3,c)],"V_CLEAR","INSTR_DONE","STEP_RESET")
