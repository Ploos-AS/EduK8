# K8 Classic Clock, Reset and Single-Step v1

K8 must be usable as both a computer and a visible digital-logic laboratory. Clocking therefore prioritises clean edges and observability over raw frequency.

## Clock modes

The board provides three mutually exclusive modes:

1. STEP — one debounced hardware pulse per button press.
2. SLOW — human-visible oscillator for teaching.
3. RUN — normal oscillator for software execution.

A hardware selector chooses the source before a final conditioned clock stage. Clock sources must not be directly wire-ORed or switched in a way that can create runt pulses.

## STEP mode

The push button is debounced and converted into exactly one clean clock edge.

Recommended implementation uses ordinary logic such as a Schmitt-trigger input plus latch/one-shot circuitry. Exact parts are selected during schematic capture.

Holding the button must not generate repeated clocks.

## SLOW mode

The teaching oscillator should cover approximately 1-10 Hz, with a default around 2 Hz. A visible CLK LED may be driven through a buffered indicator path so the LED does not load timing logic.

## RUN mode

The initial Classic board does not chase maximum frequency. Start conservatively and qualify faster oscillator options after timing analysis and hardware tests.

A socketed oscillator or configurable divider is preferred so experiments do not require redesigning the CPU.

## Clock integrity

- one conditioned CPU clock net
- local decoupling at every IC
- short clock routing where practical
- no front-panel LED directly loading the clock net
- source switching only through glitch-resistant selection
- labelled CLK test point

## Reset

Reset must be deterministic after power-up and manually repeatable.

Reset establishes at least:

- microstep = T0
- PC loaded from reset-vector sequence/defined reset mechanism
- SP = $FF
- architectural flags in their defined reset state
- HALT cleared
- AGUC cleared
- interrupt/control pending state cleared

The final electrical circuit should combine power-on reset with a debounced RESET button. Reset pulse width must satisfy every sequential component.

## Instruction-step versus microstep

Physical STEP advances one microstep. This is essential for teaching the datapath.

A later debug/front-panel feature may add INSTRUCTION STEP, which automatically clocks until INSTR_DONE, but it must be layered on top of the same sequencer rather than bypassing it.

## Front-panel indicators

Recommended buffered indicators:

- CLK
- RESET
- HALT
- IRQ
- INSTR_DONE
- microstep binary bits S0-S4

An optional teaching board can decode S0-S4 into T0-T31 indicators. The base CPU PCB only needs compact binary LEDs plus headers.

## Debug header

Expose:

- CLK
- RESET
- STEP request
- selected clock mode
- S0-S4
- INSTR_DONE
- HALT
- IRQ
- IRQ_ACK

## FPGA correspondence

The FPGA version uses a clock-enable for educational stepping rather than creating arbitrary fabric clocks. It exposes the same architectural step/reset state to the debugger.

## Qualification

Hardware qualification must verify:

1. one button press produces exactly one microstep
2. button bounce cannot double-step
3. switching modes cannot create an unintended CPU edge
4. reset always returns the sequencer to T0
5. repeated reset/step cycles are deterministic
6. slow and run modes execute the same conformance ROM
7. logic-analyser traces match documented fetch timing.

## Teaching exercise

Load a small ROM containing NOP followed by HALT. Select STEP and observe:

    T0: PC -> MAR
    T1: memory -> MDR
    T2: MDR -> IR and PC increments
    T3+: NOP completes

Then repeat in SLOW and RUN modes without changing the program.