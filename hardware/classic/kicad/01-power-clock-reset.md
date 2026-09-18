# KiCad sheet 01 — Power / Clock / Reset

The electrical intent and preliminary references for this sheet are frozen in:

- `POWER_CLOCK_RESET_DESIGN.md`
- `power-clock-reset-bom.csv`

The next KiCad edit must instantiate these components and nets rather than inventing a different clock/reset architecture.

Sheet outputs:

- `CLK`
- `RESET_N`
- `STEP_PULSE`

Debug-only/local nets include `SLOW_CLK` and `RUN_CLK`.

Clock-mode changes require RESET asserted until glitch-free switching is electrically qualified.
