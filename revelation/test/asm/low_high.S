#include "epiphany-macros.h"
.global main
main:
    mov  r3, %low(0xFFFFFFFF)
    movt r3, %high(0xFFFFFFFF)
TEAR_DOWN
