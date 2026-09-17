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

**M0 — Project foundation**

The repository currently establishes the project identity, architecture direction and development roadmap. No hardware or software implementation is considered complete yet.

## License

License and contribution terms will be established as part of the M0 foundation work.
