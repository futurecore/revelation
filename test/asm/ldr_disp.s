#include "epiphany-macros.h"
SET_UP
    ldrb r31, [r2]    ; loads byte
    ldr r0, [r2, #1]  ; loads word
TEAR_DOWN
