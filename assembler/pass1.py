"""Pass 1: assign K8 source addresses and collect symbols."""

import json
from pathlib import Path

from assembler.expression import ExpressionError, evaluate
from assembler.parser import ParseError, Statement, parse


_ISA = json.loads((Path(__file__).parents[1] / "spec" / "isa.json").read_text())
_LENGTHS = {}
for opcode, mnemonic, mode, length in _ISA["instructions"]:
    _LENGTHS.setdefault(mnemonic.upper(), {})[mode] = length


def _define(symbols: dict[str, int], name: str, value: int, line: int) -> None:
    if name in symbols:
        raise ParseError(line, f"duplicate symbol: {name}")
    symbols[name] = value


def _instruction_length(stmt: Statement) -> int:
    modes = _LENGTHS.get(stmt.operation or "")
    if modes is None:
        raise ParseError(stmt.line, f"unknown mnemonic: {stmt.operation}")
    if stmt.operand is None:
        if "imp" not in modes:
            raise ParseError(stmt.line, f"operand required for {stmt.operation}")
        return modes["imp"]
    # Pass 1 intentionally chooses the longest matching encoding. Pass 2 may
    # shrink a resolved operand to zero page and then recompute until stable.
    return max(modes.values())


def first_pass(source: str, origin: int = 0) -> tuple[list[Statement], dict[str, int]]:
    statements = parse(source)
    symbols: dict[str, int] = {}
    pc = origin & 0xFFFF

    for stmt in statements:
        if stmt.label and stmt.operation != ".equ":
            _define(symbols, stmt.label, pc, stmt.line)

        if stmt.operation is None:
            continue

        if stmt.directive:
            op = stmt.operation
            if op == ".org":
                if stmt.operand is None:
                    raise ParseError(stmt.line, ".org requires an address")
                try:
                    pc = evaluate(stmt.operand, symbols)
                except ExpressionError as exc:
                    raise ParseError(stmt.line, str(exc)) from exc
                if not 0 <= pc <= 0xFFFF:
                    raise ParseError(stmt.line, ".org address out of range")
            elif op == ".equ":
                if stmt.label is None or stmt.operand is None:
                    raise ParseError(stmt.line, ".equ requires NAME .equ value")
                try:
                    value = evaluate(stmt.operand, symbols)
                except ExpressionError as exc:
                    raise ParseError(stmt.line, str(exc)) from exc
                _define(symbols, stmt.label, value, stmt.line)
            elif op == ".byte":
                if stmt.operand is None:
                    raise ParseError(stmt.line, ".byte requires data")
                pc += len([x for x in stmt.operand.split(",") if x.strip()])
            elif op == ".word":
                if stmt.operand is None:
                    raise ParseError(stmt.line, ".word requires data")
                pc += 2 * len([x for x in stmt.operand.split(",") if x.strip()])
            else:
                raise ParseError(stmt.line, f"unknown directive: {op}")
        else:
            pc += _instruction_length(stmt)

        if pc > 0x10000:
            raise ParseError(stmt.line, "assembly address exceeds 16-bit address space")

    return statements, symbols
