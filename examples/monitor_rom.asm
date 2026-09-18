; K8 Monitor ROM v0.2
; Interactive line editor with the first real command: HELP.
KEY_DATA     = $C010
KEY_STATUS   = $C011
VIDEO_RAM    = $7800
CMD_BUFFER   = $0200
CURSOR       = $00F0
BUFFER_LEN   = $00F1

.org $8000
reset:
    LDX #$00
    STX CURSOR
    LDA #$4B
    STA VIDEO_RAM,X
    INX
    LDA #$38
    STA VIDEO_RAM,X
    INX
    LDA #$3E
    STA VIDEO_RAM,X
    INX
    LDA #$20
    STA VIDEO_RAM,X
    INX
    STX CURSOR

main:
    LDX CURSOR
wait:
    LDA KEY_STATUS
    AND #$01
    BEQ wait
    LDA KEY_DATA

    ; CR terminates the command line.
    CMP #$0D
    BEQ command

    ; Backspace is reserved for the next line-editor revision.
    CMP #$08
    BEQ wait

    ; Keep the first version bounded to 32 visible characters.
    CPX #$20
    BCS wait

    STA CMD_BUFFER,X
    STA VIDEO_RAM,X
    INX
    STX CURSOR
    JMP wait

command:
    LDX #$00
    LDA CMD_BUFFER,X
    CMP #$48
    BNE unknown
    INX
    LDA CMD_BUFFER,X
    CMP #$45
    BNE unknown
    INX
    LDA CMD_BUFFER,X
    CMP #$4C
    BNE unknown
    INX
    LDA CMD_BUFFER,X
    CMP #$50
    BNE unknown

help:
    ; A minimal response proves that line editing and dispatch work.
    LDX #$00
    LDA #$48
    STA VIDEO_RAM+$28,X
    INX
    LDA #$45
    STA VIDEO_RAM+$28,X
    INX
    LDA #$4C
    STA VIDEO_RAM+$28,X
    INX
    LDA #$50
    STA VIDEO_RAM+$28,X
    INX
    LDA #$20
    STA VIDEO_RAM+$28,X
    INX
    LDA #$4F
    STA VIDEO_RAM+$28,X
    INX
    LDA #$4B
    STA VIDEO_RAM+$28,X
    JMP reset

unknown:
    ; Unknown command: show '?' on the second row and restart.
    LDX #$00
    LDA #$3F
    STA VIDEO_RAM+$28,X
    JMP reset

; K8 v1 reset and IRQ vectors
.org $FFFC
.word reset
.word reset
