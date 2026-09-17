# K8 Control Unit

**Status:** M2/M4 architectural draft

The control unit is the bridge between the K8 ISA and the physical machine. Its primary design goal is observability: a learner should be able to follow an instruction using LEDs, test points, a logic analyser, the emulator trace, and the schematic.

## Internal CPU registers

In addition to programmer-visible A, X, Y, PC, SP and F, the implementation defines:

| Register | Width | Purpose |
|---|---:|---|
| IR | 8 | instruction register |
| MAR | 16 | memory address register |
| MDR | 8 | memory data register |
| TMP | 8 | temporary ALU/control value |

These are implementation-visible: software cannot address them, but educational tooling may display them.

## Buses

- DB: 8-bit internal data bus
- AB: 16-bit address bus
- memory data bus: 8-bit
- control bus: individual named control lines

The first physical implementation should favour one clearly observable shared data path over clever internal optimisation.

## Clock model

An instruction consists of numbered microsteps T0..Tn. One microstep is one control-unit state.

Baseline fetch:

| Step | Transfer/action |
|---|---|
| T0 | PC -> MAR |
| T1 | MEM[MAR] -> MDR |
| T2 | MDR -> IR; PC <- PC + 1 |
| T3+ | opcode-specific execution |

HALT stops automatic sequencing without destroying architectural state. Single-step hardware may advance one microstep at a time.

## Initial control signals

### Register/bus

- A_OUT, A_IN
- X_OUT, X_IN
- Y_OUT, Y_IN
- PC_OUT, PC_IN, PC_INC
- SP_OUT, SP_IN, SP_INC, SP_DEC
- IR_IN
- MAR_IN_LO, MAR_IN_HI
- MDR_OUT, MDR_IN
- TMP_OUT, TMP_IN
- F_IN

### Memory

- MEM_READ
- MEM_WRITE

### ALU

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
- ALU_FLAGS

### Sequencer

- STEP_RESET
- INSTR_DONE
- HALT
- IRQ_ACK

Names are logical signals. PCB polarity will be made explicit later; active-low electrical nets should use a consistent suffix.

## Example: LDA immediate

| Step | Control intent |
|---|---|
| T0 | PC -> MAR |
| T1 | MEM_READ, memory -> MDR |
| T2 | MDR -> IR, PC_INC |
| T3 | PC -> MAR |
| T4 | MEM_READ, memory -> MDR |
| T5 | MDR -> A, update Z/N, PC_INC, INSTR_DONE |

## Example: ADD immediate

| Step | Control intent |
|---|---|
| T0 | PC -> MAR |
| T1 | MEM_READ, memory -> MDR |
| T2 | MDR -> IR, PC_INC |
| T3 | PC -> MAR |
| T4 | MEM_READ, memory -> MDR |
| T5 | A + MDR + C -> A, update C/Z/N/V, PC_INC, INSTR_DONE |

## Example: STA absolute

| Step | Control intent |
|---|---|
| T0-T2 | common opcode fetch |
| T3 | PC -> MAR; fetch low address byte |
| T4 | memory -> MDR; PC_INC |
| T5 | MDR -> TMP |
| T6 | PC -> MAR; fetch high address byte |
| T7 | memory -> MDR; PC_INC |
| T8 | TMP/MDR form 16-bit MAR |
| T9 | A -> MDR |
| T10 | MEM_WRITE MDR -> MEM[MAR], INSTR_DONE |

The exact gate-level implementation may refine these steps, but externally visible architectural results must not change.

## Sequencer implementation

The preferred first design is a deliberately understandable microcoded/sequenced control unit rather than a dense programmable device hiding the CPU.

Candidate implementation:

1. binary microstep counter
2. opcode in IR
3. flags/condition inputs
4. EEPROM control store
5. decoded/latching control signals

Using EEPROM for the control store is acceptable because its contents are part of the educational design: the complete control word format and generated image must be published and inspectable.

A later hardwired-control exercise can implement a subset of the same ISA using gates.

## Observability requirements

The physical K8 should expose at least:

- T0..Tn/current microstep
- clock
- reset
- DB[7:0]
- AB[15:0]
- IR[7:0]
- memory read/write
- ALU operation
- instruction-done
- halt

Where practical, front-panel LEDs should show the data bus, address bus, current instruction and microstep.

## Emulator contract

The emulator's micro-operation trace should converge on this document. Microsteps are part of the educational model, but only programmer-visible ISA state is software compatibility state.

## Hardware constraint

Control-unit elegance is secondary to clarity, repairability, probeability and hand assembly. A few additional inexpensive logic ICs are preferable to hiding an important concept.
