#include "epiphany-macros.h"
.global _main
_main:
    mov r0, %low(0x87654321)
    movt r0, %high(0x87654321)
    bitr r0, r0               ; r0 gets 0x84C2A6B1
TEAR_DOWN
