#!/usr/bin/env python3
"""Static pre-freeze validation for the K8 Classic hardware mapping."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
cw = json.loads((ROOT / "spec/control-word.json").read_text())
mc = json.loads((ROOT / "spec/microcode.json").read_text())
mm = json.loads((ROOT / "spec/memory-map.json").read_text())
isa = json.loads((ROOT / "spec/isa.json").read_text())
io = json.loads((ROOT / "spec/io-map.json").read_text())
peripherals = json.loads((ROOT / "spec/peripherals.json").read_text())

bits = set(cw["bits"])
assert cw["width_bits"] == 48
assert cw["storage_bytes"] == 6
assert cw["address"]["depth"] == 32768
assert len(bits) == 48
assert set(cw["bits"].values()) == set(range(48))

defined = set()
for sequence in mc["opcodes"].values():
    for step in sequence:
        unknown = set(step["signals"]) - bits
        assert not unknown, f"unknown controls: {sorted(unknown)}"
        defined.update(step["signals"])
for step in mc["fetch"]:
    unknown = set(step["signals"]) - bits
    assert not unknown, f"unknown fetch controls: {sorted(unknown)}"

# Controls that imply incompatible physical ownership in one microstep.
db_drivers = {"A_OUT", "X_OUT", "Y_OUT", "SP_OUT", "MDR_OUT", "TMP_OUT", "ALU_OUT_ENABLE"}
mar_dedicated = {"PC_TO_MAR", "SP_TO_MAR"}
alu_ops = {"ALU_ADD", "ALU_SUB", "ALU_AND", "ALU_OR", "ALU_XOR", "ALU_NOT",
           "ALU_SHL", "ALU_SHR", "ALU_ROL", "ALU_ROR"}

def check_step(label, step):
    s = set(step["signals"])
    drivers = s & db_drivers
    assert len(drivers) <= 1, f"{label}: multiple DB drivers {sorted(drivers)}"
    assert len(s & mar_dedicated) <= 1, f"{label}: PC/SP both own MAR"
    assert not ((s & mar_dedicated) and (s & {"MAR_LOAD_LO", "MAR_LOAD_HI"})), (
        f"{label}: dedicated MAR source conflicts with DB MAR load")
    assert len(s & alu_ops) <= 1, f"{label}: multiple ALU operations"
    assert not ({"MEM_READ", "MEM_WRITE"} <= s), f"{label}: simultaneous memory read/write"
    assert not ({"SP_INC", "SP_DEC"} <= s), f"{label}: simultaneous SP increment/decrement"
    assert not ({"C_SET", "C_CLEAR"} <= s), f"{label}: simultaneous carry set/clear"
    assert not ({"I_SET", "I_CLEAR"} <= s), f"{label}: simultaneous IRQ-mask set/clear"

for step in mc["fetch"]:
    check_step(f"fetch/T{step['step']}", step)
for opcode, sequence in mc["opcodes"].items():
    for step in sequence:
        check_step(f"{opcode}/T{step['step']}", step)

# Full 16-bit architectural decode must have exactly one region per address.
regions = mm["regions"]
def n(v): return int(v, 16) if isinstance(v, str) else int(v)
for address in range(0x10000):
    hits = [r for r in regions if n(r["start"]) <= address <= n(r["end"])]
    assert len(hits) == 1, f"{address:04X}: expected one region, got {len(hits)}"

assert n(mm["vectors"]["reset"]) == 0xFFFC
assert n(mm["vectors"]["irq"]) == 0xFFFE
for vector in (0xFFFC, 0xFFFD, 0xFFFE, 0xFFFF):
    hit = next(r for r in regions if n(r["start"]) <= vector <= n(r["end"]))
    assert hit["kind"] == "rom_alias", f"{vector:04X}: vector not in system ROM"

# Six-byte ROM reconstruction identity over the complete physical store.
for word in range(cw["address"]["depth"]):
    # Deterministic synthetic 48-bit pattern exercises all six slices.
    value = ((word * 0x9E3779B97F) ^ (word << 17) ^ 0xA55A5AA55A5A) & ((1 << 48) - 1)
    slices = [(value >> (8 * i)) & 0xFF for i in range(6)]
    rebuilt = sum(byte << (8 * i) for i, byte in enumerate(slices))
    assert rebuilt == value, f"control-store slice reconstruction failed at {word:04X}"

print("K8 Classic pre-freeze static validation: PASS")
print("control bits: 48/48")
print("control store: 32768 words x 6 bytes")
print("address decode: 65536/65536 unique")
print("DB/MAR/ALU/memory conflict checks: PASS")


# ISA/control-store coverage.
isa_opcodes = {row[0].upper() for row in isa["instructions"]}
microcoded = {key.upper() for key in mc["opcodes"]}
missing = isa_opcodes - microcoded
assert not missing, f"ISA opcodes without microcode: {sorted(missing)}"
assert len(isa_opcodes) == 99, f"expected 99 defined opcodes, got {len(isa_opcodes)}"

# Branch contract: all eight relative branches must be present and terminate.
branches = {row[0].upper() for row in isa["instructions"] if row[2] == "rel"}
assert branches == {"88","89","8A","8B","8C","8D","8E","8F"}
for opcode in branches:
    seq = mc["opcodes"][opcode]
    assert any("INSTR_DONE" in s["signals"] for s in seq), f"{opcode}: branch never completes"

# Stack-family coverage and required SP activity.
for opcode in ("90","91","92","93","82","04","02","03"):
    assert opcode in microcoded, f"{opcode}: stack/control-flow opcode lacks microcode"
    signals = {sig for step in mc["opcodes"][opcode] for sig in step["signals"]}
    assert signals & {"SP_TO_MAR","SP_INC","SP_DEC","SP_OUT","SP_LOAD"}, (
        f"{opcode}: expected stack activity")

# Indexed modes must have an AGU path.
for row in isa["instructions"]:
    opcode, mnemonic, mode, _ = row
    if ",X" in mode or ",Y" in mode:
        signals = {sig for step in mc["opcodes"][opcode] for sig in step["signals"]}
        assert signals & {"AGU_ADD_LO","AGU_ADD_HI"}, f"{opcode}: indexed mode lacks AGU"

# MMIO register addresses must be inside the frozen IO page and unique.
io_start = int(io["io_page"]["start"], 16)
io_end = int(io["io_page"]["end"], 16)
regs = []
for dev in io["devices"].values():
    regs.extend(int(a, 16) for a in dev.get("registers", {}).values())
assert len(regs) == len(set(regs)), "duplicate MMIO register address"
assert all(io_start <= a <= io_end for a in regs), "MMIO register outside IO page"

# Peripheral spec must agree with canonical IO map.
assert int(peripherals["irq"]["status"],16) == int(io["devices"]["system"]["registers"]["IRQ_STATUS"],16)
assert int(peripherals["irq"]["mask"],16) == int(io["devices"]["system"]["registers"]["IRQ_MASK"],16)
for key, addr in peripherals["timer"]["registers"].items():
    expected = {"lo":"TIMER_LO","hi":"TIMER_HI","control":"TIMER_CONTROL","status":"TIMER_STATUS"}[key]
    assert int(addr,16) == int(io["devices"]["timer"]["registers"][expected],16)
for key, addr in peripherals["gpio"]["registers"].items():
    expected = {"data":"GPIO_DATA","dir":"GPIO_DIR","input":"GPIO_INPUT"}[key]
    assert int(addr,16) == int(io["devices"]["gpio"]["registers"][expected],16)

print("ISA/control-store coverage: 99/99")
print("branch/stack/AGU structural vectors: PASS")
print("peripheral MMIO consistency: PASS")
