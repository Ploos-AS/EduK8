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


def test_monitor_rom_help_command():
    cpu=boot_monitor()
    cpu.io.inject_key(ord("?"))

    for _ in range(128):
        cpu.step()
        if bytes(cpu.memory[VRAM_START:VRAM_START+8]) == b"K8> HELP":
            break

    assert bytes(cpu.memory[VRAM_START:VRAM_START+8]) == b"K8> HELP"


def test_monitor_rom_line_editor_help():
    cpu=boot_monitor()
    for ch in b"HELP\\r":
        cpu.io.inject_key(ch)
        for _ in range(64):
            cpu.step()
            if ch == 13 and bytes(cpu.memory[VRAM_START+40:VRAM_START+47]) == b"HELP OK":
                break
    assert bytes(cpu.memory[VRAM_START:VRAM_START+8]) == b"K8> HELP"
    assert bytes(cpu.memory[VRAM_START+40:VRAM_START+47]) == b"HELP OK"
