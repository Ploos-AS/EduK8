"""Minimal interactive terminal front end for the K8 educational simulator."""

from simulator.core import K8Simulator
from simulator.view import render_text\nfrom simulator.display import render_text as render_display, render_status as render_video_status


HELP = """Commands: show, micro, clock, instruction, reset, release, mem <addr> [len], load <addr> <hex-bytes>, gpio [input|dir|data] [value], key <byte>, display, timer [tick|set] [value], quit"""


def execute(sim: K8Simulator, command: str) -> bool:
    command = command.strip().lower()
    if op in {"quit", "q", "exit"}:
        return False
    if op in {"show", "s", ""}:
        return True
    if op in {"micro", "m"}:
        sim.microstep()
    elif op in {"clock", "c"}:
        sim.clock_step()
    elif op in {"instruction", "i", "step"}:
        sim.instruction_step()
    elif op == "reset":
        sim.assert_reset()
    elif op == "release":
        sim.release_reset()
    elif op == "mem":\n        if len(parts) not in (2, 3):\n            raise ValueError("usage: mem <addr> [len]")\n        address = int(parts[1], 0)\n        length = int(parts[2], 0) if len(parts) == 3 else 16\n        data = [sim.memory.read((address + i) & 0xFFFF) for i in range(length)]\n        print(f"{address & 0xFFFF:04X}: " + " ".join(f"{b:02X}" for b in data))\n    elif op == "load":\n        if len(parts) < 3:\n            raise ValueError("usage: load <addr> <hex-bytes>")\n        address = int(parts[1], 0)\n        data = bytes(int(x, 16) for x in parts[2:])\n        sim.load_image(address, data, force=True)\n    elif op == "gpio":\n        regs = {"data": 0xC040, "dir": 0xC041, "input": 0xC042}\n        if len(parts) == 1:\n            print("GPIO DATA=%02X DIR=%02X INPUT=%02X" % tuple(sim.memory.read(regs[k]) for k in ("data", "dir", "input")))\n        elif len(parts) == 3 and parts[1] in regs:\n            value = int(parts[2], 0) & 0xFF\n            # INPUT represents external switches/pins; DATA/DIR represent CPU-visible registers.\n            sim.memory.mmio.write(regs[parts[1]], value)\n        else:\n            raise ValueError("usage: gpio [input|dir|data] [value]")\n    elif op == "key":\n        if len(parts) != 2:\n            raise ValueError("usage: key <byte>")\n        sim.memory.mmio.inject_key(int(parts[1], 0))\n    elif op in {"display", "screen"}:\n        print(render_video_status(sim.memory), end="")\n        print(render_display(sim.memory), end="")\n    elif op == "timer":\n        if len(parts) == 1:\n            print(f"TIMER COUNT={sim.memory.mmio.timer_counter:04X} CTRL={sim.memory.read(0xC032):02X} STATUS={sim.memory.read(0xC033):02X}")\n        elif len(parts) == 2 and parts[1] == "tick":\n            sim.memory.mmio.tick_timer()\n        elif len(parts) == 3 and parts[1] == "set":\n            value = int(parts[2], 0) & 0xFFFF\n            sim.memory.write(0xC030, value & 0xFF)\n            sim.memory.write(0xC031, value >> 8)\n        else:\n            raise ValueError("usage: timer [tick|set <value>]")\n    elif op in {"help", "h", "?"}:
        pass
    else:
        raise ValueError(f"unknown command: {command}")
    return True


def main() -> None:
    sim = K8Simulator()
    print("K8 simulator TUI")
    print(HELP)
    while True:
        print(render_text(sim.snapshot()), end="")
        try:
            command = input("k8> ")
            if not execute(sim, command):
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except ValueError as exc:
            print(exc)


if __name__ == "__main__":
    main()
