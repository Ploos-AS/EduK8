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
