#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "spec/control-word.json").read_text())
BITS = SPEC["bits"]
WIDTH = SPEC["width_bits"]

DB_SOURCES = {"A_OUT","X_OUT","Y_OUT","SP_OUT","MDR_OUT","TMP_OUT","ALU_OUT_ENABLE"}
ALU = {"ALU_ADD","ALU_SUB","ALU_AND","ALU_OR","ALU_XOR","ALU_NOT","ALU_SHL","ALU_SHR","ALU_ROL","ALU_ROR"}
AGU = {"AGU_ADD_LO","AGU_ADD_HI"}

def encode(signals):
    signals = set(signals)
    unknown = signals - set(BITS)
    if unknown:
        raise ValueError("unknown signals: " + ", ".join(sorted(unknown)))
    if len(signals & DB_SOURCES) > 1:
        raise ValueError("multiple DB sources: " + ", ".join(sorted(signals & DB_SOURCES)))
    if {"MEM_READ","MEM_WRITE"} <= signals:
        raise ValueError("MEM_READ and MEM_WRITE conflict")
    if len(signals & ALU) > 1:
        raise ValueError("multiple ALU operations")
    if len(signals & AGU) > 1:
        raise ValueError("multiple AGU phases")
    if "HALT" in signals and len(signals - {"HALT","INSTR_DONE"}) > 0:
        raise ValueError("HALT conflicts with active controls")
    value = 0
    for signal in signals:
        value |= 1 << BITS[signal]
    return value

def bytes_le(value):
    return value.to_bytes(SPEC["storage_bytes"], "little")

def describe(signals):
    value = encode(signals)
    return {"signals": list(signals), "hex": f"{value:012X}", "bytes_le": bytes_le(value).hex()}

if __name__ == "__main__":
    examples = {
        "fetch_t0": ["PC_TO_MAR"],
        "fetch_t1": ["MEM_READ","MDR_LOAD"],
        "fetch_t2": ["MDR_OUT","IR_LOAD","PC_INC"],
        "halt": ["HALT"],
    }
    for name, signals in examples.items():
        print(name, json.dumps(describe(signals), sort_keys=True))
