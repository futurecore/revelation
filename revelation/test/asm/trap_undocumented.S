#include "epiphany-macros.h"
.global main
main:
    mov r0, %low(filename)
    movt r0, %high(filename)
    mov r1, #0      ; flags.
    mov r2, #0      ; mode.
    trap #2         ; open() -- places file descriptor in r0.
    mov r1, 0xfff0  ; buffer.
    mov r2, #14     ; number of bytes to read.
    trap #1         ; read()
    trap #6         ; close()
    mov r0, #1      ; file descriptor (STDOUT).
    trap #0         ; write()
TEAR_DOWN
filename:
    .ascii "revelation/test/c/hello.txt"
