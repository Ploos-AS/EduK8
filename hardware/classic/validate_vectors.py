#!/usr/bin/env python3
"""Boundary vectors shared by the K8 architectural emulator and hardware simulator."""

from emulator.k8 import CPU, FLAG_Z
from simulator.core import K8Simulator


def emu(program, pc, setup=None):
    c = CPU(); c.pc = pc; c.memory[pc:pc+len(program)] = bytes(program)
    if setup: setup(c)
    c.step(); return c


def sim(program, pc, setup=None):
    s = K8Simulator(); s.reset(); s.release_reset()
    s.datapath.pc.load(pc); s.load_image(pc, bytes(program))
    if setup: setup(s)
    s.instruction_step(); return s

# Branch signed extrema and page crossings. BEQ taken.
for pc, raw, expected in (
    (0x1200, 0x7F, 0x1281),   # +127
    (0x1280, 0x80, 0x1202),   # -128
    (0x12FE, 0x7F, 0x137F),   # forward page crossing
    (0x1300, 0x80, 0x1282),   # backward page crossing
):
    e = emu([0x88, raw], pc, lambda c: setattr(c, "f", FLAG_Z))
    s = sim([0x88, raw], pc, lambda x: x.datapath.flags.load(FLAG_Z))
    assert e.pc == expected, (hex(pc), hex(e.pc), hex(expected))
    assert s.datapath.pc.value == expected, (hex(pc), hex(s.datapath.pc.value), hex(expected))

# Branch not taken consumes the operand only.
e = emu([0x88, 0x7F], 0x12FE)
s = sim([0x88, 0x7F], 0x12FE)
assert e.pc == s.datapath.pc.value == 0x1300

# Stack byte push/pop wraps SP modulo 256.
e = emu([0x90], 0x2000, lambda c: (setattr(c, "a", 0xA5), setattr(c, "sp", 0x00)))
assert e.memory[0x0100] == 0xA5 and e.sp == 0xFF
s = sim([0x90], 0x2000, lambda x: (x.datapath.a.load(0xA5), x.datapath.sp.load(0x00)))
assert s.memory.read(0x0100) == 0xA5 and s.datapath.sp.value == 0xFF

# AGU zero-page indexed wrap.
e = emu([0x16, 0xF0], 0x2000, lambda c: (setattr(c, "x", 0x30), c.memory.__setitem__(0x20, 0x5A)))
s = sim([0x16, 0xF0], 0x2000, lambda x: (x.datapath.x.load(0x30), x.memory.write(0x20, 0x5A)))
assert e.a == 0x5A and e.mar == 0x20
assert s.datapath.a.value == 0x5A and s.datapath.mar.value == 0x20

# AGU absolute indexed page crossing.
e = emu([0x13, 0xF0, 0x12], 0x2000, lambda c: (setattr(c, "x", 0x30), c.memory.__setitem__(0x1320, 0x6B)))
s = sim([0x13, 0xF0, 0x12], 0x2000, lambda x: (x.datapath.x.load(0x30), x.memory.write(0x1320, 0x6B)))
assert e.a == 0x6B and e.mar == 0x1320
assert s.datapath.a.value == 0x6B and s.datapath.mar.value == 0x1320

# BRK/RTI round-trip: frame is PC high, PC low, flags|B; live B stays clear.
def setup_brk_e(c):
    c.sp = 0xFF; c.f = 0x05
    c.memory[0xFFFE] = 0x00; c.memory[0xFFFF] = 0x40
    c.memory[0x4000] = 0x03

def setup_brk_s(x):
    x.datapath.sp.load(0xFF); x.datapath.flags.load(0x05)
    x.memory.load(0xFFFE, bytes([0x00, 0x40]), force=True)
    x.memory.write(0x4000, 0x03)

e = emu([0x02], 0x2345, setup_brk_e)
s = sim([0x02], 0x2345, setup_brk_s)
assert e.pc == s.datapath.pc.value == 0x4000
assert e.sp == s.datapath.sp.value == 0xFC
assert e.memory[0x01FF] == s.memory.read(0x01FF) == 0x23
assert e.memory[0x01FE] == s.memory.read(0x01FE) == 0x46
assert e.memory[0x01FD] == s.memory.read(0x01FD) == 0x25
assert not (e.f & 0x20) and not (s.datapath.flags.value & 0x20)

e.step(); s.instruction_step()
assert e.pc == s.datapath.pc.value == 0x2346
assert e.sp == s.datapath.sp.value == 0xFF
assert e.f == s.datapath.flags.value == 0x05

# Canonical keyboard MMIO side effects in both models: depth one,
# preserve unread byte on overrun, DATA read consumes only the unread byte.
from emulator.io import IO
from simulator.memory import MMIO
eio = IO(); sio = MMIO()
for dev in (eio, sio):
    dev.inject_key(0x41); dev.inject_key(0x42)
assert eio.read(0xC011) == sio.read(0xC011) == 0x03
assert eio.read(0xC010) == sio.read(0xC010) == 0x41
assert eio.read(0xC011) == sio.read(0xC011) == 0x02

# KEY_CONTROL is readable/writable and bit 0 gates the simulator IRQ source.
eio.write(0xC012, 1); sio.write(0xC012, 1)
assert eio.read(0xC012) == sio.read(0xC012) == 1
sio.inject_key(0x55); sio.write(0xC001, 0x01)
assert sio.irq_status() & 0x01 and sio.irq_pending()

# Timer side effects: reload/counter composition, expiry, periodic reload,
# one-shot disable and IRQ masking.
t = MMIO()
t.write(0xC030, 0x02); t.write(0xC031, 0x00)
t.write(0xC032, 0x05); t.write(0xC001, 0x02)
t.tick_timer(); assert t.read(0xC030) == 1 and not t.timer_expired
t.tick_timer(); assert t.timer_expired and not (t.registers[0xC032] & 1)
assert t.irq_status() == 0x02 and t.irq_pending()
t.write(0xC033, 0); assert not t.timer_expired

t.write(0xC030, 0x02); t.write(0xC031, 0x00); t.write(0xC032, 0x03)
t.tick_timer(); t.tick_timer()
assert t.timer_expired and t.timer_counter == 2

# GPIO direction/data/input registers retain independent canonical values.
g = MMIO()
g.write(0xC040, 0xA5); g.write(0xC041, 0xF0); g.write(0xC042, 0x3C)
assert g.read(0xC040) == 0xA5
assert g.read(0xC041) == 0xF0
assert g.read(0xC042) == 0x3C

print("K8 Classic boundary vectors: PASS")
print("branch extrema/page crossings: PASS")
print("stack wrap and BRK/RTI frame: PASS")
print("AGU zero-page/absolute page crossing: PASS")
print("peripheral MMIO side effects: PASS")
