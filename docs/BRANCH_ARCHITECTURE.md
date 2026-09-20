# K8 Branch Architecture

**Status:** M2.5 frozen

K8 relative branches use the existing 16-bit address-generation datapath rather than a simulator-only instruction shortcut. This keeps K8 Classic, FPGA, simulator, and the reference emulator aligned.

## Architectural behaviour

The branch instructions are `BEQ`, `BNE`, `BCS`, `BCC`, `BMI`, `BPL`, `BVS`, and `BVC`.

The byte following the opcode is a signed two's-complement displacement in the range -128..+127. The displacement is relative to the PC **after** the displacement byte has been fetched.

If the branch is not taken, execution continues at that post-operand PC. If taken:

`PC <- (PC + sign_extend(displacement)) & 0xffff`

16-bit wraparound is architectural.

## Condition decode

Branch truth is decoded from the opcode and the architectural flags before the control-store lookup for the branch decision phase:

| Opcode | Instruction | Taken when |
|---|---|---|
| 88 | BEQ | Z = 1 |
| 89 | BNE | Z = 0 |
| 8A | BCS | C = 1 |
| 8B | BCC | C = 0 |
| 8C | BMI | N = 1 |
| 8D | BPL | N = 0 |
| 8E | BVS | V = 1 |
| 8F | BVC | V = 0 |

The frozen two-bit condition field is encoded as:

- `00`: unconditional/default
- `01`: branch condition false
- `10`: branch condition true
- `11`: reserved

The branch decoder therefore produces only `01` or `10` for the decision phase. Other instructions use `00`.

This encoding deliberately keeps flag selection and polarity outside the 48-bit control word. The opcode already identifies which flag and polarity a branch needs.

## Relative-address datapath

The fetched displacement is held in `TMP`. The branch address unit consumes:

- the current 16-bit PC,
- the signed 8-bit TMP displacement,
- the decoded branch-taken condition.

For a taken branch it performs a 16-bit signed add and loads PC. For a not-taken branch PC is unchanged.

This is a digital address-generation operation, not an ALU-visible arithmetic instruction: it does not modify C, Z, N, or V.

The implementation may reuse the physical adder resources of the AGU, but the architectural operation is distinct from indexed addressing. K8 Classic and FPGA implementations must expose an equivalent `PC + signed TMP` path.

## Control-store contract

Conditional branch rows may specify a `condition` field in `spec/microcode.json`. A row without `condition` remains shared across all four condition addresses. A condition-specific row overrides the shared row at that opcode/microstep/condition address.

This allows operand fetch to remain unconditional while the decision microstep has separate false/true control words.

The physical control store remains 48 bits wide. Branch selection therefore does **not** consume a new control-word bit.

## Observability

The educational simulator must expose:

- branch opcode,
- selected architectural flag,
- required polarity,
- decoded condition value,
- raw displacement byte,
- sign-extended displacement,
- pre-branch PC,
- resulting PC,
- taken/not-taken state.

## Qualification

Qualification must include every branch polarity plus:

- taken and not-taken paths,
- positive displacement,
- negative displacement,
- forward 16-bit wraparound,
- backward 16-bit wraparound,
- emulator/simulator architectural-state comparison.

No branch implementation is qualified by simulator-only behaviour.
