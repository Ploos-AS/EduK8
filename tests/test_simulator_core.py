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
    assert sim.datapath.agu_index_select == 0
    assert sim.datapath.agu_index_value == 0
    assert sim.datapath.aguc == 0
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
    assert sim.datapath.agu_index_select == 0
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


def test_load_zero_page_and_absolute_addressing():
    cases = [
        (0x11, [0x42], 0x0042, "a", 0xA5),
        (0x19, [0x43], 0x0043, "x", 0x80),
        (0x21, [0x44], 0x0044, "y", 0x00),
        (0x12, [0x34, 0x12], 0x1234, "a", 0x5A),
        (0x1A, [0x35, 0x12], 0x1235, "x", 0x7E),
        (0x22, [0x36, 0x12], 0x1236, "y", 0x81),
    ]
    for opcode, operand, address, register, value in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode, *operand]))
        sim.load_image(address, bytes([value]))
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert getattr(sim.datapath, register).value == value
        assert sim.datapath.pc.value == 0x8000 + 1 + len(operand)
        assert bool(sim.datapath.flags.value & 0x02) == (value == 0)
        assert bool(sim.datapath.flags.value & 0x04) == bool(value & 0x80)


def test_absolute_indexed_loads_use_frozen_agu():
    cases = [
        (0x1B, 0x12F0, 0x20, "y", "x", 0xA6, 0x1310),
        (0x23, 0x1230, 0x0F, "x", "y", 0x5B, 0x123F),
    ]
    for opcode, base, index, index_reg, target_reg, value, effective in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode, base & 0xFF, base >> 8]))
        sim.load_image(effective, bytes([value]))
        getattr(sim.datapath, index_reg).load(index)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert getattr(sim.datapath, target_reg).value == value
        assert sim.datapath.pc.value == 0x8003
        assert sim.datapath.mar.value == effective


def test_zero_page_indexed_loads_wrap_within_page_zero():
    cases = [
        (0x16, 0xF0, 0x20, "x", "a", 0xA1, 0x10),
        (0x1C, 0xF8, 0x10, "y", "x", 0xB2, 0x08),
        (0x24, 0x40, 0x05, "x", "y", 0xC3, 0x45),
    ]
    for opcode, base, index, index_reg, target_reg, value, effective in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode, base]))
        sim.load_image(effective, bytes([value]))
        getattr(sim.datapath, index_reg).load(index)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert getattr(sim.datapath, target_reg).value == value
        assert sim.datapath.pc.value == 0x8002
        assert sim.datapath.mar.value == effective
        assert sim.datapath.aguc == 0


def test_direct_store_family_zero_page_and_absolute():
    cases = [
        (0x28, "a", 0x42, 0x0042, 0xA1),
        (0x30, "x", 0x43, 0x0043, 0xB2),
        (0x34, "y", 0x44, 0x0044, 0xC3),
        (0x29, "a", 0x34, 0x1234, 0xD4),
        (0x31, "x", 0x35, 0x1235, 0xE5),
        (0x35, "y", 0x36, 0x1236, 0xF6),
    ]
    for opcode, reg, low, address, value in cases:
        sim = K8Simulator()
        operand = bytes([low]) if address < 0x100 else bytes([low, address >> 8])
        sim.load_image(0x8000, bytes([opcode]) + operand)
        getattr(sim.datapath, reg).load(value)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert sim.memory.read(address) == value
        assert sim.datapath.pc.value == 0x8000 + 1 + len(operand)
        assert sim.datapath.mar.value == address


def test_indexed_store_family_uses_agu_and_zero_page_wrap():
    cases = [
        (0x2A, "a", 0xD1, "x", 0x20, bytes([0xF0, 0x12]), 0x1310),
        (0x2B, "a", 0xD2, "y", 0x0F, bytes([0x30, 0x12]), 0x123F),
        (0x2C, "a", 0xD3, "x", 0x20, bytes([0xF0]), 0x0010),
        (0x32, "x", 0xD4, "y", 0x10, bytes([0xF8]), 0x0008),
        (0x36, "y", 0xD5, "x", 0x05, bytes([0x40]), 0x0045),
    ]
    for opcode, source, value, index_reg, index, operand, address in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode]) + operand)
        getattr(sim.datapath, source).load(value)
        getattr(sim.datapath, index_reg).load(index)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert sim.memory.read(address) == value
        assert sim.datapath.pc.value == 0x8001 + len(operand)
        assert sim.datapath.mar.value == address
        assert sim.datapath.aguc == 0


