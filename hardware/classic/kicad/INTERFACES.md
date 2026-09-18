# Schematic Interface Contract v1

These names are frozen for the first schematic pass.

## Global

- CLK
- RESET_N
- IRQ
- IRQ_ACK
- MEM_RD_N
- MEM_WR_N
- INSTR_DONE
- HALT

## Buses

- DB[0..7]
- AB[0..15]

## Register/control

- A_LOAD, A_OUT
- X_LOAD, X_OUT
- Y_LOAD, Y_OUT
- IR_LOAD
- PC_INC, PC_LOAD_LO, PC_LOAD_HI
- MAR_LOAD_LO, MAR_LOAD_HI
- SP_LOAD, SP_INC, SP_DEC, SP_OUT
- TMP_LOAD, TMP_OUT
- FLAGS_LATCH
- AGUC_LOAD, AGUC_CLEAR

## ALU

- ALU_OP[0..3]
- ALU_B_INV
- ALU_CIN
- ALU_OUT_ENABLE
- ALU_CARRY
- ALU_OVERFLOW
- ALU_ZERO
- ALU_NEGATIVE

## Memory selects

- RAM_CS_N
- VRAM_CS_N
- ROM_CS_N
- IO_CS_N
- SYSROM_CS_N

## Debug

- STEP_REQ
- MICROSTEP[0..4]
- IR_DEBUG[0..7]
- AGUC
