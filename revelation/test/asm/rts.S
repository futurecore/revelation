#include "epiphany-macros.h"
.global main
main:
    bl _my_func ; save PC to LR and jump to _my_func
    nop
    nop
    nop
    b _end
    _my_func:
        mov r1, #100
        mov r2, #200
        add r3, r1, r2
        rts  ; branch back to callee
    _end:
TEAR_DOWN
