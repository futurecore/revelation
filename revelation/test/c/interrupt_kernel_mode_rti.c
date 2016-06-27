/* Based on code by Ola Jeppsson @olajep
 * From: https://github.com/olajep/esim-test-bins
 */
#include <stdio.h>
#include <stdint.h>

int main() {
    register uint32_t r38 __asm__("r38"); /* Temp for adjusting system registers. */

    /* Disable kernel mode / activate user mode. */
    __asm__("movfs r38, status");
    r38 &= ~(1 << 2);
    __asm__("movts status, r38");

    /* Enable kernel / user mode. */
    __asm__("movfs r38, config");
    r38 |= (1 << 25);
    __asm__("movts config, r38");

    /* RTI (should switch to user mode). */
    __asm__("rti");

    return 0;
}
