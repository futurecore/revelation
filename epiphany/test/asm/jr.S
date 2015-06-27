#include "epiphany-macros.h"
SET_UP
    mov  r3, %low(_add_label)  ; _add_label is small, don't have to use %high.
    jr r3  ; jump to add_label
_add_label:
    mov r1, #1
    mov r2, #2
    add r0, r1, r2
TEAR_DOWN
