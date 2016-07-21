/* Based on code by Ola Jeppsson @olajep
 * From: https://github.com/olajep/esim-test-bins
 */
#include <stdio.h>
#include <stdint.h>

void fpu_interrupt_handler() __attribute__ ((interrupt));
void fpu_interrupt_handler() {
    printf("FPU exception fired.\n");
}

int main() {
    register uint32_t r38 __asm__("r38"); /* tmp for enabling fp exceptions. */

    float a = 1e38;
    float b = 1e38;
    float c;

    uint32_t *ivt_usr, *ivt_exception; /* Interrupt vector pointers. */
    uint32_t addr_usr, addr_exception; /* Relative branch address. */
    uint32_t br32_usr, br32_exception; /* Relative address branch instruction. */

    ivt_usr = (uint32_t *) 0x4;
    addr_usr = (uint32_t) &fpu_interrupt_handler;
    addr_usr -= (uint32_t) ivt_usr; /* Adjust for user interrupt branch address. */
    addr_usr = (addr_usr >> 1);     /* Lowest bit is skipped (alignment). */
    br32_usr = 0xe8;
    br32_usr |= ((addr_usr & (0x00ffffff))) << 8;
    *ivt_usr = br32_usr;

    /* Clear imask. */
    __asm__("movt r40, 0");
    __asm__("mov r40, 0");
    __asm__("movts imask, r40");

    /* Enable float exceptions. */
    __asm__("movfs r38, config");
    r38 |= 14;
    __asm__("movts config, r38");

    /* Trigger fpu interrupt. */
    c = a * b;

    /* Disable fpu exceptions. */
    __asm__("movfs r38, config");
    r38 = r38 & ~(1 << 1);  /* Invalid floating-point exception.   */
    r38 = r38 & ~(1 << 2);  /* Overflow floating-point exception.  */
    r38 = r38 & ~(1 << 3);  /* Underflow floating-point exception. */
    __asm__("movts config, r38");

    /* Trigger fpu interrupt.*/
    c = a * b;

    return 0;
}
