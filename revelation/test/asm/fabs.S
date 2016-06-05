#include "epiphany-macros.h"
.global _main
_main:
    mov r0, #5
    mov r1, #0
    float r0, r0
    float r1, r1
    fsub r2, r1, r0
    fabs r3, r0
    fabs r4, r1
    fabs r5, r2
TEAR_DOWN
