# K8 Instruction Set

**Status:** M1 ALU, stack, call and interrupt semantics frozen

The current opcode allocation is the K8 v1 working allocation. Arithmetic and flag behaviour below is normative for emulator, FPGA, microcode and Classic hardware.

## Instruction classes

| Class | Instructions |
|---|---|
| Load/store | LDA, LDX, LDY, STA, STX, STY |
| Transfer | TAX, TAY, TXA, TYA |
| Arithmetic | ADD, SUB, INC, DEC, INX, DEX, INY, DEY |
| Logic | AND, OR, XOR, NOT |
| Shift/rotate | SHL, SHR, ROL, ROR |
| Compare | CMP, CPX, CPY |
| Branch | BEQ, BNE, BCS, BCC, BMI, BPL, BVS, BVC |
| Flow | JMP, JSR, RTS |
| Stack | PHA, PLA, PHP, PLP |
| System | NOP, BRK, RTI, CLI, SEI, CLC, SEC, CLV, HALT |

## Operand forms

    LDA #$42
    LDA $42
    LDA $1234
    LDA $1234,X
    LDA $1234,Y

Branches:

    BEQ label
    BNE label

Implied instructions:

    NOP
    HALT
    INX

Instruction names and semantics should remain stable even if binary opcode allocation changes during M1.


## K8 v1 arithmetic and flag semantics

K8 v1 uses binary arithmetic only. Decimal mode is removed. Opcodes `$0A` and `$0B`, formerly provisional CLD/SED, are reserved/illegal in v1.

### ADD

`ADD operand` computes:

    A = A + operand + C

C is therefore an input carry. After the operation:

- C = unsigned carry out of bit 7
- Z = result is zero
- N = result bit 7
- V = signed two's-complement overflow

### SUB

`SUB operand` computes:

    A = A - operand - (1-C)

C is therefore the conventional no-borrow input. After the operation:

- C = 1 when no unsigned borrow occurred; otherwise 0
- Z = result is zero
- N = result bit 7
- V = signed two's-complement overflow

This lets `SEC; SUB` perform an ordinary subtraction and permits multi-byte subtraction using C.

### Compare

CMP/CPX/CPY perform subtraction for flags without storing the result. They update C/Z/N and preserve V.

### Logic

AND, OR, XOR and NOT update Z and N only. They preserve C and V.

### Shift and rotate

SHL and SHR update C/Z/N. C receives the bit shifted out.

ROL and ROR rotate through architectural C and update C/Z/N.

All four preserve V.

### Increment/decrement and transfers

INC, DEC, INX, DEX, INY, DEY and TAX/TAY/TXA/TYA update Z/N only and preserve C/V.

### Loads

LDA/LDX/LDY update Z/N only.

Stores do not modify flags.

### Flag instructions

CLC clears C; SEC sets C; CLV clears V. CLI/SEI modify I only.

## Decimal mode

K8 v1 deliberately has no decimal/BCD arithmetic mode. This keeps the discrete ALU and teaching model smaller and avoids carrying a feature with no implemented arithmetic semantics.


## Stack, calls and interrupt semantics

K8 uses page $01 as an 8-bit descending stack. SP points to the next occupied/top stack byte.

Push:

    memory[$0100 | SP] = value
    SP = SP - 1

Pop:

    SP = SP + 1
    value = memory[$0100 | SP]

Reset initializes SP to $FF.

### JSR / RTS

JSR fetches its complete 16-bit target first. At that point PC already points to the instruction following JSR.

JSR pushes that return PC high byte first, then low byte, and loads PC with the target.

RTS pops low byte, then high byte, and loads that exact 16-bit value into PC. RTS does not add one.

This intentionally simple convention makes the stacked return address the actual continuation address.

### IRQ model

K8 v1 has one maskable IRQ input and no NMI.

An external IRQ is accepted only at an instruction boundary when I=0. Once accepted:

1. push current PC high byte
2. push current PC low byte
3. push F with B=0
4. set I=1
5. load PC from the little-endian IRQ vector at $FFFE/$FFFF

The stacked PC is the address of the next instruction that would otherwise execute.

### BRK

BRK is a one-byte software interrupt, not HALT.

After its opcode fetch PC already points to the following byte. BRK:

1. pushes current PC high byte
2. pushes current PC low byte
3. pushes F with B=1
4. sets I=1
5. loads PC from $FFFE/$FFFF

BRK and external IRQ therefore share the same vector. Software distinguishes them using B in the stacked flags byte.

B is a stack-image marker, not persistent CPU state: the live F register reads B as 0. BRK does not leave B set in live F.

### RTI

RTI pops:

1. flags
2. PC low byte
3. PC high byte

It restores C/Z/N/V/I from the stacked flags byte, ignores stacked B/reserved bits, and resumes at the restored PC.

### PHP / PLP

PHP pushes the live flags with B=0 and reserved bits zero.

PLP restores C/Z/N/V/I and ignores B/reserved bits.

### IRQ pending while masked

I prevents IRQ acceptance; it does not itself clear the peripheral's pending condition. Peripheral-specific acknowledge/clear rules remain authoritative. After CLI or RTI clears I, a still-asserted IRQ can be accepted at the next instruction boundary.

### HALT

HALT remains separate from BRK. HALT stops instruction execution until reset/debug intervention; it does not push state or enter the IRQ vector.
