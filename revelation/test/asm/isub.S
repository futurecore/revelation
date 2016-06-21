#include "epiphany-macros.h"
.global main
main:
    mov r0, #0
    mov r1, #2
    mov r2, #5
    float r0, r0
    float r1, r1
    float r2, r2
    isub r3, r2, r0 ;  5 = 5 - 0
    isub r4, r2, r1 ;  3 = 5 - 2
    isub r5, r1, r2 ; -3 = 2 - 5
TEAR_DOWN
