.macro SET_UP
.global main  // gcc needs this to create a valid elf
 main:
.endm

.macro TEAR_DOWN
    bkpt // Terminate the program by calling setting a breakpoint.
.endm
