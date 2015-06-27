#include "epiphany-macros.h"
SET_UP
    mov r0, #5
    mov r1, #15
    mov r2, #0
    sub r0, r0, r0 ; 0 = 5 - 5
    moveq r2, r1   ; copies r1 to r2 if the EQ
    mov r3, r1     ; copies r1 to r3
TEAR_DOWN
