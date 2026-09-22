# M3 — K8 Assembler Qualification

## Status

**PASS / QUALIFIED**

M3 qualifies the K8 assembler against the frozen K8 v1 architecture and the M3 roadmap requirements.

## Qualified scope

- documented K8 assembly syntax
- lexer/parser
- expressions and constants
- symbols, labels and forward references
- `.org`, `.byte`, `.word` and `.equ`
- K8 instruction encoding from the canonical ISA specification
- little-endian 16-bit output
- relative branch encoding and range validation
- addressing-mode selection
- binary generation
- source-line diagnostics
- execution of assembler-generated machine code in the reference emulator

## Evidence

The qualification test suite includes parser, expression, pass-1, encoder, end-to-end binary generation, diagnostic-contract and assembler-to-emulator execution tests.

GitHub Actions run **#408** (head `13d9c01bd4fd6a13be37f38697e50d78167d0e95`) completed successfully and includes the M3 diagnostic contract together with the existing project regression suite.

The assembler-to-reference-emulator cross-test was qualified by GitHub Actions run **#406** (head `572b1733a87486da2aa9bc373bbb458da15c12bb`), which completed successfully.

## Qualification rule

The qualification-document candidate commit was verified by GitHub Actions run **#410**, which completed successfully.

## Result

**M3 — K8 Assembler: PASS / QUALIFIED.**
