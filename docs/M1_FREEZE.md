# M1 Architecture Freeze Review

**Status:** PASS — K8 v1 architecture frozen for M1  
**Date:** 2026-09-19

## Scope

This review closes the EduK8 M1 architecture milestone. The freeze covers the programmer-visible architecture and the contracts required by the emulator, assembler, compiler, FPGA implementation and K8 Classic hardware.

## Frozen K8 v1 contracts

- 8-bit data path and 16-bit address space
- Programmer-visible registers: A, X, Y, PC, SP and F
- C/Z/N/V/I flag semantics; B exists only in stacked flag images
- 64 KiB little-endian address space
- Page-$01 descending hardware stack
- Reset vector at $FFFC/$FFFD and IRQ/BRK vector at $FFFE/$FFFF
- One maskable IRQ and no NMI in K8 v1
- Memory-mapped I/O in $C000-$C0FF
- PS/2 keyboard, 40x25 text/VGA, timer and 8-bit GPIO v1 I/O contracts
- Instruction semantics and addressing modes in `docs/ISA.md`
- Binary opcode allocation in `spec/isa.json`
- Binary-only arithmetic; no decimal mode
- JSR/RTS, BRK/IRQ/RTI and stack semantics
- Initial compiler ABI in `docs/ABI.md`
- Machine-readable I/O map in `spec/io-map.json`
- Architectural conformance vectors as the cross-implementation reference contract

## Review findings

The architecture documents and machine-readable specifications are sufficiently defined to serve as the K8 v1 architectural reference. The reference emulator and conformance work can therefore proceed against a frozen M1 contract.

Later M2/M4 implementation details such as control-store encoding, physical EEPROM organisation, datapath wiring and PCB implementation are not part of the programmer-visible M1 freeze. They may evolve provided they preserve the frozen K8 v1 architectural behaviour.

## Change control after freeze

Any incompatible change to the frozen programmer-visible architecture requires an explicit architecture revision. Implementation fixes that preserve observable K8 v1 behaviour do not reopen M1.

## Result

**M1 — K8 Architecture: PASS / FROZEN.**
