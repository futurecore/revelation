#include "epiphany-macros.h"
SET_UP
    mov r0, #1
    mov r1, #5
    asr r2, r0, r1 ; 0 = 1 >> 5
    asr r3, r0, #5 ; 0 = 1 >> 5
TEAR_DOWN
