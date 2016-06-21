#include "epiphany-macros.h"
.global main
main:
    mov r0, #7
    movts IRET, r0  ; copies r0 IRET register
    movfs r63, IRET ; copies IRET register to r63
TEAR_DOWN
