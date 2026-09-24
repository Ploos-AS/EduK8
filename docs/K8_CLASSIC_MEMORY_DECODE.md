# K8 Classic Memory and MMIO Decode

## Status

**M4 schematic-definition candidate**

This document defines the physical memory-bus and decode contract for K8 Classic. The frozen architectural memory map remains authoritative.

## Address space

K8 exposes a 16-bit address bus and therefore 64 KiB of architectural address space.

The dedicated MMIO window is:

- C000-C0FF: memory-mapped I/O

All decode must be combinationally unambiguous: at most one writable target may be selected for an address cycle.

## Memory implementation strategy

Classic should use ordinary 5 V-compatible parallel SRAM and EEPROM/flash-style ROM devices where practical.

The first hardware revision should favor simple decode and socketable devices over maximum density. Exact manufacturer part numbers belong in the BOM; the schematic should document capacity and pin-function requirements so equivalent devices remain possible.

Requirements:

- SRAM: asynchronous parallel, 8-bit data, 5 V-compatible
- ROM: parallel, 8-bit data, electrically programmable development workflow
- socketable DIP preferred
- memory outputs must not directly drive internal DB; reads pass through the MDR path
- writes originate from the qualified memory-data path

## Decode hierarchy

Use a two-level decode:

1. coarse region decode from upper address bits
2. local decode for MMIO registers or memory chip enables

74HC138/74HC139-class decoders are preferred building blocks.

MMIO has priority over any larger physical RAM/ROM device that would otherwise respond to C000-C0FF.

## MMIO page

Decode C000-C0FF from A15..A8 = C0.

Within the page, A7..A0 select registers.

Frozen allocations include:

- C000 IRQ status
- C001 IRQ mask
- C010 keyboard data
- C011 keyboard status
- C012 keyboard control
- C013 keyboard raw
- C020-C025 video/cursor control
- C030 timer low
- C031 timer high
- C032 timer control
- C033 timer status
- C040 GPIO data
- C041 GPIO direction
- C042 GPIO input

Unassigned addresses in the page are reserved for future K8 peripherals and must not alias existing registers.

## Text video memory

The frozen text display uses VRAM at 7800-7BFF, with the visible 40x25 area occupying 1000 bytes.

The physical video design may use dual-port behavior, arbitration or time-multiplexed access, but CPU-visible semantics must remain identical to the simulator.

VRAM decode must not collide with MMIO or general RAM.

## Vector region

Reset and interrupt vectors are architectural locations:

- FFFC/FFFD reset vector
- FFFE/FFFF IRQ/BRK vector

The selected ROM mapping must guarantee that these addresses are readable immediately after reset.

## Read cycle

A read cycle shall:

1. present MAR on A0..A15
2. assert exactly one target chip/select
3. assert MEM_READ
4. allow target data to settle
5. capture the byte into MDR
6. deassert read/select before the next conflicting cycle

Exact phase timing is finalized by the clock sheet.

## Write cycle

A write cycle shall:

1. present MAR on A0..A15
2. present stable write data
3. assert exactly one writable target
4. assert MEM_WRITE for a qualified interval
5. remove write enable before address/data change

Reset and HALT transitions must never create spurious writes.

## Bus buffering

Use 74HC245/74HC244/74HC541-class buffering where needed for fan-out, isolation or direction control.

External memory data is separated from internal DB by MDR. This boundary is deliberate and should remain visible in the schematic.

## Decode safety

The design and validation shall ensure:

- RAM and ROM are never simultaneously enabled onto the read-data path
- MMIO overrides overlapping broad memory decode
- MEM_READ and MEM_WRITE are not active together
- write enable is never asserted for ROM
- reserved MMIO does not alias implemented peripherals
- reset inhibits writes until control state is valid

## Debug/observation

Expose:

- A0..A15
- memory data D0..D7
- RAM_CS
- ROM_CS
- MMIO_CS
- VRAM_CS
- MEM_READ
- MEM_WRITE
- local peripheral selects
- decode enable/reset inhibit

A logic-analyzer-friendly header grouping address, data and key strobes is strongly recommended.

## KiCad partition

1. address-bus input/buffering
2. coarse address decode
3. SRAM socket/interface
4. ROM socket/interface
5. VRAM decode/interface
6. MMIO-page decode
7. peripheral register decode
8. memory-data bus/MDR interface
9. write-protect/reset safety
10. debug header

## Qualification

Before schematic freeze, automated decode vectors shall cover all 65536 addresses and prove mutually exclusive target selection.

Explicit tests shall include:

- first/last byte of each memory region
- 77FF/7800 and 7BFF/7C00 video boundaries
- BFFF/C000 and C0FF/C100 MMIO boundaries
- FFFC-FFFF vectors
- every implemented MMIO register
- reserved MMIO addresses
- read/write exclusivity
- reset write inhibition

The expected decode map comes from the frozen K8 specifications and qualified simulator.
