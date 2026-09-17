from dataclasses import dataclass, field

FLAG_C = 1 << 0
FLAG_Z = 1 << 1
FLAG_N = 1 << 2
FLAG_V = 1 << 3
FLAG_I = 1 << 4
FLAG_B = 1 << 5

class K8IllegalOpcode(Exception): pass

@dataclass
class CPU:
    a: int = 0
    x: int = 0
    y: int = 0
    pc: int = 0
    sp: int = 0xFF
    f: int = 0
    halted: bool = False
    memory: bytearray = field(default_factory=lambda: bytearray(65536))

    def reset(self, pc=None):
        self.a = self.x = self.y = 0
        self.sp = 0xFF
        self.f = 0
        self.halted = False
        self.pc = ((self.memory[0xFFFC] | (self.memory[0xFFFD] << 8)) if pc is None else pc) & 0xFFFF

    def _fetch8(self):
        value = self.memory[self.pc]
        self.pc = (self.pc + 1) & 0xFFFF
        return value

    def _set_zn(self, value):
        value &= 0xFF
        self.f &= ~(FLAG_Z | FLAG_N)
        if value == 0: self.f |= FLAG_Z
        if value & 0x80: self.f |= FLAG_N

    def _add(self, rhs):
        lhs = self.a
        carry = 1 if self.f & FLAG_C else 0
        result = lhs + rhs + carry
        value = result & 0xFF
        self.f &= ~(FLAG_C | FLAG_Z | FLAG_N | FLAG_V)
        if result > 0xFF: self.f |= FLAG_C
        if value == 0: self.f |= FLAG_Z
        if value & 0x80: self.f |= FLAG_N
        if (~(lhs ^ rhs) & (lhs ^ value) & 0x80): self.f |= FLAG_V
        self.a = value

    def step(self):
        if self.halted: return
        pc_before = self.pc
        opcode = self._fetch8()
        if opcode == 0x00: return
        if opcode == 0x01: self.halted = True; return
        if opcode == 0x05: self.f &= ~FLAG_C; return
        if opcode == 0x06: self.f |= FLAG_C; return
        if opcode == 0x10: self.a = self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x18: self.x = self._fetch8(); self._set_zn(self.x); return
        if opcode == 0x20: self.y = self._fetch8(); self._set_zn(self.y); return
        if opcode == 0x40: self._add(self._fetch8()); return
        if opcode == 0x50: self.a &= self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x54: self.a |= self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x58: self.a ^= self._fetch8(); self._set_zn(self.a); return
        if opcode == 0x5C: self.a = (~self.a) & 0xFF; self._set_zn(self.a); return
        if opcode == 0x7C: self.x = (self.x + 1) & 0xFF; self._set_zn(self.x); return
        if opcode == 0x7D: self.x = (self.x - 1) & 0xFF; self._set_zn(self.x); return
        if opcode == 0x7E: self.y = (self.y + 1) & 0xFF; self._set_zn(self.y); return
        if opcode == 0x7F: self.y = (self.y - 1) & 0xFF; self._set_zn(self.y); return
        if opcode == 0x94: self.x = self.a; self._set_zn(self.x); return
        if opcode == 0x95: self.y = self.a; self._set_zn(self.y); return
        if opcode == 0x96: self.a = self.x; self._set_zn(self.a); return
        if opcode == 0x97: self.a = self.y; self._set_zn(self.a); return
        raise K8IllegalOpcode(f'illegal opcode {opcode:02X} at {pc_before:04X}')

    def run(self, steps=100000):
        for _ in range(steps):
            if self.halted: return
            self.step()
        raise RuntimeError('K8 execution limit exceeded')
