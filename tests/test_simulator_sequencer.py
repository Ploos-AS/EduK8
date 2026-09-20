from simulator.datapath import Datapath
from simulator.sequencer import ControlStore, Sequencer, MAX_STEPS


def test_control_store_exposes_shared_fetch():
    store = ControlStore.from_spec()
    assert store.signals(0x10, 0) == ("PC_TO_MAR",)\n    assert store.signals(0x10, 1) == ("MEM_READ", "MDR_LOAD")


def test_opcode_microstep_lookup():
    store = ControlStore.from_spec()
    signals = store.signals(0x10, 5)
    assert "A_LOAD" in signals
    assert "INSTR_DONE" in signals


def test_reset_and_release():
    dp = Datapath()
    dp.microstep = 12
    seq = Sequencer(dp)
    seq.reset()
    assert dp.reset is True
    assert dp.microstep == 0
    assert seq.current_signals() == ()
    seq.release_reset()
    assert dp.reset is False


def test_microstep_advances_and_wraps():
    dp = Datapath()
    seq = Sequencer(dp, ControlStore())
    seq.advance(())
    assert dp.microstep == 1
    dp.microstep = MAX_STEPS - 1
    seq.advance(())
    assert dp.microstep == 0


def test_instruction_done_returns_to_fetch():
    dp = Datapath()
    dp.microstep = 7
    seq = Sequencer(dp, ControlStore())
    seq.advance(("INSTR_DONE",))
    assert dp.microstep == 0


def test_halt_stops_control_lookup():
    dp = Datapath()
    seq = Sequencer(dp, ControlStore(fetch={0: ("HALT",)}))
    assert seq.current_signals() == ("HALT",)
    seq.advance(("HALT",))
    assert seq.halted is True
    assert seq.current_signals() == ()


def test_clock_is_explicit_and_deterministic():
    dp = Datapath()
    seq = Sequencer(dp, ControlStore())
    assert dp.clock == 0
    assert seq.tick_clock() == 1
    assert seq.tick_clock() == 0
