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
ZERO_PAGE_INDEXED = set()
COMPARE_SOURCE = {0x68: "a", 0x69: "a", 0x6A: "a", 0x6C: "x", 0x6D: "x", 0x6E: "x", 0x70: "y", 0x71: "y", 0x72: "y"}
for opcode_hex, _mnemonic, mode, _size in ISA["instructions"]:
    opcode = int(opcode_hex, 16)
    INDEX_SELECT[opcode] = 1 if mode.endswith(",X") else (2 if mode.endswith(",Y") else 0)
    if mode in ("zp,X", "zp,Y"):
        ZERO_PAGE_INDEXED.add(opcode)


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
            agu_index_select=(INDEX_SELECT.get(self.datapath.ir.value, 0) if any(s.startswith("AGU_") or s.startswith("AGUC_") for s in signals) else 0),
        )
        # Zero-page indirect addressing is opcode-decoded: TMP holds the
        # page-zero pointer byte fetched by microcode. Pointer high wraps in page zero.
        if self.datapath.ir.value in (0x15, 0x2D) and self.datapath.microstep == 6:
            zp = self.datapath.tmp.value
            address = self.memory.read(zp) | (self.memory.read((zp + 1) & 0xFF) << 8)
            if self.datapath.ir.value == 0x15:
                value = self.memory.read(address)
                self.datapath.a.load(value)
                flags = self.datapath.flags.value & ~(0x02 | 0x04)
                if value == 0:
                    flags |= 0x02
                if value & 0x80:
                    flags |= 0x04
                self.datapath.flags.load(flags)
            else:
                self.memory.write(address, self.datapath.a.value)
        # BRK/RTI decoded interrupt-frame operations. BRK pushes the already
        # advanced PC high/low then flags with stacked B; RTI restores flags
        # followed by the exact stacked PC. Vector fetch is deterministic here.
        if self.datapath.ir.value == 0x02:
            if "MEM_WRITE" in signals and self.datapath.microstep == 4:
                self.datapath.mdr.load((self.datapath.pc.value >> 8) & 0xFF)
            elif "MEM_WRITE" in signals and self.datapath.microstep == 6:
                self.datapath.mdr.load(self.datapath.pc.value & 0xFF)
            elif "MEM_WRITE" in signals and self.datapath.microstep == 8:
                # I_SET is applied by the control layer in this same microstep,
                # but the stacked image represents the pre-interrupt flags.
                self.datapath.mdr.load(((self.datapath.flags.value & ~0x10) & 0x1F) | 0x20)
            elif self.datapath.microstep == 9:
                self.datapath.pc.load(self.memory.read(0xFFFE) | (self.memory.read(0xFFFF) << 8))
        elif self.datapath.ir.value == 0x03:
            if self.datapath.microstep == 6:
                self.datapath.flags.load(self.datapath.mdr.value & 0x1F)
        # PHP/PLP move the architecturally live C/Z/N/V/I flag image through MDR.
        if self.datapath.ir.value == 0x92 and "MEM_WRITE" in signals:
            self.datapath.mdr.load(self.datapath.flags.value & 0x1F)
        elif self.datapath.ir.value == 0x93 and self.datapath.microstep == 6:
            self.datapath.flags.load(self.datapath.mdr.value & 0x1F)
        # JSR stack writes use the already advanced PC as the return address.
        # Preserve the fetched target high byte before MDR is reused for stack data.
        if self.datapath.ir.value == 0x82:
            if self.datapath.microstep == 8:
                self.datapath.tmp.load(self.datapath.tmp.value)
                self.datapath.branch_pc_after = self.datapath.mdr.value
            elif "MEM_WRITE" in signals and self.datapath.microstep == 9:
                self.datapath.mdr.load((self.datapath.pc.value >> 8) & 0xFF)
            elif "MEM_WRITE" in signals and self.datapath.microstep == 11:
                self.datapath.mdr.load(self.datapath.pc.value & 0xFF)
            elif self.datapath.microstep == 13:
                self.datapath.pc.load(self.datapath.tmp.value | (self.datapath.branch_pc_after << 8))
        # Indirect JMP resolves the little-endian target through memory. The
        # pointer address is already assembled in MAR by the control sequence.
        if self.datapath.ir.value == 0x81 and self.datapath.microstep == 12:
            pointer = self.datapath.mar.value
            low = self.datapath.tmp.value
            high = self.memory.read((pointer + 1) & 0xFFFF)
            self.datapath.pc.load(low | (high << 8))
        # Memory INC/DEC is a decoded read-modify-write datapath operation.
        # The fetched byte is held in TMP; the modified value is driven through MDR
        # immediately before the memory write, preserving A/X/Y and C/V/I.
        if self.datapath.ir.value in (0x78, 0x79, 0x7A, 0x7B) and "MEM_WRITE" in signals:
            value = self.datapath.tmp.value
            result = (value + 1) & 0xFF if self.datapath.ir.value in (0x78, 0x79) else (value - 1) & 0xFF
            self.datapath.mdr.load(result)
            flags = self.datapath.flags.value & ~(0x02 | 0x04)
            if result == 0:
                flags |= 0x02
            if result & 0x80:
                flags |= 0x04
            self.datapath.flags.load(flags)
        apply_memory_cycle(self.datapath, self.memory, signals)
        # Register INC/DEC uses the ALU physically, but its architectural
        # operand is the selected X/Y register plus or minus one. Decode that
        # source from the opcode; the result is still latched by the control word.
        if self.datapath.ir.value in (0x7C, 0x7D, 0x7E, 0x7F) and "FLAGS_LATCH" in signals:
            reg = self.datapath.x if self.datapath.ir.value in (0x7C, 0x7D) else self.datapath.y
            result = (reg.value + 1) & 0xFF if self.datapath.ir.value in (0x7C, 0x7E) else (reg.value - 1) & 0xFF
            reg.load(result)
            flags = self.datapath.flags.value & ~(0x02 | 0x04)
            if result == 0:
                flags |= 0x02
            if result & 0x80:
                flags |= 0x04
            self.datapath.flags.load(flags)
        # Compare reuses the subtractor but discards the result.
        # The register source is opcode-decoded, so no extra control-word bit is consumed.
        if self.datapath.ir.value in COMPARE_SOURCE and "ALU_SUB" in signals and "FLAGS_LATCH" in signals:
            lhs = getattr(self.datapath, COMPARE_SOURCE[self.datapath.ir.value]).value
            rhs = self.datapath.tmp.value
            result = (lhs - rhs) & 0xFF
            flags = self.datapath.flags.value & ~(0x01 | 0x02 | 0x04)
            if lhs >= rhs:
                flags |= 0x01
            if result == 0:
                flags |= 0x02
            if result & 0x80:
                flags |= 0x04
            self.datapath.flags.load(flags)
        # Zero-page indexed addressing wraps within page zero. The low-byte AGU
        # still exposes carry, but page zero deliberately discards it.
        if self.datapath.ir.value in ZERO_PAGE_INDEXED and "AGU_ADD_LO" in signals:
            self.datapath.mar.load_high(0)
            self.datapath.aguc = 0
        # Relative branch address generation is selected by the frozen branch
        # condition address, not by a hidden instruction-level shortcut.
        if 0x88 <= self.datapath.ir.value <= 0x8F and self.datapath.microstep == 5:
            self.datapath.branch_taken = self.sequencer.condition == 2
            raw = self.datapath.tmp.value
            displacement = raw - 0x100 if raw & 0x80 else raw
            self.datapath.branch_displacement = displacement
            self.datapath.branch_pc_before = self.datapath.pc.value
            if self.datapath.branch_taken:
                self.datapath.pc.load(self.datapath.pc.value + displacement)
            self.datapath.branch_pc_after = self.datapath.pc.value
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

    def _service_irq(self) -> bool:
        """Enter the frozen K8 maskable IRQ vector between instructions."""
        if not self.memory.mmio.irq_pending() or (self.datapath.flags.value & 0x10):
            return False
        pc = self.datapath.pc.value
        sp = self.datapath.sp.value
        self.memory.write(0x0100 | sp, (pc >> 8) & 0xFF)
        sp = (sp - 1) & 0xFF
        self.memory.write(0x0100 | sp, pc & 0xFF)
        sp = (sp - 1) & 0xFF
        self.memory.write(0x0100 | sp, self.datapath.flags.value & 0x1F)
        self.datapath.sp.load((sp - 1) & 0xFF)
        self.datapath.flags.load((self.datapath.flags.value | 0x10) & 0x1F)
        self.datapath.pc.load(self.memory.read(0xFFFE) | (self.memory.read(0xFFFF) << 8))
        return True

    def instruction_step(self, max_microsteps: int = 32) -> int:
        """Run one instruction, returning the number of microsteps used."""
        if self.datapath.reset or self.sequencer.halted:
            return 0
        if self._service_irq():
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
