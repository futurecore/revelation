#include "epiphany-macros.h"
.global main
main:
    mov r0, #1
    mov r1, #2
    mov r2, #3
    mov r3, #4
    mov r4, #5
    mov r5, #6
    mov r6, #7
    mov r7, #8
    mov r8, #9
    mov r9, #10
    mov r10, #11
    mov r11, #12
    movts CONFIG, r0  ; copies contents of r0 to CONFIG register
    movts STATUS, r1
    ; movts pc, r2
    movts LC, r3
    movts LS, r4
    movts LE, r5
    movts IRET, r6
    movts IMASK, r7
    movts ILATST, r9
    movts ILATCL, r10
    movts IPEND, r11

    movts ILAT, r8  ; ILAT is set by some aliased registers, so do this last.

TEAR_DOWN
