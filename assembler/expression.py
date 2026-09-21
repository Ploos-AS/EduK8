"""Small expression evaluator for the K8 M3 assembler."""

import ast
import re


HEX = re.compile(r"\$([0-9A-Fa-f]+)")
BINARY = re.compile(r"%([01]+)")
CHAR = re.compile(r"'([^'\\]|\\.)'")


class ExpressionError(ValueError):
    pass


def _normalise(text: str) -> str:
    text = HEX.sub(lambda m: str(int(m.group(1), 16)), text)
    text = BINARY.sub(lambda m: str(int(m.group(1), 2)), text)
    return text


def evaluate(text: str, symbols: dict[str, int] | None = None) -> int:
    symbols = symbols or {}
    try:
        node = ast.parse(_normalise(text.strip()), mode="eval").body
    except (SyntaxError, ValueError) as exc:
        raise ExpressionError(f"invalid expression: {text}") from exc

    def visit(n):
        if isinstance(n, ast.Constant):
            if isinstance(n.value, int):
                return n.value
            if isinstance(n.value, str) and len(n.value) == 1:
                return ord(n.value)
            raise ExpressionError("only integer and character literals are allowed")
        if isinstance(n, ast.Name):
            if n.id not in symbols:
                raise ExpressionError(f"undefined symbol: {n.id}")
            return symbols[n.id]
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            value = visit(n.operand)
            return value if isinstance(n.op, ast.UAdd) else -value
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub)):
            left, right = visit(n.left), visit(n.right)
            return left + right if isinstance(n.op, ast.Add) else left - right
        raise ExpressionError("unsupported expression")

    return visit(node)
