#include "epiphany-macros.h"
.global _main
_main:
    mov r0, #5
    float r0, r0
    fix r0, r0
TEAR_DOWN
