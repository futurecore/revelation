#include "epiphany-macros.h"
.global main
main:
    mov r0, #3
    mov r1, #1
    lsr r2, r0, r1 ; 1 = 3 >> 1
    lsr r3, r0, #1 ; 1 = 3 >> 1
TEAR_DOWN
