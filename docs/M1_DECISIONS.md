# M1 Architecture Decisions

## Decision 1 — 8-bit data path

K8 uses an 8-bit data path. This is the central educational constraint.

## Decision 2 — 16-bit address space

K8 uses a 16-bit address bus and a 64 KiB architectural address space.

## Decision 3 — Small programmer-visible state

The initial programmer-visible state is A, X, Y, PC, SP and F.

## Decision 4 — Memory-mapped I/O

I/O is memory mapped. This avoids introducing a second I/O instruction mechanism and makes hardware/software interaction directly visible.

## Decision 5 — Reference emulator

The emulator is the executable reference implementation and must be tested from architectural conformance vectors.

## Decision 6 — Hardware-first observability

The physical K8 must expose useful buses, control signals and test points. Educational observability takes priority over maximum component minimisation.

## Decision 7 — No opcode freeze yet

Instruction groups and semantics are defined, but exact opcode allocation is postponed until instruction encoding has been evaluated against compiler and hardware control requirements.

## Decision 8 — Through-hole target

The first physical K8 revision targets through-hole components and a two-layer PCB wherever practical.

## Decision 9 — Compiler is a design constraint

The architecture must support a small educational C-like language. Compiler requirements therefore influence calling convention, stack behaviour and addressing modes.

## Decision 10 — Emulator before PCB freeze

The emulator and conformance tests should exist before the final PCB architecture is frozen.
