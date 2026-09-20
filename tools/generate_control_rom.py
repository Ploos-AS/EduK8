#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from tools.control_word import encode, bytes_le
from tools.control_store import build_microcode

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
    words = build_microcode(MICROCODE)
    image = bytearray(IMAGE_SIZE)
    for logical, value in enumerate(words):
        pos = logical * WORD_BYTES
        image[pos:pos+WORD_BYTES] = bytes_le(value)
    return image

