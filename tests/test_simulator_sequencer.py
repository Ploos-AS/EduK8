from simulator.datapath import Datapath
from simulator.sequencer import ControlStore, Sequencer, MAX_STEPS, decode_condition


def test_control_store_exposes_shared_fetch():
    store = ControlStore.from_spec()
    assert store.signals(0x10, 0) == ("PC_TO_MAR",)
    assert store.signals(0x10, 1) == ("MEM_READ", "MDR_LOAD")


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


def test_branch_condition_decode_all_flag_polarities():
    cases = [
        (0x88, 0x02, 2), (0x88, 0x00, 1),
        (0x89, 0x00, 2), (0x89, 0x02, 1),
        (0x8A, 0x01, 2), (0x8A, 0x00, 1),
        (0x8B, 0x00, 2), (0x8B, 0x01, 1),
        (0x8C, 0x04, 2), (0x8C, 0x00, 1),
        (0x8D, 0x00, 2), (0x8D, 0x04, 1),
        (0x8E, 0x08, 2), (0x8E, 0x00, 1),
        (0x8F, 0x00, 2), (0x8F, 0x08, 1),
    ]
    for opcode, flags, expected in cases:
        assert decode_condition(opcode, flags) == expected


def test_non_branch_condition_is_unconditional():
    assert decode_condition(0x10, 0xFF) == 0
