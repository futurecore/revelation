#include "epiphany-macros.h"
SET_UP
    /* Example of trying to lock on value in memory. */
    _loop:
        mov r2, r3             ; value to write
        testset r2, [r0, r1]   ; test-set
        sub r2, r2, #0         ; check result
//        BNE_loop               ; keep trying
TEAR_DOWN
