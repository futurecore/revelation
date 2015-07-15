#include "epiphany-macros.h"
.global _main
_main:
    mov r0, #0
    mov r1, #2
    mov r2, #5
    float r0, r0
    float r1, r1
    float r2, r2
    fsub r3, r2, r0 ;  5 = 5 - 0
    fsub r4, r2, r1 ;  3 = 5 - 2
    fsub r5, r1, r2 ; -3 = 2 - 5
TEAR_DOWN
