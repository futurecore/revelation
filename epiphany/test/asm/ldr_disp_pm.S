#include "epiphany-macros.h"
SET_UP
    mov  r1, %low(0x00100000)
    movt r1, %high(0x00100000)
    ldr  r0, [r1], #1 ; loads double, updates r2
TEAR_DOWN
