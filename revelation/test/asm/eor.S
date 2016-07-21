#include "epiphany-macros.h"
.global main
main:
    mov r0, #5
    mov r1, #7
    eor r2, r0, r1 ; 2 = 5 ^ 7
TEAR_DOWN
