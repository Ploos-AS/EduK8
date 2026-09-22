"""M3 cross-check: execute assembler-generated machine code in reference emulator."""

from assembler.assembler import assemble
from emulator.k8 import CPU


def test_assembled_program_executes_in_reference_emulator():
    program = assemble("""
.org $8000
    LDA #$2A
    TAX
    INX
    HALT
""")

    cpu = CPU()
    cpu.mem[program.origin : program.origin + len(program.data)] = program.data
    cpu.pc = program.origin

    for _ in range(16):
        cpu.step()
        if cpu.halted:
            break

    assert cpu.halted
    assert cpu.a == 0x2A
    assert cpu.x == 0x2B
