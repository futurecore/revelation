#include "epiphany-macros.h"
SET_UP
    mov r0, #_labA ; move label into register
    jr r0 ;        ; jump to _labA
TEAR_DOWN
