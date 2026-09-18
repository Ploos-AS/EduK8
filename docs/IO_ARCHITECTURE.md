# K8 v1 I/O Architecture

K8 uses simple memory-mapped I/O so a learner can follow an operation from an instruction, across the address/data buses, into a peripheral.

## v1 I/O page

The first I/O page is $C000-$C0FF. Devices receive deliberately visible, fixed register blocks.

| Range | Device |
|---|---|
| $C000-$C00F | system / board control |
| $C010-$C01F | keyboard |
| $C020-$C02F | video |
| $C030-$C03F | timer |
| $C040-$C04F | GPIO |
| $C050-$C0FF | reserved for teaching/expansion |

Unimplemented/reserved reads return $00 in v1 and writes are ignored.

## Keyboard — PS/2

The first physical keyboard interface is PS/2. USB is intentionally not required for K8 v1: PS/2 is simple enough to implement, probe and teach.

- $C010 KEY_DATA: read next received byte
- $C011 KEY_STATUS: bit0 DATA_READY, bit1 OVERRUN
- $C012 KEY_CONTROL: bit0 IRQ_ENABLE
- $C013 KEY_RAW: current sampled PS/2 clock/data in bits 0/1 for teaching/debug

Reading KEY_DATA clears DATA_READY when no further byte is queued. The first lessons poll DATA_READY; later lessons enable IRQ.

## Video — text first

K8 v1 has a hardware text display. The initial target is 40x25 characters with an 8x8 glyph cell and a 256-glyph character ROM.

The video generator reads character codes from dedicated video RAM and glyph rows from character ROM. This keeps the complete path visible:

    CPU -> video RAM -> character code -> character ROM -> pixels -> VGA

Initial video RAM is mapped at $7800-$7BFF. 1000 bytes are visible; remaining bytes in the 1 KiB window are reserved.

Video registers:

- $C020 VIDEO_CONTROL: bit0 DISPLAY_ENABLE
- $C021 VIDEO_STATUS: bit0 VBLANK
- $C022 CURSOR_X: 0-39
- $C023 CURSOR_Y: 0-24
- $C024 CURSOR_CONTROL: bit0 ENABLE, bit1 BLINK
- $C025 BORDER: reserved for future colour-capable hardware; reads $00 in monochrome v1

The initial K8 can therefore display useful text without requiring bitmap graphics. Graphics/colour are extension milestones, not hidden requirements of the base machine.

### Display connector

VGA is the initial educational display output. The timing generator and character pipeline must be documented and probeable. A later adapter may provide a modern display connector without changing the CPU-visible interface.

## Timer

- $C030 TIMER_LO
- $C031 TIMER_HI
- $C032 TIMER_CONTROL: bit0 ENABLE, bit1 PERIODIC, bit2 IRQ_ENABLE
- $C033 TIMER_STATUS: bit0 EXPIRED

The timer is intentionally simple enough to teach counters, polling and interrupts.

## GPIO

- $C040 GPIO_DATA
- $C041 GPIO_DIR
- $C042 GPIO_INPUT

Eight GPIO bits allow LEDs, switches and breadboard experiments to become software-visible peripherals.

## Interrupt model

Keyboard and timer can request the single K8 IRQ line. A small interrupt-status register identifies the source:

- $C000 IRQ_STATUS: bit0 KEYBOARD, bit1 TIMER
- $C001 IRQ_MASK: bit0 KEYBOARD, bit1 TIMER

This deliberately introduces shared interrupt arbitration without requiring a complex interrupt controller.

## Hardware-learning requirements

Schematics and PCB silkscreen should expose labels/test points for I/O select, device selects, R/W, DB0-DB7 and relevant peripheral clocks. Emulator tracing should show I/O reads/writes by symbolic register name.

No MCU may implement these peripherals invisibly. A helper MCU may later exist as an optional programmer/debug adapter, but the educational K8 hardware path remains independently understandable.
