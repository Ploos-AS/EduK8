"""Minimal interactive terminal front end for the K8 educational simulator."""

from simulator.core import K8Simulator
from simulator.view import render_text
from simulator.display import render_text as render_display, render_status as render_video_status


HELP = """Commands: show, micro, clock, instruction, reset, release, mem <addr> [len], load <addr> <hex-bytes>, gpio [input|dir|data] [value], switches [value], leds, key <byte>, display, timer [tick|set] [value], quit"""


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
        sim.reset()
    elif op == "release":
        sim.release_reset()
    elif op == "mem":
        if len(parts) not in (2, 3):
            raise ValueError("usage: mem <addr> [len]")
        address = int(parts[1], 0)
        length = int(parts[2], 0) if len(parts) == 3 else 16
        data = [sim.memory.read((address + i) & 0xFFFF) for i in range(length)]
        print(f"{address & 0xFFFF:04X}: " + " ".join(f"{b:02X}" for b in data))
    elif op == "load":
        if len(parts) < 3:
            raise ValueError("usage: load <addr> <hex-bytes>")
        address = int(parts[1], 0)
        data = bytes(int(x, 16) for x in parts[2:])
        sim.load_image(address, data, force=True)
    elif op == "gpio":
        regs = {"data": 0xC040, "dir": 0xC041, "input": 0xC042}
        if len(parts) == 1:
            print("GPIO DATA=%02X DIR=%02X INPUT=%02X" % tuple(sim.memory.read(regs[k]) for k in ("data", "dir", "input")))
        elif len(parts) == 3 and parts[1] in regs:
            value = int(parts[2], 0) & 0xFF
            # INPUT represents external switches/pins; DATA/DIR represent CPU-visible registers.
            sim.memory.mmio.write(regs[parts[1]], value)
        else:
            raise ValueError("usage: gpio [input|dir|data] [value]")
    elif op == "switches":
        if len(parts) == 1:
            print(f"SWITCHES={sim.memory.read(0xC042):02X}")
        elif len(parts) == 2:
            sim.memory.mmio.write(0xC042, int(parts[1], 0) & 0xFF)
        else:
            raise ValueError("usage: switches [value]")
    elif op == "leds":
        if len(parts) != 1:
            raise ValueError("usage: leds")
        direction = sim.memory.read(0xC041)
        data = sim.memory.read(0xC040)
        print(f"LEDS={(data & direction):02X}")
    elif op == "key":
        if len(parts) != 2:
            raise ValueError("usage: key <byte>")
        sim.memory.mmio.inject_key(int(parts[1], 0))
    elif op in {"display", "screen"}:
        print(render_video_status(sim.memory), end="")
        print(render_display(sim.memory), end="")
    elif op == "timer":
        if len(parts) == 1:
            print(f"TIMER COUNT={sim.memory.mmio.timer_counter:04X} CTRL={sim.memory.read(0xC032):02X} STATUS={sim.memory.read(0xC033):02X}")
        elif len(parts) == 2 and parts[1] == "tick":
            sim.memory.mmio.tick_timer()
        elif len(parts) == 3 and parts[1] == "set":
            value = int(parts[2], 0) & 0xFFFF
            sim.memory.write(0xC030, value & 0xFF)
            sim.memory.write(0xC031, value >> 8)
        else:
            raise ValueError("usage: timer [tick|set <value>]")
    elif op in {"help", "h", "?"}:
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
