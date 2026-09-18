; K8 Monitor ROM v0.1
; Boot banner plus polling keyboard echo.
KEY_DATA     = $C010
KEY_STATUS   = $C011
VIDEO_RAM    = $7800

.org $8000
reset:
    LDX #$00

    ; Visible boot banner: "K8> "
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

keyboard_wait:
    LDA KEY_STATUS
    AND #$01
    BEQ keyboard_wait
    LDA KEY_DATA

    ; First monitor command: '?' is a compact HELP command.
    ; It avoids hidden parsing machinery while the monitor is still tiny.
    CMP #$3F
    BEQ help

    STA VIDEO_RAM,X
    INX
    JMP keyboard_wait

help:
    LDA #$48       ; H
    STA VIDEO_RAM,X
    INX
    LDA #$45       ; E
    STA VIDEO_RAM,X
    INX
    LDA #$4C       ; L
    STA VIDEO_RAM,X
    INX
    LDA #$50       ; P
    STA VIDEO_RAM,X
    INX
    JMP keyboard_wait

; K8 v1 reset and IRQ vectors
.org $FFFC
.word reset
.word reset
