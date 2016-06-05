#include "epiphany-macros.h"
.global _main
_main:
    mov r0, #5
    mov r1, #7
    lsl r2, r0, r1 ; 640 = 5 << 7
    lsl r3, r0, #7 ; 640 = 5 << 7
TEAR_DOWN
