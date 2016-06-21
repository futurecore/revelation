#include "epiphany-macros.h"
.global main
main:
    mov r0, #7
    movts IRET, r0 ; copies r0 to IRET register
TEAR_DOWN
