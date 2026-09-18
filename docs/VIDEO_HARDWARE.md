# K8 Classic Text Video Hardware v1

K8 Classic video is intentionally simple enough to understand with a schematic and logic analyser. The v1 display is a monochrome 40x25 character generator with 8x8 glyphs.

## Logical display

- 40 columns
- 25 rows
- 8x8 pixel glyphs
- 320x200 active character pixels
- 256 character codes
- 1 KiB CPU-visible VRAM at $7800-$7BFF
- first 1000 bytes displayed
- remaining 24 bytes reserved

## Pipeline

    timing counters
         |
         +--> character column/row
         |        |
         |        +--> VRAM address --> character code
         |                              |
         +--> glyph row ----------------+--> character ROM
                                              |
                                           8 pixels
                                              |
                                        shift register
                                              |
                                           VIDEO

## Timing generator

Use ordinary counters and decode logic to generate horizontal and vertical timing. The first hardware target uses a VGA-compatible electrical output with conservative standard timing.

The character generator does not need to expose a 320x200 VGA mode to software; software only sees the 40x25 text abstraction.

Exact pixel clock and porch/sync counts are frozen after timing simulation and monitor-compatibility qualification.

## Character clock

Eight pixel clocks form one character cell. Horizontal counters therefore expose both pixel-within-glyph and character-column state.

Vertical timing exposes scanline-within-glyph and character-row state.

## VRAM address generation

For visible cells:

    address = row * 40 + column

and the CPU-visible base is $7800.

The video address generator uses counters/adders or a simple deterministic mapping that remains visible in the schematic. No MCU computes framebuffer addresses.

## CPU/video VRAM sharing

Video requires predictable reads while the CPU can write characters.

Preferred v1 strategy is deterministic time-slot arbitration between CPU and display fetches. The exact SRAM arrangement is selected during schematic timing work.

Requirements:

- CPU writes must not corrupt display timing
- video fetches must not stall unpredictably
- arbitration must be observable
- emulator and FPGA retain the same software-visible VRAM semantics

## Character ROM

A ROM/EEPROM contains 256 glyphs x 8 rows x 8 bits = 2048 bytes.

Character-ROM address:

    character_code[7:0] | glyph_row[2:0]

The output byte is loaded into a parallel-to-serial shift register for eight pixels.

The font is an EduK8 project asset and must have redistribution-friendly licensing.

## Output

v1 is monochrome. A simple VGA output stage generates:

- HSYNC
- VSYNC
- pixel/video level
- ground

Use resistor networks/buffering appropriate to VGA electrical levels; do not drive the connector directly from unqualified logic outputs.

## Video registers

The existing software interface remains:

    $C020 VIDEO_CONTROL
    $C021 VIDEO_STATUS
    $C022 CURSOR_X
    $C023 CURSOR_Y
    $C024 CURSOR_CONTROL
    $C025 BORDER

Display enable is implemented in hardware. VBLANK comes from the timing generator.

Cursor can be implemented by comparing current row/column with cursor registers and modifying/inverting the glyph output. Blink derives from a divided frame counter.

BORDER remains architecturally present but monochrome v1 may define its visible effect conservatively.

## Signals to expose

- PIXEL_CLK
- HSYNC
- VSYNC
- H character count
- V character count
- glyph row
- VRAM address
- VRAM character byte
- glyph ROM byte
- shift-register output
- VBLANK
- CPU/VIDEO arbitration state

## FPGA correspondence

The FPGA implementation uses the same 40x25 character model, glyph ROM contents, VRAM layout and register interface. Shared framebuffer/font test vectors should compare FPGA output with the emulator.

## Qualification

1. render all 1000 visible character cells
2. verify first/last visible VRAM addresses
3. verify the 24 reserved VRAM bytes are not displayed
4. verify glyph rows and bit order
5. verify HSYNC/VSYNC timing in simulation
6. verify CPU writes during active display
7. verify VBLANK register behaviour
8. verify cursor enable/blink
9. display a common K8 test screen on emulator, FPGA and Classic hardware

## Teaching exercises

1. Write `A` to $7800 and trace its character code into the glyph ROM.
2. Probe the eight glyph bits as they leave the shift register.
3. Change one byte in the font ROM and observe the resulting glyph.
4. Count eight pixel clocks per character.
5. Follow row/column counters to the VRAM address.
6. Observe CPU/video arbitration while software writes text.