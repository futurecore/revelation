#include "epiphany_macros.h"
SET_UP
    mov  r0, %low(x87654321)
    mov  r0, %high(x87654321)
    bitr r0, r0 ; r0 gets 0x84C2A6B1
TEAR_DOWN
