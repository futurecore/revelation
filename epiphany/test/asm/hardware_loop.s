#include "epiphany_macros.h"
SET_UP
        mov r1, %low(loop_start) ;
        movt r1, %high(loop_start) ;
        movts ls, r1 ;         // setting loop start address
        mov r1, %low(loop_end) ;
        movt r1, %high(loop_end) ;
        movts le, r1 ;         // setting loop end address
        mov r1, #0x10 ;
        movts lc, r1 ;         // setting loop count
        gid ;                  // disabling interrupts
    .balignw 8,0x01a2 ;        // align to 8-byte boundary
    loop_start:
        add.l r1, r1, r0 ;     // first instruction in loop
        add.l r2, r2, r0 ;     // ".l" forces 32 bit instruction
        add.l r3, r3, r0 ;
        add.l r4, r4, r0 ;
        add.l r5, r5, r0 ;
        add.l r6, r6, r0;
    .balignw 8,0x01a2 ;        // align to 8-byte boundary
        add.l r7, r7, r0 ;
    loop_end:
        add.l r8, r8, r0 ;     // last instruction
        gie ;                  // enabling interrupts
TEAR_DOWN
