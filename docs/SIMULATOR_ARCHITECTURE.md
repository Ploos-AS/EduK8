# K8 Simulator Architecture

**Milestone:** M2.5  
**Status:** scope defined  
**Architecture baseline:** frozen K8 v1

## Purpose

The K8 Simulator is the hardware-level and educational model of K8. It complements, rather than replaces, the qualified reference emulator.

- **Reference emulator:** executes the programmer-visible K8 architecture correctly and efficiently.
- **Simulator:** exposes how the machine produces that behaviour through datapath components, buses, control signals, clock phases and microsteps.
- **Physical K8 / FPGA:** later implementations are checked against the same frozen architecture and shared conformance material.

The simulator must therefore avoid becoming a second instruction interpreter. Architectural state at instruction boundaries must agree with the reference emulator, while the simulator additionally exposes intermediate hardware state.

## Simulation model

The deterministic simulator core will model:

- A, X and Y registers
- PC, SP and flags
- IR, MAR, MDR and temporary/internal registers required by the datapath
- ALU inputs, operation and result
- address-generation state
- data/address buses
- memory read/write cycles
- memory-mapped I/O decode
- control word and active control signals
- clock/reset
- control-store sequencing and microsteps T0-T31

The machine-readable specifications in `spec/` remain the source contracts. The simulator must consume or derive from those contracts rather than silently duplicating ISA/control definitions.

## Execution levels

The simulator will support three pedagogical stepping levels:

1. **Instruction step** — run until the current instruction completes.
2. **Microstep** — advance one control-store/microcode step.
3. **Clock step** — expose the clock-level state transition used by the simulated datapath.

A deterministic headless core is required so all three modes can be tested in CI. A graphical/interactive view is a presentation layer on top of that core.

## Observable state

At any simulation point the UI/API should be able to expose:

- register values and flags
- current opcode/instruction
- current microstep
- active control signals
- ALU inputs/output
- address and data buses
- memory address/data and read/write state
- decoded I/O device
- clock/reset state

Later visualization may highlight active datapath routes directly on a K8 block diagram.

## Peripherals

M2.5 models the architectural K8 peripherals needed for software and teaching:

- keyboard
- text/video memory path
- timer
- GPIO

Interactive switches, LEDs and other educational front-panel elements may wrap the same deterministic peripheral model.

## Conformance

The reference emulator remains the programmer-visible oracle.

Simulator qualification requires:

- loading the same K8 binaries/ROM images
- shared architectural conformance vectors
- deterministic simulator tests
- emulator/simulator comparison at instruction boundaries
- matching programmer-visible CPU, memory and I/O state where the architecture defines it

Intermediate simulator-only state is tested against the datapath/control contracts, not against hidden emulator implementation details.

## Layering

The implementation should keep these layers separate:

```
simulator core
    |
    +-- datapath/components
    +-- control store / sequencer
    +-- memory + I/O
    +-- trace/snapshot API
    |
front ends
    +-- CLI/headless qualification
    +-- educational visualizer
```

This allows CI qualification without a GUI and later enables richer visual teaching tools without changing simulation semantics.

## Non-goals for M2.5

M2.5 does not require:

- transistor-level or analogue simulation
- gate propagation timing
- electrical signal-integrity modelling
- exact PCB trace timing
- replacing the reference emulator
- completing the final K8 Studio UI

Those may be separate future tools or teaching material.

## M2.5 scope decision

The K8 Simulator is therefore defined as a **deterministic, hardware-oriented digital simulator of the frozen K8 v1 datapath and control unit, with explicit microstep/clock visibility and automated architectural cross-checking against the qualified reference emulator**.
