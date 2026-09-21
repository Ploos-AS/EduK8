# K8 Assembly Language Syntax

**Status:** M3 syntax baseline

K8 assembly is deliberately small and explicit. Source is UTF-8 text, while identifiers and instruction/directive names use ASCII characters.

## Lexical rules

- One statement per line.
- Whitespace separates tokens and is otherwise insignificant.
- `; comment` starts a comment through end of line.
- Mnemonics, directives and register suffixes are case-insensitive.
- Labels and symbols are case-sensitive.
- Identifiers start with a letter or underscore and continue with letters, digits or underscores.

## Numbers

- Decimal: `42`
- Hexadecimal: `$2A`
- Binary: `%00101010`
- Character byte: `'A'`

All addresses are 16-bit. Values emitted as bytes must fit 0..255 unless a directive explicitly emits a word.

## Labels and symbols

A label ends in a colon:

    start:
        LDA #$42
        STA $C040
        JMP start

A label may appear before an instruction on the same line.

Constants use `.equ`:

    GPIO_DATA .equ $C040

Forward label references are permitted.

## Instruction operands

The assembler follows the addressing forms frozen in `spec/isa.json`:

    NOP
    LDA #$42
    LDA $42
    LDA $1234
    LDA $42,X
    LDA $1234,X
    LDA $1234,Y
    LDA ($42)
    JMP ($1234)
    BEQ done

`#` selects immediate addressing. Parentheses select indirect addressing. `,X` and `,Y` select indexed addressing.

For an unqualified numeric or symbolic memory operand, the assembler selects zero-page when the resolved address is <= $00FF and a matching zero-page opcode exists; otherwise it selects absolute addressing. Forward references whose size is not yet known are assembled conservatively as absolute. A future explicit size-forcing syntax may be added without changing K8 machine code.

Branches take a label or address expression and encode the signed displacement relative to PC after the branch operand. The target must fit -128..127 bytes.

## Directives

M3 starts with a minimal portable set:

- `.org address` — set assembly address.
- `.byte value[, value ...]` — emit bytes.
- `.word value[, value ...]` — emit little-endian 16-bit words.
- `.equ value` — define a constant on the preceding identifier.

Directive names are case-insensitive.

## Expressions

The initial expression grammar supports:

- symbols
- numeric literals
- parentheses
- unary `+` and `-`
- binary `+` and `-`

More operators may be added later, but source accepted by this baseline must retain its meaning.

## Diagnostics

Assembler errors must include a source line number and a concise reason. At minimum M3 diagnoses unknown mnemonics/directives, duplicate symbols, undefined symbols, invalid addressing modes, out-of-range byte/word values and out-of-range branches.

## Example

    GPIO_DATA .equ $C040

    .org $8000

    start:
        LDA #$AA
        STA GPIO_DATA
        LDX #10
    loop:
        DEX
        BNE loop
        HALT

    .org $FFFC
    .word start
    .word start
