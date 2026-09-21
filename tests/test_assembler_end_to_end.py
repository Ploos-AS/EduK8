import pytest

from assembler.assembler import assemble
from assembler.parser import ParseError


def test_complete_program_binary_and_symbols():
    result = assemble("""
GPIO .equ $C040
.org $8000
start:
    LDA #$2A
    STA GPIO
    LDX #2
loop:
    DEX
    BNE loop
    HALT
""")
    assert result.origin == 0x8000
    assert result.symbols["GPIO"] == 0xC040
    assert result.symbols["start"] == 0x8000
    assert result.symbols["loop"] == 0x8007
    assert result.data == bytes([
        0x10, 0x2A,
        0x29, 0x40, 0xC0,
        0x18, 0x02,
        0x7D,
        0x89, 0xFD,
        0x01,
    ])


def test_data_words_and_forward_symbol():
    result = assemble("""
.org $1000
    .byte 1, $02, %00000011
    .word $1234, later
later:
    NOP
""")
    assert result.symbols["later"] == 0x1007
    assert result.data == bytes([1, 2, 3, 0x34, 0x12, 0x07, 0x10, 0x00])


def test_org_gap_is_zero_filled():
    result = assemble(".org $2000\n.byte 1\n.org $2003\n.byte 2")
    assert result.origin == 0x2000
    assert result.data == bytes([1, 0, 0, 2])


def test_overlapping_org_is_rejected():
    with pytest.raises(ParseError, match="address overlap"):
        assemble(".org $2000\n.byte 1\n.org $2000\n.byte 2")


def test_byte_and_word_ranges_are_checked():
    with pytest.raises(ParseError, match=".byte value out of range"):
        assemble(".byte 256")
    with pytest.raises(ParseError, match=".word value out of range"):
        assemble(".word $10000")
