; EduK8 keyboard echo
; Poll the PS/2 keyboard and copy each received byte to video RAM.
; This first example writes successive characters across the first row.

KEY_DATA   = $C010
KEY_STATUS = $C011
VRAM       = $7800

start:
    LDX #$00
wait:
    LDA KEY_STATUS
    AND #$01
    BEQ wait
    LDA KEY_DATA
    STA VRAM,X
    INX
    JMP wait
