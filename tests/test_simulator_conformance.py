"""Cross-check programmer-visible state between emulator and simulator."""

import pytest

from emulator.k8 import CPU
from simulator.core import K8Simulator
from tests.conformance_vectors import VECTORS


def states(cpu, sim):
    dp = sim.datapath
    return {
        "a": (cpu.a, dp.a.value),
        "x": (cpu.x, dp.x.value),
        "y": (cpu.y, dp.y.value),
        "pc": (cpu.pc, dp.pc.value),
        "sp": (cpu.sp, dp.sp.value),
        "f": (cpu.f, dp.flags.value),
        "halted": (cpu.halted, sim.sequencer.halted),
    }


def assert_architecture_matches(cpu, sim):
    mismatches = {k: v for k, v in states(cpu, sim).items() if v[0] != v[1]}
    assert mismatches == {}


def apply_initial(cpu, sim, initial):
    mapping = {
        "a": (cpu, "a", sim.datapath.a),
        "x": (cpu, "x", sim.datapath.x),
        "y": (cpu, "y", sim.datapath.y),
        "sp": (cpu, "sp", sim.datapath.sp),
        "f": (cpu, "f", sim.datapath.flags),
    }
    for name, value in initial.items():
        target_cpu, attr, target_sim = mapping[name]
        setattr(target_cpu, attr, value)
        target_sim.load(value)


def run_vector(vector, pc=0x8000):
    image = bytes(vector["image"])
    cpu = CPU()
    cpu.memory[pc:pc + len(image)] = image
    cpu.reset(pc=pc)

    sim = K8Simulator()
    sim.datapath.pc.load(pc)
    sim.load_image(pc, image, force=True)

    apply_initial(cpu, sim, vector.get("initial", {}))
    cpu.step()
    sim.instruction_step()
    assert_architecture_matches(cpu, sim)

    for name, expected in vector.get("expected", {}).items():
        actual = cpu.halted if name == "halted" else getattr(cpu, name)
        assert actual == expected


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: v["name"])
def test_shared_architectural_vector(vector):
    run_vector(vector)
