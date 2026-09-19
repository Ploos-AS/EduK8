import json

import pytest

from emulator.k8 import CPU


def test_save_load_round_trip_restores_complete_state():
    cpu = CPU()
    cpu.a = 0x12
    cpu.x = 0x34
    cpu.y = 0x56
    cpu.pc = 0x8123
    cpu.sp = 0x9A
    cpu.f = 0x1B
    cpu.halted = True
    cpu.mar = 0x4567
    cpu.aguc = 1
    cpu.irq_line = True
    cpu.trace_enabled = True
    cpu.trace.append({"phase": "test", "value": 7})
    cpu.memory[0x1234] = 0xAB
    cpu.memory[0x7800] = ord("K")
    cpu.io.inject_key(0x41)
    cpu.io.key_control = 1
    cpu.io.video_control = 0
    cpu.io.cursor_x = 17
    cpu.io.cursor_y = 9
    cpu.io.cursor_control = 3

    state = cpu.save_state()
    json.dumps(state)  # Public snapshot contract is JSON-serialisable.

    restored = CPU()
    restored.load_state(state)

    assert restored.save_state() == state


def test_snapshot_is_independent_of_later_mutation():
    cpu = CPU()
    cpu.memory[0x2000] = 0x55
    cpu.io.inject_key(0x42)
    state = cpu.save_state()

    cpu.memory[0x2000] = 0xAA
    cpu.io.keyboard.clear()

    restored = CPU()
    restored.load_state(state)
    assert restored.memory[0x2000] == 0x55
    assert restored.io.keyboard == [0x42]


def test_load_rejects_unknown_state_version():
    cpu = CPU()
    state = cpu.save_state()
    state["version"] = 999
    with pytest.raises(ValueError, match="unsupported K8 state version"):
        CPU().load_state(state)


def test_load_rejects_invalid_memory_size():
    cpu = CPU()
    state = cpu.save_state()
    state["memory"] = "00"
    with pytest.raises(ValueError, match="65536"):
        CPU().load_state(state)
