# K8 Classic Datapath

## Status

**M4 baseline candidate**

This document freezes the logical datapath partition for the discrete-logic K8 Classic implementation. The frozen K8 v1 architecture, ISA, control-word specification and simulator remain authoritative.

## Design goals

K8 Classic is an educational, observable and repairable 8-bit computer. Functional blocks must remain understandable on the schematic and practical to probe on physical hardware. The implementation should prefer readily available logic and socketed through-hole parts where practical.

## Datapath buses

### DB — 8-bit data bus

DB is the primary internal 8-bit bus. Register outputs, MDR and the ALU result use controlled output enables. The control-word safety rules must prevent multiple active DB drivers.

Expose DB0..DB7 at labelled test points or a debug header.

### Address path

The 16-bit MAR drives A0..A15 toward memory and MMIO decode. PC and SP reach MAR through the frozen control architecture rather than sharing an uncontrolled external address bus.

Expose A0..A15 sufficiently for educational observation; grouped debug headers are acceptable.

## Programmer-visible registers

- A — 8-bit accumulator
- X — 8-bit index register
- Y — 8-bit index register
- SP — 8-bit stack pointer
- F — architectural flags
- PC — 16-bit program counter

## Internal registers

- IR — 8-bit instruction register
- MAR — 16-bit memory address register
- MDR — 8-bit memory data register
- TMP — 8-bit temporary register
- AGUC — 1-bit address-generation carry

The physical implementation must expose the logical state required by the simulator model even when several logical functions share a device package.

## ALU

The ALU accepts the operands defined by the frozen datapath/control model and implements:

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

Outputs include the 8-bit result plus carry and overflow information required by F. ALU output reaches DB only when `ALU_OUT_ENABLE` is active.

The schematic should expose ALU inputs, result and important status outputs for probing.

## Address generation

Indexed addressing uses the frozen AGU model:

1. add X or Y to MAR low byte,
2. latch carry into AGUC,
3. add AGUC to MAR high byte.

Zero-page indexed addressing forces the effective high byte to zero according to the architectural specification.

The physical implementation may reuse arithmetic hardware where doing so remains observable and preserves the control contract.

## Program counter

PC is 16 bits and supports:

- increment,
- loading low byte,
- loading high byte,
- transfer to MAR.

Branch handling must preserve the frozen signed-relative branch semantics.

## Stack pointer

SP is 8 bits. Stack addresses are in page `$0100-$01FF`. The datapath supports SP output, load, increment, decrement and transfer into the MAR stack-address path.

## Memory interface

MAR supplies the address. MDR buffers data between the internal datapath and memory/MMIO path.

Required logical controls:

- `MEM_READ`
- `MEM_WRITE`
- `MDR_LOAD`
- `MDR_OUT`

Memory and MMIO decode must preserve the frozen K8 memory map.

## Flags

F implements the live architectural flags C, Z, N, V and I. B is not a live state bit; it is synthesized only in the stacked status representation required by BRK/PHP semantics.

Direct controls include the frozen `C_SET`, `C_CLEAR`, `I_SET`, `I_CLEAR` and `V_CLEAR` behavior.

## Control interface

The datapath consumes the canonical 48-bit logical control word defined in `spec/control-word.json`.

The physical control implementation may divide this across ROM slices, latches or boards, but it must not change the logical control contract.

## Observability

At minimum the Classic hardware design shall provide practical observation points for:

- clock and reset
- microstep
- DB0..DB7
- A0..A15 / MAR address
- A, X and Y state
- ALU result/status
- memory read/write
- instruction register
- important control signals

LEDs are useful for slow/single-step operation, while headers/test points remain the primary electrical debug interface.

## Schematic partition

The KiCad design should use hierarchical sheets or clearly separated functional areas:

1. clock/reset/single-step
2. control/sequencer
3. A/X/Y registers and DB
4. ALU/flags
5. PC/branch path
6. SP/stack path
7. MAR/MDR/AGU
8. memory and address decode
9. MMIO/peripherals
10. power, decoupling and debug headers

## Qualification requirement

The Classic datapath is not qualified by documentation alone. M4 must establish electrical schematics and shared verification vectors, and M5 must validate physical behavior against the emulator/simulator reference models.
