#include "epiphany-macros.h"
SET_UP
    _inf: mov r0, #10    ; loop 10 times
    _loopA:
        add r1, r1, #1   ; some operation
        sub r0, r0, #1   ; decrement loop counter
        beq _loopa       ; branch while true
        b _inf           ; keep executing forever
TEAR_DOWN
