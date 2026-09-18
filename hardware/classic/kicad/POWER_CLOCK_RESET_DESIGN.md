# Power / Clock / Reset Schematic Design v0.1

This is the component-level design contract for the first electrical KiCad sheet.

## 5 V power entry

- J1: 2-pin 5 V input
- F1: resettable fuse, value selected during electrical review
- D1: reverse-polarity protection, implementation selected before PCB freeze
- C1: bulk input capacitor
- C2: bulk logic-rail capacitor
- one 100 nF local capacitor at every logic IC
- PWR LED driven from +5V through its own resistor

The first revision accepts regulated +5 V. It does not put an unnecessary high-dissipation linear regulator in front of a large TTL/CMOS board.

## U1 — 74HCT14 input conditioning

Use Schmitt-trigger sections for mechanical controls.

- U1A: STEP button conditioning
- U1B: RESET button conditioning
- remaining sections available for oscillator/reset conditioning after timing review

STEP and RESET switches use defined pull resistors. No logic input may float.

## STEP pulse

A debounced level is not by itself sufficient: holding STEP must produce only one CPU edge.

The first schematic therefore reserves a one-shot/edge-forming stage after U1A. Candidate implementation is a 74HCT74 edge latch or 74HCT123 one-shot. The exact device is deliberately not frozen until minimum/maximum pulse-width requirements of the sequencer are calculated.

Output net:

    STEP_PULSE

## SLOW clock

Use an RC Schmitt oscillator followed by a binary divider.

Candidate blocks:

- one 74HCT14 oscillator section
- 74HC4040 divider

Select a divider tap that gives a human-visible default near 2 Hz. Component values and divider tap are calculated from measured/qualified oscillator frequency rather than copied from a nominal RC formula alone.

Output net:

    SLOW_CLK

## RUN clock

J2/U2 provides a socketed 5 V oscillator module.

Initial bring-up oscillator should be conservative. Faster oscillator modules are qualification options, not architecture changes.

Output net:

    RUN_CLK

## Clock selection

SW3 is a three-position STEP / SLOW / RUN user selector.

Do not route the three raw clock sources directly through a mechanical switch to CLK. The selector produces static mode-control signals; logic gates/multiplexers create a conditioned source path.

A mode change is only considered safe when it cannot create a runt or extra CPU edge. Until the glitch-free switching circuit is proven, the operating rule is:

> Change clock mode while RESET is asserted.

This is an explicit v0.1 safety rule rather than pretending asynchronous source switching is solved.

## Final clock buffer

The selected source passes through a dedicated buffer/Schmitt stage before becoming:

    CLK

CLK LED is driven from a buffered copy, never directly from the CPU clock net.

## Power-on/manual reset

RESET button and power-on reset combine into an asynchronous reset request.

A capacitor/resistor plus Schmitt input is acceptable for initial POR only if rise/fall behaviour is electrically verified. A supervisor IC remains an option if it gives more deterministic power-on behaviour without hiding CPU function.

Output:

    RESET_N

Reset must remain asserted long enough for:

- clock/control sequencer
- register reset paths
- IRQ/peripheral latches

## Debug header JDBG1

Expose:

- +5V
- GND
- CLK
- RESET_N
- STEP_PULSE
- SLOW_CLK
- RUN_CLK
- clock-mode selects

## LEDs

Buffered indicators:

- POWER
- CLK
- RESET
- HALT (from CPU sheet)
- IRQ (from IRQ sheet)

## Open electrical decisions before schematic freeze

1. STEP edge-former: 74HCT74 vs 74HCT123.
2. Exact oscillator module frequency.
3. SLOW RC values and 4040 divider tap.
4. POR RC versus voltage-supervisor IC.
5. Exact glitch-free source-select topology.
6. Input protection/fuse values.

These are electrical engineering decisions and must be calculated/qualified before a PCB is ordered.
