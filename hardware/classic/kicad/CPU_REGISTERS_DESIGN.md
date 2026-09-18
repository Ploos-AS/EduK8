# CPU Register Bank and Data Bus — schematic design v0.1

This sheet implements the first concrete K8 CPU datapath block: A, X, Y, IR and TMP around DB[0..7].

## Electrical convention

- +5 V HCT logic.
- Active-low output enables use the suffix `_OE_N`.
- Architectural control names such as A_OUT are decoded to the electrical enable locally.
- No unused CMOS input may float.
- Every IC receives 100 nF local decoupling.

## DB[0..7]

DB is an 8-bit shared tri-state bus.

The register sheet may drive DB from only these sources:

- A
- X
- Y
- TMP

IR does not drive DB in v1.

Other sheets later add MDR/memory, ALU and peripheral bus sources.

A bus source uses a 74HCT245-class buffer between stored register outputs and DB. This makes the source enable explicit and gives a clean place to probe/isolate each register.

## A register

- U10: 74HCT574, A storage.
- U11: 74HCT245, A -> DB driver.
- D inputs: DB[0..7].
- Clock/load: A_LOAD-qualified register clock.
- Stored outputs: A_Q[0..7].
- A_Q feeds ALU input A continuously.
- A_OUT enables U11.

Debug header exposes A_Q[0..7].

## X register

- U12: 74HCT574.
- U13: 74HCT245, X -> DB.
- D inputs: DB[0..7].
- X_Q[0..7] also feeds AGU index input.
- X_LOAD and X_OUT are explicit controls.

## Y register

- U14: 74HCT574.
- U15: 74HCT245, Y -> DB.
- D inputs: DB[0..7].
- Y_Q[0..7] also feeds AGU index input.
- Y_LOAD and Y_OUT are explicit controls.

## IR register

- U16: 74HCT574.
- D inputs: DB[0..7].
- IR_LOAD latches the fetched opcode.
- IR_Q[0..7] goes directly to the control-unit opcode address.
- IR_Q is exposed on the debug header.
- No general DB output driver is fitted.

## TMP register

- U17: 74HCT574.
- U18: 74HCT245, TMP -> DB.
- D inputs: DB[0..7].
- TMP_LOAD and TMP_OUT are explicit controls.
- TMP_Q[0..7] is debug-visible.

## Register loading

74HCT574 is edge-triggered, not a level-sensitive register. Therefore the control design must produce a safe write/latch edge from CLK and each logical LOAD control.

Do not gate CLK with an arbitrary AND gate in the final schematic. The load-clock topology must be chosen as part of the clock/control timing review. If clock gating proves undesirable, a register family with explicit enable may replace the 574 before schematic freeze.

This is an intentional open electrical decision.

## Bus contention rule

At most one DB output enable may be active in a microstep.

For this sheet:

    popcount(A_OUT, X_OUT, Y_OUT, TMP_OUT) <= 1

The repository control-ROM checker must eventually enforce this together with bus sources on the ALU, memory and peripheral sheets.

## Debug header JDBG_REG

Expose:

- DB[0..7]
- A_Q[0..7]
- X_Q[0..7]
- Y_Q[0..7]
- IR_Q[0..7]
- TMP_Q[0..7]
- A_OUT/X_OUT/Y_OUT/TMP_OUT
- A_LOAD/X_LOAD/Y_LOAD/IR_LOAD/TMP_LOAD

Large buses may be split across more than one physical 0.1-inch header while preserving these labels.

## Reset behaviour

A, X, Y, IR and TMP are not required to contain architecturally meaningful values immediately after reset unless the ISA says otherwise. Software-visible reset requirements must be met by control sequencing rather than assuming a 74HCT574 has an asynchronous clear input.

This avoids adding fake reset behaviour that the chosen IC cannot provide.

## Qualification

1. load each register from DB
2. drive each bus source independently
3. verify disabled drivers are high impedance
4. transfer A -> DB -> X
5. transfer X -> DB -> Y
6. verify IR feeds opcode debug/control signals
7. verify TMP round-trip
8. prove no legal microcode enables two DB sources
9. compare captured register trace with FPGA simulation
