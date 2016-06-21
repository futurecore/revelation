#include "epiphany-macros.h"
.global main
main:
    ; Temporary register - r0
    ; Function argument  - r1
    ; Function return    - r2
    mov r1, #5
    mov r2, #0
    bl _my_func ; save PC to LR and jump to _my_func
    b _end
    _my_func:
        mov r0, #0
        mov r2, #0
        _loop:
            add r0, r0, r1
            sub r1, r1, #1
            bne _loop
        add r2, r0, #0
        rts  ; branch back to callee
    _end:
TEAR_DOWN  ; Sets breakpoint.
