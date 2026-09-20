# K8 Control Word

**Status:** M2.5 canonical

The K8 control store uses a deliberately wide 48-bit control word. The machine-readable source of truth is `spec/control-word.json`; this document explains that frozen mapping.

## Width and mapping

Each microinstruction is 48 bits, stored as six bytes. K8 Classic keeps the control word wide so the hardware and simulator can expose individual control lines directly.

| Bit | Signal |
|---:|---|
| 0 | A_OUT |
| 1 | A_LOAD |
| 2 | X_OUT |
| 3 | X_LOAD |
| 4 | Y_OUT |
| 5 | Y_LOAD |
| 6 | PC_INC |
| 7 | PC_LOAD_LO |
| 8 | PC_LOAD_HI |
| 9 | PC_TO_MAR |
| 10 | SP_OUT |
| 11 | SP_LOAD |
| 12 | SP_INC |
| 13 | SP_DEC |
| 14 | SP_TO_MAR |
| 15 | IR_LOAD |
| 16 | MAR_LOAD_LO |
| 17 | MAR_LOAD_HI |
| 18 | MDR_OUT |
| 19 | MDR_LOAD |
| 20 | TMP_OUT |
| 21 | TMP_LOAD |
| 22 | FLAGS_LATCH |
| 23 | MEM_READ |
| 24 | MEM_WRITE |
| 25 | ALU_ADD |
| 26 | ALU_SUB |
| 27 | ALU_AND |
| 28 | ALU_OR |
| 29 | ALU_XOR |
| 30 | ALU_NOT |
| 31 | ALU_SHL |
| 32 | ALU_SHR |
| 33 | ALU_ROL |
| 34 | ALU_ROR |
| 35 | ALU_OUT_ENABLE |
| 36 | STEP_RESET |
| 37 | INSTR_DONE |
| 38 | HALT |
| 39 | C_SET |
| 40 | I_SET |
| 41 | I_CLEAR |
| 42 | AGU_ADD_LO |
| 43 | AGU_ADD_HI |
| 44 | AGUC_LOAD |
| 45 | AGUC_CLEAR |
| 46 | V_CLEAR |
| 47 | C_CLEAR |

There are currently no reserved bits in the 48-bit v1 mapping.

`PC_TO_MAR` and `SP_TO_MAR` are direct 16-bit datapath transfers and do not drive the 8-bit data bus. `ALU_OUT_ENABLE` is the explicit ALU-to-data-bus enable. `C_SET`, `C_CLEAR`, `I_SET`, `I_CLEAR`, and `V_CLEAR` directly control the corresponding architectural flag latches.

The AGU controls are `AGU_ADD_LO`, `AGU_ADD_HI`, `AGUC_LOAD`, and `AGUC_CLEAR`. Index/source selection is intentionally not represented by the obsolete `IDX_X`/`IDX_Y` one-hot controls; its encoded datapath selection must be frozen before indexed-addressing hardware is qualified.

## Addressing the control store

The logical microaddress is:

- opcode: 8 bits
- microstep: 5 bits (T0-T31)
- condition: 2 bits

The condition encoding is `00` unconditional/default, `01` branch-false, `10` branch-true, and `11` reserved. Branch flag selection and polarity are decoded from the opcode as frozen in `BRANCH_ARCHITECTURE.md`.

This is a 15-bit address space containing 32,768 control words. The canonical logical address is:

`(opcode << 7) | (microstep << 2) | condition`

At 48 bits per word, the monolithic image is 196,608 bytes. K8 Classic can expose the same store as six 32,768-byte 8-bit ROM slices.

## Why a wide word?

A narrow encoded microinstruction would reduce ROM size but add decoding logic between the control store and the machine. For EduK8, direct control bits make the CPU easier to inspect, teach, debug, and reproduce.

## Safety validation

The canonical builder rejects invalid control words, including multiple data-bus sources, simultaneous `MEM_READ`/`MEM_WRITE`, multiple ALU operations, unknown signals, and `INSTR_DONE` without `STEP_RESET`.

Both the monolithic ROM image and the six physical ROM slices are generated from the same validated control-store representation.
