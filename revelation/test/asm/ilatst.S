#include "epiphany-macros.h"
.global main
main:
    mov r0, #0x3ff
    movts ilatst, r0  ; After this instruction ILAT will hold 0x3fe. One bit
                      ; will be cleared and put into IPEND.
TEAR_DOWN
