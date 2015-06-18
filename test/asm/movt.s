#include "epiphany-macros.h"
SET_UP
    mov r0,  %low(0x90000000)   ; sets all 32 bits
    movt r0, %high(0x90000000)  ; sets upper 16-bits
TEAR_DOWN
