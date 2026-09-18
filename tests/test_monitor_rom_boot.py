from pathlib import Path

from assembler.k8asm import assemble
from emulator.k8 import CPU
from emulator.io import VRAM_START

def test_monitor_rom_boots_from_reset_vector():
    source=Path("examples/monitor_rom.asm").read_text()
    image=assemble(source,image=True)
    cpu=CPU()
    cpu.memory[:]=image

    # No PC override: this is the real K8 reset-vector path.
    cpu.reset()
    assert cpu.pc == 0x8000

    for _ in range(16):
        cpu.step()
        if bytes(cpu.memory[VRAM_START:VRAM_START+2]) == b"K8":
            break

    assert bytes(cpu.memory[VRAM_START:VRAM_START+2]) == b"K8"
    assert cpu.io.text(cpu.memory).splitlines()[0].startswith("K8")
