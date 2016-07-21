#include "epiphany-macros.h"
.global main
main:
    mov  r1, %low(0x00100004)
    movt r1, %high(0x00100004)
    ldr  r0, [r1], #0 ; loads double, updates r2
TEAR_DOWN
