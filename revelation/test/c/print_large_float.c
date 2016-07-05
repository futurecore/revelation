/* COMPILE WITH: -mfp-mode= (can be int, truncate, round-nearest). */
#include <float.h>
#include <stdio.h>
#include <stdint.h>

int main() {
    register uint32_t r38 __asm__("r38"); /* tmp for setting CONFIG register. */

    float d = 0xffffffffffffffff;
    __asm__("movfs r38, config");
    r38 = 0;
    __asm__("movts config, r38");
    printf("d     = %.*e\n", DECIMAL_DIG, d);
    printf("d - 1 = %.*e\n", DECIMAL_DIG, d - 1);

    return 0;
}
