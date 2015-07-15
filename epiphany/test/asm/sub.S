#include "epiphany-macros.h"
.global _main
_main:
    mov r0, #100
    mov r1, #20
    sub r2, r0, r1  ; 80 = 100 - 20
    sub r3, r0, #20 ; 80 = 100 - 20
TEAR_DOWN