def test_alu_zero_page_and_absolute_addressing():
    cases = [
        (0x41, bytes([0x42]), 0x0042, 0x20, 0x22, 0x42),
        (0x49, bytes([0x43]), 0x0043, 0x30, 0x10, 0x1F),
        (0x51, bytes([0x44]), 0x0044, 0xA5, 0x0F, 0x05),
        (0x56, bytes([0x34, 0x12]), 0x1234, 0xA0, 0x0F, 0xAF),
        (0x5A, bytes([0x35, 0x12]), 0x1235, 0xAA, 0xFF, 0x55),
        (0x42, bytes([0x36, 0x12]), 0x1236, 0x7F, 0x01, 0x80),
    ]
    for opcode, operand, address, initial_a, rhs, expected in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode]) + operand)
        sim.load_image(address, bytes([rhs]))
        sim.datapath.a.load(initial_a)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert sim.datapath.a.value == expected
        assert sim.datapath.pc.value == 0x8001 + len(operand)
        assert sim.datapath.mar.value == address


def test_indexed_add_sub_use_agu_with_page_crossing():
    cases = [
        (0x43, "x", 0x20, 0x12F0, 0x1310, 0x20, 0x22, 0x42),
        (0x44, "y", 0x0F, 0x1230, 0x123F, 0x10, 0x05, 0x15),
        (0x4B, "x", 0x20, 0x12F0, 0x1310, 0x30, 0x10, 0x1F),
        (0x4C, "y", 0x0F, 0x1230, 0x123F, 0x20, 0x05, 0x1A),
    ]
    for opcode, index_reg, index, base, effective, initial_a, rhs, expected in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode, base & 0xFF, base >> 8]))
        sim.load_image(effective, bytes([rhs]))
        sim.datapath.a.load(initial_a)
        getattr(sim.datapath, index_reg).load(index)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert sim.datapath.a.value == expected
        assert sim.datapath.mar.value == effective
        assert sim.datapath.pc.value == 0x8003
        assert sim.datapath.aguc == 0


def test_compare_family_all_addressing_modes_preserves_registers_and_vi():
    cases = [
        (0x68, "a", 0x40, bytes([0x40]), None, 0x0B),
        (0x69, "a", 0x20, bytes([0x42]), (0x0042, 0x30), 0x0C),
        (0x6A, "a", 0x30, bytes([0x34, 0x12]), (0x1234, 0x10), 0x09),
        (0x6C, "x", 0x55, bytes([0x55]), None, 0x0B),
        (0x6D, "x", 0x10, bytes([0x43]), (0x0043, 0x20), 0x0C),
        (0x6E, "x", 0x40, bytes([0x35, 0x12]), (0x1235, 0x20), 0x09),
        (0x70, "y", 0x01, bytes([0x01]), None, 0x0B),
        (0x71, "y", 0x80, bytes([0x44]), (0x0044, 0x01), 0x09),
        (0x72, "y", 0x00, bytes([0x36, 0x12]), (0x1236, 0x01), 0x0C),
    ]
    for opcode, reg, value, operand, memory, expected_cznv in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode]) + operand)
        if memory:
            sim.load_image(memory[0], bytes([memory[1]]))
        getattr(sim.datapath, reg).load(value)
        sim.datapath.flags.load(0x18)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert getattr(sim.datapath, reg).value == value
        assert sim.datapath.flags.value == (0x10 | expected_cznv)
        assert sim.datapath.pc.value == 0x8001 + len(operand)


def test_register_increment_decrement_updates_zn_and_preserves_other_flags():
    cases = [
        (0x7C, "x", 0x7F, 0x80),
        (0x7D, "x", 0x01, 0x00),
        (0x7E, "y", 0xFF, 0x00),
        (0x7F, "y", 0x00, 0xFF),
    ]
    for opcode, reg, initial, expected in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode]))
        getattr(sim.datapath, reg).load(initial)
        sim.datapath.a.load(1)
        sim.datapath.flags.load(0x18)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert getattr(sim.datapath, reg).value == expected
        assert sim.datapath.flags.value & 0x18 == 0x18
        assert bool(sim.datapath.flags.value & 0x02) == (expected == 0)
        assert bool(sim.datapath.flags.value & 0x04) == bool(expected & 0x80)


def test_memory_inc_dec_zero_page_and_absolute_read_modify_write():
    cases = [
        (0x78, bytes([0x42]), 0x0042, 0xFF, 0x00),
        (0x79, bytes([0x34, 0x12]), 0x1234, 0x7F, 0x80),
        (0x7A, bytes([0x43]), 0x0043, 0x00, 0xFF),
        (0x7B, bytes([0x35, 0x12]), 0x1235, 0x01, 0x00),
    ]
    for opcode, operand, address, initial, expected in cases:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([opcode]) + operand)
        sim.load_image(address, bytes([initial]))
        sim.datapath.a.load(0x55)
        sim.datapath.x.load(0x66)
        sim.datapath.y.load(0x77)
        sim.datapath.flags.load(0x19)
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert sim.memory.read(address) == expected
        assert (sim.datapath.a.value, sim.datapath.x.value, sim.datapath.y.value) == (0x55, 0x66, 0x77)
        assert sim.datapath.flags.value & 0x19 == 0x19
        assert bool(sim.datapath.flags.value & 0x02) == (expected == 0)
        assert bool(sim.datapath.flags.value & 0x04) == bool(expected & 0x80)


