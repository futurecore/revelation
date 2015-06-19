#include "epiphany-macros.h"
SET_UP
//    ldrs r31, [r2], r1    ; loads short, updates R2
    ldrd r0, [r2], r1     ; loads double, updates R2
TEAR_DOWN
