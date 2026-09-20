# K8 Address Generation Unit (AGU)

**Status:** M2.5 implementation freeze

The AGU is an internal K8 implementation detail. It must preserve the programmer-visible addressing modes frozen in M1 while keeping K8 Classic understandable and practical to wire.

## Purpose

Indexed addressing forms an effective address from a 16-bit base address in MAR plus one 8-bit index register. The AGU performs this as two observable byte operations:

1. low byte: `MAR.lo + index` → `MAR.lo`, carry → AGUC
2. high byte: `MAR.hi + AGUC` → `MAR.hi`

AGUC is a one-bit internal carry latch and is not programmer-visible.

## Index selection

The index source is selected by the decoded opcode/addressing mode, not by additional one-hot control-store bits. The selector is a small encoded datapath control derived from the instruction decoder:

| Select | Source |
|---:|---|
| 0 | none / zero |
| 1 | X |
| 2 | Y |
| 3 | reserved |

This keeps the 48-bit control word stable and avoids reviving the obsolete `IDX_X` and `IDX_Y` control bits.

The selector is valid only during AGU phases. For non-indexed instructions it must select zero. A reserved selector value is invalid and must be rejected by simulator/HDL validation.

## Control signals

- `AGU_ADD_LO`: add the selected index to MAR low byte.
- `AGUC_LOAD`: latch the low-byte carry into AGUC.
- `AGU_ADD_HI`: add AGUC to MAR high byte.
- `AGUC_CLEAR`: explicitly clear AGUC.

A normal indexed-address sequence uses `AGU_ADD_LO + AGUC_LOAD`, followed by `AGU_ADD_HI`. The implementation must ensure stale AGUC state cannot leak into a later address calculation.

## Architectural contract

The selector is an internal implementation signal, not part of the 48-bit microinstruction and not visible in the ISA. Opcode/addressing-mode decode must deterministically select X or Y according to `spec/isa.json`.

The emulator remains the programmer-visible oracle. Simulator, FPGA and K8 Classic implementations must produce the same effective 16-bit address, including page crossing from the low-byte carry.

## Observability

For educational/debugging use the simulator and hardware should expose:

- selected index source
- selected index value
- AGU low-byte inputs/result
- AGUC
- effective MAR value

This freeze does not change the M1 ISA.
