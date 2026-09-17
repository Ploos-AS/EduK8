from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class MicroOp:
    name: str
    source: str = ""
    destination: str = ""
    note: str = ""

FETCH = (
    MicroOp("ADDRESS", "PC", "address bus"),
    MicroOp("READ", "memory", "data bus"),
    MicroOp("LATCH", "data bus", "IR"),
    MicroOp("INCREMENT", "PC", "PC"),
)

EXECUTION = {
    0x00: (),
    0x01: (MicroOp("HALT", note="stop clocked instruction execution"),),
    0x10: (
        MicroOp("ADDRESS", "PC", "address bus"),
        MicroOp("READ", "memory", "data bus"),
        MicroOp("LATCH", "data bus", "A"),
        MicroOp("FLAGS", "A", "Z,N"),
        MicroOp("INCREMENT", "PC", "PC"),
    ),
    0x40: (
        MicroOp("ADDRESS", "PC", "address bus"),
        MicroOp("READ", "memory", "data bus"),
        MicroOp("ALU_ADD", "A,data bus,C", "ALU"),
        MicroOp("LATCH", "ALU", "A"),
        MicroOp("FLAGS", "ALU", "C,Z,N,V"),
        MicroOp("INCREMENT", "PC", "PC"),
    ),
    0x29: (
        MicroOp("FETCH_ADDR_LO", "memory", "MAR.low"),
        MicroOp("FETCH_ADDR_HI", "memory", "MAR.high"),
        MicroOp("ADDRESS", "MAR", "address bus"),
        MicroOp("WRITE", "A", "memory"),
    ),
    0x80: (
        MicroOp("FETCH_ADDR_LO", "memory", "TMP.low"),
        MicroOp("FETCH_ADDR_HI", "memory", "TMP.high"),
        MicroOp("LATCH", "TMP", "PC"),
    ),
    0x90: (
        MicroOp("ADDRESS", "stack(SP)", "address bus"),
        MicroOp("WRITE", "A", "memory"),
        MicroOp("DECREMENT", "SP", "SP"),
    ),
    0x91: (
        MicroOp("INCREMENT", "SP", "SP"),
        MicroOp("ADDRESS", "stack(SP)", "address bus"),
        MicroOp("READ", "memory", "data bus"),
        MicroOp("LATCH", "data bus", "A"),
        MicroOp("FLAGS", "A", "Z,N"),
    ),
}

def microcode_for(opcode):
    return FETCH + EXECUTION.get(opcode, (MicroOp("EXECUTE", note="semantic execution; detailed microcode pending"),))

def serialise_microcode(opcode):
    return [asdict(op) for op in microcode_for(opcode)]
