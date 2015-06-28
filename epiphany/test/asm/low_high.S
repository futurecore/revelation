#include "epiphany-macros.h"
SET_UP
    mov  r3, %low(0xFFFFFFFF)
    movt r3, %high(0xFFFFFFFF)
TEAR_DOWN
