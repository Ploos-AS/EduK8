# K8 Calling Convention

Status: M1 candidate

The calling convention is designed for the EduK8 compiler while remaining understandable when inspected in assembly.

## Registers
- A: primary 8-bit expression/result register
- X: temporary/index register
- Y: temporary/index register
- PC: program counter
- SP: stack pointer
- F: status flags

## Stack

The hardware stack is page $0100-$01FF and grows downward. A call pushes the return address. RTS restores it.

## Arguments

The initial compiler ABI passes arguments on the stack. For a function with arguments, the caller pushes arguments in right-to-left order and then executes JSR.

## Return value

An 8-bit scalar return value is returned in A. Boolean results use $00 for false and $01 for true.

## Caller/callee responsibilities

The first ABI revision treats A, X and Y as caller-saved. The callee preserves only state explicitly required by its generated prologue/epilogue.

## Local variables

The compiler may reserve stack space for locals. Generated code must balance stack operations on every normal return path.

## Interrupts

Interrupt handlers are not part of the compiler ABI yet. RTI remains a system-level instruction.

## Design goal

The ABI should make compiler-generated code easy to inspect by hand. Optimisation must not make first educational examples difficult to understand.