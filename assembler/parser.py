"""Lexer/parser front end for K8 assembly source.

This module parses source structure only. Addressing-mode selection, symbol
resolution and expression evaluation belong to later assembler passes.
"""

from dataclasses import dataclass
import re


IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MNEMONIC = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")


@dataclass(frozen=True)
class Statement:
    line: int
    label: str | None = None
    operation: str | None = None
    operand: str | None = None
    directive: bool = False


class ParseError(ValueError):
    def __init__(self, line: int, message: str):
        super().__init__(f"line {line}: {message}")
        self.line = line


def _strip_comment(line: str) -> str:
    in_char = False
    escaped = False
    out = []
    for ch in line:
        if ch == "'" and not escaped:
            in_char = not in_char
        if ch == ";" and not in_char:
            break
        out.append(ch)
        escaped = ch == "\\" and not escaped
        if ch != "\\":
            escaped = False
    return "".join(out).strip()


def parse_line(source: str, line_number: int) -> Statement | None:
    text = _strip_comment(source)
    if not text:
        return None

    label = None
    colon = text.find(":")
    if colon >= 0:
        candidate = text[:colon].strip()
        if not IDENT.match(candidate):
            raise ParseError(line_number, "invalid label")
        label = candidate
        text = text[colon + 1 :].strip()
        if not text:
            return Statement(line_number, label=label)

    parts = text.split(None, 1)
    operation = parts[0]
    operand = parts[1].strip() if len(parts) == 2 else None
    directive = operation.startswith(".")

    if directive:
        if not IDENT.match(operation[1:]):
            raise ParseError(line_number, "invalid directive")
    elif not MNEMONIC.match(operation):
        raise ParseError(line_number, "invalid mnemonic")

    return Statement(
        line=line_number,
        label=label,
        operation=operation.lower() if directive else operation.upper(),
        operand=operand,
        directive=directive,
    )


def parse(source: str) -> list[Statement]:
    statements = []
    for number, line in enumerate(source.splitlines(), 1):
        statement = parse_line(line, number)
        if statement is not None:
            statements.append(statement)
    return statements
