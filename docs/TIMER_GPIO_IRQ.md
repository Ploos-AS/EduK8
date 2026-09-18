# K8 Classic Timer, GPIO and Shared IRQ v1

These peripherals are deliberately small and built from visible standard logic.

## Timer

Registers:

    $C030 TIMER_LO
    $C031 TIMER_HI
    $C032 TIMER_CONTROL
    $C033 TIMER_STATUS

The timer is a 16-bit down-counter assembled from cascaded counter/register stages.

TIMER_CONTROL:

- bit 0 ENABLE
- bit 1 PERIODIC
- bit 2 IRQ_ENABLE

TIMER_STATUS:

- bit 0 EXPIRED

Writing TIMER_LO/TIMER_HI defines the reload value. Enabling loads/starts the counter according to the documented sequence. At terminal count EXPIRED is latched. In PERIODIC mode the reload value is restored; otherwise counting stops.

The timer uses a divided system-clock tick so software timing remains useful while the CPU runs faster than the visible teaching clock. The exact base tick is frozen after oscillator selection.

EXPIRED must have deterministic software clear semantics; reading status alone must not accidentally acknowledge an interrupt unless explicitly specified.

## GPIO

Registers:

    $C040 GPIO_DATA
    $C041 GPIO_DIR
    $C042 GPIO_INPUT

GPIO is eight bits.

GPIO_DIR bit:

- 0 = input
- 1 = output

GPIO_DATA holds output latch values. GPIO_INPUT reads the actual conditioned pin levels.

Use 74HC245/574-class buffering/latching as appropriate. External header pins must include ground and clearly labelled bit numbers. Protection/series resistors should be considered during schematic capture.

GPIO must never expose an internal CPU bus directly to the external connector.

## Shared IRQ controller

Registers:

    $C000 IRQ_STATUS
    $C001 IRQ_MASK

Initial sources:

- bit 0 keyboard
- bit 1 timer

IRQ_STATUS reports pending sources. IRQ_MASK enables sources independently.

The CPU IRQ line is:

    IRQ = (keyboard_pending & mask0) | (timer_pending & mask1)

Source pending state is cleared at the peripheral using that peripheral's documented acknowledge/clear mechanism. Reading IRQ_STATUS does not silently clear sources.

## Interrupt boundary

The CPU samples IRQ at an instruction boundary. If IRQ is pending, enabled by the architectural interrupt state and not masked by I semantics, the control unit enters the microcoded IRQ sequence.

Precise polarity/meaning of the architectural I flag and BRK/IRQ/RTI stack semantics remain ISA-freeze items. Hardware must not freeze contradictory behaviour before that decision.

## Decode

The I/O decoder provides independent selects for:

- /SYSIO_CS
- /TIMER_CS
- /GPIO_CS

Lower address bits select registers inside each block.

## Signals to expose

Timer:

- timer tick
- counter low/high
- terminal count
- EXPIRED
- timer IRQ request

GPIO:

- output latch
- direction bits
- conditioned pin inputs

IRQ:

- keyboard pending
- timer pending
- IRQ_MASK bits
- combined CPU IRQ
- CPU IRQ_ACK

## FPGA correspondence

The FPGA implementation preserves the same registers, pending/mask logic and timer semantics. The timer tick is parameterised for simulation while retaining software-visible behaviour.

## Qualification

1. timer one-shot expiry
2. periodic reload
3. timer disabled state
4. timer IRQ masked/unmasked
5. keyboard IRQ masked/unmasked
6. simultaneous pending sources
7. IRQ_STATUS does not acknowledge
8. GPIO input read
9. GPIO output latch
10. mixed input/output directions
11. reset state for timer, GPIO and IRQ controller

## Teaching exercises

1. Blink an LED with GPIO polling.
2. Change GPIO_DIR and observe the external pin behaviour.
3. Generate a periodic timer event.
4. Poll TIMER_STATUS before enabling interrupts.
5. Enable timer IRQ and trace the shared IRQ line.
6. Trigger keyboard and timer together and inspect IRQ_STATUS.