#!/usr/bin/env python3
"""Small, deliberately readable two-pass K8 assembler."""
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ISA=json.loads((ROOT/"spec/isa.json").read_text())["instructions"]
OPS={(m,mode):(int(op,16),size) for op,m,mode,size in ISA}

def number(s, symbols):
    s=s.strip()
    if s in symbols: return symbols[s]
    if s.startswith("$"): return int(s[1:],16)
    if s.startswith("%"): return int(s[1:],2)
    return int(s,0)

def values(s): return [x.strip() for x in s.split(",") if x.strip()]

def mode_for(mnemonic, operand, symbols=None):
    symbols=symbols or {}
    if not operand:return "imp"
    if operand.startswith("#"):return "imm"
    if mnemonic.startswith("B") and mnemonic not in ("BRK","BIT"):return "rel"
    if mnemonic in ("JMP","JSR"):return "abs"
    if operand.startswith("("):return "(abs)" if mnemonic=="JMP" else "(zp)"
    suffix=""; base=operand
    if operand.upper().endswith(",X"):base=operand[:-2];suffix=",X"
    elif operand.upper().endswith(",Y"):base=operand[:-2];suffix=",Y"
    b=base.strip()
    if (b.startswith("$") and len(b)<=3) or (b in symbols and symbols[b]<=0xff):return "zp"+suffix
    return "abs"+suffix

def assemble(source, origin=0, image=False):
    records=[]; labels={}; constants={}; pc=origin; first_origin=origin
    for raw in source.splitlines():
        line=raw.split(";",1)[0].strip()
        if not line:continue
        equ=re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s+(?:=|\.equ\s+)\s*(.+)$",line,re.I)
        if equ:
            n,v=equ.groups();constants[n]=number(v,{**constants,**labels});continue
        if ":" in line:
            label,line=line.split(":",1);labels[label.strip()]=pc;line=line.strip()
            if not line:continue
        parts=line.split(None,1); m=parts[0].upper(); operand=parts[1].strip() if len(parts)>1 else ""
        if m==".ORG":
            pc=number(operand,{**constants,**labels})
            if not records:first_origin=pc
            records.append(("org",pc,None));continue
        if m in (".BYTE",".WORD"):
            size=len(values(operand))*(1 if m==".BYTE" else 2)
            records.append((m.lower(),pc,operand));pc+=size;continue
        mode=mode_for(m,operand,{**constants,**labels})
        if (m,mode) not in OPS:raise ValueError(f"unsupported instruction: {m} {operand} ({mode})")
        op,size=OPS[(m,mode)];records.append(("ins",pc,(m,operand,mode,op,size)));pc+=size
    segments=[]; current=bytearray(); addr=first_origin
    def flush():
        nonlocal current
        if current:segments.append((addr-len(current),bytes(current)));current=bytearray()
    for kind,at,data in records:
        if kind=="org":
            flush();addr=at;continue
        if not current:addr=at
        if kind in (".byte",".word"):
            for item in values(data):
                v=number(item,{**constants,**labels});current.append(v&0xff);addr+=1
                if kind==".word":current.append((v>>8)&0xff);addr+=1
            continue
        m,operand,mode,op,size=data;current.append(op);addr+=1
        if size>1:
            text=re.sub(r",[XYxy]$","",operand.replace("#","").replace("(","").replace(")","")).strip()
            v=number(text,{**constants,**labels})
            if mode=="rel":v=(v-(at+2))&0xff
            current.append(v&0xff);addr+=1
            if size==3:current.append((v>>8)&0xff);addr+=1
    flush()
    if not image:
        if len(segments)>1: raise ValueError("multiple .org segments require image=True")
        return segments[0][1] if segments else b""
    rom=bytearray(65536)
    for start,data in segments:rom[start:start+len(data)]=data
    return bytes(rom)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("source");p.add_argument("-o","--output",required=True)
    p.add_argument("--origin",default="0");p.add_argument("--image",action="store_true")
    a=p.parse_args();Path(a.output).write_bytes(assemble(Path(a.source).read_text(),int(a.origin,0),a.image))
