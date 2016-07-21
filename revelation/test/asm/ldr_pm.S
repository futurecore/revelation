#include "epiphany-macros.h"
.global main
main:
    mov  r1, %low(0x80002)
    movt r1, %high(0x80002)
    mov  r2, %low(0x80002)
    movt r2, %high(0x80002)
    ldr r0, [r1], r2        ; loads word, updates r1
TEAR_DOWN
