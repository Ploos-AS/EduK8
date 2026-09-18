# KiCad sheet 05 — Control Unit

## Microaddress

    IR[7:0] + STEP[4:0] + COND[1:0] = MA[14:0]

## Control store

Six parallel 32Kx8 slices produce CW[47:0].

## Inputs

- CLK
- RESET_N
- IR_Q[0..7]
- C/Z/N/V/I
- IRQ
- HALT

## Outputs

- STEP[0..4]
- CW[0..47]
- all decoded architectural control signals
- INSTR_DONE
- STEP_RESET
- IRQ_ACK where required by the peripheral/control contract

## Invariants

- every legal path terminates in <=32 microsteps
- unused microaddresses produce safe no-write control words
- static generation rejects DB contention and simultaneous memory read/write
