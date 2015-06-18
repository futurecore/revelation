#include "epiphany-macros.h"
SET_UP
    mov r0, #_laba     ; move label into register
    jalr r0            ; save pc in lr and jump to laba
TEAR_DOWN
