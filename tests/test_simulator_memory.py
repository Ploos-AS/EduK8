from simulator.datapath import Datapath
from simulator.memory import Memory, apply_memory_cycle


def test_memory_map_decode():
    mem = Memory()
    assert mem.region(0x0000)["kind"] == "ram"
    assert mem.region(0x7800)["kind"] == "vram"
    assert mem.region(0x8000)["kind"] == "rom"
    assert mem.region(0xC010)["kind"] == "io"
    assert mem.region(0xFFFC)["kind"] == "rom_alias"


def test_ram_and_vram_are_writable():
    mem = Memory()
    mem.write(0x0200, 0x42)
    mem.write(0x7800, 0x41)
    assert mem.read(0x0200) == 0x42
    assert mem.read(0x7800) == 0x41


def test_rom_requires_image_load():
    mem = Memory()
    mem.write(0x8000, 0x12)
    assert mem.read(0x8000) == 0
    mem.load(0x8000, bytes([0x12, 0x34]), force=True)
    assert mem.read(0x8000) == 0x12
    assert mem.read(0x8001) == 0x34


def test_reserved_reads_zero_and_ignores_writes():
    mem = Memory()
    mem.write(0x7F00, 0xFF)
    assert mem.read(0x7F00) == 0


def test_mmio_is_separate_from_backing_memory():
    mem = Memory()
    mem.write(0xC040, 0xA5)
    assert mem.read(0xC040) == 0xA5
    assert mem.data[0xC040] == 0


def test_memory_read_cycle_loads_mdr():
    dp = Datapath()
    mem = Memory()
    mem.write(0x0200, 0x5A)
    dp.mar.load(0x0200)
    apply_memory_cycle(dp, mem, ("MEM_READ", "MDR_LOAD"))
    assert dp.mdr.value == 0x5A


def test_memory_write_cycle_uses_mdr():
    dp = Datapath()
    mem = Memory()
    dp.mar.load(0x0200)
    dp.mdr.load(0x66)
    apply_memory_cycle(dp, mem, ("MEM_WRITE",))
    assert mem.read(0x0200) == 0x66
