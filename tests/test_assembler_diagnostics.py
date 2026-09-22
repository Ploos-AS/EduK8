"""M3 assembler diagnostic contract tests."""

import pytest

from assembler.assembler import assemble
from assembler.parser import ParseError


def check_error(source, line, text):
    with pytest.raises(ParseError) as caught:
        assemble(source)
    err = caught.value
    assert err.line == line
    assert text.lower() in str(err).lower()


def test_unknown_mnemonic_reports_source_line():
    check_error(".org $8000\nBOGUS #1", 2, "unknown")


def test_duplicate_symbol_reports_source_line():
    check_error("same:\nNOP\nsame:\nHALT", 3, "duplicate")


def test_unknown_symbol_reports_source_line():
    check_error(".org $8000\nLDA missing", 2, "missing")


def test_invalid_addressing_mode_reports_source_line():
    check_error(".org $8000\nSTA #1", 2, "mode")


def test_branch_out_of_range_reports_source_line():
    check_error(".org $8000\nBNE $9000", 2, "range")


def test_byte_range_reports_source_line():
    check_error(".org $8000\n.byte 256", 2, ".byte value out of range")


def test_word_range_reports_source_line():
    check_error(".org $8000\n.word $10000", 2, ".word value out of range")


def test_org_range_reports_source_line():
    check_error(".org $10000", 1, ".org address out of range")


def test_address_overlap_reports_source_line():
    check_error(".org $8000\n.byte 1\n.org $8000\n.byte 2", 4, "address overlap")
