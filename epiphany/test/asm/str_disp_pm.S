#include "epiphany-macros.h"
.global _main
_main:
    mov  r0, %low(0xFFFFFFFF)
    movt r0, %high(0xFFFFFFFF)
    mov  r1, %low(0x00100004)
    movt r1, %high(0x00100004)
    str r0, [r1], #0
TEAR_DOWN
