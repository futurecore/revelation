// Code by Ola Jeppsson @olajep
// From: https://github.com/olajep/esim-test-bins

#include <stdio.h>
#include <stdint.h>

void interrupt_handler() __attribute__ ((interrupt)) __attribute__ ((aligned(8)));

void interrupt_handler() {
    static int i = 0;
    switch (i) {
        case 0:
            printf("User interrupt 1.\n");
            break;
        case 1:
            printf("User interrupt 2.\n");
            break;
        case 2:
            printf("User interrupt 3.\n");
            break;
        case 3:
            printf("User interrupt 4.\n");
            break;
        default:
            printf("Another user interrupt.\n");
            break;
    }
    i++;
}


int main() {
    uint32_t *ivt;
    uint32_t branch_addr;
    uint32_t rel_branch_instruction32;

    ivt = (uint32_t *) 0x24;

    branch_addr = (uint32_t) &interrupt_handler;
    branch_addr -= (uint32_t) ivt;
    branch_addr = (branch_addr >> 1);

    rel_branch_instruction32 = 0xe8;
    rel_branch_instruction32 |= ((branch_addr & (0x00ffffff))) << 8;

    *ivt = rel_branch_instruction32;

    /* Loop on exception interrupt */
    ivt = (uint32_t *) 4;
    *ivt = 0x000000e8;

    /* Clear imask */
    __asm__("mov r45, 0");
    __asm__("movts imask, r45");

    /* Trigger user interrupt. */
    __asm__("mov r45, 0x200");
    __asm__("movts ilatst, r45");
    __asm__("movts ilatst, r45");
    __asm__("movts ilatst, r45");
    __asm__("movts ilatst, r45");
    __asm__("movts ilatst, r45");

    return 0;
}
