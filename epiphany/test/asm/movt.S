#include "epiphany-macros.h"
.global _main
_main:
    movt r0, %high(0x90000000)  ; sets upper 16-bits
TEAR_DOWN
