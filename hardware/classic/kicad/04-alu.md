# KiCad sheet 04 — ALU

## Inputs
- A_Q[0..7]
- B_Q[0..7]
- architectural C input
- ALU_OP[0..3]
- ALU_B_INV
- ALU_CIN
- ALU_OUT_ENABLE
- FLAGS_LATCH

## Outputs
- DB[0..7] when enabled
- ALU_RESULT[0..7]
- ALU_CARRY
- ALU_ZERO
- ALU_NEGATIVE
- ALU_OVERFLOW

## Internal probe nets
- BX[0..7]
- C4
- C8
- arithmetic/logic/shift result buses

## Rule
Combinational ALU flag outputs are candidates only; the flags register changes only under explicit control.
