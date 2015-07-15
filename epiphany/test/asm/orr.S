#include "epiphany-macros.h"
.global _main
_main:
    mov r0, #5
    mov r1, #7
    orr r2, r0, r1 ; 7 = 5 | 7
TEAR_DOWN
