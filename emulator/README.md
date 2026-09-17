# K8 Reference Emulator

The K8 emulator is the executable reference implementation of the K8 architecture.

## Goals

- deterministic execution
- exact 8-bit arithmetic
- 16-bit address space
- observable registers and flags
- instruction-level stepping
- memory inspection
- trace generation
- conformance-test execution

M2 starts with a small dependency-free reference implementation. It should remain readable and deterministic; performance is not the goal.

Architectural tests live under tests/conformance/.