import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from emulator.k8 import CPU, FLAG_C, FLAG_Z, FLAG_N

def run_program(program):
    cpu = CPU()
    cpu.memory[:len(program)] = bytes(program)
    cpu.reset(pc=0)
    cpu.run(20)
    return cpu

def test_lda_and_halt():
    cpu = run_program([0x10, 0x42, 0x01])
    assert cpu.a == 0x42
    assert cpu.pc == 3
    assert cpu.halted

def test_add():
    cpu = run_program([0x10, 0x05, 0x40, 0x03, 0x01])
    assert cpu.a == 8

def test_zero_and_negative():
    assert run_program([0x10, 0x00, 0x01]).f & FLAG_Z
    assert run_program([0x10, 0x80, 0x01]).f & FLAG_N

def test_carry():
    cpu = run_program([0x10, 0xFF, 0x06, 0x40, 0x00, 0x01])
    assert cpu.a == 0
    assert cpu.f & FLAG_C
    assert cpu.f & FLAG_Z

def test_transfer():
    cpu = run_program([0x10, 0x37, 0x94, 0x95, 0x96, 0x97, 0x01])
    assert cpu.a == cpu.x == cpu.y == 0x37
