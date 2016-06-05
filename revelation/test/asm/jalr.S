#include "epiphany-macros.h"
.global _main
_main:
    mov  r0, %low(_laba)
;    movt r0, %high(_laba)
    jalr r0        ; save pc in lr and jump to _laba
    _laba:
        mov r3, #100
TEAR_DOWN
