#include "epiphany-macros.h"
SET_UP
    gie ; enable interrupts, set STATSUS[1]=0
    gid ; disable interrupts, set STATUS[1] = 1
TEAR_DOWN
