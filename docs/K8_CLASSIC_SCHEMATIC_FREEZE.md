# K8 Classic Schematic Freeze Checklist

## Status

**M4 pre-freeze review**

This checklist is the gate between the signal-level architecture documents and the first complete KiCad Classic schematic.

A checked item means the interface is sufficiently defined to draw and review the schematic. It does not mean physical hardware has been qualified.

## Source-of-truth hierarchy

1. frozen K8 architectural specifications
2. qualified emulator/simulator behavior
3. canonical control-word/microcode specifications
4. K8 Classic signal-level documents
5. KiCad schematic
6. PCB

If a lower layer disagrees with a higher layer, the lower layer must be corrected or the architectural change must go through an explicit re-freeze.

## Datapath

- [x] A/X/Y register and DB contract defined
- [x] ALU and flags contract defined
- [x] PC and branch path defined
- [x] SP and stack path defined
- [x] MAR/MDR contract defined
- [x] AGU contract defined
- [x] internal DB single-driver rule defined
- [x] programmer-visible and internal state identified

## Control

- [x] 48-bit canonical control word defined
- [x] T0-T31 sequencer contract defined
- [x] opcode/control-store addressing defined
- [x] condition addressing defined
- [x] six-ROM physical slicing defined
- [x] control output stabilization requirement defined
- [x] reset/HALT safety requirements defined
- [ ] verify every physical control net has exactly one canonical source
- [ ] verify no required physical action lacks a canonical control path

## Memory and addressing

- [x] 16-bit MAR/address bus defined
- [x] MDR boundary defined
- [x] indexed addressing/AGUC defined
- [x] zero-page wrap defined
- [x] PC-to-MAR defined
- [x] SP-to-MAR defined
- [x] MMIO page decode defined
- [x] vector addresses defined
- [x] VRAM region defined
- [ ] freeze exact RAM/ROM chip capacities and address ranges
- [ ] prove full 65536-address decode table

## Peripherals

- [x] PS/2 hardware blocks defined
- [x] keyboard ready/overrun/IRQ concept defined
- [x] 16-bit timer hardware blocks defined
- [x] GPIO hardware blocks defined
- [x] text-video hardware blocks defined
- [x] IRQ aggregation concept defined
- [x] reconcile keyboard depth/overrun semantics across spec, emulator and simulator
- [x] freeze exact video arbitration implementation (deterministic time-slot arbitration; exact oscillator remains clock/BOM work)
- [ ] verify all MMIO register side effects against canonical tests

## Clock, reset and power

- [x] 5 V logic baseline defined
- [x] per-IC decoupling policy defined
- [x] RUN clock defined
- [x] manual microstep defined
- [x] reset sources and write inhibit defined
- [x] HALT recovery requirement defined
- [ ] select exact oscillator/frequency
- [ ] select exact power regulator/input arrangement
- [ ] select exact power-on reset implementation
- [ ] complete worst-case timing budget from chosen parts

## Physical implementation

- [x] 74HC family baseline
- [x] DIP/socket preference
- [x] buffered LEDs/debug policy
- [x] test-point policy
- [x] no hidden MCU in Classic datapath/control/peripherals
- [ ] assign concrete IC reference designators
- [ ] freeze connector families/pinouts
- [ ] freeze ROM/EEPROM device
- [ ] freeze SRAM device
- [ ] freeze font ROM device
- [ ] produce preliminary package-count/power estimate

## KiCad hierarchy

The first full schematic shall use these hierarchical sheets:

1. power / clock / reset / single-step
2. control / sequencer / microcode ROM
3. A/X/Y registers and DB
4. ALU / flags
5. PC / branch
6. SP / stack
7. MAR / MDR / AGU
8. memory / address decode
9. IRQ / keyboard / timer / GPIO
10. video / VRAM / character generator
11. external connectors / debug

Sheet boundaries may be adjusted only when doing so improves electrical clarity without hiding architectural paths.

## Required automated pre-freeze checks

Before marking the Classic datapath schematic frozen:

- [ ] canonical control-store validator passes
- [ ] six-slice ROM reconstruction passes for all 32768 words
- [ ] all 99 defined opcodes retain microcode coverage
- [ ] full address decoder test passes for all 65536 addresses
- [ ] DB single-driver validation passes for every generated microstep
- [ ] illegal control-combination validation passes
- [ ] branch vectors pass including +127/-128 and page crossings
- [ ] stack vectors pass including wrap and BRK/RTI
- [ ] AGU zero-page and absolute-index vectors pass
- [ ] peripheral MMIO side-effect vectors pass
- [ ] reset sequence matches simulator state transitions

## Review blockers found before freeze

The following items require explicit resolution before the schematic can be called frozen:

1. **PC branch update control:** the logical control word has no generic BRANCH_LOAD_PC signal. The schematic must map branch PC update to the existing qualified sequencer/control behavior without inventing an incompatible architectural control bit.
2. **MAR source selection:** PC_TO_MAR and SP_TO_MAR exist, while MAR_LOAD_LO/HI and AGU operations must be reconciled into one unambiguous physical input-selection network.
3. **Keyboard model — RESOLVED:** canonical depth is one unread byte; a new byte while occupied sets overrun and preserves the unread byte. Emulator and simulator now use this contract.
4. **Video arbitration — RESOLVED:** Classic v1 uses deterministic CPU/video time-slot arbitration over single-port asynchronous SRAM VRAM; see `docs/K8_CLASSIC_VIDEO_ARBITRATION.md`.
5. **Memory population:** architectural regions are known, but actual SRAM/ROM devices and resulting chip-select equations must be selected.
6. **Clock/control timing:** whether ROM outputs require registered control-byte stages depends on the final clock frequency and selected EEPROM access time.

These are engineering blockers, not reasons to reopen the frozen ISA.

## Freeze criterion

Classic schematic status may change to **FROZEN** only when:

- every unchecked blocker above is resolved,
- a complete KiCad schematic exists,
- ERC is clean except documented intentional exceptions,
- generated net/control tables match canonical specifications,
- automated pre-freeze checks pass,
- schematic review records the exact commit used for qualification.

Physical PCB bring-up remains a later milestone and is not implied by schematic freeze.
