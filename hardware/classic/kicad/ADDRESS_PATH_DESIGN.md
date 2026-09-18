# PC, MAR, SP and AGUC Address Path — schematic design v0.1

This sheet makes K8's 16-bit address path explicit. It avoids pretending that the 16-bit PC is a source on the 8-bit data bus.

## Address bus ownership

AB[0..15] is driven by MAR during ordinary memory cycles.

    PC ----            > address-source/load path -> MAR -> AB[15:0]
    AGU ---/
    SP/page-$01 path

PC and SP do not directly drive external memory address pins in the normal cycle.

## Program Counter

PC is split into PCL and PCH and must support:

- increment by one
- load low byte
- load high byte
- transfer complete 16-bit value to MAR
- visible carry from PCL increment into PCH

Baseline candidate: cascaded 74HCT163-class synchronous counters/registers.

Signals:

- PC_INC
- PC_LOAD_LO
- PC_LOAD_HI
- PC_TO_MAR
- PC_CARRY
- PC_Q[15:0]

The exact parallel-load wiring from DB into PCL/PCH is resolved in schematic capture. Only one byte is loaded from DB at a time.

## MAR

MAR is two 8-bit storage stages:

- MARL
- MARH

Baseline candidate: 74HCT574-class storage, subject to the same safe-load-clock review as the register bank.

MAR drives AB continuously through appropriately buffered address outputs.

Inputs can come from:

1. PC transfer path
2. DB low/high byte load
3. AGU result
4. stack-address formation

Signals:

- MAR_LOAD_LO
- MAR_LOAD_HI
- MAR_FROM_PC
- MAR_FROM_AGU
- MAR_STACK
- MAR_Q[15:0]

The final mux structure is implemented with 74HCT157-class devices.

## Stack address

Architectural stack address is:

    $0100 | SP

SP is 8-bit and supports load, increment and decrement.

For a stack memory cycle:

    MARL <- SP
    MARH <- $01

The high byte is explicitly forced to $01 through the MAR source mux. It does not depend on a previous MAR value.

Candidate SP implementation: 74HCT193-class up/down counter if timing and load behaviour qualify; otherwise a small explicit register + increment/decrement path.

Signals:

- SP_LOAD
- SP_INC
- SP_DEC
- SP_TO_MAR
- SP_Q[7:0]

## AGU result path

Indexed 16-bit address generation is byte-serial and educational:

    low-byte base + X/Y -> low result + AGUC
    high-byte base + AGUC -> high result

AGUC is a dedicated one-bit latch.

Signals:

- IDX_X
- IDX_Y
- AGU_ADD_LO
- AGU_ADD_HI
- AGUC_LOAD
- AGUC_CLEAR
- AGUC

AGUC must never alias the architectural C flag.

## Address source mux

The address-load mux must make the source visible. Candidate 74HCT157 stages select among DB/PC/AGU/stack sources.

No combinational source is allowed to fight another source; selection is muxed rather than tri-state where practical on the internal 16-bit address path.

## Debug headers

Expose:

- PC_Q[15:0]
- MAR_Q[15:0]
- AB[15:0]
- SP_Q[7:0]
- PC_CARRY
- AGUC
- source-select controls

## Reset

Architectural reset sets SP=$FF. Because candidate counter/register IC reset facilities differ, the physical implementation may use a reset microsequence or explicit preset/load circuitry. The implementation must match emulator/FPGA-visible reset state.

PC reset is defined by loading the reset vector, not by assuming PC=0.

AGUC is cleared on reset.

## Qualification

1. PC increment $0000->$0001
2. PC carry $00FF->$0100
3. PC transfer to MAR
4. load PCL/PCH independently from DB
5. MAR drives exact AB value
6. SP reset/load to $FF
7. stack addresses $01FF and $01FE
8. indexed low-byte add without carry
9. indexed low-byte add with AGUC carry into high byte
10. prove architectural C remains unchanged by AGUC
