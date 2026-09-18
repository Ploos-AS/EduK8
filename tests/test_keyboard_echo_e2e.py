from pathlib import Path

from assembler.k8asm import assemble
from emulator.k8 import CPU
from emulator.io import VRAM_START

def test_keyboard_echo_end_to_end():
    source=Path("examples/keyboard_echo.asm").read_text()
    program=assemble(source)
    cpu=CPU()
    cpu.memory[:len(program)]=program

    # Run until the polling loop is established.
    for _ in range(8):
        cpu.step()

    for ch in b"K8":
        cpu.io.inject_key(ch)
        # One character takes a small, visible instruction sequence.
        for _ in range(16):
            cpu.step()
            if cpu.memory[VRAM_START + (cpu.x - 1 & 0xff)] == ch:
                break

    assert bytes(cpu.memory[VRAM_START:VRAM_START+2]) == b"K8"
    assert cpu.io.text(cpu.memory).splitlines()[0].startswith("K8")
