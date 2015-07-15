#include "epiphany-macros.h"
.global _main
_main:
    mov  r1, %low(0x00100004)
    movt r1, %high(0x00100004)
    mov  r2, #0
    ldr r0, [r1,+r2]     ; loads word
TEAR_DOWN
