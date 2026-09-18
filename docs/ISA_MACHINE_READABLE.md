# K8 Machine-readable ISA

`spec/isa.json` is the machine-readable catalogue of assigned K8 opcodes. It lets the emulator, assembler, compiler and microcode tooling check themselves against the same allocation.

## Microcode coverage

Run `python tools/check_microcode_coverage.py`.

The command exits non-zero until every assigned opcode has executable microcode. During M2 partial coverage is expected and must remain visible rather than being presented as complete.
