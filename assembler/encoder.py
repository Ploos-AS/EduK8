"""K8 M3 instruction encoder."""

import json
from pathlib import Path
import re

from assembler.expression import ExpressionError, evaluate
from assembler.parser import ParseError, Statement


_SPEC = json.loads((Path(__file__).parents[1] / "spec" / "isa.json").read_text())
_OPCODES = {(m.upper(), mode): int(op, 16) for op, m, mode, _ in _SPEC["instructions"]}
_BRANCHES = {"BEQ", "BNE", "BCS", "BCC", "BMI", "BPL", "BVS", "BVC"}


def _value(expr: str, symbols: dict[str, int], line: int) -> int:
    try:
        return evaluate(expr.strip(), symbols)
    except ExpressionError as exc:
        raise ParseError(line, str(exc)) from exc


def encode_instruction(stmt: Statement, pc: int, symbols: dict[str, int]) -> bytes:
    mnemonic = stmt.operation or ""
    operand = stmt.operand

    if operand is None:
        key = (mnemonic, "imp")
        if key not in _OPCODES:
            raise ParseError(stmt.line, f"operand required or invalid mode for {mnemonic}")
        return bytes([_OPCODES[key]])

    if mnemonic in _BRANCHES:
        target = _value(operand, symbols, stmt.line)
        displacement = target - (pc + 2)
        if not -128 <= displacement <= 127:
            raise ParseError(stmt.line, "branch target out of range")
        return bytes([_OPCODES[(mnemonic, "rel")], displacement & 0xFF])

    mode = None
    expr = operand.strip()
    if expr.startswith("#"):
        mode, expr = "imm", expr[1:].strip()
    else:
        indirect = re.fullmatch(r"\((.+)\)", expr)
        indexed = re.fullmatch(r"(.+),\s*([XxYy])", expr)
        if indirect:
            expr = indirect.group(1).strip()
            value = _value(expr, symbols, stmt.line)
            mode = "(zp)" if value <= 0xFF and (mnemonic, "(zp)") in _OPCODES else "(abs)"
        elif indexed:
            expr = indexed.group(1).strip()
            reg = indexed.group(2).upper()
            value = _value(expr, symbols, stmt.line)
            zp_mode, abs_mode = f"zp,{reg}", f"abs,{reg}"
            mode = zp_mode if value <= 0xFF and (mnemonic, zp_mode) in _OPCODES else abs_mode
        else:
            value = _value(expr, symbols, stmt.line)
            mode = "zp" if value <= 0xFF and (mnemonic, "zp") in _OPCODES else "abs"

    value = _value(expr, symbols, stmt.line)
    key = (mnemonic, mode)
    if key not in _OPCODES:
        raise ParseError(stmt.line, f"invalid addressing mode for {mnemonic}: {mode}")

    opcode = _OPCODES[key]
    if mode in {"imm", "zp", "zp,X", "zp,Y", "(zp)"}:
        if not 0 <= value <= 0xFF:
            raise ParseError(stmt.line, "byte operand out of range")
        return bytes([opcode, value])
    if not 0 <= value <= 0xFFFF:
        raise ParseError(stmt.line, "word operand out of range")
    return bytes([opcode, value & 0xFF, value >> 8])
