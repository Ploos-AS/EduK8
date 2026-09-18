# K8 Instruction Set

**Status:** M1 arithmetic/flag semantics frozen; interrupt semantics still pending

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
