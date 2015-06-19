#include "epiphany-macros.h"
SET_UP
///    strs r31, [r2], #2 ; stores short to addr in r2
    strd r0, [r2], #1  ; stores double to addr in r2
TEAR_DOWN
