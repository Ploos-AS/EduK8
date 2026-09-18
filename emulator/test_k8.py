from emulator.k8 import CPU, FLAG_C, FLAG_Z, FLAG_N, FLAG_I

def run_program(program, steps=100):
    cpu = CPU()
    cpu.memory[:len(program)] = bytes(program)
    cpu.reset(pc=0)
    cpu.run(steps)
    return cpu

def test_lda_and_halt():
    cpu = run_program([0x10, 0x42, 0x01])
    assert cpu.a == 0x42
    assert cpu.pc == 3
    assert cpu.halted

def test_add():
    cpu = run_program([0x10, 0x05, 0x40, 0x03, 0x01])
    assert cpu.a == 8

def test_zero_and_negative():
    assert run_program([0x10, 0x00, 0x01]).f & FLAG_Z
    assert run_program([0x10, 0x80, 0x01]).f & FLAG_N

def test_carry():
    cpu = run_program([0x10, 0xFF, 0x06, 0x40, 0x00, 0x01])
    assert cpu.a == 0
    assert cpu.f & FLAG_C
    assert cpu.f & FLAG_Z

def test_memory_load_store():
    cpu = run_program([0x10, 0x5A, 0x29, 0x00, 0x20, 0x11, 0x00, 0x20, 0x01])
    assert cpu.a == 0x5A
    assert cpu.memory[0x2000] == 0x5A

def test_indexed_load():
    cpu = CPU()
    cpu.memory[0x2001] = 0x37
    cpu.memory[:6] = bytes([0x18, 0x01, 0x13, 0x00, 0x20, 0x01])
    cpu.reset(pc=0)
    cpu.run()
    assert cpu.a == 0x37

def test_subtract_and_compare():
    cpu = run_program([0x10, 0x08, 0x06, 0x48, 0x03, 0x68, 0x05, 0x01])
    assert cpu.a == 0x05
    assert cpu.f & FLAG_C
    assert not (cpu.f & FLAG_Z)

def test_branches():
    cpu = run_program([0x10, 0x00, 0x88, 0x02, 0x10, 0xFF, 0x01])
    assert cpu.a == 0

def test_jsr_rts():
    cpu = CPU()
    cpu.memory[:10] = bytes([0x82, 0x06, 0x00, 0x01, 0x00, 0x00, 0x10, 0x42, 0x04, 0x00])
    cpu.reset(pc=0)
    cpu.run()
    assert cpu.a == 0x42
    assert cpu.halted

def test_stack():
    cpu = run_program([0x10, 0xA5, 0x90, 0x10, 0x00, 0x91, 0x01])
    assert cpu.a == 0xA5
    assert cpu.sp == 0xFF

def test_shift_carry():
    cpu = run_program([0x10, 0x80, 0x60, 0x01])
    assert cpu.a == 0
    assert cpu.f & FLAG_C
    assert cpu.f & FLAG_Z

def test_flag_control():
    cpu = run_program([0x06, 0x08, 0x01])
    assert cpu.f & FLAG_C
    assert cpu.f & FLAG_I

def test_illegal_opcode():
    cpu = CPU()
    cpu.memory[0] = 0xFF
    cpu.reset(pc=0)
    try:
        cpu.step()
    except Exception as exc:
        assert "illegal opcode FF" in str(exc)
    else:
        raise AssertionError("illegal opcode was accepted")

def test_agu_page_crossing():
    cpu = CPU()
    assert cpu._agu_index(0x12F8, 0x10) == 0x1308
    assert cpu.aguc == 1

def test_agu_zero_page_wrap():
    cpu = CPU()
    assert cpu._agu_index(0x00F8, 0x10, zero_page=True) == 0x0008
    assert cpu.aguc == 0

def test_zero_page_pointer_wrap():
    cpu = CPU()
    cpu.memory[0x00FF] = 0x34
    cpu.memory[0x0000] = 0x12
    assert cpu._read16_zp(0xFF) == 0x1234

def test_lda_absolute_x_uses_agu():
    cpu = CPU(x=0x10)
    cpu.memory[0:3] = bytes([0x13, 0xF8, 0x12])
    cpu.memory[0x1308] = 0x5A
    cpu.step()
    assert cpu.a == 0x5A
    assert cpu.mar == 0x1308
