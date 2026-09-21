# M2.5 — K8 Simulator Qualification

Status: **PASS candidate — awaiting CI qualification of this record**

The K8 hardware-level educational simulator is qualified against the frozen K8 v1 architectural contracts by deterministic CI tests.

## Qualified areas

- CPU datapath, buses, flags, ALU, AGU, branch state and active control signals are observable.
- Clock, reset, microstep and instruction stepping are deterministic.
- The frozen control store and 99/99 defined ISA opcode coverage are enforced.
- Shared architectural conformance vectors cross-check programmer-visible state against the reference emulator.
- Memory decode, ROM/RAM/VRAM and MMIO are exercised.
- 40x25 text video, cursor registers, GPIO, switches, LEDs and PS/2 keyboard are represented.
- The 16-bit timer and IRQ controller are represented.
- Keyboard and timer IRQ paths are qualified through CPU interrupt entry and RTI return.
- Integrated peripheral tests cover simultaneous interrupt sources and independent acknowledgement.
- Binary and ROM images can be loaded deterministically.

## Qualification rule

M2.5 becomes **PASS / QUALIFIED** only when the GitHub Actions workflow for this qualification record and the full test suite completes successfully.

This qualification covers the K8 v1 architectural simulator. It does not claim that the future discrete-logic or FPGA physical implementations have been electrically qualified.
