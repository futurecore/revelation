.macro SET_UP
.global _start
_start:
.endm

.macro TEAR_DOWN
    bkpt // Terminate the program by setting a breakpoint.
.endm
