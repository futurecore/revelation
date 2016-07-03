#include "epiphany-macros.h"
.global main
main:
    mov r0, %low(0xffffffff)
    movt r0, %high(0xffffffff)
    movts fstatus, r0
TEAR_DOWN
