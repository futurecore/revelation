#include "epiphany-macros.h"
.global main
main:
    mov r0, #25
    float r1, r0
TEAR_DOWN
