# K8 Micro-operations and Trace Model

The K8 emulator exposes two related views of execution:

1. architectural state — what software observes
2. micro-operations — how the educational machine explains the work

A micro-operation is a small data movement or control action such as:

    T0: PC -> MAR
    T1: MEM[MAR] -> MDR
    T2: MDR -> IR; PC++

For an immediate load, execution can then continue as:

    PC -> address bus
    memory -> data bus
    data bus -> A
    update Z,N
    PC++

## Important distinction

The micro-operation model is an educational hardware contract, not merely decorative debugger text.

As the physical control unit is designed, these operations will be refined into real control signals and clock phases. The emulator and PCB documentation should converge on the same terminology.

## Trace levels

K8 tooling should eventually support:

- instruction trace
- micro-operation trace
- bus trace
- control-signal trace

This allows a learner to start with assembly and progressively reveal lower layers without changing the program being executed.

## M2 scope

M2 establishes the representation and detailed examples for representative instructions. Full per-opcode microcode is completed alongside control-unit design so that software does not accidentally invent hardware behaviour that cannot be built simply.


## Control-unit specification

The canonical internal registers, buses, microstep model and logical control signals are documented in `docs/CONTROL_UNIT.md` and `spec/control-signals.json`.
