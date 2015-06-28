#include "epiphany-macros.h"
SET_UP
    mov  r0, %low(0xFFFFFFFF)
    movt r0, %high(0xFFFFFFFF)
    mov  r1, %low(0x00100000)
    movt r1, %high(0x00100000)
    mov r2, #4
    str r0, [r1], r2
TEAR_DOWN
