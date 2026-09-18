from pathlib import Path
from assembler.k8asm import assemble
from emulator.k8 import CPU
from emulator.io import VRAM_START

def boot_monitor():
    source=Path("examples/monitor_rom.asm").read_text()
    image=assemble(source,image=True)
    cpu=CPU()
    cpu.memory[:]=image
    cpu.reset()
    return cpu

def test_monitor_rom_boots_from_reset_vector():
    cpu=boot_monitor()
    assert cpu.pc == 0x8000

    for _ in range(32):
        cpu.step()
        if bytes(cpu.memory[VRAM_START:VRAM_START+4]) == b"K8> ":
            break

    assert bytes(cpu.memory[VRAM_START:VRAM_START+4]) == b"K8> "
    assert cpu.io.text(cpu.memory).splitlines()[0].startswith("K8> ")

def test_monitor_rom_echoes_keyboard_input():
    cpu=boot_monitor()
    cpu.io.inject_key(ord("A"))

    for _ in range(64):
        cpu.step()
        if bytes(cpu.memory[VRAM_START:VRAM_START+5]) == b"K8> A":
            break

    assert bytes(cpu.memory[VRAM_START:VRAM_START+5]) == b"K8> A"
