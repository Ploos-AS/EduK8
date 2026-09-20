"""Hardware-oriented K8 simulator datapath primitives.

This module deliberately models state and buses rather than executing K8
instructions. Control sequencing is layered on top in later M2.5 work.
"""

from dataclasses import dataclass, field
from typing import Optional


def u8(value: int) -> int:
    return value & 0xFF


def u16(value: int) -> int:
    return value & 0xFFFF


@dataclass
class Register8:
    name: str
    value: int = 0

    def load(self, value: int) -> None:
        self.value = u8(value)

    def output(self) -> int:
        return self.value


@dataclass
class Register16:
    name: str
    value: int = 0

    def load(self, value: int) -> None:
        self.value = u16(value)

    def load_low(self, value: int) -> None:
        self.value = (self.value & 0xFF00) | u8(value)

    def load_high(self, value: int) -> None:
        self.value = (u8(value) << 8) | (self.value & 0x00FF)

    def output(self) -> int:
        return self.value


@dataclass
class Bus8:
    """Single-driver 8-bit bus with explicit contention detection."""

    name: str
    value: Optional[int] = None
    driver: Optional[str] = None

    def clear(self) -> None:
        self.value = None
        self.driver = None

    def drive(self, source: str, value: int) -> None:
        if self.driver is not None:
            raise ValueError(
                f"{self.name} contention: {self.driver} and {source}"
            )
        self.driver = source
        self.value = u8(value)


@dataclass
class ALU:
    a: int = 0
    b: int = 0
    result: int = 0
    carry_out: int = 0
    overflow: int = 0

    def evaluate(self, operation: str, carry_in: int = 0) -> int:
        a, b = u8(self.a), u8(self.b)
        if operation == "PASS_A":
            raw = a
        elif operation == "PASS_B":
            raw = b
        elif operation == "ADD":
            raw = a + b + (carry_in & 1)
        elif operation == "SUB":
            raw = a - b - (1 - (carry_in & 1))
        elif operation == "AND":
            raw = a & b
        elif operation == "OR":
            raw = a | b
        elif operation == "XOR":
            raw = a ^ b
        elif operation == "NOT":
            raw = ~a
        elif operation == "SHL":
            raw = a << 1
        elif operation == "SHR":
            raw = a >> 1
        elif operation == "ROL":
            raw = (a << 1) | (carry_in & 1)
        elif operation == "ROR":
            raw = (a >> 1) | ((carry_in & 1) << 7)
        else:
            raise ValueError(f"unsupported ALU operation: {operation}")

        self.result = u8(raw)
        if operation == "ADD":
            self.carry_out = int(raw > 0xFF)
        elif operation == "SUB":
            self.carry_out = int(raw >= 0)
        elif operation in {"SHL", "ROL"}:
            self.carry_out = int(bool(a & 0x80))
        elif operation in {"SHR", "ROR"}:
            self.carry_out = int(bool(a & 0x01))
        else:
            self.carry_out = 0
        if operation in {"ADD", "SUB"}:
            b_eff = b if operation == "ADD" else u8(~b)
            self.overflow = int((~(a ^ b_eff) & (a ^ self.result) & 0x80) != 0)
        else:
            self.overflow = 0
        return self.result


@dataclass
class Datapath:
    """Stateful digital datapath visible to the educational simulator."""

    a: Register8 = field(default_factory=lambda: Register8("A"))
    x: Register8 = field(default_factory=lambda: Register8("X"))
    y: Register8 = field(default_factory=lambda: Register8("Y"))
    sp: Register8 = field(default_factory=lambda: Register8("SP", 0xFF))
    flags: Register8 = field(default_factory=lambda: Register8("F"))
    ir: Register8 = field(default_factory=lambda: Register8("IR"))
    mdr: Register8 = field(default_factory=lambda: Register8("MDR"))
    tmp: Register8 = field(default_factory=lambda: Register8("TMP"))
    pc: Register16 = field(default_factory=lambda: Register16("PC"))
    mar: Register16 = field(default_factory=lambda: Register16("MAR"))
    data_bus: Bus8 = field(default_factory=lambda: Bus8("DB"))
    alu: ALU = field(default_factory=ALU)
    agu_index_select: int = 0
    agu_index_value: int = 0
    agu_low_input: int = 0
    agu_low_result: int = 0
    aguc: int = 0
    branch_taken: bool = False
    branch_displacement: int = 0
    branch_pc_before: int = 0
    branch_pc_after: int = 0
    microstep: int = 0
    clock: int = 0
    reset: bool = False
    active_controls: tuple[str, ...] = ()

    def begin_cycle(self) -> None:
        self.data_bus.clear()
        self.active_controls = ()

    def snapshot(self) -> dict:
        return {
            "registers": {
                "A": self.a.value,
                "X": self.x.value,
                "Y": self.y.value,
                "SP": self.sp.value,
                "F": self.flags.value,
                "IR": self.ir.value,
                "MDR": self.mdr.value,
                "TMP": self.tmp.value,
                "PC": self.pc.value,
                "MAR": self.mar.value,
            },
            "bus": {"DB": self.data_bus.value, "driver": self.data_bus.driver},
            "alu": {
                "a": self.alu.a,
                "b": self.alu.b,
                "result": self.alu.result,
                "carry_out": self.alu.carry_out,
                "overflow": self.alu.overflow,
            },
            "agu": {
                "index_select": self.agu_index_select,
                "index_value": self.agu_index_value,
                "low_input": self.agu_low_input,
                "low_result": self.agu_low_result,
                "carry": self.aguc,
            },
            "branch": {
                "taken": self.branch_taken,
                "displacement": self.branch_displacement,
                "pc_before": self.branch_pc_before,
                "pc_after": self.branch_pc_after,
            },
            "microstep": self.microstep,
            "clock": self.clock,
            "reset": self.reset,
            "active_controls": list(self.active_controls),
        }
