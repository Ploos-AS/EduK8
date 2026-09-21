"""Two-pass K8 assembler."""
from dataclasses import dataclass
from assembler.encoder import encode_instruction
from assembler.expression import ExpressionError, evaluate
from assembler.parser import ParseError
from assembler.pass1 import first_pass

@dataclass(frozen=True)
class Assembly:
    origin: int
    data: bytes
    symbols: dict[str, int]

def _eval(expr, symbols, line):
    try:
        return evaluate(expr, symbols)
    except ExpressionError as exc:
        raise ParseError(line, str(exc)) from exc

def _items(operand, line):
    if operand is None:
        raise ParseError(line, "directive requires data")
    items = [x.strip() for x in operand.split(",")]
    if not items or any(not x for x in items):
        raise ParseError(line, "invalid data list")
    return items

def assemble(source: str, origin: int = 0) -> Assembly:
    statements, symbols = first_pass(source, origin)
    pc = origin & 0xFFFF
    image = {}

    def emit(data, line):
        nonlocal pc
        for value in data:
            if not 0 <= pc <= 0xFFFF:
                raise ParseError(line, "assembly address exceeds 16-bit address space")
            if pc in image:
                raise ParseError(line, "address overlap at $%04X" % pc)
            image[pc] = value
            pc += 1

    for stmt in statements:
        if stmt.operation is None or stmt.operation == ".equ":
            continue
        if stmt.directive:
            if stmt.operation == ".org":
                pc = _eval(stmt.operand or "", symbols, stmt.line)
                if not 0 <= pc <= 0xFFFF:
                    raise ParseError(stmt.line, ".org address out of range")
            elif stmt.operation == ".byte":
                values = [_eval(x, symbols, stmt.line) for x in _items(stmt.operand, stmt.line)]
                if any(not 0 <= x <= 0xFF for x in values):
                    raise ParseError(stmt.line, ".byte value out of range")
                emit(bytes(values), stmt.line)
            elif stmt.operation == ".word":
                values = [_eval(x, symbols, stmt.line) for x in _items(stmt.operand, stmt.line)]
                if any(not 0 <= x <= 0xFFFF for x in values):
                    raise ParseError(stmt.line, ".word value out of range")
                for value in values:
                    emit(bytes([value & 0xFF, value >> 8]), stmt.line)
            else:
                raise ParseError(stmt.line, "unknown directive: " + stmt.operation)
        else:
            emit(encode_instruction(stmt, pc, symbols), stmt.line)

    if not image:
        return Assembly(origin & 0xFFFF, b"", symbols)
    start, end = min(image), max(image)
    return Assembly(start, bytes(image.get(a, 0) for a in range(start, end + 1)), symbols)
