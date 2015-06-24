#include "epiphany-macros.h"
SET_UP
    ; Temporary register - r14
    ; Function argument  - r15
    ; Function return    - r16
    mov r15, #5
    mov r16, #0
    bl _my_func ; save PC to LR and jump to _my_func
    b _end
    _my_func:
        mov r14, #0
        mov r16, #0
        _loop:
            add r14, r14, r15
            sub r15, r15, #1
            bne _loop
        add r16, r16, r14
        b lr  ; branch back to callee
    _end:
TEAR_DOWN
