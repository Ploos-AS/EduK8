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
    """Deterministic K8 peripheral and interrupt-controller model."""

    registers: dict[int, int] = field(default_factory=dict)
    key_data: int | None = None
    key_overrun: bool = False
    timer_counter: int = 0
    timer_reload: int = 0
    timer_expired: bool = False

    def inject_key(self, value: int) -> None:
        if self.key_data is not None:
            self.key_overrun = True
            return
        self.key_data = value & 0xFF

    def irq_status(self) -> int:
        status = 0
        if self.key_data is not None and (self.registers.get(0xC012, 0) & 0x01):
            status |= 0x01
        if self.timer_expired and (self.registers.get(0xC032, 0) & 0x04):
            status |= 0x02
        return status

    def irq_pending(self) -> bool:
        return bool(self.irq_status() & self.registers.get(0xC001, 0))

    def tick_timer(self) -> None:
        control = self.registers.get(0xC032, 0)
        if not (control & 0x01):
            return
        if self.timer_counter > 0:
            self.timer_counter -= 1
        if self.timer_counter == 0:
            self.timer_expired = True
            if control & 0x02:
                self.timer_counter = self.timer_reload
            else:
                self.registers[0xC032] = control & ~0x01

    def read(self, address: int) -> int:
        address &= 0xFFFF
        if address == 0xC000:
            return self.irq_status()
        if address == 0xC010:
            value = self.key_data if self.key_data is not None else 0
            self.key_data = None
            return value
        if address == 0xC011:
            return (1 if self.key_data is not None else 0) | (2 if self.key_overrun else 0)
        if address == 0xC030:
            return self.timer_counter & 0xFF
        if address == 0xC031:
            return (self.timer_counter >> 8) & 0xFF
        if address == 0xC033:
            return 1 if self.timer_expired else 0
        return self.registers.get(address, 0)

    def write(self, address: int, value: int) -> None:
        address &= 0xFFFF
        value &= 0xFF
        self.registers[address] = value
        if address in (0xC030, 0xC031):
            lo = self.registers.get(0xC030, 0)
            hi = self.registers.get(0xC031, 0)
            self.timer_reload = self.timer_counter = lo | (hi << 8)
        elif address == 0xC033:
            self.timer_expired = bool(value & 0x01)


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
