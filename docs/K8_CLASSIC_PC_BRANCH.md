# K8 Classic Program Counter and Branch Path

## Status

**M4 schematic-definition candidate**

This document defines the signal-level contract for the K8 Classic 16-bit program counter and signed-relative branch path.

## Architectural contract

PC is a 16-bit register and supports:

- increment by one
- load low byte
- load high byte
- transfer of PC to MAR
- signed relative branch update

The frozen emulator/simulator semantics remain authoritative.

## Physical partition

Represent PC explicitly as:

- PCL[7..0]
- PCH[7..0]

The implementation must keep both bytes observable and separately loadable.

## Register implementation

Use edge-triggered 8-bit register stages with a common clean CPU clock. As with A/X/Y, avoid locally generated asynchronous register clocks.

The preferred implementation uses D-input hold/select muxing:

- PC_LOAD_LO selects DB into PCL
- PC_LOAD_HI selects DB into PCH
- otherwise the selected next-PC value is presented to the register inputs

The final device choice may use 74HC574/273-class registers plus 74HC157-class muxing provided the architectural controls remain explicit.

## Increment path

PC_INC computes:

`PC_NEXT = PC + 1`

Use an explicit 16-bit HC arithmetic path, preferably four 74HC283 4-bit adders if the incrementer is dedicated.

A reduced incrementer made from counters or simpler carry logic is acceptable if it preserves:

- separate low/high loads
- exact 16-bit wrap behavior
- visibility of carry from low to high byte
- deterministic single-step timing

Educational clarity takes precedence over saving a few packages.

## PC to MAR

The frozen logical control `PC_TO_MAR` transfers the current PC value into MAR.

Because the internal DB is 8 bits, the physical implementation must sequence or provide dedicated paths for the low/high halves exactly as required by the qualified microcode/datapath model.

Do not expose both PC bytes onto DB simultaneously.

## Relative branch semantics

Conditional branches use an 8-bit signed displacement relative to PC **after the branch operand has been fetched**.

Interpret TMP as signed two's-complement displacement:

- $00..$7F = 0..+127
- $80..$FF = -128..-1

The branch result is:

`PC_NEXT = PC_AFTER_OPERAND + sign_extend(TMP)`

The operation wraps modulo 16 bits.

## Branch condition selection

The control-store condition address uses the frozen condition states:

- 00 — default/unconditional path
- 01 — branch condition false
- 10 — branch condition true
- 11 — reserved

The branch decoder evaluates the opcode against architectural flags C/Z/N/V and presents the selected condition to the sequencer.

The physical branch decoder must remain visible logic; a hidden MCU is not permitted.

## Branch arithmetic

The branch adder may physically reuse the address-generation arithmetic hardware if timing and control remain clear. Otherwise use a dedicated HC adder path.

A dedicated path is preferred for the first Classic schematic revision because it makes signed PC-relative addressing easier to teach and probe.

For a dedicated implementation:

1. add TMP to PCL,
2. capture carry/borrow propagation,
3. add sign extension plus low-byte carry to PCH,
4. latch the resulting PCL/PCH together at the qualified update edge.

The exact high-byte correction must be verified exhaustively against the simulator for all 256 displacement values around page boundaries.

## Branch flag equations

The decoder implements:

- BEQ: Z = 1
- BNE: Z = 0
- BCS: C = 1
- BCC: C = 0
- BMI: N = 1
- BPL: N = 0
- BVS: V = 1
- BVC: V = 0

Opcode decode plus the selected flag determines BRANCH_TAKEN.

## Debug/observation

Provide labelled observation points for:

- PCL[7..0]
- PCH[7..0]
- PC low-to-high increment carry
- PC_INC
- PC_LOAD_LO
- PC_LOAD_HI
- PC_TO_MAR
- branch displacement TMP[7..0]
- BRANCH_TAKEN
- branch condition true/false
- branch-adder carry/correction signals
- CPU_CLK

A grouped 16-bit PC debug header is recommended.

## Reset

Architectural reset loads PC from the reset vector at $FFFC/$FFFD through the defined memory/control sequence. The physical PC register does not need a separate hard-coded reset address.

Electrical power-up state before the reset sequence is not architecturally observable.

## Safety invariants

The control/schematic design shall prevent contradictory PC updates in the same microstep. In particular, mutually incompatible combinations of:

- PC_INC
- PC_LOAD_LO / PC_LOAD_HI
- branch PC update

must be rejected or explicitly defined by the control validator.

## KiCad partition

Draw the PC/branch hierarchical sheet in functional order:

1. PCL register and load/hold mux
2. PCH register and load/hold mux
3. increment path
4. TMP sign-extension path
5. branch arithmetic
6. next-PC selection
7. branch condition decoder
8. PC-to-MAR interface
9. debug/test header

## Qualification vectors

Before schematic freeze, automated vectors shall include:

- increment $0000 -> $0001
- increment $00FF -> $0100
- increment $FFFF -> $0000
- independent low/high loads
- reset-vector PC load sequence
- branch not taken
- displacement $00
- displacement $01
- displacement $7F
- displacement $FF (-1)
- displacement $80 (-128)
- forward and backward page crossings
- wrap across $FFFF/$0000
- every branch opcode for both flag outcomes

The expected state transitions are generated from the qualified reference emulator/simulator.
