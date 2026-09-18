# K8 Implementation Strategy

K8 has two normative hardware implementations sharing one architecture:

1. **K8 Classic** — discrete 74HC/HCT logic on a maker-friendly PCB.
2. **K8 FPGA** — synthesizable HDL implementation of the same architecture.

The emulator is the executable architectural reference.

## Three-way consistency

    K8 ISA/specification
          |
      architecture
       /       \
K8 Classic    K8 FPGA
       \       /
        emulator

The FPGA must not introduce architectural behaviour that cannot be explained by the documented K8 datapath.

## K8 Classic goals

- through-hole components where practical
- sockets for ICs where useful
- clearly labelled buses and test points
- separate functional blocks
- repairable and probeable construction
- no hidden MCU implementing CPU behaviour
- affordable PCB fabrication and assembly
- beginner-friendly schematics

Functional blocks:

- register bank
- 8-bit ALU
- 16-bit program counter
- stack pointer
- instruction register
- flags register
- 16-bit MAR
- educational 16-bit AGU
- control sequencer
- microcode/control ROM
- RAM
- ROM
- memory/I/O decode
- keyboard interface
- text video generator
- timer/GPIO

## K8 FPGA goals

The HDL implementation must preserve the same:

- programmer-visible registers and flags
- instruction encodings
- memory map
- I/O register map
- reset/interrupt behaviour
- AGU semantics
- microstep-visible control model

The FPGA target should expose internal signals for simulation and educational debugging.

## Verification

Every ISA feature should eventually have:

- emulator test
- HDL simulation test
- Classic hardware qualification procedure

The same ROM/program binaries should be usable on emulator, FPGA and Classic K8 whenever the target requires no hardware-specific peripheral.

## Documentation requirement

For each functional block, EduK8 will provide:

- what the block does
- why it exists
- schematic
- truth/dataflow explanation
- timing explanation
- assembly-visible effect
- beginner exercise
- troubleshooting/probing exercise

This is an explicit project requirement, not optional documentation.
