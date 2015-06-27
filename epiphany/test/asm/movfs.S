#include "epiphany-macros.h"
SET_UP
    mov r0, #7
    movts CONFIG, r0  ; copies r0 to CONFIG register
    movfs r63, CONFIG ; copies CONFIG register to r63
TEAR_DOWN
