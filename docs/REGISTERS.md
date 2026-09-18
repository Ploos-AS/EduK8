# K8 Classic Register Block v1

The register block is designed for visibility, single-stepping and straightforward 74HC/HCT implementation.

## Central data bus

DB0-DB7 is the shared 8-bit CPU data bus. Register outputs are tri-stated or isolated through 74HC245-class transceivers. The control unit must never enable two bus drivers simultaneously.

## A, X and Y

Each is an 8-bit register with explicit load and output-enable controls.

Preferred implementation: 74HC574-class octal D register plus 74HC245-class bus isolation where needed. The schematic keeps LOAD and OUT signals individually labelled.

- A_LOAD / A_OUT
- X_LOAD / X_OUT
- Y_LOAD / Y_OUT

A also feeds the ALU A input. X and Y feed the AGU index selection path.

## Instruction Register IR

IR is an 8-bit 74HC574-class register loaded during fetch.

- IR_LOAD
- IR[7:0] feeds the control-ROM opcode address
- IR bits are available on a labelled debug header

IR does not need to drive the general data bus in v1.

## Program Counter PC

PC is 16-bit and split visibly into PCL and PCH.

Requirements:

- PC_LOAD_LO / PC_LOAD_HI
- PC_INC
- PC address output
- independently probeable PCL/PCH

Use counter/register parts in the 74HC161/163 family or an equivalent transparent implementation after timing verification. The final schematic must show how carry propagates from low to high byte.

PC drives the internal address-selection path rather than pretending a 16-bit value is an 8-bit data-bus source.

## Memory Address Register MAR

MAR is 16-bit, split into MARL and MARH, and directly drives AB0-AB15.

- MAR_LOAD_LO
- MAR_LOAD_HI
- MARL/MARH debug headers

During fetch, PC is transferred to MAR through the dedicated address path. This resolves the earlier abstract PC_OUT-to-8-bit-bus ambiguity.

## Stack Pointer SP

SP is 8-bit. The physical stack address is formed as:

    $0100 | SP

Provide:

- SP_LOAD
- SP_INC
- SP_DEC
- SP_OUT when an 8-bit value is required
- dedicated page-$01 address selection when SP supplies an address

This avoids relying on MARH accidentally containing $01.

## Flags register F

Architectural flag latches:

- C carry
- Z zero
- N negative
- V overflow
- I interrupt enable
- B break/software-interrupt state

Flags use explicit latch/set/clear controls. ALU flag updates affect C/Z/N/V only. I and B have separate control paths.

Reserved flag bits read as their architecturally defined value and are not floating hardware state.

## Temporary register TMP

TMP is an internal 8-bit register used by multi-step instructions, address generation and control sequences.

It is intentionally visible in schematics and on debug points even though software cannot address it.

## AGUC

AGUC is a dedicated one-bit address-generation carry latch. It is not the architectural C flag.

- AGUC_LOAD
- AGUC_CLEAR
- labelled LED/test point recommended

## Physical layout

Place registers in a visually coherent bank:

    A   X   Y   IR
    PCL PCH MARL MARH
    SP  F   TMP AGUC

Silkscreen each block with its architectural name rather than only IC reference numbers.

## Debug / front-panel signals

Expose at minimum:

- A[7:0]
- X[7:0]
- Y[7:0]
- IR[7:0]
- PC[15:0]
- MAR[15:0]
- SP[7:0]
- C/Z/N/V/I/B
- TMP[7:0]
- AGUC

## FPGA correspondence

The HDL register file must preserve these named registers and address-path boundaries for simulation/debug, even if synthesis could optimise them away.

## Teaching exercises

1. Load A manually and observe DB0-DB7.
2. Transfer A to X through the bus.
3. Increment PC across $00FF->$0100 and observe byte carry.
4. Form stack addresses $01FF and $01FE from SP.
5. Demonstrate that AGUC and C are independent.
6. Trace PC -> MAR -> memory -> IR during instruction fetch.