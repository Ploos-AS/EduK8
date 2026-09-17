from emulator.microcode import microcode_for

def names(opcode):
    return [op.name for op in microcode_for(opcode)]

def test_every_instruction_starts_with_fetch():
    assert names(0x10)[:4] == ["ADDRESS", "READ", "LATCH", "INCREMENT"]

def test_lda_immediate_exposes_data_path():
    ops = microcode_for(0x10)
    assert any(op.destination == "A" for op in ops)
    assert any(op.destination == "Z,N" for op in ops)

def test_add_exposes_alu():
    ops = microcode_for(0x40)
    assert any(op.name == "ALU_ADD" for op in ops)
    assert any(op.destination == "C,Z,N,V" for op in ops)

def test_unknown_detail_remains_explicit():
    assert names(0x12)[-1] == "EXECUTE"
