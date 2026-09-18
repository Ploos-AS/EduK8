# K8 Classic Component Decisions

## Logic family

Default to 74HCT where TTL-compatible thresholds simplify mixed 5 V interfacing. 74HC equivalents may be approved per signal domain after electrical review.

## Packaging

DIP/through-hole is preferred for the educational core. Parts unavailable in practical DIP form may move to small adapter/modules only after documenting the trade-off.

## Memory

- 62256-class SRAM is the baseline main-RAM candidate.
- 28C256-class EEPROM is the baseline firmware-ROM candidate.
- video receives dedicated SRAM unless schematic/timing work proves a simpler shared-memory design is equally understandable and deterministic.

## Microcode storage warning

The control unit now has a 15-bit logical microaddress. Therefore each physical control-store slice requires 32K addresses. Do not accidentally select an 8K-only EEPROM based on the earlier 14-bit/4-bit-step design.

## Procurement rule

Architecture documents name component classes. Exact manufacturer part numbers belong in the purchasing BOM only after availability and electrical qualification.