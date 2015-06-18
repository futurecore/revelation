#include "epiphany-macros.h"
SET_UP
    add r2, r1, #2 ;
    add r2, r1, #-100 ;
    add r1, r1, r3 ;
TEAR_DOWN
