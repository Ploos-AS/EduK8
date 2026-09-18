#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ISA=json.loads((ROOT/"spec/isa.json").read_text())
MICRO=json.loads((ROOT/"spec/microcode.json").read_text())

def report():
    defined={row[0] for row in ISA["instructions"]}
    implemented=set(MICRO["opcodes"])
    return {
        "defined":len(defined),
        "microcoded":len(defined & implemented),
        "missing":sorted(defined-implemented),
        "unknown":sorted(implemented-defined),
    }

def main():
    r=report()
    print(f'defined={r["defined"]} microcoded={r["microcoded"]}')
    if r["missing"]: print("missing:", " ".join(r["missing"]))
    if r["unknown"]: print("unknown:", " ".join(r["unknown"]))
    raise SystemExit(1 if r["missing"] or r["unknown"] else 0)

if __name__=="__main__":
    main()
