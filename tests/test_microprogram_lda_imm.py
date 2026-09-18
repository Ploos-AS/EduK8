import json
from pathlib import Path
from tools.control_store import addr, build

ROOT=Path(__file__).resolve().parents[1]
BITS=json.loads((ROOT/"spec/control-word.json").read_text())["bits"]

def has(word,*signals):
    return all(word & (1 << BITS[s]) for s in signals)

def test_lda_immediate_end_to_end_microprogram():
    src=json.loads((ROOT/"microcode/control-store.json").read_text())
    words=build(src)
    for c in range(4):
        assert has(words[addr(0x10,0,c)],"PC_TO_MAR")
        assert has(words[addr(0x10,1,c)],"MEM_READ","MDR_LOAD")
        assert has(words[addr(0x10,2,c)],"MDR_OUT","IR_LOAD","PC_INC")
        assert has(words[addr(0x10,3,c)],"PC_TO_MAR")
        assert has(words[addr(0x10,4,c)],"MEM_READ","MDR_LOAD")
        assert has(words[addr(0x10,5,c)],"MDR_OUT","A_LOAD","PC_INC")
        assert has(words[addr(0x10,6,c)],"FLAGS_LATCH","INSTR_DONE","STEP_RESET")
