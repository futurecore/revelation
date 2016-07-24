#include "epiphany-macros.h"
.global main
main:
    mov r0, 0x1
    mov r1, 100
    mov r9, %low(0x500)     ; ARITHMODE == 0, CTIMER1CFG == 5
    movt r9, %high(0x500)
    mov r10, %low(0x80400)  ; ARITHMODE == 4, CTIMER1CFG == 4
    movt r10, %high(0x80400)
    ; Floating-point mode.
    movts CTIMER1, r1   ; Reset CTIMER1 to 100.
    movts CONFIG, r9
    float r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0     ; CTIMER1 should hold 94.
    movfs r16, CTIMER1  ; Save CTIMER1.
    ; Signed integer mode.
    mov r0, #1
    movts CTIMER1, r1   ; Reset CTIMER1 to 100.
    movts CONFIG, r10
    iadd r0, r0, r0
    iadd r0, r0, r0
    iadd r0, r0, r0
    iadd r0, r0, r0
    iadd r0, r0, r0     ; CTIMER1 should hold 95.
TEAR_DOWN
