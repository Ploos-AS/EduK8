# K8 Classic Stack Pointer and Stack Path

## Status

**M4 schematic-definition candidate**

This document defines the signal-level contract for the K8 Classic 8-bit stack pointer and its fixed-page stack address path.

## Architectural contract

SP is an 8-bit register. The architectural stack occupies:

`$0100-$01FF`

The effective stack address is therefore:

`$0100 | SP`

The stack grows downward. Push and pull sequencing is defined by the frozen ISA/microcode semantics.

## Required controls

The physical SP block consumes the canonical controls:

- `SP_OUT`
- `SP_LOAD`
- `SP_INC`
- `SP_DEC`
- `SP_TO_MAR`

Contradictory SP update controls in one microstep are illegal unless explicitly defined by the control specification.

## Register implementation

Use one edge-triggered 8-bit register stage with a common clean `CPU_CLK`.

The preferred implementation follows the other K8 Classic registers:

- register device: 74HC574/273-class
- D-input next-state selection
- no locally generated asynchronous SP clock

SP_LOAD selects DB[7..0] as the next SP value.

Otherwise SP holds its current value unless SP_INC or SP_DEC selects an arithmetic next state.

## Increment/decrement

SP must support modulo-256 arithmetic:

- `$FF + 1 -> $00`
- `$00 - 1 -> $FF`

Use an explicit HC arithmetic path or counter arrangement whose behavior is visible and deterministic.

A pair of 74HC283 devices with operand conditioning is acceptable and consistent with the rest of K8 Classic. A suitable 8-bit up/down counter arrangement may be used if it preserves parallel load, observability and clean clocking.

The first schematic revision should prefer the implementation that produces the clearest educational signal flow rather than the smallest package count.

## SP on DB

`SP_OUT` permits SP[7..0] to drive DB through a tri-state output stage.

If the chosen SP register has a suitable tri-state output, it may be used directly. Otherwise use a 74HC541/244-class buffer.

The global bus-safety rules apply: SP_OUT must never contend with another DB source.

## SP to MAR

`SP_TO_MAR` constructs the 16-bit stack address:

- MAR low = SP[7..0]
- MAR high = $01

The constant high byte must be implemented as explicit hardwired logic or a clearly labelled constant-source path. Do not store a hidden $01 state solely for stack addressing.

The transfer must fit the frozen MAR load/control sequencing.

## Push sequencing

A push uses the architectural ordering defined by the microcode. The physical design must preserve the selected K8 convention for when memory is written relative to SP_DEC.

Qualification vectors shall explicitly cover the ordering rather than relying on assumptions inherited from another CPU family.

## Pull sequencing

Likewise, pull operations must preserve the frozen ordering between SP_INC, SP_TO_MAR and memory read.

PHA/PLA, PHP/PLP, JSR/RTS and BRK/RTI are the authoritative integration cases.

## Reset

Architectural reset establishes:

`SP = $FF`

The Classic implementation may achieve this through the reset microsequence or an explicit reset/load path if needed electrically. Any hardware shortcut must produce exactly the same programmer-visible result.

## Debug/observation

Provide labelled observation for:

- SP[7..0]
- SP_LOAD
- SP_INC
- SP_DEC
- SP_OUT
- SP_TO_MAR
- stack address low byte
- stack-page constant/high byte
- CPU_CLK

A small buffered LED bank for SP is useful during slow/single-step operation but is optional.

## Safety invariants

Validate at least:

1. SP_INC and SP_DEC are not asserted together,
2. SP_LOAD is not combined with an incompatible arithmetic update,
3. SP_OUT obeys global DB single-driver rules,
4. SP_TO_MAR cannot conflict with another MAR source,
5. stack high byte is always $01 during SP_TO_MAR.

## KiCad partition

Draw the SP/stack hierarchical sheet in this order:

1. SP register
2. increment/decrement arithmetic
3. next-state mux
4. DB output buffer
5. $01 stack-page source
6. SP-to-MAR path
7. debug/test header

## Qualification vectors

Before schematic freeze, shared vectors shall cover:

- reset -> SP=$FF
- explicit SP load
- increment normal case
- decrement normal case
- increment $FF -> $00
- decrement $00 -> $FF
- PHA then PLA round trip
- PHP then PLP round trip
- JSR then RTS return-address behavior
- BRK then RTI stack-frame behavior
- consecutive pushes across SP wrap
- SP_TO_MAR always produces $01xx

Expected state and memory transitions come from the qualified K8 emulator/simulator.
