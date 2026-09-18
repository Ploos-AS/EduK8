# K8 Address Generation Unit

**Decision:** optimise for learning, visibility and hand-built hardware rather than minimum chip count.

K8 v1 uses an explicit 16-bit Address Generation Unit (AGU). Effective-address arithmetic is visible hardware, not a hidden microcode operation.

## Why a separate AGU?

Indexed addressing teaches how an 8-bit CPU manipulates a 16-bit address. A simple AGU lets a learner observe the base address in MAR, X/Y offset, low-byte addition, carry into the high byte, and final effective address.

## Datapath

Inputs are MAR[15:0], X[7:0] or Y[7:0], and carry. The result returns to MAR. V1 performs two explicit byte phases using an 8-bit adder path:

    low  = MAR.low + index
    high = MAR.high + carry

Carry is held in an implementation-visible one-bit AGUC latch. AGUC is not programmer-visible and does not alter architectural C.

Logical controls: IDX_X, IDX_Y, AGU_ADD_LO, AGU_ADD_HI, AGUC_IN, AGUC_CLR. Only one index source may be selected.

## Absolute indexed

After an absolute operand has produced MAR=$1234, an indexed load with X performs:

    T9   MAR.low + X -> MAR.low; carry -> AGUC
    T10  MAR.high + AGUC -> MAR.high
    T11  MEM[MAR] -> MDR
    T12  MDR -> A; update Z/N; instruction done

## Zero-page indexed

Zero-page indexing wraps within page zero:

    effective = (operand + index) & $FF

MAR.high is explicitly zero and low-byte carry is discarded. This teaches page-local modular arithmetic.

## Indirect zero-page pointers

For (zp), pointer-byte addressing wraps within zero page. A pointer at $FF reads its low byte at $00FF and high byte at $0000, not $0100. This is specified K8 behaviour.

## Absolute indirect

JMP (abs) reads adjacent bytes in normal 16-bit address space. The second byte increments normally across a page boundary. K8 does not reproduce historical page-boundary quirks.

## Teaching/debug requirements

The emulator and hardware debugger should expose MAR, selected index, AGUC, low-byte AGU phase, high-byte AGU phase and final effective address. A lesson should single-step base $12F8 plus X=$10 so the learner sees $F8+$10=$08 with carry, then $12+1=$13.
