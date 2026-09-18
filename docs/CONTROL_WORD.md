# K8 Control Word

**Status:** M2 draft

The K8 control store uses a deliberately wide, directly readable control word. The first revision prioritises teaching and straightforward wiring over ROM-byte efficiency.

## Width

The logical control word is 48 bits, stored as six bytes per microinstruction.

Bits are assigned permanently once the first hardware control board is frozen.

| Bit | Signal |
|---:|---|
| 0 | A_OUT |
| 1 | A_IN |
| 2 | X_OUT |
| 3 | X_IN |
| 4 | Y_OUT |
| 5 | Y_IN |
| 6 | PC_OUT |
| 7 | PC_IN |
| 8 | PC_INC |
| 9 | SP_OUT |
| 10 | SP_IN |
| 11 | SP_INC |
| 12 | SP_DEC |
| 13 | IR_IN |
| 14 | MAR_IN_LO |
| 15 | MAR_IN_HI |
| 16 | MDR_OUT |
| 17 | MDR_IN |
| 18 | TMP_OUT |
| 19 | TMP_IN |
| 20 | F_IN |
| 21 | MEM_READ |
| 22 | MEM_WRITE |
| 23 | ALU_ADD |
| 24 | ALU_SUB |
| 25 | ALU_AND |
| 26 | ALU_OR |
| 27 | ALU_XOR |
| 28 | ALU_NOT |
| 29 | ALU_SHL |
| 30 | ALU_SHR |
| 31 | ALU_ROL |
| 32 | ALU_ROR |
| 33 | ALU_FLAGS |
| 34 | STEP_RESET |
| 35 | INSTR_DONE |
| 36 | HALT |
| 37 | IRQ_ACK |
| 38-47 | reserved |

Reserved bits must be zero in M2-generated images.

## Addressing the control store

The conceptual control-store address is formed from:

- opcode: 8 bits
- microstep: 4 bits
- condition page: 2 bits

This yields a 14-bit logical address space. Condition pages allow branch/interrupt decisions without making the basic sequencer opaque.

The initial generator may emit a sparse image. Physical EEPROM selection and banking are an M4 electrical decision.

## Why a wide word?

A narrow encoded microinstruction would reduce ROM size but require another decoder between the control store and the machine. For EduK8, direct bits make it possible to point at a ROM bit and explain exactly which control line it drives.

## Safety validation

The generator must reject impossible or dangerous combinations, including:

- multiple ordinary sources driving DB simultaneously
- MEM_READ and MEM_WRITE together
- conflicting ALU operations
- HALT combined with an unrelated write
- reserved bits set

These checks become part of the hardware design contract.
