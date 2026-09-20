#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from tools.control_word import encode, bytes_le

ROOT = Path(__file__).resolve().parents[1]
CONTROL = json.loads((ROOT / "spec/control-word.json").read_text())
MICROCODE = json.loads((ROOT / "spec/microcode.json").read_text())

OPCODES = 256
STEPS = 1 << CONTROL["address"]["microstep_bits"]
CONDITIONS = 4
WORD_BYTES = CONTROL["storage_bytes"]
LOGICAL_WORDS = 1 << CONTROL["address"]["total_bits"]
IMAGE_SIZE = LOGICAL_WORDS * WORD_BYTES

def address(opcode, step, condition=0):
    if not 0 <= opcode < OPCODES: raise ValueError("opcode out of range")
    if not 0 <= step < STEPS: raise ValueError("microstep out of range")
    if not 0 <= condition < CONDITIONS: raise ValueError("condition page out of range")
    logical = (opcode << 7) | (step << 2) | condition
    return logical * WORD_BYTES

def build_image():
    image = bytearray(IMAGE_SIZE)
    fetch = MICROCODE["fetch"]
    for opcode_hex, execution in MICROCODE["opcodes"].items():
        opcode = int(opcode_hex, 16)
        seen = set()
        for entry in fetch + execution:
            step = entry["step"]
            if step in seen: raise ValueError(f"duplicate step {step} for opcode {opcode_hex}")
            seen.add(step)
            value = encode(entry["signals"])
            for condition in range(CONDITIONS):
                pos = address(opcode, step, condition)
                image[pos:pos+WORD_BYTES] = bytes_le(value)
    return image

def manifest():
    rows = []
    for opcode_hex, execution in MICROCODE["opcodes"].items():
        opcode = int(opcode_hex, 16)
        for entry in MICROCODE["fetch"] + execution:
            rows.append({"opcode": opcode_hex, "step": entry["step"],
                         "signals": entry["signals"],
                         "control_word": f'{encode(entry["signals"]):012X}',
                         "byte_offset_condition0": address(opcode, entry["step"])})
    return {"format":1,"word_bytes":WORD_BYTES,"logical_words":LOGICAL_WORDS,
            "image_bytes":IMAGE_SIZE,"entries":rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default=str(ROOT/"build/k8-control.bin"))
    p.add_argument("--manifest",default=str(ROOT/"build/k8-control.json"))
    args=p.parse_args()
    out=Path(args.output); man=Path(args.manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(build_image())
    man.write_text(json.dumps(manifest(),indent=2)+"\n")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    print(f"wrote {man}")

if __name__=="__main__":
    main()
