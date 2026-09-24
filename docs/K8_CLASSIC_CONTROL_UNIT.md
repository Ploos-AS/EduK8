# K8 Classic Control Unit and Microcode ROM

## Status

**M4 schematic-definition candidate**

This document maps the qualified K8 logical control store onto an observable discrete control unit.

## Canonical contract

Authoritative sources are spec/control-word.json, spec/control-signals.json, spec/microcode.json and tools/control_store.py. Classic consumes the same 48-bit logical control word as the simulator.

## Control-store geometry

The address is 15 bits: opcode 8 bits, microstep 5 bits and condition 2 bits.

Address = (opcode << 7) | (step << 2) | condition.

This gives 32768 logical words. Each word is 48 bits / 6 bytes, for a canonical image of 196608 bytes.

## Physical ROM slicing

Use six parallel 8-bit ROM/EEPROM slices:

- ROM0: bits 0..7
- ROM1: bits 8..15
- ROM2: bits 16..23
- ROM3: bits 24..31
- ROM4: bits 32..39
- ROM5: bits 40..47

All slices receive the same 15-bit address. Repository-generated slice images are authoritative.

## ROM requirements

Each slice needs at least 32K x 8, 5 V-compatible parallel I/O, a practical programming workflow and timing compatible with CPU_CLK. Socketable DIP EEPROM is preferred during development.

## Sequencer

The sequencer implements T0..T31 and the canonical STEP_RESET, INSTR_DONE and HALT behavior. Microstep state must be observable.

IR[7..0] supplies opcode address bits and remains stable during instruction execution.

## Conditions

Condition address values are 00 default, 01 false, 10 true and 11 reserved. The branch/condition decoder derives these from frozen architectural state. Reserved 11 must not occur normally.

## Control outputs

ROM outputs map to canonical control bits without changing allocation. Active-low physical pins may use explicit polarity conversion while architectural net names remain active-high.

A control-word output latch is preferred if needed to prevent ROM address-transition glitches. Six octal latch/register stages may capture ROM bytes on a phase that guarantees stable controls before datapath update.

## Clock phases

Expose explicit timing phases for control-address transition, ROM settle/capture, datapath settle and architectural update. Single-step must execute one complete hardware cycle deterministically.

## Reset and safety

Reset places the sequencer in reset/fetch entry, inhibits unsafe writes/drivers, starts the qualified reset-vector sequence and establishes PC from FFFC/FFFD plus SP=FF.

Validation must reject multiple DB drivers, multiple ALU operations, SP_INC+SP_DEC, contradictory flag controls, incompatible PC updates and memory read/write conflict.

## Programming workflow

1. generate canonical ROM from spec/microcode.json
2. generate six slice images
3. verify reconstruction
4. program ROM0..ROM5
5. read back/checksum
6. install in labelled sockets

PCB silkscreen must make slice order unambiguous.

## Observability

Expose ROM A0..A14, IR[7..0], T[4..0], condition bits, six ROM byte outputs, latched control bytes, STEP_RESET, INSTR_DONE, HALT, clock phases and reset.

## KiCad partition

1. IR/opcode address
2. microstep sequencer
3. condition decoder
4. control-store address bus
5. six ROM sockets
6. six control-byte latches/buffers
7. polarity conversion
8. reset/safety gating
9. programming/debug headers

## Qualification

Before freeze, verify all 32768 addresses against tools/control_store.py, six-slice reconstruction, T0..T31 sequencing, conditions 00/01/10, STEP_RESET, INSTR_DONE, HALT, reset entry, control safety and representative electrical/digital control words.

The qualified emulator/simulator and generated control-store artifacts remain the reference.
