#include "epiphany-macros.h"
.global _main
_main:
    mov r0, #0
    mov r1, #2
    mov r2, #5
    mov r3, #7
    mov r4, #7
    float r0, r0
    float r1, r1
    float r2, r2
    float r3, r3
    float r4, r4
    fmadd r3, r2, r1 ; 17 = 7 + (5 * 2)
    fmadd r4, r2, r0 ;  7 = 7 + (5 * 0)
TEAR_DOWN
