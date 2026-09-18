# K8 Classic KiCad hardware

This directory is the source of truth for the discrete K8 Classic hardware.

## Schematic hierarchy

The intended hierarchy is:

1. power-clock-reset
2. cpu-registers
3. alu
4. control
5. memory-decode
6. video
7. keyboard
8. timer-gpio-irq
9. connectors-debug

The root `k8-classic.kicad_sch` is intentionally a minimal valid scaffold. Electrical sheets are added only when their interfaces and parts are explicit; placeholder wires are not treated as a design.

## Rules

- KiCad sources are reviewed like software.
- No hidden MCU/CPLD may implement normative Classic CPU behaviour.
- Net names follow the architecture docs.
- Every IC receives local decoupling.
- Bus drivers must be statically reviewable for contention.
- Test/debug nets are first-class schematic signals.
- Generated fabrication outputs are not canonical sources.
