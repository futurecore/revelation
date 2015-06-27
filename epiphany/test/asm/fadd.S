#include "epiphany-macros.h"
SET_UP
    mov r4, #0
    mov r3, #10
    mov r2, #5
    float r2, r2
    float r3, r3
    float r4, r4
    fadd r0, r2, r3 ; 15 = 10 + 5
    fadd r1, r2, r4 ;  5 = 5 + 0
TEAR_DOWN
