# K8 Instruction Set

**Status:** M1 candidate

The binary opcode allocation remains provisional until the architecture freeze is complete.

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
| System | NOP, BRK, RTI, CLI, SEI, CLC, SEC, CLV, CLD, SED, HALT |

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
