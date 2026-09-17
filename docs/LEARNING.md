# EduK8 Learning Philosophy

**Learn how computers work, one bit at a time.**

EduK8 is intended to be used as a progressive laboratory.

## Levels

### 1. Electronics
Learn voltage, current, resistors, capacitors, LEDs, switches, pull-ups and clock signals.

### 2. Digital logic
Learn gates, latches, flip-flops, counters, multiplexers, decoders and tri-state buses.

### 3. Computer organisation
Learn registers, buses, RAM, ROM, the ALU, program counters and instruction registers.

### 4. CPU operation
Learn fetch, decode, execute, control signals, flags and micro-operations.

### 5. Machine language
Learn opcodes, operands, addressing and binary programs.

### 6. Assembly
Write readable K8 assembly and understand its exact machine-code representation.

### 7. Compilers
Follow a small high-level language through parsing, semantic analysis, intermediate representation and K8 code generation.

### 8. Operating systems
Explore booting, memory, I/O, filesystems and simple task management.

### 9. Hardware engineering
Design the K8 in KiCad, manufacture the PCB, solder it, test it and debug it with measurement equipment.

## The no-magic rule

Every major abstraction should have a way to inspect what is happening underneath it.

For example, a compiler exercise should make it possible to inspect:

- source code
- generated assembly
- generated machine code
- emulator trace
- register changes
- memory accesses

The physical K8 should expose the same concepts through labelled buses, LEDs and test points wherever practical.
