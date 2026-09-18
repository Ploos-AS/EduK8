# K8 Classic Control Unit — component design v0.1

The control unit is deliberately visible microcoded logic. It converts opcode, microstep and condition state into the 48 control signals defined by the architecture.

## Microaddress

The logical microaddress is 15 bits:

    MA[14:0] = IR[7:0] : STEP[4:0] : COND[1:0]

This provides 32768 control-store addresses.

- IR[7:0] identifies the instruction.
- STEP[4:0] selects T0..T31.
- COND[1:0] selects one of four conditional microcode variants.

The exact COND encoding is a control-ROM build-time contract and must be frozen before ROM images are generated.

## Microstep sequencer

A synchronous binary counter provides STEP[4:0].

Required operations:

- reset to T0 on RESET
- advance one microstep on each CPU microclock
- return to T0 on STEP_RESET / INSTR_DONE
- remain stopped while HALT is active

Candidate implementation uses cascaded 74HCT163-class counters. Only five state bits are architecturally used.

STEP[0..4] must be visible on LEDs/test header through buffered outputs.

## Control store

The control word is 48 bits wide, implemented as six parallel 8-bit ROM/EEPROM slices:

    U60 -> CW[7:0]
    U61 -> CW[15:8]
    U62 -> CW[23:16]
    U63 -> CW[31:24]
    U64 -> CW[39:32]
    U65 -> CW[47:40]

Each slice requires at least 15 address inputs and 32768 byte locations.

All six devices share MA[14:0] and output-enable timing.

The ROM technology/MPN remains an electrical/BOM freeze item. 28C256-class 32Kx8 EEPROM is the preferred educational baseline if qualified parts are obtainable.

## Conditional selection

COND[1:0] is generated from selected architectural conditions rather than exploding the ROM address with every flag.

Candidate condition mux inputs include:

- C
- Z
- N
- V
- IRQ eligible = IRQ && !I
- fixed true/false

74HCT151/153-class mux logic is preferred so selection remains probeable.

The condition selector itself is driven by explicit control/decode state. The final encoding must allow all branch instructions and instruction-boundary IRQ acceptance without hidden combinational behaviour.

## Fetch

T0 onward implements the common instruction fetch sequence. The control ROM owns the exact physical microsteps, but the visible intent remains:

    PC -> MAR
    memory read -> MDR/DB
    DB -> IR
    PC increment
    execute opcode microsequence

No instruction bypasses the sequencer with a hidden CPU path.

## Instruction completion

INSTR_DONE terminates an instruction and resets the sequencer to T0.

STEP_RESET is the electrical sequencer reset control. The control-ROM generator/checker must ensure every legal instruction path terminates within T0..T31.

Undefined opcodes must enter a deterministic illegal-opcode/trap sequence; they must never execute random EEPROM contents.

## Interrupt boundary

IRQ is sampled for acceptance at an instruction boundary.

When IRQ && !I is accepted, the control unit enters the architecturally frozen interrupt-entry sequence before the next opcode fetch:

1. push PC high
2. push PC low
3. push F with B=0
4. set I
5. read $FFFE/$FFFF
6. load PC
7. return to fetch

BRK uses its opcode microsequence and pushes B=1.

## Safe control-word rules

Static tooling must reject at least:

- more than one DB source enabled
- MEM_READ and MEM_WRITE simultaneously
- incompatible ALU operations simultaneously
- invalid register-load combinations
- missing termination within 32 steps
- writes from undefined/reserved opcodes
- control words using reserved bits

Unused control-store addresses are generated as a safe no-write word, not left to erased-device assumptions.

## Programming interface

The six EEPROM slices must be removable/socketed or in-circuit programmable through a dedicated programming header whose circuitry cannot drive the CPU buses during normal operation.

Generated microcode binaries are build artifacts. The machine-readable microcode source and generator are canonical.

## Debug header

Expose:

- MA[0..14]
- IR[0..7]
- STEP[0..4]
- COND[0..1]
- CW[0..47] preferably split over headers
- INSTR_DONE
- STEP_RESET
- IRQ
- I
- HALT

At minimum, all microaddress bits and sequencer state must be easy to probe.

## Qualification

1. RESET -> T0
2. STEP advances T0..T31
3. STEP_RESET returns to T0
4. every EEPROM sees identical MA
5. known address returns expected 48-bit word
6. NOP fetch/execute/terminate trace
7. branch taken/not-taken condition paths
8. IRQ masked/unmasked boundary paths
9. BRK interrupt-entry path
10. undefined opcode reaches deterministic trap
11. static bus-contention checker passes entire ROM
12. Classic trace matches emulator/FPGA architectural trace
