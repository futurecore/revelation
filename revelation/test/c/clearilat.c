#include <stdio.h>
#include <stdint.h>

void interrupt_handler() __attribute__ ((interrupt)) __attribute__ ((aligned(8)));

void interrupt_handler() {
    printf("Sync interrupt caused by ILATST (should only appear once).\n");
    __asm__("mov r45, 0x3ff");
    printf("Clearing all ILAT with ILATCL.\n");
    __asm__("movts ilatcl, r45");
}


int main() {
    uint32_t *ivt_exception; /* Interrupt vector pointers. */
    uint32_t addr_exception; /* Relative branch address. */
    uint32_t br32_exception; /* Relative address branch instruction. */

    ivt_exception = (uint32_t *) 0x20;
    addr_exception = (uint32_t) &interrupt_handler;
    addr_exception -= (uint32_t) ivt_exception; /* Adjust for user interrupt branch addr. */
    addr_exception = (addr_exception >> 1);     /* Lowest bit is skipped (alignment). */
    br32_exception = 0xe8;
    br32_exception |= ((addr_exception & (0x00ffffff))) << 8;
    *ivt_exception = br32_exception;

    /* Clear imask */
    __asm__("mov r45, 0");
    __asm__("movts imask, r45");

    /* Trigger user interrupt. */
    __asm__("mov r45, 0x300");
    __asm__("movts ilatst, r45");

    return 0;
}
