; EduK8 keyboard echo
; Poll the PS/2 keyboard and copy each received byte to video RAM.
; This first example writes successive characters across the first row.

KEY_DATA   = $C010
KEY_STATUS = $C011
VRAM       = $7800

; Current assembler v0 keeps constants literal until .equ support lands.
start:
    LDX #$00
wait:
    LDA $C011
    AND #$01
    BEQ wait
    LDA $C010
    STA $7800,X
    INX
    JMP wait
