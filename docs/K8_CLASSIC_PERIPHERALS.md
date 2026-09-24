# K8 Classic MMIO Peripherals

## Status

**M4 schematic-definition candidate**

This document defines the hardware-level Classic implementation contract for the frozen K8 keyboard, timer, GPIO and text-video peripherals.

The architectural register map remains defined by spec/io-map.json, spec/keyboard.json, spec/peripherals.json and spec/video.json.

## Design rules

Classic peripherals must remain understandable and probeable.

- no hidden MCU may implement architectural peripheral behavior
- 5 V 74HC/discrete logic is preferred
- external voltage domains require explicit level conversion
- every peripheral has a visible chip-select and read/write path
- interrupt sources are explicit and independently observable
- unused inputs must never float

## Keyboard

The keyboard interface accepts PS/2 clock and data.

Because PS/2 electrical signaling is open-collector/open-drain, provide suitable pull-ups and input protection. If the connector-side voltage differs from Classic logic voltage, use proper level translation.

Hardware blocks:

1. PS/2 connector/protection
2. synchronized PS2_CLK input
3. synchronized PS2_DATA input
4. falling-edge detector
5. 11-bit receive shift path
6. start/parity/stop validation
7. scan-code latch
8. ready/overrun state
9. IRQ generation

The architectural receive depth for K8 Classic is one byte unless the frozen keyboard specification is revised.

Registers:

- C010 keyboard data
- C011 keyboard status
- C012 keyboard control
- C013 keyboard raw

Reading/acknowledging data must follow the exact ready/overrun clearing semantics in the canonical specification.

## Timer

The timer is a deterministic 16-bit counter/peripheral rather than an analog RC timer.

Registers:

- C030 timer low
- C031 timer high
- C032 timer control
- C033 timer status

Preferred implementation:

- two cascaded 8-bit counter stages or equivalent HC logic
- explicit timer tick input/divider
- enable control
- terminal/compare event as required by the frozen peripheral model
- latched status
- maskable IRQ request

Expose the timer tick separately from CPU_CLK so its relationship to CPU execution can be qualified.

## GPIO

Registers:

- C040 GPIO data
- C041 GPIO direction
- C042 GPIO input

Provide eight GPIO pins.

Each bit has explicit direction control. Output data is latched; input state is read through an input buffer.

Use buffering/protection suitable for an educational header. Do not expose fragile internal DB nodes directly.

Recommended header also provides labelled 5 V, GND and a warning that GPIO is logic-level I/O, not a power driver.

LEDs may show output state through buffering. Switches may provide optional demonstration inputs without preventing external GPIO use.

## Text video

The frozen display is 40x25 text with VRAM at 7800-7BFF.

Registers C020-C025 provide the frozen video/cursor control interface.

Classic video hardware is split into:

1. VRAM CPU interface
2. character-cell address generator
3. character ROM/font lookup
4. scan-line/pixel shift logic
5. horizontal timing
6. vertical timing
7. cursor overlay
8. physical display output

The first implementation should target a simple, documented VGA-compatible output if its timing can be generated cleanly with available logic.

Video timing must not alter CPU-visible VRAM semantics.

## VRAM arbitration

The display continuously consumes VRAM while the CPU may access it.

Acceptable Classic approaches are:

- dual-port-compatible memory
- deterministic time-slot arbitration
- display fetch during a clock phase unavailable to CPU memory access

The selected method must be explicit in the schematic and testable. Random wait behavior is not acceptable.

## Character generator

Use a separate socketable ROM/EEPROM for the bitmap font where practical.

The character code from VRAM plus character scan row forms the font-ROM address. Font data then feeds the pixel serializer.

Font contents are project data, not architectural CPU state, and may be regenerated/replaced independently.

## IRQ aggregation

Keyboard and timer IRQ sources feed the architectural IRQ status/mask logic at:

- C000 IRQ status
- C001 IRQ mask

Each source remains visible before aggregation.

The CPU receives one maskable IRQ line. Masking a source must not erase its underlying status unless the canonical peripheral semantics explicitly require it.

## External connectors

Provide clearly labelled connectors for:

- PS/2 keyboard
- video output
- GPIO
- optional timer tick/test input

Add ESD/protection parts where appropriate for user-accessible connectors.

## Debug/observation

Expose at least:

- keyboard clock/data
- keyboard bit counter / byte-ready
- keyboard IRQ
- timer tick
- timer count
- timer IRQ
- GPIO data/direction/input
- video H/V timing
- pixel/character clock
- VRAM address
- character code
- IRQ source lines
- aggregated IRQ

## KiCad partition

Use separate hierarchical sheets for:

1. IRQ status/mask
2. PS/2 keyboard
3. timer
4. GPIO
5. VRAM arbitration
6. video timing
7. character generator/pixel path
8. external connectors/protection

This keeps peripherals teachable and allows individual sheets to be replaced or demonstrated independently.

## Qualification

Before schematic freeze, shared vectors shall cover:

- valid PS/2 frame
- parity/start/stop errors
- keyboard ready/overrun/ack behavior
- keyboard IRQ masking
- timer enable/disable
- timer rollover/event/status
- timer IRQ masking
- GPIO input/output/direction for every bit
- video register read/write
- all 1000 visible character positions
- VRAM boundary addresses
- cursor behavior
- IRQ aggregation and masking

Where practical, these vectors should be derived from the same peripheral specifications used by emulator and simulator tests.
