#include "epiphany-macros.h"
SET_UP
    mov r1, #5
    mov r2, #5
    mov r3, #0
    add r2, r1, #2    ; r2 = 7
    add r3, r1, #100  ; r3 = 105
    add r1, r1, r3    ; r1 = 110
TEAR_DOWN
