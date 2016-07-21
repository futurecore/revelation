#include "epiphany-macros.h"
.global main
main:
    mov r1, #100
    mov r0, #10          ; loop 10 times
    _loopa:
        add r1, r1, #1   ; some operation
        sub r0, r0, #1   ; decrement loop counter
        bne _loopa       ; branch while true
TEAR_DOWN
