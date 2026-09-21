"""Minimal interactive terminal front end for the K8 educational simulator."""

from simulator.core import K8Simulator
from simulator.view import render_text


HELP = """Commands: show, micro, clock, instruction, reset, release, quit"""


def execute(sim: K8Simulator, command: str) -> bool:
    command = command.strip().lower()
    if command in {"quit", "q", "exit"}:
        return False
    if command in {"show", "s", ""}:
        return True
    if command in {"micro", "m"}:
        sim.microstep()
    elif command in {"clock", "c"}:
        sim.clock_step()
    elif command in {"instruction", "i", "step"}:
        sim.instruction_step()
    elif command == "reset":
        sim.assert_reset()
    elif command == "release":
        sim.release_reset()
    elif command in {"help", "h", "?"}:
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
