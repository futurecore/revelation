#include "epiphany-macros.h"
.global main
main:
    movt r0, %high(0x90000000)  ; sets upper 16-bits
TEAR_DOWN
