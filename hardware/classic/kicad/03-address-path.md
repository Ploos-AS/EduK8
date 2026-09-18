# KiCad sheet 03 — PC / MAR / SP / AGUC

## Inputs

- CLK
- RESET_N
- DB[0..7]
- PC_INC
- PC_LOAD_LO
- PC_LOAD_HI
- MAR_LOAD_LO
- MAR_LOAD_HI
- SP_LOAD
- SP_INC
- SP_DEC
- IDX_X / IDX_Y
- AGU_ADD_LO / AGU_ADD_HI
- AGUC_LOAD / AGUC_CLEAR

## Outputs

- AB[0..15]
- PC_Q[0..15]
- MAR_Q[0..15]
- SP_Q[0..7]
- PC_CARRY
- AGUC

## Invariant

Normal external memory cycles are addressed from MAR. PC and SP reach memory through explicit MAR/address-source paths.
