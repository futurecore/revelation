#include "epiphany-macros.h"
.global main
interrupt_handler:
    mov r0, #1
    mov r1, %low(message)
    movt r1, %high(message)
    mov r2, #17
    mov r3, #5
    trap #7
    rti
main:
    ; ivt = (uint32_t *) 0x24;
    mov r0, #0x24
    ; branch_addr = (uint32_t) &interrupt_handler;
    mov r1, %low(interrupt_handler)
    movt r1, %high(interrupt_handler)
    ; branch_addr -= (uint32_t) ivt;
    sub r2, r1, r0
    ; branch_addr = (branch_addr >> 1);
    lsr r2, r2, #1
    ; rel_branch_instruction32 = 0xe8;
    mov r3, 0xe8
    ; rel_branch_instruction32 |= ((branch_addr & (0x00ffffff))) << 8;
    mov r4, %low(0x00ffffff)
    movt r4, %high(0x00ffffff)
    and r5, r2, r4  ; branch_addr & (0x00ffffff)
    mov r6, #8
    lsl r7, r5, r6  ; (branch_addr & 0x00ffffff) << 8
    orr r8, r3, r7
    ; *ivt = rel_branch_instruction32;
    str r8, [r0, #0]
    ; Clear interrupt mask.
    mov r45, 0
    movts imask, r45
    ; Enable interrupts.
    gie
    ; Set interrupt latch.
    mov r45, 0x200
    movts ilatst, r45
    TEAR_DOWN
message:
    .ascii "Interrupt fired.\n"
