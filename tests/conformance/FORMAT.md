# K8 Conformance Format v1

The JSON vectors in this directory are deliberately implementation-neutral.

## Fields

- setup: initial CPU registers and memory bytes
- action.reset: perform architectural reset
- action.steps: number of instructions to execute
- expect: architectural state after execution

Numbers are hexadecimal strings so the files remain easy to compare with schematics, assembly listings and logic-analyzer captures.

Flag expectations may be expressed individually as c, z, n, v, i and b.

## Purpose

The same vector files are intended to validate:

1. the Python reference emulator
2. future emulator implementations
3. HDL/FPGA implementations
4. hardware test harnesses connected to the physical K8

A backend may translate the vector into its own control mechanism, but it must not reinterpret the architectural expectation.