def test_jmp_absolute_loads_encoded_target():
    sim = K8Simulator()
    sim.load_image(0x8000, bytes([0x80, 0x34, 0x12]))
    sim.datapath.pc.load(0x8000)
    sim.release_reset()
    sim.instruction_step()
    assert sim.datapath.pc.value == 0x1234


def test_jmp_indirect_reads_little_endian_target_and_wraps_pointer():
    for pointer, low_address, high_address in [(0x2345, 0x2345, 0x2346), (0xFFFF, 0xFFFF, 0x0000)]:
        sim = K8Simulator()
        sim.load_image(0x8000, bytes([0x81, pointer & 0xFF, pointer >> 8]))
        sim.load_image(low_address, bytes([0x78]))
        sim.load_image(high_address, bytes([0x56]))
        sim.datapath.pc.load(0x8000)
        sim.release_reset()
        sim.instruction_step()
        assert sim.datapath.pc.value == 0x5678


def test_jsr_pushes_next_pc_and_rts_returns_exactly_to_it():
    sim = K8Simulator()
    sim.load_image(0x8000, bytes([0x82, 0x00, 0x90]))
    sim.load_image(0x9000, bytes([0x04]))
    sim.datapath.sp.load(0xFF)
    sim.datapath.pc.load(0x8000)
    sim.release_reset()

    sim.instruction_step()
    assert sim.datapath.pc.value == 0x9000
    assert sim.datapath.sp.value == 0xFD
    assert sim.memory.read(0x01FF) == 0x80
    assert sim.memory.read(0x01FE) == 0x03

    sim.instruction_step()
    assert sim.datapath.pc.value == 0x8003
    assert sim.datapath.sp.value == 0xFF


def test_stack_push_pull_accumulator_and_flags():
    sim = K8Simulator()
    sim.load_image(0x8000, bytes([0x90, 0x91, 0x92, 0x93]))
    sim.datapath.a.load(0xA5)
    sim.datapath.flags.load(0x19)
    sim.datapath.sp.load(0xFF)
    sim.datapath.pc.load(0x8000)
    sim.release_reset()

    sim.instruction_step()
    assert sim.memory.read(0x01FF) == 0xA5
    assert sim.datapath.sp.value == 0xFE

    sim.datapath.a.load(0)
    sim.instruction_step()
    assert sim.datapath.a.value == 0xA5
    assert sim.datapath.sp.value == 0xFF

    # PLA updates Z/N from the pulled accumulator; restore the intended
    # flag image before testing PHP/PLP themselves.
    sim.datapath.flags.load(0x19)
    sim.instruction_step()
    assert sim.memory.read(0x01FF) == 0x19
    assert sim.datapath.sp.value == 0xFE

    sim.datapath.flags.load(0)
    sim.instruction_step()
    assert sim.datapath.flags.value == 0x19
    assert sim.datapath.sp.value == 0xFF


def test_brk_rti_round_trip_interrupt_frame():
    sim = K8Simulator()
    sim.load_image(0x8000, bytes([0x02]))
    sim.load_image(0x9000, bytes([0x03]))
    sim.load_image(0xFFFE, bytes([0x00, 0x90]), force=True)
    sim.datapath.flags.load(0x09)
    sim.datapath.sp.load(0xFF)
    sim.datapath.pc.load(0x8000)
    sim.release_reset()

    sim.instruction_step()
    assert sim.datapath.pc.value == 0x9000
    assert sim.datapath.sp.value == 0xFC
    assert sim.memory.read(0x01FF) == 0x80
    assert sim.memory.read(0x01FE) == 0x01
    assert sim.memory.read(0x01FD) == 0x29
    assert sim.datapath.flags.value == 0x19

    sim.instruction_step()
    assert sim.datapath.pc.value == 0x8001
    assert sim.datapath.sp.value == 0xFF
    assert sim.datapath.flags.value == 0x09


def test_zero_page_indirect_load_store_and_pointer_wrap():
    sim = K8Simulator()
    sim.load_image(0x8000, bytes([0x15, 0xFF, 0x2D, 0x20]))
    sim.load_image(0x00FF, bytes([0x34]))
    sim.load_image(0x0000, bytes([0x12]))
    sim.load_image(0x1234, bytes([0x80]))
    sim.load_image(0x0020, bytes([0x78, 0x56]))
    sim.datapath.flags.load(0x11)
    sim.datapath.pc.load(0x8000)
    sim.release_reset()

    sim.instruction_step()
    assert sim.datapath.a.value == 0x80
    assert sim.datapath.flags.value & 0x04
    assert sim.datapath.flags.value & 0x11 == 0x11

    sim.instruction_step()
    assert sim.memory.read(0x5678) == 0x80
