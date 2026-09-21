import pytest

from assembler.encoder import encode_instruction
from assembler.parser import ParseError, Statement


def ins(op, operand=None, line=1):
    return Statement(line, operation=op, operand=operand)


def test_implied_and_immediate_encoding():
    assert encode_instruction(ins("NOP"), 0x8000, {}) == bytes([0x00])
    assert encode_instruction(ins("LDA", "#$42"), 0x8000, {}) == bytes([0x10, 0x42])


def test_zero_page_and_absolute_selection():
    assert encode_instruction(ins("LDA", "$42"), 0, {}) == bytes([0x11, 0x42])
    assert encode_instruction(ins("LDA", "$1234"), 0, {}) == bytes([0x12, 0x34, 0x12])


def test_indexed_and_indirect_modes():
    assert encode_instruction(ins("LDA", "$42,X"), 0, {}) == bytes([0x16, 0x42])
    assert encode_instruction(ins("LDA", "$1234,X"), 0, {}) == bytes([0x13, 0x34, 0x12])
    assert encode_instruction(ins("LDA", "($42)"), 0, {}) == bytes([0x15, 0x42])
    assert encode_instruction(ins("JMP", "($1234)"), 0, {}) == bytes([0x81, 0x34, 0x12])


def test_symbol_and_relative_branch_encoding():
    symbols = {"value": 0x2345, "loop": 0x8000}
    assert encode_instruction(ins("STA", "value"), 0, symbols) == bytes([0x29, 0x45, 0x23])
    assert encode_instruction(ins("BNE", "loop"), 0x8004, symbols) == bytes([0x89, 0xFA])


def test_forward_branch_range_is_checked():
    with pytest.raises(ParseError, match="branch target out of range"):
        encode_instruction(ins("BEQ", "$9000", line=7), 0x8000, {})


def test_invalid_addressing_mode_is_rejected():
    with pytest.raises(ParseError, match="invalid addressing mode"):
        encode_instruction(ins("STA", "#1", line=4), 0, {})
