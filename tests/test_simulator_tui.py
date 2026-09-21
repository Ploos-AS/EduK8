import pytest

from simulator.core import K8Simulator
from simulator.tui import execute


def test_tui_executes_step_commands():
    sim = K8Simulator()
    sim.load_image(0x8000, bytes([0x00]), force=True)
    sim.datapath.pc.load(0x8000)
    sim.release_reset()

    assert execute(sim, "micro")
    assert sim.datapath.microstep != 0 or sim.datapath.clock != 0
    assert execute(sim, "show")
    assert not execute(sim, "quit")


def test_tui_reset_and_release():
    sim = K8Simulator()
    execute(sim, "reset")
    assert sim.datapath.reset
    execute(sim, "release")
    assert not sim.datapath.reset


def test_tui_rejects_unknown_command():
    with pytest.raises(ValueError):
        execute(K8Simulator(), "banana")


def test_tui_loads_hex_bytes_and_inspects_memory(capsys):
    sim = K8Simulator()
    assert execute(sim, "load 0x8000 10 42 00")
    assert [sim.memory.read(0x8000 + i) for i in range(3)] == [0x10, 0x42, 0x00]

    assert execute(sim, "mem 0x8000 3")
    assert capsys.readouterr().out == "8000: 10 42 00\n"


def test_tui_memory_commands_validate_arguments():
    sim = K8Simulator()
    with pytest.raises(ValueError):
        execute(sim, "mem")
    with pytest.raises(ValueError):
        execute(sim, "load 0x8000")


def test_tui_gpio_switches_and_register_view(capsys):
    sim = K8Simulator()
    assert execute(sim, "gpio input 0xA5")
    assert execute(sim, "gpio dir 0xF0")
    assert execute(sim, "gpio data 0x3C")
    assert sim.memory.read(0xC042) == 0xA5
    assert sim.memory.read(0xC041) == 0xF0
    assert sim.memory.read(0xC040) == 0x3C

    assert execute(sim, "gpio")
    assert capsys.readouterr().out == "GPIO DATA=3C DIR=F0 INPUT=A5\n"


def test_tui_gpio_rejects_bad_form():
    with pytest.raises(ValueError):
        execute(K8Simulator(), "gpio banana 1")


def test_tui_keyboard_injection_and_one_byte_overrun():
    sim = K8Simulator()
    assert execute(sim, "key 0x1C")
    assert sim.memory.read(0xC011) == 0x01
    assert sim.memory.read(0xC010) == 0x1C
    assert sim.memory.read(0xC011) == 0x00

    execute(sim, "key 0x1D")
    execute(sim, "key 0x1E")
    assert sim.memory.read(0xC011) == 0x03
    assert sim.memory.read(0xC010) == 0x1D


def test_tui_key_requires_one_byte():
    with pytest.raises(ValueError):
        execute(K8Simulator(), "key")
