#include "epiphany-macros.h"
SET_UP
    gid ; disable interrupts, set STATUS[1] = 1
    gie ; enable interrupts, set STATSUS[1]=0
TEAR_DOWN
