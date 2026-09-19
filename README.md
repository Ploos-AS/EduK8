# EduK8

**Learn how computers work, one bit at a time.**

EduK8 is an open educational computer platform built around the **K8 — Komputer 8 bit**.

The goal is not merely to build an 8-bit computer. EduK8 is designed as a complete learning environment where the same architecture can be explored from logic gates and registers all the way through machine code, assembly, compilation, operating-system software, emulation, debugging, and physical hardware.

## K8

The K8 is the physical 8-bit computer.

The initial design targets:

- 8-bit data path
- simple, explicit architecture
- through-hole components where practical
- 2-layer hobby-friendly PCB
- 2.54 mm component spacing
- inexpensive and hand-solderable parts
- visible buses, registers, ALU and control signals
- test points for oscilloscope and logic-analyzer work
- expansion capability
- a design suitable for small PCBWay-style production runs

The hardware design will be documented so that the PCB itself can be read as a block diagram.

## EduK8 software stack

The project will eventually include:

- **K8 Emulator** — reference software implementation of the machine
- **K8 Assembler** — assembler for K8 machine code
- **K8 Compiler** — a small educational high-level language compiler
- **K8 Debugger** — instruction, register, memory and source-level debugging
- **K8 Studio** — integrated learning/development environment
- **K8 OS** — a small operating system for the physical computer
- **EduK8 Lessons** — progressive hardware and software experiments

The emulator is a first-class component. It should execute the same binaries as the physical K8 and provide visibility into registers, buses, memory, instructions and micro-operations.

## Learning philosophy

EduK8 follows one principle:

> **No magic.**

Whenever practical, an abstraction should be possible to inspect at the level below it.

A program should be traceable through:

```
source code
    ↓
compiler
    ↓
assembly
    ↓
machine code
    ↓
instruction fetch
    ↓
control signals
    ↓
registers / buses
    ↓
ALU
    ↓
memory / I/O
    ↓
physical signals
```

The emulator, documentation and hardware should reinforce the same mental model.

## Repository structure

The planned structure is:

```
hardware/      KiCad schematics, PCB and BOM
emulator/      K8 reference emulator
assembler/     K8 assembler
compiler/      K8 educational compiler
debugger/      K8 debugger
studio/        K8 Studio
os/            K8 operating system
lessons/       educational material
docs/          architecture and design documentation
tests/         cross-layer conformance tests
examples/      example programs
tools/         development utilities
```

## Status

**M1 — K8 Architecture: complete and frozen**

The K8 v1 programmer-visible architecture is frozen. The reference emulator is substantially implemented, including deterministic execution, tracing, the microstep/control model and conformance tests. Hardware/control-unit development is also underway while M2 is completed.

Current focus: finish the remaining M2 reference-emulator work, especially save/load state and qualification, then continue the assembler and hardware implementation. See [ROADMAP.md](ROADMAP.md) and [docs/M1_FREEZE.md](docs/M1_FREEZE.md).

## Manufacturing

For fabrication files, release-package conventions, manufacturer choices, and funding/affiliate disclosure, see [MANUFACTURING.md](MANUFACTURING.md). Released hardware remains vendor-neutral and may be manufactured by any suitable PCB manufacturer. For project-specific PCB ordering options, see [ORDERING.md](ORDERING.md).

## License

Hardware design materials — including schematics, PCB layouts, manufacturing files, and HDL/RTL that describes hardware — are licensed under the **CERN Open Hardware Licence Version 2 - Permissive (CERN-OHL-P-2.0)**. See [LICENSE-HARDWARE](LICENSE-HARDWARE).

Software — including firmware, drivers, host tools, emulators, assemblers, compilers, utilities, and other executable code unless explicitly stated otherwise — is licensed under the **MIT License**. See [LICENSE-SOFTWARE](LICENSE-SOFTWARE).

Documentation, lessons, course material, tutorials, exercises, illustrations, and other educational content are licensed under the **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. See [LICENSE-DOCUMENTATION](LICENSE-DOCUMENTATION).

Files that incorporate third-party material remain subject to their respective licences and notices.
