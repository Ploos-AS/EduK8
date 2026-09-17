import json
from pathlib import Path

from emulator.k8 import CPU, FLAG_C, FLAG_Z, FLAG_N, FLAG_V, FLAG_I, FLAG_B

FLAGS = {"c": FLAG_C, "z": FLAG_Z, "n": FLAG_N, "v": FLAG_V, "i": FLAG_I, "b": FLAG_B}

def hx(value):
    return int(value, 16)

def apply_setup(cpu, setup):
    for address, value in setup.get("memory", {}).items():
        cpu.memory[hx(address)] = hx(value)
    if "pc" in setup:
        cpu.pc = hx(setup["pc"])
    if "a" in setup:
        cpu.a = hx(setup["a"])
    if "x" in setup:
        cpu.x = hx(setup["x"])
    if "y" in setup:
        cpu.y = hx(setup["y"])
    if "sp" in setup:
        cpu.sp = hx(setup["sp"])
    if "f" in setup:
        cpu.f = hx(setup["f"])

def verify(cpu, expected):
    scalar = {"a": cpu.a, "x": cpu.x, "y": cpu.y, "pc": cpu.pc, "sp": cpu.sp, "f": cpu.f}
    for name, actual in scalar.items():
        if name in expected:
            assert actual == hx(expected[name]), f"{name}: {actual:04X} != {expected[name]}"
    if "halted" in expected:
        assert cpu.halted is expected["halted"]
    for name, mask in FLAGS.items():
        if name in expected:
            assert bool(cpu.f & mask) is expected[name], f"flag {name}"
    for address, value in expected.get("memory", {}).items():
        actual = cpu.memory[hx(address)]
        assert actual == hx(value), f"memory {address}: {actual:02X} != {value}"

def run_vector(vector):
    cpu = CPU()
    apply_setup(cpu, vector.get("setup", {}))
    action = vector.get("action", {})
    if action.get("reset"):
        cpu.reset()
    for _ in range(action.get("steps", 0)):
        cpu.step()
    verify(cpu, vector.get("expect", {}))

def test_conformance_vectors():
    path = Path(__file__).with_name("v1.json")
    suite = json.loads(path.read_text())
    assert suite["architecture"] == "K8"
    for vector in suite["vectors"]:
        try:
            run_vector(vector)
        except AssertionError as exc:
            raise AssertionError(f'{vector["name"]}: {exc}') from exc
