# K8 Classic ALU Sheet — component design v0.1

This sheet turns the architectural ALU into a concrete 5 V HCT datapath.

## Inputs and result

- A_Q[0..7] is arithmetic/logic operand A.
- B_Q[0..7] is the selected second operand supplied by the datapath/TMP path.
- ALU_RESULT[0..7] is selected from arithmetic, logic or shift paths.
- ALU_RESULT reaches DB[0..7] only through an explicitly enabled 74HCT245-class driver.

## Arithmetic path

U40 and U41 are cascaded 74HCT283 4-bit adders.

    A[3:0] + BX[3:0] + CIN -> U40 -> C4
    A[7:4] + BX[7:4] + C4  -> U41 -> C8

C4 and C8 are labelled/probeable.

BX is B or inverted B according to ALU_B_INV. B inversion uses XOR gates so each bit computes:

    BXn = Bn XOR ALU_B_INV

A 74HCT86 bank provides this path.

For ADD:
- ALU_B_INV=0
- CIN selected according to instruction semantics

For SUB:
- ALU_B_INV=1
- CIN provides the two's-complement +1/no-borrow convention

The exact ISA rule for whether ADD/SUB consume architectural C must be frozen before final control ROM qualification.

## Logic path

Parallel ordinary gates compute:

- A AND B
- A OR B
- A XOR B
- NOT A

Candidate packages:
- 74HCT08
- 74HCT32
- 74HCT86
- 74HCT04

A mux tree selects the requested logic result.

## Shift/rotate path

v1 implements single-bit operations:

- SHL
- SHR
- ROL through C
- ROR through C

The wiring is explicit bit routing plus mux selection. Shifted-out bit becomes the candidate carry output.

No opaque barrel shifter is used.

## Result selection

A 74HCT157-class mux tree selects one of:

1. arithmetic
2. logic
3. shift/rotate

ALU_OP controls the selection.

The selected result is available internally for flag generation and through U_ALU_DB only when ALU_OUT_ENABLE is asserted.

## Carry

Carry source depends on operation:

- arithmetic: U41 C8
- SHL/ROL: old bit 7
- SHR/ROR: old bit 0
- logic operations: architecturally defined unchanged/ignored behaviour

A mux selects ALU_CARRY_NEXT.

## Zero and negative

N is simply:

    ALU_NEGATIVE = ALU_RESULT[7]

Z is true only when all result bits are zero. Implement as OR reduction followed by inversion, using ordinary gates.

## Signed overflow

ADD:

    Vadd = ~(A7 XOR B7) AND (A7 XOR R7)

SUB:

    Vsub = (A7 XOR B7) AND (A7 XOR R7)

Gate-level intermediate signals are labelled so signed overflow can be demonstrated with probes.

Logic/shift V behaviour must follow the frozen ISA rather than silently inheriting arithmetic state.

## Flags latch boundary

The ALU only produces candidate C/Z/N/V values.

FLAGS_LATCH from the control unit determines when architectural flags change. I and B do not originate in this sheet.

This separation is important: combinational ALU signals are not themselves the architectural F register.

## Electrical bus safety

U_ALU_DB is the only ALU driver onto DB.

When ALU_OUT_ENABLE=0 it is high impedance.

Global microcode invariant must eventually include:

    popcount(A_OUT, X_OUT, Y_OUT, TMP_OUT, ALU_OUT_ENABLE, MDR_OUT, ...) <= 1

## Debug

Expose:

- A_Q[0..7]
- B_Q[0..7]
- BX[0..7]
- arithmetic result
- logic result
- shift result
- ALU_RESULT[0..7]
- C4
- C8
- CIN
- ALU_B_INV
- C/Z/N/V candidates
- ALU_OP
- ALU_OUT_ENABLE

## Required bench vectors

- $00 + $00 -> $00, Z=1
- $01 + $01 -> $02
- $FF + $01 -> $00, C=1, Z=1
- $7F + $01 -> $80, V=1, N=1, C=0
- $80 + $80 -> $00, V=1, C=1
- $00 - $01 -> $FF with unsigned borrow represented by C convention
- $80 - $01 -> $7F, V=1
- AND/OR/XOR/NOT known patterns
- SHL/SHR shifted-out carry
- ROL/ROR carry insertion and extraction

## Open freeze items

1. ADD/SUB interaction with architectural C.
2. Exact C/V preservation for logic operations.
3. Exact V behaviour for shifts/rotates.
4. Physical mux count/topology after propagation-delay analysis.

These must be resolved against ISA.md before PCB ordering.
