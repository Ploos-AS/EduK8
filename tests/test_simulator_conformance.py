"""Cross-check programmer-visible state between emulator and simulator."""

from emulator.k8 import CPU
from simulator.core import K8Simulator


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


def run_one(image, pc=0x8000):
    cpu = CPU()
    cpu.memory[pc:pc + len(image)] = image
    cpu.reset(pc=pc)

    sim = K8Simulator()
    sim.datapath.pc.load(pc)
    sim.load_image(pc, image, force=True)

    cpu.step()
    sim.instruction_step()
    assert_architecture_matches(cpu, sim)
    return cpu, sim


def test_nop_matches_reference_emulator():
    run_one(bytes([0x00]))


def test_lda_immediate_matches_reference_emulator():
    cpu, sim = run_one(bytes([0x10, 0x42]))
    assert cpu.a == sim.datapath.a.value == 0x42
