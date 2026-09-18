# K8 Classic PCB Block Plan v1

The first PCB is partitioned into visible functional areas rather than minimising board area.

## Board zones

1. CLOCK / RESET
2. CONTROL
3. REGISTERS
4. ALU
5. AGU
6. CPU BUS
7. MEMORY / DECODE
8. I/O

## Assembly strategy

- DIP ICs on sockets where useful
- through-hole passive components
- screw/header connectors for expansion and test equipment
- clearly marked orientation/pin-1 indicators
- no unnecessary tiny-pitch parts on the core CPU
- decoupling capacitor footprint for every logic IC

## Test access

Provide labelled test headers for:

- DB[0:7]
- AB[0:15]
- CLK
- RESET
- IR[0:7]
- microstep
- AGUC
- ALU carry
- IRQ

The headers must be usable with inexpensive logic analysers and jumper wires.

## Cost discipline

PCB cost should be kept reasonable through board size and routing efficiency, but component count is not aggressively reduced if doing so makes the machine harder to learn or repair.

## Future expansion

Leave documented expansion headers for:

- FPGA bridge/reference board
- additional I/O
- educational front panel
- logic analyser connections
- optional serial/Ethernet peripherals

No expansion may change the normative K8 ISA without an explicit architecture revision.
