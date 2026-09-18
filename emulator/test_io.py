from emulator.k8 import CPU
from emulator.io import KEY_DATA, KEY_STATUS, VRAM_START

def test_keyboard_injection_and_status():
    cpu=CPU()
    cpu.io.inject_key(ord("K"))
    assert cpu._read8(KEY_STATUS) & 1
    assert cpu._read8(KEY_DATA) == ord("K")
    assert not (cpu._read8(KEY_STATUS) & 1)

def test_store_to_video_ram_and_render_text():
    cpu=CPU()
    cpu._write8(VRAM_START, ord("K"))
    assert cpu.io.text(cpu.memory).splitlines()[0][0] == "K"

def test_cpu_can_load_keyboard_register():
    cpu=CPU()
    cpu.io.inject_key(0x41)
    cpu.memory[0:3]=bytes([0x12, KEY_DATA & 0xff, KEY_DATA >> 8])
    cpu.step()
    assert cpu.a == 0x41
