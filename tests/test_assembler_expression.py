import pytest

from assembler.expression import ExpressionError, evaluate


def test_numeric_literals_and_arithmetic():
    assert evaluate("42") == 42
    assert evaluate("$2A") == 42
    assert evaluate("%00101010") == 42
    assert evaluate("'A'") == 65
    assert evaluate("$20 + 3 - 1") == 34


def test_symbols_and_parentheses():
    assert evaluate("(base + 4) - 1", {"base": 0x1000}) == 0x1003


def test_unary_plus_minus():
    assert evaluate("-2 + +5") == 3


def test_undefined_symbol_is_diagnostic():
    with pytest.raises(ExpressionError, match="undefined symbol: missing"):
        evaluate("missing + 1")


@pytest.mark.parametrize("expr", ["1 * 2", "1 << 2", "__import__('os')", "'AB'"])
def test_unsupported_expressions_are_rejected(expr):
    with pytest.raises(ExpressionError):
        evaluate(expr)
