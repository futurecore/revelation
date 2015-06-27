#include "epiphany-macros.h"
SET_UP
    ; Example of trying to lock on value in memory.
    ; A more realistic example would loop until the testset is successful.
    mov r0, #0xFFFF
    mov  r1, %low(0x00100000)  ; sets all 32 bits
    movt r1, %high(0x00100000) ; sets upper 16-bits
    mov r2, #0x3               ; why is this not 0x4?
    testset r0, [r2,+r1]       ; test-set memory location: 0x00100004
    sub r0, r0, #0             ; check result
TEAR_DOWN
