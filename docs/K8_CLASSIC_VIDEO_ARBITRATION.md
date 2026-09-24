# K8 Classic Video and VRAM Arbitration

## Status

**M4 implementation decision — FROZEN for first Classic schematic**

This document resolves the Classic video-arbitration pre-freeze blocker.

## Decision

The first K8 Classic implementation uses **deterministic time-slot arbitration with single-port asynchronous SRAM VRAM**.

A CPU-visible VRAM access and a video fetch never drive the SRAM at the same time. Video and CPU receive fixed non-overlapping memory slots derived from the video timing clock.

This avoids dual-port SRAM dependency while keeping the arbitration visible and teachable.

## Architectural contract

CPU-visible VRAM remains at $7800-$7BFF. The visible 40x25 text area occupies 1000 bytes.

Arbitration is purely physical. It does not change:
- the K8 memory map
- instruction timing semantics exposed by the architecture
- character values stored in VRAM
- video control-register behavior

## Clock domains

Video timing uses its own stable pixel/timing clock.

CPU_CLK is not used as the video pixel clock.

The arbiter derives a repeatable memory-slot phase from the video timing domain:
- VIDEO_SLOT: SRAM address/data path belongs to display fetch
- CPU_SLOT: SRAM address/data path may service a pending CPU VRAM access

The exact pixel divider and oscillator frequency are finalized with the VGA timing sheet/BOM, but the ownership protocol is frozen here.

## CPU access rule

A CPU access to $7800-$7BFF is decoded as VRAM.

If the request arrives outside CPU_SLOT, the VRAM interface holds the request until the next CPU_SLOT. The CPU-side memory cycle must therefore expose a deterministic READY/WAIT-style completion condition inside the Classic implementation.

The wait is a hardware implementation detail and must not allow the CPU to sample MDR or complete a write before VRAM confirms the slot.

Normal RAM, ROM and MMIO accesses are unaffected.

## Video fetch rule

During VIDEO_SLOT:
1. video address generator owns VRAM address pins,
2. VRAM is read-only from the display side,
3. fetched character code is captured into a video latch,
4. ownership returns according to the fixed slot schedule.

Font ROM and pixel serialization operate from the captured character code, so VRAM does not need to remain connected for the whole character cell.

## Address mux

VRAM address input is selected between:
- CPU MAR address
- video character-cell address

Use explicit HC multiplexers/buffers. Ownership signal and selected address source must be probeable.

## Data path

CPU write data reaches VRAM only during CPU_SLOT and a qualified MEM_WRITE.

CPU read data is captured into MDR only after a qualified CPU_SLOT read.

Video read data is captured into a separate character latch. It never drives internal DB.

## Write safety

VRAM_WE may assert only when all are true:
- VRAM_CS
- CPU_SLOT
- CPU memory ownership
- MEM_WRITE
- reset not asserted

VIDEO_SLOT can never write VRAM.

## Determinism

The arbiter is not first-come/first-served and contains no asynchronous contention resolver.

For a given video phase, a CPU VRAM request has a bounded, deterministic wait until the next CPU_SLOT.

This behavior is suitable for emulator/simulator modeling and hardware qualification.

## Why not dual-port SRAM

Dual-port SRAM remains a possible future implementation, but it is not the Classic baseline because it is less maker-friendly, often less available in DIP/socketable form, and hides the educational arbitration problem.

## Why not unsynchronised stealing

Allowing video to seize SRAM based on incidental propagation delays is forbidden. Ownership changes only on defined timing boundaries.

## Observability

Expose:
- VIDEO_SLOT
- CPU_SLOT
- VRAM_OWNER
- VRAM_WAIT
- VRAM_CS
- VRAM_OE
- VRAM_WE
- selected VRAM address
- video character address
- captured character byte
- CPU VRAM request

## Qualification

Before schematic freeze, verify:
- all 1000 visible cells fetch correctly
- CPU read of every VRAM byte
- CPU write of every VRAM byte
- simultaneous CPU request/video fetch
- CPU request at every arbiter phase
- bounded wait
- no video-side writes
- no CPU MDR capture before completion
- no address/data contention
- reset inhibits VRAM writes
- repeated CPU writes while video runs
- deterministic results across at least one complete video frame

## Result

The video-arbitration blocker is resolved: K8 Classic v1 uses deterministic time-slot arbitration over single-port asynchronous SRAM VRAM.
