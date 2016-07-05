// Code by Ola Jeppsson @olajep
// From: https://github.com/olajep/esim-test-bins
#include <stdio.h>
#include <e_lib.h>
/*
asm(".global __CORE_ROW_;");
asm(".set __CORE_ROW_,0x20;");
asm(".global __CORE_COL_;");
asm(".set __CORE_COL_,0x8;");
*/
int main() {
    int a = 0;
    int b = 1;

    register int zero __asm__("r32");
    zero = 0;

    register int *ptra __asm__ ("r33");
    register int *ptrb __asm__ ("r34");

    register int r35 __asm__ ("r35");
    register int r36 __asm__ ("r36");

    /* Local addresses will segfault. */
    ptra = (int *) (((int) &a) | ((int) (e_get_coreid() << 20)));
    ptrb = (int *) (((int) &b) | ((int) (e_get_coreid() << 20)));

    r35 = 10;
    r36 = 20;

    printf("Before testset:\n");
    printf("a: %d\tb: %d\n", a, b);
    __asm__("testset r35, [r33,r32]");
    __asm__("testset r36, [r34,r32]");
    printf("After testset:\n");
    printf("a: %d\tb: %d\n", a, b);
    printf("r35: %d\tr36: %d\n", r35, r36);

    return 0;
}
