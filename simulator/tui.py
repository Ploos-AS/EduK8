"""Minimal interactive terminal front end for the K8 educational simulator."""

from simulator.core import K8Simulator
from simulator.view import render_text


HELP = """Commands: show, micro, clock, instruction, reset, release, mem <addr> [len], load <addr> <hex-bytes>, quit"""


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
    elif op == "mem":\n        if len(parts) not in (2, 3):\n            raise ValueError("usage: mem <addr> [len]")\n        address = int(parts[1], 0)\n        length = int(parts[2], 0) if len(parts) == 3 else 16\n        data = [sim.memory.read((address + i) & 0xFFFF) for i in range(length)]\n        print(f"{address & 0xFFFF:04X}: " + " ".join(f"{b:02X}" for b in data))\n    elif op == "load":\n        if len(parts) < 3:\n            raise ValueError("usage: load <addr> <hex-bytes>")\n        address = int(parts[1], 0)\n        data = bytes(int(x, 16) for x in parts[2:])\n        sim.load_image(address, data, force=True)\n    elif op in {"help", "h", "?"}:
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
