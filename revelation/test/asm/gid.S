#include "epiphany-macros.h"
.global main
main:
    gie ; enable interrupts, set STATSUS[1] = 0
    gid ; disable interrupts, set STATUS[1] = 1
TEAR_DOWN
