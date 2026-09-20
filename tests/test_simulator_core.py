from simulator.core import K8Simulator


def test_real_fetch_t0_t1_t2_through_integrated_core():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.load_image(0x8000, bytes([0x10]), force=True)

    assert sim.microstep() == ("PC_TO_MAR",)
    assert sim.datapath.mar.value == 0x8000
    assert sim.datapath.microstep == 1

    assert sim.microstep() == ("MEM_READ", "MDR_LOAD")
    assert sim.datapath.mdr.value == 0x10
    assert sim.datapath.microstep == 2

    assert sim.microstep() == ("MDR_OUT", "IR_LOAD", "PC_INC")
    assert sim.datapath.ir.value == 0x10
    assert sim.datapath.pc.value == 0x8001
    assert sim.datapath.microstep == 3


def test_clock_rising_edge_executes_microstep():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8123)
    assert sim.clock_step() == 1
    assert sim.datapath.mar.value == 0x8123
    assert sim.datapath.microstep == 1
    assert sim.clock_step() == 0
    assert sim.datapath.microstep == 1


def test_reset_blocks_execution_until_released():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.reset()
    assert sim.microstep() == ()
    assert sim.datapath.microstep == 0
    sim.release_reset()
    sim.microstep()
    assert sim.datapath.microstep == 1


def test_snapshot_exposes_integrated_machine_state():
    sim = K8Simulator()
    snap = sim.snapshot()
    assert snap["registers"]["SP"] == 0xFF
    assert snap["microstep"] == 0
    assert snap["halted"] is False
    assert snap["condition"] == 0


def test_complete_nop_instruction_returns_to_fetch():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.load_image(0x8000, bytes([0x00]), force=True)
    used = sim.instruction_step()
    assert used == 4
    assert sim.datapath.ir.value == 0x00
    assert sim.datapath.pc.value == 0x8001
    assert sim.datapath.microstep == 0
    assert sim.sequencer.halted is False


def test_complete_lda_immediate_instruction():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.load_image(0x8000, bytes([0x10, 0x42]), force=True)
    used = sim.instruction_step()
    assert used == 6
    assert sim.datapath.a.value == 0x42
    assert sim.datapath.pc.value == 0x8002
    assert sim.datapath.microstep == 0


def test_core_decodes_x_index_source_from_opcode():
    sim = K8Simulator()
    sim.datapath.ir.load(0x13)  # LDA abs,X
    sim.datapath.x.load(0x21)
    sim.datapath.mar.load(0x12F0)
    from simulator.control import apply_controls
    from simulator.core import INDEX_SELECT
    apply_controls(
        sim.datapath,
        ("AGU_ADD_LO", "AGUC_LOAD"),
        agu_index_select=INDEX_SELECT[sim.datapath.ir.value],
    )
    assert sim.datapath.agu_index_select == 1
    assert sim.datapath.agu_index_value == 0x21
    assert sim.datapath.mar.value == 0x1211
    assert sim.datapath.aguc == 1


def test_isa_index_decoder_covers_x_y_and_nonindexed_modes():
    from simulator.core import INDEX_SELECT
    assert INDEX_SELECT[0x13] == 1  # LDA abs,X
    assert INDEX_SELECT[0x14] == 2  # LDA abs,Y
    assert INDEX_SELECT[0x10] == 0  # LDA immediate
    assert INDEX_SELECT[0x1B] == 2  # LDX abs,Y


def test_complete_lda_absolute_x_with_page_cross():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.datapath.x.load(0x20)
    sim.load_image(0x8000, bytes([0x13, 0xF0, 0x12]), force=True)
    sim.load_image(0x1310, bytes([0xA5]), force=True)
    used = sim.instruction_step()
    assert used == 14
    assert sim.datapath.a.value == 0xA5
    assert sim.datapath.pc.value == 0x8003
    assert sim.datapath.mar.value == 0x1310
    assert sim.datapath.agu_index_select == 1
    assert sim.datapath.aguc == 1
    assert sim.datapath.microstep == 0


def test_complete_lda_absolute_y_without_page_cross():
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.datapath.y.load(0x0F)
    sim.load_image(0x8000, bytes([0x14, 0x30, 0x12]), force=True)
    sim.load_image(0x123F, bytes([0x5A]), force=True)
    used = sim.instruction_step()
    assert used == 14
    assert sim.datapath.a.value == 0x5A
    assert sim.datapath.pc.value == 0x8003
    assert sim.datapath.mar.value == 0x123F
    assert sim.datapath.agu_index_select == 2
    assert sim.datapath.aguc == 0


import pytest


@pytest.mark.parametrize(
    "opcode,a,carry,result,expected_carry",
    [
        (0x5C, 0x55, 0, 0xAA, 0),  # NOT
        (0x60, 0x81, 0, 0x02, 1),  # SHL
        (0x61, 0x81, 0, 0x40, 1),  # SHR
        (0x62, 0x80, 1, 0x01, 1),  # ROL
        (0x63, 0x01, 1, 0x80, 1),  # ROR
    ],
)
def test_unary_shift_instructions_end_to_end(opcode, a, carry, result, expected_carry):
    sim = K8Simulator()
    sim.datapath.pc.load(0x8000)
    sim.datapath.a.load(a)
    sim.datapath.flags.load(carry)
    sim.load_image(0x8000, bytes([opcode]), force=True)
    used = sim.instruction_step()
    assert used == 4
    assert sim.datapath.a.value == result
    assert sim.datapath.pc.value == 0x8001
    assert sim.datapath.microstep == 0
    if opcode != 0x5C:
        assert (sim.datapath.flags.value & 0x01) == expected_carry


def _run_branch(opcode, offset, flags, start=0x8000):
    sim = K8Simulator()
    sim.load_image(start, bytes([opcode, offset]))
    sim.datapath.pc.load(start)
    sim.datapath.flags.load(flags)
    sim.release_reset()
    steps = sim.instruction_step()
    return sim, steps


def test_relative_branch_taken_positive_and_observable():
    sim, steps = _run_branch(0x88, 0x05, 0x02)
    assert sim.datapath.pc.value == 0x8007
    assert sim.datapath.branch_taken is True
    assert sim.datapath.branch_displacement == 5
    assert sim.datapath.branch_pc_before == 0x8002
    assert sim.datapath.branch_pc_after == 0x8007
    assert steps == 6


def test_relative_branch_not_taken():
    sim, _ = _run_branch(0x88, 0x05, 0x00)
    assert sim.datapath.pc.value == 0x8002
    assert sim.datapath.branch_taken is False


def test_relative_branch_taken_negative():
    sim, _ = _run_branch(0x89, 0xFC, 0x00)
    assert sim.datapath.pc.value == 0x7FFE
    assert sim.datapath.branch_displacement == -4


def test_relative_branch_wraparound_forward_and_backward():
    sim, _ = _run_branch(0x8A, 0x7F, 0x01, start=0xFF80)
    assert sim.datapath.pc.value == 0x0001
    sim, _ = _run_branch(0x8B, 0x80, 0x00, start=0x0000)
    assert sim.datapath.pc.value == 0xFF82
