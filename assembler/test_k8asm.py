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
    assert len(binary) == 19


def test_named_constants():
    source="KEY_DATA = $C010\nLDA KEY_DATA"
    assert assemble(source) == bytes([0x12,0x10,0xC0])


def test_equ_constant():
    source="PORT .equ $42\nLDA PORT"
    assert assemble(source) == bytes([0x11,0x42])


def test_byte_and_word_directives():
    assert assemble(".byte $12,$34\n.word $1234") == bytes([0x12,0x34,0x34,0x12])


def test_rom_image_and_vectors():
    src=".org $8000\nstart: HALT\n.org $FFFC\n.word start\n.word start"
    image=assemble(src,image=True)
    assert len(image)==65536
    assert image[0x8000]==0x01
    assert image[0xFFFC:0x10000]==bytes([0x00,0x80,0x00,0x80])
