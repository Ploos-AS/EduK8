"""Integrated deterministic K8 hardware simulator core."""

from dataclasses import dataclass, field
import json
from pathlib import Path

from simulator.control import apply_controls
from simulator.datapath import Datapath
from simulator.memory import Memory, apply_memory_cycle
from simulator.sequencer import ControlStore, Sequencer

ROOT = Path(__file__).resolve().parents[1]
ISA = json.loads((ROOT / "spec/isa.json").read_text())
INDEX_SELECT = {}
for opcode_hex, _mnemonic, mode, _size in ISA["instructions"]:
    INDEX_SELECT[int(opcode_hex, 16)] = 1 if mode.endswith(",X") else (2 if mode.endswith(",Y") else 0)


@dataclass
class K8Simulator:
    datapath: Datapath = field(default_factory=Datapath)
    memory: Memory = field(default_factory=Memory)
    store: ControlStore = field(default_factory=ControlStore.from_spec)
    sequencer: Sequencer = field(init=False)

    def __post_init__(self) -> None:
        self.sequencer = Sequencer(self.datapath, self.store)

    def reset(self) -> None:
        self.sequencer.reset()

    def release_reset(self) -> None:
        self.sequencer.release_reset()

    def load_image(self, address: int, payload: bytes, *, force: bool = True) -> None:
        self.memory.load(address, payload, force=force)

    def microstep(self) -> tuple[str, ...]:
        """Execute one complete logical K8 microstep.

        Direct datapath controls are applied first, then memory-side effects,
        then the control sequencer advances. This keeps every intermediate
        state inspectable and deterministic.
        """
        if self.datapath.reset or self.sequencer.halted:
            return ()

        signals = self.sequencer.current_signals()
        apply_controls(
            self.datapath,
            signals,
            agu_index_select=INDEX_SELECT.get(self.datapath.ir.value, 0),
        )
        apply_memory_cycle(self.datapath, self.memory, signals)
        self.sequencer.advance(signals)
        return signals

    def clock_step(self) -> int:
        """Toggle the visible hardware clock.

        A rising edge executes the current logical microstep; a falling edge
        only exposes the complementary clock phase.
        """
        level = self.sequencer.tick_clock()
        if level == 1:
            self.microstep()
        return level

    def instruction_step(self, max_microsteps: int = 32) -> int:
        """Run one instruction, returning the number of microsteps used."""
        if self.datapath.reset or self.sequencer.halted:
            return 0

        count = 0
        while count < max_microsteps:
            signals = self.microstep()
            count += 1
            if "INSTR_DONE" in signals or "HALT" in signals:
                return count
        raise RuntimeError("instruction did not complete within T0-T31")

    def snapshot(self) -> dict:
        state = self.datapath.snapshot()
        state["halted"] = self.sequencer.halted
        state["condition"] = self.sequencer.condition
        return state
