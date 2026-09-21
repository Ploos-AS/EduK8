"""Text observability view for the educational K8 simulator.

This is intentionally UI-toolkit independent: Studio/TUI/GUI front ends can
render the same deterministic snapshot without changing the simulator core.
"""

FLAG_BITS = (("C", 0x01), ("Z", 0x02), ("N", 0x04), ("V", 0x08), ("I", 0x10), ("B", 0x20))


def observable(snapshot: dict) -> dict:
    regs = snapshot["registers"]
    f = regs["F"]
    return {
        "registers": dict(regs),
        "flags": {name: bool(f & mask) for name, mask in FLAG_BITS},
        "bus": dict(snapshot["bus"]),
        "alu": dict(snapshot["alu"]),
        "agu": dict(snapshot["agu"]),
        "branch": dict(snapshot["branch"]),
        "microstep": snapshot["microstep"],
        "clock": snapshot["clock"],
        "reset": snapshot["reset"],
        "active_controls": list(snapshot["active_controls"]),
    }


def render_text(snapshot: dict) -> str:
    view = observable(snapshot)
    r, f, bus, alu = view["registers"], view["flags"], view["bus"], view["alu"]
    flags = " ".join(f"{name}={int(value)}" for name, value in f.items())
    db = "--" if bus["DB"] is None else f"{bus['DB']:02X}"
    driver = bus["driver"] or "-"
    controls = ", ".join(view["active_controls"]) or "-"
    return "\n".join([
        f"CLK={view['clock']} T={view['microstep']} RESET={int(view['reset'])}",
        f"A={r['A']:02X} X={r['X']:02X} Y={r['Y']:02X} SP={r['SP']:02X} F={r['F']:02X}",
        f"PC={r['PC']:04X} MAR={r['MAR']:04X} IR={r['IR']:02X} MDR={r['MDR']:02X} TMP={r['TMP']:02X}",
        f"FLAGS {flags}",
        f"DB={db} DRIVER={driver}",
        f"ALU A={alu['a']:02X} B={alu['b']:02X} OUT={alu['result']:02X} C={alu['carry_out']} V={alu['overflow']}",
        f"CTRL {controls}",
    ]) + "\n"
