#include "epiphany-macros.h"
.global main
main:
    ; This testset should fail, as the absolute address used for the test and
    ; set instruction must be located within the on-chip local memory and must
    ; be greater than 0x00100000 (2^20).
    mov r0, #0xFFFF
    mov r1, #0x00002
    mov r2, #0x00002        ; location in memory: 0x00000004
    testset r0, [r1, r2]   ; test-set
    sub r0, r0, #0         ; check result
TEAR_DOWN
