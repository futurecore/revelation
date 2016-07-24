#include "epiphany-macros.h"
.global main
main:
    mov r0, 0x1
    mov r1, 100
    mov r9, %low(0x50)      ; ARITHMODE == 0, CTIMER0CFG == 5
    movt r9, %high(0x50)
    mov r10, %low(0x80040)  ; ARITHMODE == 4, CTIMER0CFG == 4
    movt r10, %high(0x80040)
    ; Floating-point mode.
    movts CTIMER0, r1   ; Reset CTIMER0 to 100.
    movts CONFIG, r9
    float r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0
    fadd r0, r0, r0     ; CTIMER0 should hold 95.
    movfs r16, CTIMER0  ; Save CTIMER0.
    ; Signed integer mode.
    mov r0, #1
    movts CTIMER0, r1   ; Reset CTIMER0 to 100.
    movts CONFIG, r10
    iadd r0, r0, r0
    iadd r0, r0, r0
    iadd r0, r0, r0
    iadd r0, r0, r0
    iadd r0, r0, r0     ; CTIMER0 should hold 95.
TEAR_DOWN
