#include "epiphany-macros.h"
.global main
main:
    movfs r0, coreid
TEAR_DOWN
