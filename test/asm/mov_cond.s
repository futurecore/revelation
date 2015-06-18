#include "epiphany-macros.h"
SET_UP
    moveq r2, r0   ; copies r0 to r2 if the EQ
    mov r3, r1     ; copies r1 to r3
TEAR_DOWN
