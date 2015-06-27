#include "epiphany-macros.h"
SET_UP
    mov r0, _laba
    jalr r0        ; save pc in lr and jump to _laba
    _laba:
        mov r3, #100
TEAR_DOWN
