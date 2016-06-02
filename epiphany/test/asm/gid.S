#include "epiphany-macros.h"
.global _main
_main:
    gie ; enable interrupts, set STATSUS[1] = 0
    gid ; disable interrupts, set STATUS[1] = 1
TEAR_DOWN
