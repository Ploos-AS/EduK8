# K8 Classic Datapath Resolution: PC Branch and MAR Routing

## Status

**M4 pre-freeze blocker resolution**

This document resolves schematic-freeze blockers 1 and 2 without changing the frozen ISA or 48-bit control word.

## Rule

No new architectural control bit is introduced. Physical select signals may be derived combinationally from canonical control outputs, IR/microstep state and the qualified sequencer state.

## PC branch update

Conditional branch execution is a sequencer action, not a new programmer-visible transfer.

The physical control unit derives an internal net named `PC_BRANCH_LOAD` only when the current qualified branch microstate selects the taken path.

`PC_BRANCH_LOAD` is therefore a decoded physical net, not bit 48 or an extension of the canonical control word.

Inputs to the decode are limited to:
- IR/opcode
- current microstep
- canonical condition result
- canonical control-store state

The branch target is `PC_AFTER_OPERAND + sign_extend(TMP)`. On the qualified update edge, `PC_BRANCH_LOAD` selects that result for both PC bytes.

Not-taken execution leaves PC at the already advanced post-operand value.

### PC next-state priority

Illegal overlaps are rejected by validation. The physical mux contract is:

1. branch load when the qualified taken-branch microstate is active
2. explicit PC_LOAD_LO / PC_LOAD_HI for the affected byte
3. PC_INC
4. hold

The generated microcode must never depend on priority to resolve two intended simultaneous updates.

## MAR source routing

MAR remains two architectural bytes, MARL and MARH. Its physical input network has explicit source selection derived from canonical controls.

### DB loads

`MAR_LOAD_LO` and `MAR_LOAD_HI` load the corresponding MAR byte from DB during ordinary operand/address construction.

### PC_TO_MAR

`PC_TO_MAR` selects a dedicated PC-to-MAR path:
- MARL <- PCL
- MARH <- PCH

This is a 16-bit internal transfer and does not place PC on DB.

### SP_TO_MAR

`SP_TO_MAR` selects:
- MARL <- SP
- MARH <- $01

This is also a dedicated path and does not consume DB.

### AGU result

AGU microstates derive a physical `AGU_TO_MAR` select from the existing AGU_ADD_LO / AGU_ADD_HI / AGUC sequencing. It is not a new architectural control bit.

The low and high result bytes are committed only in the qualified AGU microstates.

## MAR mux contract

Each MAR byte uses an explicit input mux.

MARL sources:
- hold
- DB
- PCL
- SP
- AGU low result

MARH sources:
- hold
- DB
- PCH
- constant $01
- AGU high result

74HC157/153-class devices may be cascaded as required. Source selection must be visible on schematic nets.

## Conflict rules

Validation must reject any microstep that requests incompatible MAR sources, including:
- PC_TO_MAR with SP_TO_MAR
- PC_TO_MAR with DB MAR load
- SP_TO_MAR with DB MAR load
- AGU commit with PC_TO_MAR or SP_TO_MAR
- multiple PC update intents in one edge

Derived physical selects must be generated from one reviewed decode table.

## Verification artifact

Before schematic freeze, generate a table for every defined opcode/microstep/condition tuple containing:
- canonical 48-bit control word
- PC next-state source
- MARL source
- MARH source
- DB driver
- memory read/write state

The table must prove that every selected source is unique and that no derived signal changes architectural behavior.

## Result

Blocker 1 is resolved by a derived `PC_BRANCH_LOAD` tied to the already-qualified branch microstate.

Blocker 2 is resolved by explicit MAR low/high source muxes, with PC/SP dedicated transfers and AGU commit derived from canonical AGU sequencing.

Neither resolution changes the ISA, microcode word width, opcode map or programmer-visible architecture.
