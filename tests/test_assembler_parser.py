import pytest

from assembler.parser import ParseError, Statement, parse, parse_line


def test_blank_and_comment_lines_are_ignored():
    assert parse_line(" ; comment", 1) is None
    assert parse_line("", 2) is None


def test_label_instruction_and_comment():
    assert parse_line("loop: lda #$42 ; load", 7) == Statement(
        7, label="loop", operation="LDA", operand="#$42"
    )


def test_label_only_and_directive():
    assert parse_line("start:", 1) == Statement(1, label="start")
    assert parse_line(".ORG $8000", 2) == Statement(
        2, operation=".org", operand="$8000", directive=True
    )


def test_semicolon_inside_character_literal_is_not_comment():
    stmt = parse_line(".byte ';' ; real comment", 3)
    assert stmt.operand == "';'"


def test_parse_preserves_source_line_numbers():
    source = """
start:
    LDA #1
    BNE start
"""
    statements = parse(source)
    assert [s.line for s in statements] == [2, 3, 4]
    assert [s.operation for s in statements] == [None, "LDA", "BNE"]


@pytest.mark.parametrize("source", ["1bad:", ".123 4", "@bad"])
def test_invalid_source_reports_line(source):
    with pytest.raises(ParseError, match="line 9:"):
        parse_line(source, 9)
