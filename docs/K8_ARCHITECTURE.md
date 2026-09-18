# K8 Architecture Specification

**Status:** M1 draft

The K8 is the physical 8-bit computer in the EduK8 learning platform.

The architecture is deliberately small, regular and observable. The specification is designed to support the reference emulator, assembler, compiler and later physical PCB implementation.

## Programmer-visible CPU state

| Name | Width | Purpose |
|---|---:|---|
| A | 8 bit | General-purpose accumulator |
| X | 8 bit | General-purpose index/register |
| Y | 8 bit | General-purpose index/register |
| PC | 16 bit | Program counter |
| SP | 8 bit | Stack pointer |
| F | 8 bit | Status flags |

Status flags:

| Bit | Name | Meaning |
|---:|---|---|
| 0 | C | Carry |
| 1 | Z | Zero |
| 2 | N | Negative/sign |
| 3 | V | Signed overflow |
| 4 | I | Interrupt mask |
| 5 | B | Break marker in stacked flag images; live value is 0 |
| 6 | - | Reserved, reads as 0 |
| 7 | - | Reserved, reads as 0 |

## Data and address widths

- Data path: 8 bit
- Address path: 16 bit
- Address space: 64 KiB
- Byte: 8 bits
- Little-endian multi-byte values

## Memory map

| Range | Function |
|---|---|
| $0000-$7EFF | RAM |
| $7F00-$7FFF | Reserved / expansion |
| $8000-$BFFF | ROM |
| $C000-$C0FF | I/O |
| $C100-$FEFF | Reserved / expansion |
| $FF00-$FFFF | System ROM / vectors |

## Stack

The stack occupies page $0100-$01FF. SP contains the low byte of the stack position. The stack grows downward. Reset initializes SP to $FF.

## Reset and vectors

- $FFFC-$FFFD = reset vector
- $FFFE-$FFFF = IRQ vector

The reset sequence loads PC from $FFFC-$FFFD. K8 v1 has one maskable IRQ vector at $FFFE-$FFFF and no NMI.

## Instruction encoding

K8 instructions use one to three bytes:

    opcode
    opcode operand
    opcode operand low operand high

The opcode is always the first byte.

## Addressing modes

The initial instruction set supports:

- implied
- immediate
- absolute
- absolute indexed by X
- absolute indexed by Y
- zero-page
- zero-page indexed by X
- zero-page indexed by Y
- indirect
- relative

## Instruction groups

### Data movement
LDA, LDX, LDY, STA, STX, STY, TAX, TAY, TXA, TYA

### Arithmetic
ADD, SUB, INC, DEC, INX, DEX, INY, DEY

### Logic
AND, OR, XOR, NOT

### Shifts and rotates
SHL, SHR, ROL, ROR

### Compare
CMP, CPX, CPY

### Branch/control flow
JMP, JSR, RTS, BEQ, BNE, BCS, BCC, BMI, BPL, BVS, BVC

### Stack
PHA, PLA, PHP, PLP

### System/control
NOP, BRK, RTI, CLI, SEI, CLC, SEC, CLV, HALT

This list is an M1 architectural candidate, not yet a frozen binary opcode table.

## ALU semantics

Arithmetic is 8-bit.

Addition computes A + operand + C and updates C, Z, N and V.

Subtraction uses conventional carry/no-borrow semantics and updates C, Z, N and V.

Logical operations update Z and N.

## Branches

Conditional branches use a signed 8-bit relative displacement from the address following the branch instruction.

## I/O model

I/O occupies $C000-$C0FF.

The initial implementation reserves memory-mapped registers for console output, console input/status, general-purpose GPIO and system control. Exact register allocation is to be frozen with the hardware design.

## Control model

A typical instruction follows:

    FETCH
      PC -> address bus
      memory -> data bus
      data bus -> IR
      PC++

    EXECUTE
      decode IR
      perform operand fetch
      execute ALU/register operation
      update architectural state

The emulator should expose equivalent trace information.

## Emulator contract

The emulator must provide deterministic reset, deterministic instruction execution, register inspection, memory inspection, instruction trace, I/O hooks, save/load state and single-step execution.

## Compiler considerations

The ISA must support a useful small C-like language. The compiler backend will need byte arithmetic, comparisons, conditional branches, calls/returns, stack operations, indexed addressing and memory load/store.

The final calling convention will be documented before compiler implementation begins.

## Hardware principles

The K8 PCB should make the architecture visible. Buses are labelled, major registers are identifiable, control signals have test points, clock/reset are accessible, ALU inputs/outputs can be probed, and logic-analyzer headers are provided where practical.

The first revision targets hand-solderable through-hole parts and an inexpensive two-layer PCB.

## M1 freeze criteria

M1 is complete only when programmer-visible state, memory map, addressing modes, instruction semantics, flags, reset/vector behaviour, I/O contract and calling-convention requirements are frozen; a complete opcode table exists; and emulator conformance vectors can be generated from the specification.

Until then, PCB implementation remains provisional.


## I/O architecture

K8 v1 includes a self-contained PS/2 keyboard interface, 40x25 text display with dedicated video RAM and VGA output, timer and 8-bit GPIO. The normative register map is defined in `docs/IO_ARCHITECTURE.md` and `spec/io-map.json`.
