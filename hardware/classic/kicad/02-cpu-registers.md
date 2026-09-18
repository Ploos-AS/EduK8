# KiCad sheet 02 — CPU Register Bank

## Inputs

- CLK
- RESET_N (available for control/debug; storage ICs do not invent reset)
- DB[0..7]
- A_LOAD, A_OUT
- X_LOAD, X_OUT
- Y_LOAD, Y_OUT
- IR_LOAD
- TMP_LOAD, TMP_OUT

## Outputs

- A_Q[0..7] -> ALU
- X_Q[0..7] -> AGU
- Y_Q[0..7] -> AGU
- IR_Q[0..7] -> control unit
- TMP_Q[0..7] -> internal datapath/debug
- DB[0..7] through enabled source buffers

## Open item

The final register-load clock topology must be resolved before electrical schematic freeze. 74HCT574 is retained as the baseline storage candidate, but unsafe combinational clock gating is prohibited.
