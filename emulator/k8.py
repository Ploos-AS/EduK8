from dataclasses import dataclass, field

from emulator.io import IO

FLAG_C = 1 << 0
FLAG_Z = 1 << 1
FLAG_N = 1 << 2
FLAG_V = 1 << 3
FLAG_I = 1 << 4
FLAG_B = 1 << 5

class K8IllegalOpcode(Exception):
    pass

@dataclass
class CPU:
    a: int = 0
    x: int = 0
    y: int = 0
    pc: int = 0
    sp: int = 0xFF
    f: int = 0
    halted: bool = False
    mar: int = 0
    aguc: int = 0
    trace_enabled: bool = False
    trace: list = field(default_factory=list)
    memory: bytearray = field(default_factory=lambda: bytearray(65536))
    io: IO = field(default_factory=IO)

    def reset(self, pc=None):
        self.a = self.x = self.y = 0
        self.sp = 0xFF
        self.f = 0
        self.halted = False
        self.mar = 0
        self.aguc = 0
        self.trace.clear()
        self.pc = ((self.memory[0xFFFC] | self.memory[0xFFFD] << 8)
                   if pc is None else pc) & 0xFFFF

    def _fetch8(self):
        value = self.memory[self.pc]
        self.pc = (self.pc + 1) & 0xFFFF
        return value

    def _fetch16(self):
        lo = self._fetch8()
        hi = self._fetch8()
        return lo | (hi << 8)

    def _read16(self, address):
        return self.memory[address] | (self.memory[(address + 1) & 0xFFFF] << 8)

    def _read8(self, address):
        address &= 0xFFFF
        value = self.io.read(address)
        return self.memory[address] if value is None else value

    def _write8(self, address, value):
        address &= 0xFFFF
        if not self.io.write(address, value):
            self.memory[address] = value & 0xFF

    def _push8(self, value):
        self.memory[0x0100 | self.sp] = value & 0xFF
        self.sp = (self.sp - 1) & 0xFF

    def _pop8(self):
        self.sp = (self.sp + 1) & 0xFF
        return self.memory[0x0100 | self.sp]

    def _set_zn(self, value):
        value &= 0xFF
        self.f &= ~(FLAG_Z | FLAG_N)
        if value == 0:
            self.f |= FLAG_Z
        if value & 0x80:
            self.f |= FLAG_N

    def _add(self, rhs):
        lhs = self.a
        carry = 1 if self.f & FLAG_C else 0
        result = lhs + rhs + carry
        value = result & 0xFF
        self.f &= ~(FLAG_C | FLAG_Z | FLAG_N | FLAG_V)
        if result > 0xFF:
            self.f |= FLAG_C
        if value == 0:
            self.f |= FLAG_Z
        if value & 0x80:
            self.f |= FLAG_N
        if (~(lhs ^ rhs) & (lhs ^ value) & 0x80):
            self.f |= FLAG_V
        self.a = value

    def _sub(self, rhs):
        lhs = self.a
        borrow = 0 if self.f & FLAG_C else 1
        result = lhs - rhs - borrow
        value = result & 0xFF
        self.f &= ~(FLAG_C | FLAG_Z | FLAG_N | FLAG_V)
        if result >= 0:
            self.f |= FLAG_C
        if value == 0:
            self.f |= FLAG_Z
        if value & 0x80:
            self.f |= FLAG_N
        if ((lhs ^ rhs) & (lhs ^ value) & 0x80):
            self.f |= FLAG_V
        self.a = value

    def _cmp(self, lhs, rhs):
        value = (lhs - rhs) & 0xFF
        self.f &= ~(FLAG_C | FLAG_Z | FLAG_N)
        if lhs >= rhs:
            self.f |= FLAG_C
        if value == 0:
            self.f |= FLAG_Z
        if value & 0x80:
            self.f |= FLAG_N

    def _branch(self, condition):
        offset = self._fetch8()
        if condition:
            if offset & 0x80:
                offset -= 0x100
            self.pc = (self.pc + offset) & 0xFFFF

    def _agu_index(self, base, index, zero_page=False):
        base &= 0xFFFF
        index &= 0xFF
        low_sum = (base & 0xFF) + index
        carry = 1 if low_sum > 0xFF else 0
        low = low_sum & 0xFF
        if zero_page:
            self.mar = low
            self.aguc = 0
        else:
            self.aguc = carry
            high = ((base >> 8) + carry) & 0xFF
            self.mar = (high << 8) | low
        if self.trace_enabled:
            self.trace.append({"phase": "AGU", "base": base, "index": index, "zero_page": zero_page, "result": self.mar, "carry": carry})
        return self.mar

    def _read16_zp(self, address):
        lo_addr = address & 0xFF
        hi_addr = (lo_addr + 1) & 0xFF
        return self.memory[lo_addr] | (self.memory[hi_addr] << 8)

    def _load_a(self, address):
        self.a = self._read8(address)
        self._set_zn(self.a)

    irq_line: bool = False

    def _enter_interrupt(self, break_marker=False):
        self._push8((self.pc >> 8) & 0xFF)
        self._push8(self.pc & 0xFF)
        stacked_f = (self.f & (FLAG_C | FLAG_Z | FLAG_N | FLAG_V | FLAG_I))
        if break_marker:
            stacked_f |= FLAG_B
        self._push8(stacked_f)
        self.f = (self.f | FLAG_I) & ~FLAG_B
        self.pc = self._read16(0xFFFE)

    def step(self):
        if self.halted:
            return
        if self.irq_line and not (self.f & FLAG_I):
            self._enter_interrupt(False)
            return
        pc_before = self.pc
        opcode = self._fetch8()
        if self.trace_enabled:
            self.trace.append({"phase": "FETCH", "pc": pc_before, "opcode": opcode, "micro_ops": ["PC -> address bus", "memory -> data bus", "data bus -> IR", "PC++"]})

        if opcode == 0x00: return
        if opcode == 0x01:
            self.halted = True
            return
        if opcode == 0x02:
            self._enter_interrupt(True)
            return
        if opcode == 0x05:
            self.f &= ~FLAG_C
            return
        if opcode == 0x06:
            self.f |= FLAG_C
            return
        if opcode == 0x07:
            self.f &= ~FLAG_I
            return
        if opcode == 0x08:
            self.f |= FLAG_I
            return
        if opcode == 0x09:
            self.f &= ~FLAG_V
            return
        if opcode in (0x0A, 0x0B):
            raise K8IllegalOpcode(f"illegal opcode {opcode:02X} at {pc_before:04X}")

        if opcode == 0x10:
            self.a = self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x11:
            self._load_a(self._fetch8()); return
        if opcode == 0x12:
            self._load_a(self._fetch16()); return
        if opcode == 0x13:
            self._load_a(self._agu_index(self._fetch16(), self.x)); return
        if opcode == 0x14:
            self._load_a(self._agu_index(self._fetch16(), self.y)); return
        if opcode == 0x15:
            self._load_a(self._read16_zp(self._fetch8())); return
        if opcode == 0x16:
            self._load_a(self._agu_index(self._fetch8(), self.x, zero_page=True)); return

        if opcode == 0x18:
            self.x = self._fetch8(); self._set_zn(self.x); return
        if opcode == 0x19:
            self.x = self.memory[self._fetch8()]; self._set_zn(self.x); return
        if opcode == 0x1A:
            self.x = self.memory[self._fetch16()]; self._set_zn(self.x); return
        if opcode == 0x1B:
            self.x = self.memory[self._agu_index(self._fetch16(), self.y)]; self._set_zn(self.x); return
        if opcode == 0x1C:
            self.x = self.memory[self._agu_index(self._fetch8(), self.y, zero_page=True)]; self._set_zn(self.x); return

        if opcode == 0x20:
            self.y = self._fetch8(); self._set_zn(self.y); return
        if opcode == 0x21:
            self.y = self.memory[self._fetch8()]; self._set_zn(self.y); return
        if opcode == 0x22:
            self.y = self.memory[self._fetch16()]; self._set_zn(self.y); return
        if opcode == 0x23:
            self.y = self.memory[self._agu_index(self._fetch16(), self.x)]; self._set_zn(self.y); return
        if opcode == 0x24:
            self.y = self.memory[self._agu_index(self._fetch8(), self.x, zero_page=True)]; self._set_zn(self.y); return

        if opcode == 0x28:
            self._write8(self._fetch8(), self.a); return
        if opcode == 0x29:
            self._write8(self._fetch16(), self.a); return
        if opcode == 0x2A:
            self._write8(self._fetch16() + self.x, self.a); return
        if opcode == 0x2B:
            self._write8(self._fetch16() + self.y, self.a); return
        if opcode == 0x2C:
            self._write8(self._fetch8() + self.x, self.a); return
        if opcode == 0x2D:
            self._write8(self._read16(self._fetch8()), self.a); return

        if opcode == 0x30:
            self._write8(self._fetch8(), self.x); return
        if opcode == 0x31:
            self._write8(self._fetch16(), self.x); return
        if opcode == 0x32:
            self._write8(self._fetch8() + self.y, self.x); return
        if opcode == 0x34:
            self._write8(self._fetch8(), self.y); return
        if opcode == 0x35:
            self._write8(self._fetch16(), self.y); return
        if opcode == 0x36:
            self._write8(self._fetch8() + self.x, self.y); return

        if opcode == 0x40: self._add(self._fetch8()); return
        if opcode == 0x41: self._add(self.memory[self._fetch8()]); return
        if opcode == 0x42: self._add(self.memory[self._fetch16()]); return
        if opcode == 0x43: self._add(self.memory[(self._fetch16() + self.x) & 0xFFFF]); return
        if opcode == 0x44: self._add(self.memory[(self._fetch16() + self.y) & 0xFFFF]); return
        if opcode == 0x48: self._sub(self._fetch8()); return
        if opcode == 0x49: self._sub(self.memory[self._fetch8()]); return
        if opcode == 0x4A: self._sub(self.memory[self._fetch16()]); return
        if opcode == 0x4B: self._sub(self.memory[(self._fetch16() + self.x) & 0xFFFF]); return
        if opcode == 0x4C: self._sub(self.memory[(self._fetch16() + self.y) & 0xFFFF]); return

        if opcode == 0x50: self.a &= self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x51: self.a &= self.memory[self._fetch8()]; self._set_zn(self.a); return
        if opcode == 0x52: self.a &= self.memory[self._fetch16()]; self._set_zn(self.a); return
        if opcode == 0x54: self.a |= self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x55: self.a |= self.memory[self._fetch8()]; self._set_zn(self.a); return
        if opcode == 0x56: self.a |= self.memory[self._fetch16()]; self._set_zn(self.a); return
        if opcode == 0x58: self.a ^= self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x59: self.a ^= self.memory[self._fetch8()]; self._set_zn(self.a); return
        if opcode == 0x5A: self.a ^= self.memory[self._fetch16()]; self._set_zn(self.a); return
        if opcode == 0x5C: self.a = (~self.a) & 0xFF; self._set_zn(self.a); return

        if opcode == 0x60:
            carry = (self.a >> 7) & 1
            self.a = (self.a << 1) & 0xFF
            self.f = (self.f & ~FLAG_C) | (FLAG_C if carry else 0)
            self._set_zn(self.a); return
        if opcode == 0x61:
            carry = self.a & 1
            self.a >>= 1
            self.f = (self.f & ~FLAG_C) | (FLAG_C if carry else 0)
            self._set_zn(self.a); return
        if opcode == 0x62:
            old = 1 if self.f & FLAG_C else 0
            carry = (self.a >> 7) & 1
            self.a = ((self.a << 1) & 0xFF) | old
            self.f = (self.f & ~FLAG_C) | (FLAG_C if carry else 0)
            self._set_zn(self.a); return
        if opcode == 0x63:
            old = 1 if self.f & FLAG_C else 0
            carry = self.a & 1
            self.a = (self.a >> 1) | (old << 7)
            self.f = (self.f & ~FLAG_C) | (FLAG_C if carry else 0)
            self._set_zn(self.a); return

        if opcode == 0x68: self._cmp(self.a, self._fetch8()); return
        if opcode == 0x69: self._cmp(self.a, self.memory[self._fetch8()]); return
        if opcode == 0x6A: self._cmp(self.a, self.memory[self._fetch16()]); return
        if opcode == 0x6C: self._cmp(self.x, self._fetch8()); return
        if opcode == 0x6D: self._cmp(self.x, self.memory[self._fetch8()]); return
        if opcode == 0x6E: self._cmp(self.x, self.memory[self._fetch16()]); return
        if opcode == 0x70: self._cmp(self.y, self._fetch8()); return
        if opcode == 0x71: self._cmp(self.y, self.memory[self._fetch8()]); return
        if opcode == 0x72: self._cmp(self.y, self.memory[self._fetch16()]); return

        if opcode == 0x78:
            address = self._fetch8(); value = (self.memory[address] + 1) & 0xFF
            self.memory[address] = value; self._set_zn(value); return
        if opcode == 0x79:
            address = self._fetch16(); value = (self.memory[address] + 1) & 0xFF
            self.memory[address] = value; self._set_zn(value); return
        if opcode == 0x7A:
            address = self._fetch8(); value = (self.memory[address] - 1) & 0xFF
            self.memory[address] = value; self._set_zn(value); return
        if opcode == 0x7B:
            address = self._fetch16(); value = (self.memory[address] - 1) & 0xFF
            self.memory[address] = value; self._set_zn(value); return
        if opcode == 0x7C: self.x = (self.x + 1) & 0xFF; self._set_zn(self.x); return
        if opcode == 0x7D: self.x = (self.x - 1) & 0xFF; self._set_zn(self.x); return
        if opcode == 0x7E: self.y = (self.y + 1) & 0xFF; self._set_zn(self.y); return
        if opcode == 0x7F: self.y = (self.y - 1) & 0xFF; self._set_zn(self.y); return

        if opcode == 0x80: self.pc = self._fetch16(); return
        if opcode == 0x81: self.pc = self._read16(self._fetch16()); return
        if opcode == 0x82:
            target = self._fetch16()
            return_pc = self.pc
            self._push8((return_pc >> 8) & 0xFF)
            self._push8(return_pc & 0xFF)
            self.pc = target
            return

        if opcode in (0x88, 0x89, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F):
            conditions = {
                0x88: bool(self.f & FLAG_Z), 0x89: not (self.f & FLAG_Z),
                0x8A: bool(self.f & FLAG_C), 0x8B: not (self.f & FLAG_C),
                0x8C: bool(self.f & FLAG_N), 0x8D: not (self.f & FLAG_N),
                0x8E: bool(self.f & FLAG_V), 0x8F: not (self.f & FLAG_V)}
            self._branch(conditions[opcode]); return

        if opcode == 0x90: self._push8(self.a); return
        if opcode == 0x91: self.a = self._pop8(); self._set_zn(self.a); return
        if opcode == 0x92: self._push8(self.f & (FLAG_C | FLAG_Z | FLAG_N | FLAG_V | FLAG_I)); return
        if opcode == 0x93: self.f = self._pop8() & (FLAG_C | FLAG_Z | FLAG_N | FLAG_V | FLAG_I); return
        if opcode == 0x94: self.x = self.a; self._set_zn(self.x); return
        if opcode == 0x95: self.y = self.a; self._set_zn(self.y); return
        if opcode == 0x96: self.a = self.x; self._set_zn(self.a); return
        if opcode == 0x97: self.a = self.y; self._set_zn(self.a); return

        if opcode == 0x04:
            self.pc = self._pop8() | (self._pop8() << 8)
            return
        if opcode == 0x03:
            self.f = self._pop8() & (FLAG_C | FLAG_Z | FLAG_N | FLAG_V | FLAG_I)
            self.pc = self._pop8() | (self._pop8() << 8)
            return

        raise K8IllegalOpcode(f"illegal opcode {opcode:02X} at {pc_before:04X}")

    def run(self, steps=100000):
        for _ in range(steps):
            if self.halted:
                return
            self.step()
        raise RuntimeError("K8 execution limit exceeded")
