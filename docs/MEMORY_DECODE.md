# K8 Classic Memory and Address Decode v1

This document defines the first physical memory organisation and decode strategy for K8 Classic.

## Goals

- simple 5 V parts
- DIP/through-hole where practical
- easy probing and replacement
- deterministic decode
- identical programmer-visible map on Classic, FPGA and emulator

## v1 memory map

    $0000-$00FF  Zero page / fast workspace
    $0100-$01FF  Hardware stack page
    $0200-$77FF  General RAM
    $7800-$7BFF  Text VRAM (1 KiB)
    $7C00-$7EFF  General RAM
    $7F00-$7FFF  Reserved
    $8000-$BFFF  Main ROM (16 KiB)
    $C000-$C0FF  Memory-mapped I/O
    $C100-$FEFF  Reserved
    $FF00-$FFFF  System ROM / vectors

The $FF00-$FFFF window is a high alias/window of system ROM so the reset and IRQ vectors remain ROM-backed without requiring a separate tiny ROM device.

## RAM

Use a standard asynchronous SRAM large enough that one physical device can cover the RAM-backed regions. A 32 KiB 5 V SRAM such as a 62256-class device is a good candidate.

Address decoding prevents the SRAM from responding in VRAM/reserved areas even if the physical chip contains those addresses.

## ROM

A parallel EEPROM/flash device provides firmware. A 28C256-class 32 KiB EEPROM is a convenient educational candidate even though v1 exposes only selected windows.

Main ROM maps at $8000-$BFFF. The top system/vector window $FF00-$FFFF aliases a selected ROM page containing firmware vectors.

The exact alias wiring/bank selection is frozen at schematic stage and must preserve the existing software-visible vector addresses.

## Video RAM

VRAM occupies $7800-$7BFF. The first 1000 bytes are visible characters for the 40x25 text display; the remaining 24 bytes are reserved.

The video subsystem requires access independent of normal CPU reads. v1 should use either dual-port-friendly arbitration or deterministic time-sliced access built from ordinary logic. A hidden framebuffer MCU is not permitted.

## I/O

$C000-$C0FF selects the peripheral register page. Lower address bits select the individual register.

Current blocks:

    $C000-$C00F  system/IRQ
    $C010-$C01F  keyboard
    $C020-$C02F  video
    $C030-$C03F  timer
    $C040-$C04F  GPIO
    $C050-$C0FF  reserved

Reserved I/O reads return $00 and writes have no effect.

## Decode hierarchy

Use visible combinational decode rather than a programmable MCU/CPLD for K8 Classic.

A recommended hierarchy is:

1. high address bits classify RAM / ROM / I/O / high-system region
2. secondary decode isolates VRAM and reserved holes
3. I/O subdecode selects peripheral blocks

74HC138/74HC154-class decoders plus simple gates are preferred.

Every major select is exposed:

- /RAM_CS
- /VRAM_CS
- /ROM_CS
- /IO_CS
- /SYSROM_CS
- peripheral chip-selects

## Read/write control

CPU R/W control is combined with chip select to create safe memory /OE and /WE signals.

Only the selected readable device may drive DB0-DB7. Reserved reads must be actively defined where required rather than relying on a floating bus.

## Address bus

AB0-AB15 comes from MAR during ordinary memory cycles. The memory system does not infer hidden addresses from PC or SP.

## Programmer/debug support

Provide test points or headers for:

- AB0-AB15
- DB0-DB7
- /RAM_CS
- /VRAM_CS
- /ROM_CS
- /IO_CS
- /SYSROM_CS
- /MEM_RD
- /MEM_WR

## Machine-readable map

`spec/memory-map.json` is the canonical structured description for tooling. Emulator, assembler/link tooling, FPGA address decode and documentation should converge on it.

## Qualification

Shared tests must verify boundary addresses around every region, especially:

- $77FF/$7800
- $7BFF/$7C00
- $7EFF/$7F00
- $7FFF/$8000
- $BFFF/$C000
- $C0FF/$C100
- $FEFF/$FF00
- reset vector $FFFC-$FFFD
- IRQ vector $FFFE-$FFFF

## Teaching exercise

Single-step a write to $0200, a character write to $7800 and an I/O read at $C011. Probe the address bus and observe a different chip-select for each transaction.