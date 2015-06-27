#include "epiphany-macros.h"
SET_UP
    mov r3, #_add_label
    jr r3  ; jump to add_label
_add_label:
    mov r1, #1
    mov r2, #2
    add r0, r1, r2
TEAR_DOWN
