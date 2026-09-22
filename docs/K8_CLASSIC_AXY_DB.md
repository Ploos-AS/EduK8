# K8 Classic A/X/Y Register and Data-Bus Sheet

## Status

**M4 schematic-definition candidate**

This document defines the signal-level implementation contract for the A, X and Y register bank and the internal 8-bit data bus (DB). It is intended to map directly to a KiCad hierarchical sheet.

## Devices

Use three 74HC574 octal D-type registers:

- U_A — A register
- U_X — X register
- U_Y — Y register

Each device is powered from +5V and GND with a local 100 nF ceramic decoupling capacitor placed close to its supply pins.

## Data bus

The shared internal bus is named:

- DB0
- DB1
- DB2
- DB3
- DB4
- DB5
- DB6
- DB7

Each 74HC574 D input connects to the corresponding DB bit.

Each Q output connects back to the corresponding DB bit through the device's tri-state output stage.

Only one bus-driving source may be enabled at a time. This is an architectural/control-unit invariant and must also be checked by the control-word validator.

## Register output enables

74HC574 output enable is active-low. The frozen logical controls are active-high:

- A_OUT
- X_OUT
- Y_OUT

The schematic therefore derives:

- /A_OE = NOT A_OUT
- /X_OE = NOT X_OUT
- /Y_OE = NOT Y_OUT

The inversion may be implemented with a 74HC04 shared with other sheet-level control inversions.

The physical net names should retain both meanings where practical so students can see the relationship between the architectural control signal and the IC pin polarity.

## Register loading

Frozen logical load controls:

- A_LOAD
- X_LOAD
- Y_LOAD

K8 must not create asynchronous combinational glitches on individual register clocks.

The preferred Classic implementation uses a common clean CPU clock plus explicit load qualification. The final clock/control sheet shall choose one of these safe implementations:

1. clock-enable equivalent built with edge-safe gating/latching, or
2. D-input hold multiplexing so all registers share the same clock and only the selected register changes.

**D-input hold multiplexing is the preferred baseline** because it preserves a single global clock tree.

For each bit of each register:

- LOAD=1: D receives DB bit
- LOAD=0: D receives the register's current Q value

This requires an 8-bit 2:1 mux function per register, implemented with two 74HC157 devices per 8-bit register unless a suitable equivalent octal mux is selected.

Thus the baseline A/X/Y register bank is:

- 3 × 74HC574
- 6 × 74HC157
- shared inversion/buffering as required

This costs more ICs than gated clocks but makes the clocking model explicit and robust for an educational machine.

## Clock

All three 74HC574 CLK inputs connect to the same qualified CPU clock net:

- CPU_CLK

No A/X/Y-local generated clock is permitted.

The selected DB value must meet setup/hold timing at the active CPU_CLK edge.

## Reset

A/X/Y are not required to have dedicated asynchronous reset pins in the 74HC574 baseline. Architectural reset establishes required programmer-visible reset state through the reset microsequence/control path.

If later hardware qualification requires deterministic electrical zeroing before microcode executes, the register implementation may be revised to a reset-capable part without changing the architectural interface.

## Debug/observation

Provide a labelled 2x5 or similar debug header for:

- DB0..DB7
- GND
- optional +5V or key/no-connect position

Also provide labelled test points for:

- A_LOAD
- X_LOAD
- Y_LOAD
- A_OUT
- X_OUT
- Y_OUT
- CPU_CLK

Do not drive indicator LEDs directly from DB or register outputs if their loading can affect timing or logic levels. Use buffered LED observation where desired.

## Bus safety

The following combinations are illegal:

- A_OUT + X_OUT
- A_OUT + Y_OUT
- X_OUT + Y_OUT

and likewise any A/X/Y output enable combined with another DB source unless the architecture explicitly guarantees that the other source is disabled.

The control validator remains the first line of defense. Hardware may additionally provide optional contention/debug indication, but it must not alter normal DB behavior.

## KiCad hierarchical ports

The A/X/Y sheet should expose:

### Inputs

- DB[7..0] (bidirectional bus connection)
- CPU_CLK
- A_LOAD
- X_LOAD
- Y_LOAD
- A_OUT
- X_OUT
- Y_OUT
- +5V
- GND

### Observable outputs

Architecturally the register Q outputs join DB only when enabled. For debugging and simulator-correlated probing, separate non-bus observation nets may be exposed internally as:

- A_Q[7..0]
- X_Q[7..0]
- Y_Q[7..0]

If these leave the sheet, buffer them rather than adding substantial load to the register outputs.

## Qualification checks

Before this sheet is frozen:

1. verify load/hold behavior for every A/X/Y register bit,
2. verify disabled 74HC574 outputs are high impedance,
3. verify exactly one enabled register drives DB correctly,
4. verify control validator rejects multiple DB drivers,
5. verify single-step CPU_CLK causes one register update,
6. compare A/X/Y state transitions against simulator vectors.

## KiCad implementation note

The first schematic revision should favor readability over compactness: draw A, X and Y as three visually repeated blocks with DB on the left, observation/state on the right and control signals at the bottom. This makes the physical schematic useful as course material as well as manufacturing documentation.
