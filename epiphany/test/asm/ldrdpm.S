#include "epiphany-macros.h"
SET_UP
    ldrh r31, [r2], #1 ; loads short, updates r2 -- syntax error.
    ldrd  r0, [r2], #4 ; loads double, updates r2
TEAR_DOWN
