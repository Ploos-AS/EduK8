"""Clock/reset and T0-T31 control-store sequencer for K8 simulation."""

from dataclasses import dataclass, field
import json
from pathlib import Path

from simulator.datapath import Datapath

ROOT = Path(__file__).resolve().parents[1]
CONTROL_SPEC = json.loads((ROOT / "spec/control-word.json").read_text())
MAX_STEPS = 1 << CONTROL_SPEC["address"]["microstep_bits"]


@dataclass
class ControlStore:
    """Logical microcode lookup using the repository machine-readable source."""

    fetch: dict[int, tuple[str, ...]] = field(default_factory=dict)
    opcodes: dict[int, dict[int, tuple[str, ...]]] = field(default_factory=dict)

    @classmethod
    def from_spec(cls, path: Path | None = None):
        source = json.loads((path or ROOT / "spec/microcode.json").read_text())
        fetch = {
            row["step"]: tuple(row.get("signals", ()))
            for row in source.get("fetch", ())
        }
        opcodes = {}
        for opcode_text, rows in source.get("opcodes", {}).items():
            opcode = int(opcode_text, 16)
            opcodes[opcode] = {
                row["step"]: tuple(row.get("signals", ())) for row in rows
            }
        return cls(fetch=fetch, opcodes=opcodes)

    def signals(self, opcode: int, step: int, condition: int = 0) -> tuple[str, ...]:
        if not 0 <= opcode <= 0xFF:
            raise ValueError("opcode out of range")
        if not 0 <= step < MAX_STEPS:
            raise ValueError("microstep out of range")
        if not 0 <= condition < 4:
            raise ValueError("condition out of range")
        # Current source has unconditional rows. Condition is already explicit in
        # the frozen control-store address and is retained here for expansion.
        if step in self.fetch:
            return self.fetch[step]
        return self.opcodes.get(opcode, {}).get(step, ())


@dataclass
class Sequencer:
    datapath: Datapath
    store: ControlStore = field(default_factory=ControlStore.from_spec)
    condition: int = 0
    halted: bool = False

    def reset(self) -> None:
        self.datapath.microstep = 0
        self.datapath.clock = 0
        self.datapath.reset = True
        self.datapath.active_controls = ()
        self.halted = False

    def release_reset(self) -> None:
        self.datapath.reset = False

    def current_signals(self) -> tuple[str, ...]:
        if self.halted or self.datapath.reset:
            return ()
        return self.store.signals(
            self.datapath.ir.value, self.datapath.microstep, self.condition
        )

    def advance(self, signals: tuple[str, ...]) -> None:
        """Advance the control sequencer after one applied microstep."""
        if "HALT" in signals:
            self.halted = True
            return
        if "STEP_RESET" in signals or "INSTR_DONE" in signals:
            self.datapath.microstep = 0
        else:
            self.datapath.microstep = (self.datapath.microstep + 1) % MAX_STEPS

    def tick_clock(self) -> int:
        """Toggle the visible clock and return its new level."""
        self.datapath.clock ^= 1
        return self.datapath.clock
