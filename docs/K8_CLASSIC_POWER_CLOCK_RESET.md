# K8 Classic Power, Clock, Reset and Single-Step

## Status

**M4 schematic-definition candidate**

This document defines the electrical infrastructure for K8 Classic: 5 V power distribution, clock generation, reset and deterministic manual stepping.

## Power architecture

K8 Classic uses a regulated 5 V logic rail.

The board must not depend on an unregulated external supply. Preferred input is a common protected DC source followed by an onboard 5 V regulator, or a clearly specified regulated 5 V input with protection.

Provide:

- reverse-polarity protection where applicable
- input fuse/polyfuse
- bulk input capacitance
- regulated 5 V rail
- power-good indication
- accessible 5 V and GND test points
- clear current-budget documentation

No user connector may back-power the board unintentionally.

## Decoupling

Every logic IC receives a local 100 nF ceramic bypass capacitor placed close to its supply pins.

Provide bulk capacitance per functional area and near memory/video sections where switching current is concentrated.

KiCad power symbols must not hide the physical decoupling requirement; BOM and placement documentation shall account for every capacitor.

## Grounding

Use a continuous low-impedance ground strategy. Avoid daisy-chaining logic ground through headers or modules.

External connector shields/grounds and video return paths must be documented so noisy outputs do not corrupt clock/reset behavior.

## Clock source

Classic requires a stable oscillator source plus an intentionally slow/debuggable mode.

The baseline shall support:

- RUN mode from a stable oscillator
- STEP mode from a debounced pushbutton
- optional external clock/debug input

A Schmitt-trigger oscillator is acceptable for low-speed bring-up; a canned oscillator is preferred when precise video/CPU timing requires it.

CPU clock and video clock may be separate if required by the video architecture.

## Clock selection

Clock source selection must never generate runt pulses.

Do not use a raw mechanical switch as a clock mux.

Use synchronized/gated selection or require the CPU to be halted/reset while changing clock source.

Expose the selected clock source and final CPU_CLK.

## Manual single-step

One press of STEP must produce exactly one complete qualified hardware cycle, independent of button bounce or press duration.

Required blocks:

1. switch input protection
2. Schmitt cleanup
3. debounce
4. edge/pulse generation
5. clock-safe gating/selection

74HC14 plus 74HC74/123-class logic is acceptable.

The manual step circuit must not rely on software or a microcontroller.

## Microinstruction versus instruction stepping

The physical STEP button advances one hardware/microcycle.

A separate optional instruction-step mode may repeatedly clock until INSTR_DONE/STEP_RESET and then stop.

Instruction stepping must be implemented with visible control logic and must respect HALT and reset.

## Clock phases

The control-unit timing contract distinguishes:

1. sequencer/control address transition
2. ROM settle/control capture
3. datapath settle
4. architectural update

The electrical implementation may derive non-overlapping phases from a master clock or use conservative edge separation.

The final choice must be validated against worst-case ROM, memory and HC propagation delays from the actual BOM.

## Reset sources

Reset can be asserted by:

- power-on reset
- front-panel/manual RESET button
- optional external debug/reset input

All reset sources combine into one conditioned reset request.

Mechanical RESET must be debounced.

## Power-on reset

Power-on reset must hold the machine in a safe state long enough for:

- 5 V to become valid
- oscillator to stabilize
- control ROM outputs to settle
- sequencer state to become deterministic

An RC network alone is acceptable only if Schmitt-triggered and demonstrated robust across component tolerance and supply ramp. A reset supervisor is preferred if it materially improves reliability while remaining understandable.

## Reset safety

While reset is asserted:

- MEM_WRITE is inhibited
- external writable peripheral strobes are inhibited
- unsafe DB drivers are inhibited
- sequencer is forced to reset/fetch entry
- clock selection cannot create uncontrolled state changes

After release, the architectural reset microsequence establishes SP=FF and loads PC from FFFC/FFFD.

## HALT

HALT stops architectural CPU progress at a defined boundary.

Clock circuitry may stop the CPU clock, or the sequencer may hold state, but either method must avoid half-completed writes.

Manual RESET must always recover a halted machine.

## Front-panel signals

Recommended front-panel/debug indicators:

- POWER
- RESET
- RUN
- STEP
- HALT
- CPU_CLK
- optional instruction-complete pulse

LEDs on timing-sensitive nets must be buffered.

## External debug header

Provide:

- 5 V
- GND
- CPU_CLK
- external clock input
- RESET
- STEP pulse
- HALT
- INSTR_DONE
- STEP_RESET

Inputs need documented voltage levels and must not be directly paralleled with active onboard outputs.

## Qualification

Before schematic freeze, test:

- cold power-on
- slow supply ramp
- repeated reset
- reset during RUN
- reset during STEP
- reset while HALTed
- button bounce
- long STEP-button hold
- rapid repeated STEP presses
- RUN/STEP source switching
- external clock selection
- no spurious MEM_WRITE during reset/source switching
- correct T-state advancement for 1000 manual steps
- instruction-step stop at instruction boundary
- worst-case timing budget using actual BOM datasheets

## KiCad partition

1. input power/protection
2. 5 V regulation/distribution
3. decoupling/bulk power
4. oscillator
5. clock source selection
6. debounce/single-step
7. optional instruction-step controller
8. reset conditioning/power-on reset
9. HALT/clock-safe control
10. front-panel/debug header

The completed sheet is a prerequisite for freezing the full Classic datapath schematic.
