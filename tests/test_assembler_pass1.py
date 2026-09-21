import pytest

from assembler.parser import ParseError
from assembler.pass1 import first_pass


def test_org_labels_equ_and_data_layout():
    source = """
GPIO_DATA .equ $C040
.org $8000
start:
    LDA #$42
    STA GPIO_DATA
data:
    .byte 1, 2, 3
words:
    .word $1234, start
done:
    HALT
"""
    statements, symbols = first_pass(source)
    assert statements
    assert symbols["GPIO_DATA"] == 0xC040
    assert symbols["start"] == 0x8000
    assert symbols["data"] == 0x8005
    assert symbols["words"] == 0x8008
    assert symbols["done"] == 0x800C


def test_forward_reference_does_not_need_resolution_in_pass_one():
    _, symbols = first_pass("""
.org $2000
    JMP later
    NOP
later:
    HALT
""")
    assert symbols["later"] == 0x2004


def test_equ_can_reference_earlier_constant():
    _, symbols = first_pass("""
BASE .equ $1000
NEXT .equ BASE + 4
.org NEXT
here:
    NOP
""")
    assert symbols["NEXT"] == 0x1004
    assert symbols["here"] == 0x1004


def test_duplicate_symbol_reports_line():
    with pytest.raises(ParseError, match=r"line 3: duplicate symbol: x"):
        first_pass("x:\nNOP\nx:\n")


def test_unknown_mnemonic_reports_line():
    with pytest.raises(ParseError, match=r"line 1: unknown mnemonic: WAT"):
        first_pass("WAT #1")
