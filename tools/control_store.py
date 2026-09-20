#!/usr/bin/env python3
"""Generate and statically validate the six K8 Classic control-store slices."""
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/"spec/control-word.json").read_text())
BITS=SPEC["bits"]; DEPTH=1 << (SPEC["address"]["opcode_bits"]+SPEC["address"]["microstep_bits"]+SPEC["address"]["condition_bits"])
SAFE=0
BUS={"A_OUT","X_OUT","Y_OUT","SP_OUT","MDR_OUT","TMP_OUT","ALU_OUT_ENABLE"}
ALU={"ALU_ADD","ALU_SUB","ALU_AND","ALU_OR","ALU_XOR","ALU_NOT","ALU_SHL","ALU_SHR","ALU_ROL","ALU_ROR"}

def word(signals):
    unknown=set(signals)-set(BITS)
    if unknown: raise ValueError(f"unknown control signals: {sorted(unknown)}")
    return sum(1<<BITS[x] for x in signals)

def validate(signals, context=""):
    s=set(signals)
    errs=[]
    if len(s & BUS)>1: errs.append(f"multiple DB sources: {sorted(s & BUS)}")
    if {"MEM_READ","MEM_WRITE"} <= s: errs.append("MEM_READ and MEM_WRITE together")
    if len(s & ALU)>1: errs.append(f"multiple ALU operations: {sorted(s & ALU)}")
    if "INSTR_DONE" in s and "STEP_RESET" not in s: errs.append("INSTR_DONE without STEP_RESET")
    if any(BITS[x] in SPEC["reserved"] for x in s): errs.append("reserved control bit used")
    if errs: raise ValueError(f"{context}: " + "; ".join(errs))
    return word(s)

def addr(opcode, step, cond):
    if not 0<=opcode<256 or not 0<=step<32 or not 0<=cond<4: raise ValueError("microaddress field out of range")
    return (opcode << 7) | (step << 2) | cond

def source_entries(microcode):
    """Expand shared fetch + opcode execution into condition-specific rows."""
    rows=[]
    for opcode_hex, execution in microcode.get("opcodes",{}).items():
        opcode=int(opcode_hex,16)
        seen=set()
        for entry in microcode.get("fetch",[]) + execution:
            step=entry["step"]
            if step in seen: raise ValueError(f"duplicate step {step} for opcode {opcode_hex}")
            seen.add(step)
            for cond in range(4):
                rows.append({"opcode":opcode,"step":step,"condition":cond,"signals":entry.get("signals",[])})
    return {"entries":rows}

def build_microcode(microcode):
    return build(source_entries(microcode))

def build(source):
    words=[SAFE]*DEPTH
    seen=set()
    for row in source.get("entries",[]):
        op=int(row["opcode"],0) if isinstance(row["opcode"],str) else row["opcode"]
        step=row["step"]; cond=row.get("condition",0)
        a=addr(op,step,cond)
        if a in seen: raise ValueError(f"duplicate microaddress {a:#06x}")
        seen.add(a); words[a]=validate(row.get("signals",[]),f"opcode={op:#04x} T{step} C{cond}")
    return words

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("source",type=Path); ap.add_argument("-o","--output",type=Path,default=ROOT/"build/control-store")
    ns=ap.parse_args(); src=json.loads(ns.source.read_text()); words=build(src)
    ns.output.mkdir(parents=True,exist_ok=True)
    for sl in range(6):
        (ns.output/f"control-{sl}.bin").write_bytes(bytes((w>>(8*sl))&0xff for w in words))
    print(f"PASS: {len(words)} words, 6 x {len(words)}-byte slices")

if __name__=="__main__": main()
