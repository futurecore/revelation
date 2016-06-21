#include "epiphany-macros.h"
.global main
main:
    mov r0, #1
    mov r1, %low(hello_str)
    movt r1, %high(hello_str)
    mov r2, #14
    mov r3, #5
    trap #7
TEAR_DOWN
hello_str:
  .ascii "Hello, world!\n"
