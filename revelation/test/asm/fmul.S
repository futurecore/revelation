#include "epiphany-macros.h"
.global main
main:
    mov r0, #0
    mov r1, #2
    mov r2, #5
    float r0, r0
    float r1, r1
    float r2, r2
    fmul r3, r2, r0 ;  0 = 5 * 0
    fmul r4, r2, r1 ; 10 = 5 * 2
TEAR_DOWN
