#include "epiphany-macros.h"
.global main
main:
/*
    mov r1, 0x8             ; set the startup bit
    movt r1, _1D_DESCR      ; put descriptor pointer in the upper 16 bits
    movts DMA0CONFIG, r1    ; start a DMA transfer by writing to the
                            ; DMA config register.
    _1D_DESCR
    .word 0x00000003    ; configure in master mode and enable
    .word 0x00010001    ; increment src/dst address by 1 byte each transaction
    .word 0x00010008    ; transfer has 8 transactions in a single inner loop
    .word 0x00000000    ; outer loop stride not used in this example
    .word 0x00002000    ; set source address to 0x2000, a local address
    .word 0x92000000    ; set destination address to an external address
*/
TEAR_DOWN
