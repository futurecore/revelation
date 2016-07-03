#include "epiphany-macros.h"
.global main
main:
    mov r0, #0x3ff
    movts ilatcl, r0
TEAR_DOWN
