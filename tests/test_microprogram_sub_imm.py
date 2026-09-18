import json
from pathlib import Path
from tools.control_store import addr, build

ROOT=Path(__file__).resolve().parents[1]
BITS=json.loads((ROOT/"spec/control-word.json").read_text())["bits"]

def has(word,*signals):
    return all(word & (1 << BITS[s]) for s in signals)

def test_sub_immediate_uses_twos_complement_alu_path():
    words=build(json.loads((ROOT/"microcode/control-store.json").read_text()))
    for c in range(4):
        assert has(words[addr(0x48,3,c)],"PC_TO_MAR")
        assert has(words[addr(0x48,4,c)],"MEM_READ","MDR_LOAD")
        assert has(words[addr(0x48,5,c)],"ALU_SUB","ALU_OUT_ENABLE","A_LOAD","FLAGS_LATCH","PC_INC")
        assert has(words[addr(0x48,6,c)],"INSTR_DONE","STEP_RESET")
