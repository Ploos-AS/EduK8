#!/usr/bin/env python3
"""Small, deliberately readable two-pass K8 assembler."""
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ISA=json.loads((ROOT/"spec/isa.json").read_text())["instructions"]
OPS={(m,mode):(int(op,16),size) for op,m,mode,size in ISA}

def number(s, labels):
    s=s.strip()
    if s in labels: return labels[s]
    if s.startswith("$"): return int(s[1:],16)
    if s.startswith("%"): return int(s[1:],2)
    return int(s,0)

def mode_for(mnemonic, operand, symbols=None):
    symbols = symbols or {}

    if not operand: return "imp"
    if operand.startswith("#"): return "imm"
    if mnemonic.startswith("B") and mnemonic not in ("BRK","BIT"): return "rel"
    if operand.startswith("("):
        return "(abs)" if mnemonic=="JMP" else "(zp)"
    suffix=""
    base=operand
    if operand.upper().endswith(",X"): base=operand[:-2]; suffix=",X"
    elif operand.upper().endswith(",Y"): base=operand[:-2]; suffix=",Y"
    b=base.strip()
    if (b.startswith("$") and len(b)<=3) or (b in symbols and symbols[b] <= 0xFF): return "zp"+suffix
    return "abs"+suffix

def assemble(source, origin=0):
    lines=[]
    labels={}
    constants={}
    pc=origin
    for raw in source.splitlines():
        line=raw.split(";",1)[0].strip()
        if not line: continue
        equ=re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\\s+(?:=|\\.equ\\s+)\\s*(.+)$", line, re.I)
        if equ:
            name, value=equ.groups()
            constants[name]=number(value, {**constants, **labels})
            continue
        if ":" in line:
            label, line=line.split(":",1)
            labels[label.strip()]=pc
            line=line.strip()
            if not line: continue
        parts=line.split(None,1); m=parts[0].upper(); operand=parts[1].strip() if len(parts)>1 else ""
        mode=mode_for(m,operand,{**constants, **labels})
        if (m,mode) not in OPS: raise ValueError(f"unsupported instruction: {m} {operand} ({mode})")
        op,size=OPS[(m,mode)]; lines.append((pc,m,operand,mode,op,size)); pc+=size
    out=bytearray()
    for pc,m,operand,mode,op,size in lines:
        out.append(op)
        if size==1: continue
        text=operand.replace("#","").replace("(","").replace(")","")
        text=re.sub(r",[XYxy]$","",text).strip()
        value=number(text,{**constants, **labels})
        if mode=="rel": value=(value-(pc+2)) & 0xff
        out.append(value & 0xff)
        if size==3: out.append((value>>8)&0xff)
    return bytes(out)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("source"); p.add_argument("-o","--output",required=True)
    p.add_argument("--origin",default="0")
    a=p.parse_args()
    src=Path(a.source).read_text()
    Path(a.output).write_bytes(assemble(src,int(a.origin,0)))
