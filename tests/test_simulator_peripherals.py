"""M2.5 integrated peripheral qualification for the K8 simulator."""

from simulator.core import K8Simulator
from simulator.display import text_rows


def test_m25_keyboard_video_gpio_timer_and_irq_integration():
    sim = K8Simulator()

    # Video: 40x25 VRAM path and cursor MMIO.
    sim.load_image(0x7800, b"K8")
    sim.memory.write(0xC022, 7)
    sim.memory.write(0xC023, 3)
    assert text_rows(sim.memory)[0].startswith("K8")
    assert sim.memory.read(0xC022) == 7
    assert sim.memory.read(0xC023) == 3

    # GPIO: direction, output data and external input are independently visible.
    sim.memory.write(0xC041, 0xF0)
    sim.memory.write(0xC040, 0xA0)
    sim.memory.write(0xC042, 0x05)
    assert sim.memory.read(0xC041) == 0xF0
    assert sim.memory.read(0xC040) == 0xA0
    assert sim.memory.read(0xC042) == 0x05

    # Both frozen IRQ sources can be pending simultaneously.
    sim.memory.write(0xC001, 0x03)
    sim.memory.write(0xC012, 0x01)
    sim.memory.mmio.inject_key(0x1C)
    sim.memory.write(0xC030, 0x01)
    sim.memory.write(0xC031, 0x00)
    sim.memory.write(0xC032, 0x05)
    sim.memory.mmio.tick_timer()
    assert sim.memory.read(0xC000) == 0x03
    assert sim.memory.mmio.irq_pending()

    # Acknowledge each device independently.
    assert sim.memory.read(0xC010) == 0x1C
    assert sim.memory.read(0xC000) == 0x02
    sim.memory.write(0xC033, 0x00)
    assert sim.memory.read(0xC000) == 0x00
    assert not sim.memory.mmio.irq_pending()
