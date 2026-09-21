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
