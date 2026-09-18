; Minimal K8 monitor ROM skeleton
VIDEO_RAM = $7800

.org $8000
reset:
    LDX #$00
    LDA #$4B       ; 'K'
    STA VIDEO_RAM,X
    INX
    LDA #$38       ; '8'
    STA VIDEO_RAM,X
hang:
    JMP hang

; K8 v1 reset and IRQ vectors
.org $FFFC
.word reset
.word reset
