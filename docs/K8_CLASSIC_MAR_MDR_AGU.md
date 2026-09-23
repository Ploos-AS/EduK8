# K8 Classic MAR, MDR and AGU

## Status

**M4 schematic-definition candidate**

This document defines the memory-address, memory-data and address-generation path for K8 Classic.

## MAR

MAR is a 16-bit register split into MARL[7..0] and MARH[7..0]. It drives A0..A15.

Use edge-triggered 8-bit register stages with the common CPU clock. Low and high halves remain separately observable and loadable.

Required logical controls:
- MAR_LOAD_LO
- MAR_LOAD_HI

Sources may be DB, PC, SP or the AGU result according to frozen microcode. No source may silently bypass MAR.

## MDR

MDR is an 8-bit memory-data register with MDR_LOAD and MDR_OUT. MDR_LOAD captures memory/MMIO read data on the qualified CPU edge. MDR_OUT drives DB through a tri-state stage and follows the global single-driver rule.

A 74HC574-class register is preferred.

## Memory interface

Expose A0..A15, DATA_IN[7..0], DATA_OUT[7..0], MEM_READ and MEM_WRITE. Memory data must enter MDR before reaching DB.

## AGU

The AGU calculates indexed effective addresses:

1. select X or Y,
2. add index to MAR low byte,
3. latch carry into AGUC,
4. add AGUC to MAR high byte,
5. load effective address into MAR.

A dedicated HC arithmetic path is preferred for the first Classic revision. Four 74HC283-class 4-bit adders are an acceptable 16-bit baseline. 74HC157-class muxes select X/Y; a 74HC74-class flip-flop stores AGUC.

## Zero-page indexed behavior

Zero-page indexed addressing wraps the low byte and forces the effective high byte to 00. A low-byte carry must therefore be suppressed in zero-page mode.

Example: $00FF + X=1 produces $0000, not $0100.

## Absolute indexed behavior

Absolute indexed addressing propagates AGUC into the high byte. Qualification must cover page crossings and the $FFFF boundary.

## PC/SP integration

PC_TO_MAR and SP_TO_MAR follow frozen microcode. SP_TO_MAR supplies high byte $01; PC_TO_MAR transfers the complete PC through the defined low/high sequence.

## Observability

Provide test points or grouped headers for MARL, MARH, A0..A15, MDR, MDR_LOAD, MDR_OUT, MEM_READ, MEM_WRITE, selected index source, AGU low result, AGUC, AGU high result, zero-page mode and effective-address load.

## KiCad partition

1. MAR low/high registers
2. address bus/debug header
3. MDR and DB buffer
4. memory interface
5. index-source mux
6. low-byte AGU adder
7. AGUC latch
8. high-byte AGU adder
9. effective-address load path
10. debug/test header

## Qualification vectors

Before freeze, test MAR low/high load, MDR round trip, PC-to-MAR, SP-to-MAR, X/Y indexed addressing, zero-page wrap, absolute page crossing, $FFFF, memory read/write timing, MDR_OUT isolation and AGUC behavior.

Expected results come from the qualified K8 emulator and simulator.
