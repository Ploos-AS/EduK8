"""K8 simulator memory decoder and MMIO bus."""

from dataclasses import dataclass, field
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEM_SPEC = json.loads((ROOT / "spec/memory-map.json").read_text())


def _n(value):
    return int(value, 16) if isinstance(value, str) else value


@dataclass
class MMIO:
    """Deterministic register-level MMIO model.

    Device behaviour is added separately; this layer establishes address
    decode and visible register storage for simulator bus cycles.
    """

    registers: dict[int, int] = field(default_factory=dict)

    def read(self, address: int) -> int:
        return self.registers.get(address & 0xFFFF, 0)

    def write(self, address: int, value: int) -> None:
        self.registers[address & 0xFFFF] = value & 0xFF


@dataclass
class Memory:
    data: bytearray = field(default_factory=lambda: bytearray(0x10000))
    mmio: MMIO = field(default_factory=MMIO)

    def region(self, address: int) -> dict:
        address &= 0xFFFF
        for region in MEM_SPEC["regions"]:
            if _n(region["start"]) <= address <= _n(region["end"]):
                return region
        raise ValueError(f"unmapped K8 address {address:#06x}")

    def read(self, address: int) -> int:
        address &= 0xFFFF
        region = self.region(address)
        if region["kind"] == "io":
            return self.mmio.read(address)
        if region["kind"] == "reserved":
            return 0
        return self.data[address]

    def write(self, address: int, value: int) -> None:
        address &= 0xFFFF
        value &= 0xFF
        region = self.region(address)
        kind = region["kind"]
        if kind == "io":
            self.mmio.write(address, value)
        elif kind in {"ram", "vram"}:
            self.data[address] = value
        elif kind in {"rom", "rom_alias", "reserved"}:
            return
        else:
            raise ValueError(f"unsupported memory region kind: {kind}")

    def load(self, address: int, payload: bytes, *, force: bool = False) -> None:
        """Load an image. force=True permits ROM initialization."""
        for offset, value in enumerate(payload):
            target = (address + offset) & 0xFFFF
            if force:
                self.data[target] = value
            else:
                self.write(target, value)


def apply_memory_cycle(dp, memory: Memory, signals) -> None:
    """Perform the memory-side effects of one control word."""
    signals = set(signals)
    address = dp.mar.value

    if "MEM_READ" in signals:
        value = memory.read(address)
        if "MDR_LOAD" in signals:
            dp.mdr.load(value)

    if "MEM_WRITE" in signals:
        # The hardware write path is through MDR.
        memory.write(address, dp.mdr.value)
