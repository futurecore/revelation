// Code by Ola Jeppsson @olajep
// From: https://github.com/olajep/esim-test-bins

#include <stdio.h>
#include <stdint.h>

void exception_isr() __attribute__ ((interrupt)) __attribute__ ((aligned(8)));
void exception_isr(int n) {
    printf("Exception_isr %d\n", n);
}


int main() {
    register uint32_t r38 __asm__("r38"); /* Temp for enabling setting fp exceptions. */

    uint32_t *ivt_exception; /* Interrupt vector pointers. */
    uint32_t addr_exception; /* Relative branch address. */
    uint32_t br32_exception; /* Relative address branch instruction. */

    ivt_exception = (uint32_t *) 0x4;
    addr_exception = (uint32_t) &exception_isr;
    addr_exception -= (uint32_t) ivt_exception; /* Adjust for user interrupt branch addr. */
    addr_exception = (addr_exception >> 1);     /* Lowest bit is skipped (alignment). */
    br32_exception = 0xe8;
    br32_exception |= ((addr_exception & (0x00ffffff))) << 8;
    *ivt_exception = br32_exception;

    /* Clear imask. */
    __asm__("mov r40, 0");
    __asm__("movts imask, r40");

    /* Enable floating-point exceptions. */
    __asm__("movfs r38, config");
    r38 |= 14;
    __asm__("movts config, r38");

    volatile float a = 1e38;
    volatile float b = 1e38;
    float c;
    c = a*b;

    printf("End.\n");
    return  !(c == 0.0);
}
