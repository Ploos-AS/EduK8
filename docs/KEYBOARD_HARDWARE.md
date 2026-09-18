# K8 Classic PS/2 Keyboard Hardware v1

K8 Classic receives keyboard input with ordinary logic. No MCU translates or buffers the keyboard protocol.

## External interface

PS/2 provides CLOCK and DATA open-collector signals. The board provides appropriate pull-ups, input protection and Schmitt-conditioned logic-level signals before they enter the receiver.

Expose raw conditioned PS2_CLK and PS2_DATA test points.

## Receive frame

A PS/2 device sends an 11-bit frame:

    start | D0 D1 D2 D3 D4 D5 D6 D7 | parity | stop

Data is sampled on the documented PS/2 clock edge. A small counter tracks frame position and a shift register captures the eight data bits.

## Receiver blocks

    PS2 CLK/DATA
          |
     input conditioning
          |
     bit counter + shift register
          |
     parity/start/stop validation
          |
      byte latch
          |
     DATA_READY / OVERRUN
          |
       K8 I/O bus

Likely building blocks are 74HC164/165/595-class shift/register logic, 74HC161/163-class counting and ordinary gates. Exact parts are frozen after schematic/timing review.

## Validation

A received byte is accepted only after valid start, odd parity and stop state. Invalid frames are discarded and may set an internal/debug error indication.

## One-byte architectural latch

v1 exposes a simple one-byte receive latch rather than hiding a deep FIFO.

When a valid byte arrives:

- if DATA_READY=0, latch byte and set DATA_READY
- if DATA_READY=1, preserve the unread byte and set OVERRUN

This behaviour is deterministic and easy to explain.

## CPU registers

    $C010 KEY_DATA
    $C011 KEY_STATUS
    $C012 KEY_CONTROL
    $C013 KEY_RAW

KEY_STATUS:

- bit 0 DATA_READY
- bit 1 OVERRUN

KEY_CONTROL:

- bit 0 IRQ_ENABLE

KEY_RAW:

- bit 0 conditioned PS2_DATA
- bit 1 conditioned PS2_CLK
- other bits read zero

Reading KEY_DATA consumes the latched byte and clears DATA_READY. OVERRUN clearing semantics must be explicit in the final I/O specification; v1 hardware should provide a software-visible deterministic clear mechanism rather than power-cycle-only recovery.

## IRQ

When IRQ_ENABLE and DATA_READY are both set, the keyboard block asserts its interrupt request into the shared K8 IRQ logic.

Polling remains fully supported.

## Scan codes versus characters

The hardware receiver exposes PS/2 scan-code bytes. It does not secretly translate them to ASCII.

Translation belongs in K8 firmware/software. This lets learners observe make/break prefixes and extended scan-code sequences.

The current emulator keyboard injection API may use convenient byte input for tests, but hardware-accurate PS/2 tests must additionally model scan-code framing.

## Host-to-keyboard communication

v1 focuses on receive-only operation sufficient for ordinary keyboard input. Bidirectional host commands such as LED control can be added later without changing KEY_DATA semantics.

## Signals to expose

- PS2_CLK raw/conditioned
- PS2_DATA raw/conditioned
- frame bit count
- shift-register contents
- byte latch
- DATA_READY
- OVERRUN
- parity result
- keyboard IRQ request

## FPGA correspondence

The FPGA receiver implements the same frame validation, one-byte latch, status bits and register semantics. Simulation vectors should contain complete PS/2 frames, including invalid parity and overrun cases.

## Qualification

1. receive known make code
2. receive break-prefix sequence
3. reject bad start bit
4. reject bad parity
5. reject bad stop bit
6. verify DATA_READY set/consume
7. verify OVERRUN
8. verify polling
9. verify IRQ enable/disable
10. compare Classic, FPGA and hardware-accurate emulator vectors

## Teaching exercises

1. Press a key and probe its 11 serial bits.
2. Follow the eight data bits into the shift register.
3. Calculate odd parity manually.
4. Read KEY_RAW while pressing a key.
5. Poll DATA_READY and consume KEY_DATA.
6. Observe the difference between a PS/2 scan code and an ASCII character.