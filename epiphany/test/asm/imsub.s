#include "epiphany-macros.h"
SET_UP
    mov r0, #0
    mov r1, #2
    mov r2, #5
    mov r3, #7
    mov r4, #7
    float r0, r0
    float r1, r1
    float r2, r2
    float r3, r3
    float r4, r4
    imsub r3, r2, r1 ; -3 = 7 - (5 * 2)
    imsub r4, r2, r0 ;  7 = 7 + (5 * 0)
TEAR_DOWN
