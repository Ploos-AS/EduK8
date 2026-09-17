# K8 Architecture

This document defines the principles for the K8 architecture. Detailed electrical and instruction-level specifications will be frozen during M1.

## Design goals

1. Make computer architecture observable.
2. Prefer simple circuits over opaque complexity.
3. Use inexpensive, readily available components.
4. Keep the physical machine hand-solderable.
5. Make the emulator behaviourally equivalent to the physical machine.
6. Make every instruction explainable in terms of buses, registers, ALU operations and control signals.
7. Keep the architecture useful enough to run real programs.

## Physical design

The initial K8 hardware should favour:

- through-hole components
- DIP packages
- 2-layer PCB construction
- 2.54 mm pitch
- generous component spacing
- labelled signals
- accessible test points
- modular functional blocks

The PCB should visually communicate the architecture.

## Software reference model

The emulator is not a separate interpretation of K8. It is the executable reference model of the same architecture.

The following must eventually be testable against the same conformance vectors:

- instruction decoding
- register state
- ALU results
- flags
- memory accesses
- I/O behaviour
- reset state
- control sequencing where architecturally observable

## Learning model

EduK8 deliberately preserves useful intermediate representations:

source → AST → IR → assembly → machine code → instruction execution → hardware signals.

The tooling should expose these stages rather than hiding them.

## Architecture freeze

No PCB implementation should be considered final until the K8 architecture specification, instruction set, memory map and I/O model have been reviewed and frozen in M1.
