#include "epiphany-macros.h"
.global main
main:
    mov r0, #0
    mov r1, #1
    and r2, r1, r1 ; 1 = 1 & 1
    and r3, r1, r0 ; 0 = 1 & 0
    and r4, r0, r1 ; 0 = 0 & 1
    and r5, r0, r0 ; 0 = 0 & 0
TEAR_DOWN
