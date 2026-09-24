# K8 Classic Memory Population

## Status

**M4 implementation decision — FROZEN for first Classic schematic**

This resolves the Classic memory-population blocker while preserving spec/memory-map.json.

## Selected devices

### Main SRAM

Baseline: **Alliance Memory AS6C62256-55PCN**
- 32K x 8 asynchronous SRAM
- 28-pin PDIP
- 55 ns
- 2.7-5.5 V
- active/current-production device at selection time

One device covers the complete lower 32 KiB physical RAM address space. Decode logic reserves the architectural holes/VRAM rather than exposing the whole chip blindly.

### Program/system EEPROM

Baseline: **Microchip AT28C256-15PU family / 28-pin PDIP AT28C256**
- 32K x 8 parallel EEPROM
- 5 V
- 150 ns read access
- socketable/reprogrammable
- in production at selection time

One device stores the canonical ROM image. Address/decode wiring exposes it only at the frozen architectural ROM windows.

### VRAM

Use a second **AS6C62256-55PCN** as physical video SRAM.

Only $7800-$7BFF is CPU-visible as VRAM. The larger physical capacity is intentionally unused/reserved in Classic v1. This keeps the VRAM device common with main SRAM and supports the frozen CPU/video time-slot arbiter.

### Font ROM

Use a socketed **AT28C256-compatible 32K x 8 parallel EEPROM** for the first schematic.

Only the address bits required by the selected font geometry are used; unused high address bits are strapped to defined levels. The excess capacity permits multiple future font banks without changing the footprint.

## Architectural mapping

- $0000-$77FF: main SRAM
- $7800-$7BFF: dedicated VRAM SRAM
- $7C00-$7EFF: main SRAM
- $7F00-$7FFF: reserved, no RAM select
- $8000-$BFFF: program EEPROM, lower architectural ROM window
- $C000-$C0FF: MMIO, no RAM/ROM select
- $C100-$FEFF: reserved, no memory select
- $FF00-$FFFF: system-ROM alias into the same program EEPROM

The system-ROM alias maps to the EEPROM image region containing the top 256 bytes, including vectors at $FFFC-$FFFF. The exact EEPROM address equation must be documented in the decode table and ROM-image generator.

## Decode requirements

Main SRAM is selected only for the architectural RAM regions, even though its 32K capacity spans $0000-$7FFF electrically.

VRAM has a dedicated select for $7800-$7BFF and participates in the frozen arbiter.

Program EEPROM is read-only in normal CPU operation. Its write/program pins are never driven by CPU MEM_WRITE.

MMIO and reserved regions produce no memory chip select.

## Sockets

Use quality 28-pin DIP sockets for SRAM/EEPROM devices. Silkscreen shall identify:
- MAIN SRAM
- VRAM
- PROGRAM EEPROM
- FONT EEPROM

Pin 1 and device orientation must be obvious.

## Qualification

Before schematic freeze:
- enumerate all 65536 CPU addresses
- prove exactly the expected target or no target
- verify $77FF/$7800, $7BFF/$7C00, $7EFF/$7F00, $7FFF/$8000, $BFFF/$C000, $C0FF/$C100 and $FEFF/$FF00 boundaries
- verify reset/IRQ vectors reach program EEPROM
- verify CPU writes cannot assert EEPROM write
- verify reserved regions do not alias SRAM
- verify VRAM ownership rules
- generate/read back EEPROM image and vectors

## BOM note

The named parts are the qualification baseline, not a permanent single-vendor lock-in. Electrically compatible alternatives may be documented later, but any substitute must be rechecked for voltage, pinout, package and timing.
