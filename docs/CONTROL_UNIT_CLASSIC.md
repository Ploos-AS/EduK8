# K8 Classic Control Unit v1

The K8 control unit is microcoded and deliberately observable. An instruction is a sequence of small hardware actions rather than opaque combinational logic.

## Microaddress

Use a 5-bit microstep counter in v1. This gives T0-T31 and replaces the earlier provisional 4-bit/T0-T15 assumption.

Logical microaddress fields:

    opcode[7:0] | step[4:0] | condition[1:0]

Total logical address width: 15 bits.

The extra step bit is intentional: stack, interrupt and indexed-address sequences must not be distorted merely to fit 16 steps.

## Sequencer

Recommended discrete implementation:

- 74HC161/163-class counter for microstep
- reset-to-T0 control
- explicit instruction-done control
- condition selection/multiplexing
- EEPROM/flash control store

At reset, the sequencer starts at T0.

## Fetch sequence

Every instruction begins with the same conceptual fetch:

    T0: PC -> MAR
    T1: memory read -> MDR
    T2: MDR -> IR, PC++
    T3+: instruction-specific execution

The physical schematic may overlap safe actions after timing qualification, but documentation keeps the educational sequence explicit.

## Conditions

The initial two condition-address bits support microcode selection based on a small explicit condition mux. Candidate sources include C, Z, N, V, IRQ-pending and unconditional state.

The exact encoding is generated from the machine-readable control specification; it must not be hidden in schematic folklore.

## Control store

The existing 48-bit conceptual control word is retained as the architectural control interface, but physical EEPROM width may be implemented as multiple parallel devices.

Example physical arrangement:

    microaddress -> ROM A -> control bits 0..7
                 -> ROM B -> control bits 8..15
                 -> ...

This makes every control bit directly inspectable.

## Safety interlocks

The generated microcode must be statically checked for:

- more than one general data-bus source enabled
- memory read and write asserted together
- incompatible ALU operations asserted together
- instruction sequences without termination
- undefined microaddresses that could perform writes

Unused control-store entries must decode to a safe no-write state.

## Instruction completion

INSTR_DONE resets the microstep counter to T0 for the next instruction. HALT stops architectural instruction progress without creating an undocumented reset state.

## Interrupt entry

IRQ is sampled at a documented instruction boundary. Interrupt entry is a microcoded sequence and receives enough T states to push state and fetch the vector cleanly.

The precise BRK/IRQ/RTI stack byte order remains an ISA-freeze item and must be resolved before control ROM v1 is declared final.

## Clocking

v1 starts with a deliberately slow clock and supports manual single-step.

Required modes:

- manual microstep clock
- slow visible clock
- normal run clock

The first hardware target is correctness and observability, not maximum MHz.

## Front-panel/debug exposure

Expose:

- T0-T31 encoded step
- current opcode/IR
- control-store address
- clock
- instruction-done
- halt
- IRQ pending/ack
- major bus-enable controls

Optional LEDs may show the microstep and selected control-state summary, while headers expose full signals to a logic analyser.

## FPGA correspondence

The FPGA sequencer must use the same generated microcode/control definitions where practical and expose opcode, step, condition and control word in simulation.

## Tooling requirement

Control ROM images must be generated from repository specifications. Hand-editing EEPROM binary images is prohibited.

CI must eventually validate:

1. microcode schema
2. control-word legality
3. bus-contention rules
4. termination within T0-T31
5. emulator/control-ROM consistency
6. FPGA simulation against shared vectors.

## Teaching exercises

1. Single-step NOP through fetch and completion.
2. Watch PC transfer to MAR.
3. Observe IR load and PC increment.
4. Compare LDA immediate with LDA absolute.
5. Identify which microstep enables each bus driver.
6. Modify a safe educational microprogram and regenerate a ROM image.