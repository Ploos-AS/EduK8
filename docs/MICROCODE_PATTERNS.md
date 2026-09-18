# K8 Microcode Patterns

Microcode patterns describe recurring hardware actions without hiding the generated control words.

They are authoring conveniences only. Expansion must always produce explicit per-step control signals that can be inspected in generated manifests.

## Operand fetch patterns

### immediate8

- T3: PC -> MAR
- T4: MEM[MAR] -> MDR
- T5: consume MDR; PC++

### zero_page_address

- T3: PC -> MAR
- T4: MEM[MAR] -> MDR; PC++
- T5: MDR -> MAR.low, MAR.high <- 0

### absolute_address

- T3/T4: fetch low byte
- T5: preserve low byte in TMP
- T6/T7: fetch high byte
- T8: form MAR from TMP:MDR

Indexed and indirect patterns remain pending until the datapath has explicit hardware support for 16-bit effective-address addition. We do not hide that operation behind a software-only abstraction.

## Design rule

A pattern may reduce source repetition, but it may never introduce an operation that lacks a corresponding observable hardware path.
