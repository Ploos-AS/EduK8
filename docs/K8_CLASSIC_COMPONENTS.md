# K8 Classic Component Baseline

## Status

**M4 component-selection candidate**

K8 Classic uses a 5 V 74HC-family baseline. Through-hole DIP parts are preferred for the educational/repairable Classic implementation when they are reasonably obtainable. The logical architecture remains authoritative; equivalent HC/HCT parts may be substituted only when voltage thresholds, drive, timing and polarity remain compatible.

## Core rules

- nominal logic supply: 5 V
- 74HC is the default family
- socket DIP ICs where practical
- one 100 nF local decoupling capacitor per logic IC, plus bulk capacitance per board/module
- no floating CMOS inputs
- labelled test points/debug headers for important buses and controls
- bus contention must be prevented by control logic, not by relying on output resistance
- LEDs must use buffers/drivers where their loading would disturb architectural signals

## Register and bus building blocks

### 74HC574 — preferred 8-bit bus register

Use 74HC574 for A, X, Y and other 8-bit registers that benefit from an integrated tri-state output.

Properties useful to K8:

- eight edge-triggered D flip-flops
- common clock
- tri-state outputs
- direct fit for an 8-bit register connected to DB

The output-enable signal is derived from the corresponding frozen logical *_OUT control. Register loading is implemented with the clock/load gating strategy chosen on the clock/control schematic; do not create uncontrolled asynchronous clocks locally.

### 74HC273 — state register where tri-state output is unnecessary

Use 74HC273 where an octal edge-triggered register with reset is useful and its outputs do not directly share DB.

Candidate uses include internal/control state where reset behavior is valuable.

### 74HC245 — bus transceiver/buffer

Use 74HC245 for explicitly buffered 8-bit paths and external/debug isolation where bidirectional transfer is required.

### 74HC244 / 74HC541 — unidirectional buffering

Use octal tri-state buffers for address/control fan-out, debug headers and paths that do not require bidirectional transfer.

## 16-bit registers

PC and MAR are constructed as explicit high/low 8-bit halves so the schematic remains readable and the frozen low/high load controls remain visible.

The exact counter/load implementation for PC is intentionally deferred to the PC/branch schematic sheet. MAR should use two octal register stages or equivalent logical halves compatible with MAR_LOAD_LO and MAR_LOAD_HI.

## ALU

Do **not** make a vintage 74181 a mandatory production dependency.

K8's frozen ALU operation set is wider than a single convenient 74181 mapping and long-term DIP sourcing should not define the architecture. The Classic ALU will therefore be built from currently obtainable 74HC arithmetic/logic primitives, with functions selected onto the result path.

Candidate primitives:

- 74HC283 — 4-bit binary adder; two devices form the 8-bit arithmetic path
- 74HC86 — XOR
- 74HC08 — AND
- 74HC32 — OR
- 74HC04 — NOT
- 74HC157/74HC153-class multiplexers — operand/function selection
- 74HC74 or equivalent — carry/state latches where a dedicated bit is required

Shift/rotate logic should use explicit mux/wiring stages so C input/output and bit movement are visible to students.

A future optional 74181 demonstration/alternate ALU board is allowed, but it must implement the same K8 ALU contract and pass the same verification vectors.

## Flags

Architectural flags C, Z, N, V and I should be held in explicit flip-flop/register state. B is not a live flag.

Candidate parts:

- 74HC74 for individually controlled flag bits
- 74HC273/574 where grouped flag/state capture makes the schematic clearer
- 74HC688/logic reduction or discrete gates for zero detection, selected according to the final ALU sheet

## AGU

The address-generation adder should reuse the same understandable HC arithmetic approach:

- 74HC283-class addition
- explicit X/Y selection
- AGUC held in a visible flip-flop
- low-byte then high-byte operation matching the simulator/control specification

Physical arithmetic reuse between ALU and AGU is permitted only if it does not make control timing opaque. Educational clarity is preferred over saving a small number of ICs.

## SP and stack address

SP is an 8-bit register/counter function. Its physical implementation must support load, increment, decrement and output into the stack-address path while forcing address high byte to $01.

Candidate implementation uses an 8-bit register plus HC increment/decrement arithmetic/mux logic rather than introducing a programmable MCU/CPLD.

## Control/sequencer

The Classic control unit remains ROM/microcode based and consumes the canonical logical 48-bit control word.

Physical ROM organization follows the already-qualified six-byte control-ROM slicing model. Sequencing and condition selection must remain discrete/observable; no hidden MCU is permitted in the Classic control path.

EEPROM/flash part numbers are selected on the control-unit sheet because capacity, package availability and programmer support must be checked together.

## Memory

Memory parts are selected on the memory sheet, with these constraints:

- 5 V-compatible parallel interface preferred
- 16-bit addressability across the K8 64 KiB architectural space
- ROM/RAM partition must follow the frozen memory map
- sockets for replaceable memory devices
- programming/debug workflow must not require proprietary hardware

## Clock/reset

Use ordinary HC logic, Schmitt-trigger parts and/or a simple oscillator source. Manual single-step must be debounced and produce exactly one architectural clock event. Clock/reset implementation remains on its dedicated sheet.

## Procurement policy

The BOM should identify function and acceptable equivalents rather than tying K8 to one manufacturer. Each critical device needs at least one realistic current source before PCB freeze.

DIP availability is preferred but not absolute: if a function becomes difficult to source in DIP, a socketable adapter/module may be documented rather than redesigning the K8 architecture around an obsolete device.

## Next schematic decisions

Before the Classic datapath can be marked frozen, M4 still needs concrete sheet-level decisions for:

1. A/X/Y register clock/load implementation
2. 8-bit ALU function-select network
3. PC increment/load/branch circuit
4. SP increment/decrement/load circuit
5. MAR/MDR and AGU circuit
6. flags capture and zero/overflow generation
7. memory/MMIO bus buffering
8. control-ROM electrical organization
