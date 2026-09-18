from assembler.k8asm import assemble

def test_basic_program():
    assert assemble("LDA #$41\nSTA $7800\nHALT") == bytes([0x10,0x41,0x29,0x00,0x78,0x01])

def test_forward_relative_label():
    binary=assemble("loop: LDA #$00\nBEQ loop")
    assert binary == bytes([0x10,0x00,0x88,0xFC])

def test_keyboard_echo_assembles():
    from pathlib import Path
    src=Path("examples/keyboard_echo.asm").read_text()
    binary=assemble(src)
    assert binary[:2] == bytes([0x18,0x00])
    assert 0x16 <= len(binary) <= 0x30
