# K8 Classic ALU and Flags Sheet

## Status

**M4 schematic-definition candidate**

This document defines the signal-level contract for the discrete K8 Classic ALU and architectural flags. It maps the frozen ALU/control specification to a readable 5 V 74HC implementation.

## Architectural operations

The ALU implements:

- ADD
- SUB
- AND
- OR
- XOR
- NOT
- SHL
- SHR
- ROL
- ROR

Only the selected result may drive DB, and only while `ALU_OUT_ENABLE` is asserted.

## Operand buses

Define two internal 8-bit ALU operand buses:

- ALUA[7..0]
- ALUB[7..0]

The exact operand-source selection is controlled by the surrounding datapath/control sheet. A/X/Y/TMP/MDR values remain observable logical sources; the ALU itself must not hide architectural state.

Expose ALUA, ALUB and ALUR[7..0] through labelled test pads or grouped debug headers.

## Arithmetic path

Use two 74HC283 4-bit adders for an 8-bit ripple-carry arithmetic path.

### ADD

- arithmetic A input = ALUA
- arithmetic B input = ALUB
- carry-in = 0 unless the frozen instruction semantics explicitly select carry input
- result = A + B + Cin
- carry-out feeds ALU_COUT

### SUB

Subtraction uses two's-complement addition:

`A - B = A + NOT(B) + 1`

Use XOR/mux selection on the B path and set arithmetic carry-in to 1 for subtraction. The resulting carry/borrow interpretation must match the frozen emulator semantics.

## Logic path

Use ordinary HC gates:

- 74HC08 — AND
- 74HC32 — OR
- 74HC86 — XOR
- 74HC04 — NOT

The logic outputs feed the ALU result-selection network.

## Shift and rotate path

Shift/rotate must remain visible rather than being hidden in programmable logic.

A mux network selects adjacent source bits for:

- SHL
- SHR
- ROL
- ROR

For rotate operations the architectural C flag supplies the entering bit. The shifted-out bit becomes the candidate carry result.

74HC157-class multiplexers are the baseline building blocks.

## Result selection

ALUR[7..0] is selected from arithmetic, logic and shift/rotate result groups with cascaded 74HC157/74HC153-class multiplexers.

Selection decoding is derived from the mutually exclusive frozen logical controls:

- ALU_ADD
- ALU_SUB
- ALU_AND
- ALU_OR
- ALU_XOR
- ALU_NOT
- ALU_SHL
- ALU_SHR
- ALU_ROL
- ALU_ROR

No two ALU operation controls may be active simultaneously.

ALUR reaches DB through an octal tri-state stage, preferably 74HC541/74HC244, enabled only by `ALU_OUT_ENABLE`.

## Flag candidates

The ALU produces candidate values:

- C_NEXT
- Z_NEXT
- N_NEXT
- V_NEXT

### Z

Z_NEXT is asserted when ALUR is zero. Implement zero detection as an explicit reduction network. A comparator such as 74HC688 or cascaded NOR/OR logic is acceptable; choose the clearer implementation on the schematic.

### N

N_NEXT = ALUR7.

### C

For ADD/SUB, C_NEXT comes from the arithmetic carry result according to frozen K8 semantics.

For shifts/rotates, C_NEXT is the bit shifted out.

### V

For signed addition:

`V = NOT(A7 XOR B7) AND (A7 XOR R7)`

For signed subtraction:

`V = (A7 XOR B7) AND (A7 XOR R7)`

Implement with visible XOR/AND/inversion logic.

## Architectural F register

Live flags are:

- C
- Z
- N
- V
- I

B is **not** a live flag. B is synthesized only when required by stacked PHP/BRK status.

Use explicit flip-flop state, with 74HC74 as the baseline for individually controlled flags. Grouped implementation is permitted only if it preserves direct controls and keeps behavior clear.

## Flag controls

`FLAGS_LATCH` captures the ALU-generated C/Z/N/V candidates appropriate to the selected operation.

Direct frozen controls override or update their respective architectural state as defined by the control contract:

- C_SET
- C_CLEAR
- I_SET
- I_CLEAR
- V_CLEAR

Direct controls and FLAGS_LATCH must be electrically decoded so contradictory writes cannot create ambiguous state.

## Status value on DB

Instructions that push/read architectural status require an 8-bit status representation assembled from F plus the required stacked B convention.

Use a dedicated status-output mux/buffer path if necessary. Do not turn B into persistent hardware state merely to simplify PHP/BRK.

## Safety invariants

The electrical/control design shall enforce or validate:

1. at most one ALU operation select active,
2. ALU drives DB only with ALU_OUT_ENABLE,
3. ALU_OUT_ENABLE cannot coincide with another DB driver,
4. direct set/clear controls are not contradictory,
5. FLAGS_LATCH receives stable ALUR/status candidates at the active clock edge.

These invariants should be represented in machine-checkable control validation where possible.

## Debug/observation

Provide practical observation for:

- ALUA[7..0]
- ALUB[7..0]
- ALUR[7..0]
- ALU_COUT
- C, Z, N, V, I
- FLAGS_LATCH
- ALU_OUT_ENABLE
- operation-select controls

Buffered LEDs may show C/Z/N/V/I during slow/single-step operation.

## KiCad partition

Within the ALU/flags hierarchical sheet, draw functional blocks in signal flow order:

1. operand selection
2. arithmetic B conditioning
3. 8-bit 74HC283 arithmetic path
4. logic functions
5. shift/rotate network
6. result selection
7. DB output buffer
8. C/Z/N/V generation
9. architectural flag flip-flops
10. debug/test headers

## Qualification

Before the ALU/flags sheet is frozen, shared vectors shall cover every ALU operation and edge cases including:

- zero result
- negative result
- carry in/out
- signed overflow
- subtraction borrow/carry semantics
- shift bit 7/bit 0 into C
- rotate through C
- C_SET/C_CLEAR
- I_SET/I_CLEAR
- V_CLEAR

The expected results come from the qualified K8 emulator/simulator and frozen ISA semantics.
