# M2 Reference Emulator Qualification

**Target:** K8 v1 reference emulator  
**Architecture baseline:** M1 frozen  
**Status:** PASS — qualified

## Qualification scope

M2 is qualified by the repository's automated emulator workflow. The suite covers:

- CPU architectural state and reset behaviour
- core K8 v1 instruction execution
- memory and memory-mapped I/O
- keyboard/video integration paths
- deterministic instruction stepping
- instruction and micro-operation tracing
- arithmetic, flags, stack, calls and interrupts
- assembler/emulator interoperability already exercised by the suite
- architectural conformance vectors
- control-word and generated control-ROM validation
- microcode patterns and coverage
- save/load-state round trips, peripheral state and format validation

## Required command

The GitHub Actions workflow `.github/workflows/emulator.yml` is the authoritative M2 automated qualification entry point. It generates the control ROM and runs the complete selected pytest suite.

## Pass criteria

M2 PASS requires the workflow to complete successfully from a clean checkout with no failing selected tests.

## Freeze rule

After PASS, the emulator becomes the executable reference for the frozen K8 v1 programmer-visible architecture. Later simulator, FPGA and Classic hardware implementations must be cross-checked against the same architectural contracts and conformance vectors.

Implementation improvements remain allowed when they do not change frozen K8 v1 observable behaviour.

## Result

**PASS** — GitHub Actions workflow `K8 emulator` run **#195** (`35474798122`) completed successfully on commit `8c8ac97cefbd1335b16bf9e44ffaf1298b5eae60` on 2026-09-19 UTC. Both control-ROM generation and the complete selected emulator test suite passed.
