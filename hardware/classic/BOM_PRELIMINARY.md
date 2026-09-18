# K8 Classic Preliminary BOM v0.1

This is an engineering BOM for schematic capture, not yet a purchasing BOM. Exact manufacturer/order codes are intentionally deferred until electrical and availability qualification.

## CPU/register datapath

| Function | Candidate | Qty | Notes |
|---|---:|---:|---|
| A/X/Y/IR/TMP and byte latches | 74HCT574 | 5-8 | octal D registers; final count after schematic |
| Bus transceivers | 74HCT245 | 4-8 | isolate register/memory/peripheral paths |
| PC/sequencer counters | 74HCT163 | 3-5 | cascaded counters |
| Stack/count support | 74HCT193/163 | 1-2 | final choice after up/down timing review |
| Arithmetic adders | 74HCT283 | 2 | 8-bit adder |
| Multiplexers | 74HCT157 | 4-8 | ALU/address selection |
| Decoders | 74HCT138 | 3-6 | memory/I/O/control decode |
| Logic gates | 74HCT00/02/04/08/32/86 | TBD | explicit glue/ALU/flags |

## Control store

| Function | Candidate | Qty | Notes |
|---|---:|---:|---|
| Microcode ROM | parallel EEPROM/flash | 6 | conceptual 48-bit word; exact device after address-depth review |
| Firmware ROM | 28C256-class EEPROM | 1 | socketed/programmer-friendly |

IMPORTANT: the new 15-bit logical microaddress means the selected microcode storage must provide at least 32768 addresses per control-word slice. Device choice must be verified before schematic freeze.

## Memory

| Function | Candidate | Qty | Notes |
|---|---:|---:|---|
| Main SRAM | 62256-class 32 KiB SRAM | 1 | CPU RAM regions |
| Video SRAM | dedicated SRAM, size TBD | 1 | allows clean video arbitration design |
| Character ROM | EEPROM/ROM >=2 KiB | 1 | 256 x 8x8 glyphs |

## Video

| Function | Candidate | Qty | Notes |
|---|---:|---:|---|
| Timing counters | 74HCT163 | 3-5 | exact VGA timing chain TBD |
| Shift register | 74HCT166/165-class | 1 | parallel glyph byte to serial pixels |
| Comparators | 74HCT688-class | 1-3 | cursor/timing decode where useful |
| VGA output | resistor network + buffer | 1 set | electrically qualify levels |
| VGA connector | DE-15 | 1 | through-hole preferred |

## Keyboard

| Function | Candidate | Qty | Notes |
|---|---:|---:|---|
| PS/2 shift register | 74HCT164/165-class | 1-2 | exact edge/data topology TBD |
| Frame counter | 74HCT163 | 1 | 11-bit frame position |
| Byte latch | 74HCT574 | 1 | one-byte receive latch |
| PS/2 connector | Mini-DIN-6 | 1 | through-hole |

## Timer/GPIO/IRQ

| Function | Candidate | Qty | Notes |
|---|---:|---:|---|
| Timer counters | 74HCT193/163 | 2 | 16-bit timer |
| GPIO output latch | 74HCT574 | 1 | 8 outputs |
| GPIO transceiver | 74HCT245 | 1 | external isolation |
| IRQ mask/status | 74HCT574 + gates | 1+ | exact latch arrangement TBD |

## Clock/reset/front panel

| Function | Candidate | Qty | Notes |
|---|---:|---:|---|
| Schmitt inverter | 74HCT14 | 1 | debounce/conditioning |
| Oscillator | socketed 5 V oscillator | 1 | RUN clock |
| Slow clock divider | 74HCT4040-class | 1 | candidate; final division after clock selection |
| STEP button | momentary switch | 1 | debounced |
| RESET button | momentary switch | 1 | debounced |
| Mode selector | 3-position switch | 1 | STEP/SLOW/RUN |
| LEDs + resistors | TBD | ~10-20 | buffered status only |

## Board infrastructure

- DIP sockets for socket-worthy ICs
- 100 nF decoupling capacitor per logic IC
- bulk decoupling per board zone
- 5 V regulated input/protection
- power LED
- labelled test headers for DB, AB, control and clocks
- expansion connector
- GPIO connector with grounds
- programming headers/sockets where appropriate

## Preliminary scale

The first estimate is roughly 40-70 logic/memory IC packages depending on final ALU, control-store width, video implementation and how aggressively common glue logic is shared.

This is acceptable for K8 Classic: educational visibility is a stronger requirement than minimum chip count.

## Cost strategy

Before ordering:

1. freeze schematics
2. run electrical/timing review
3. generate exact quantities from KiCad
4. check currently stocked 5 V-compatible parts from multiple distributors
5. substitute only with documented electrically compatible parts
6. produce a purchasing BOM with manufacturer part numbers and current prices.

Do not buy from this preliminary BOM.