#include "epiphany-macros.h"
.global main
main:
    mov  r1, %low(0x00100000)
    movt r1, %high(0x00100000)
    ldr r0, [r1, #1]  ; loads word
TEAR_DOWN
