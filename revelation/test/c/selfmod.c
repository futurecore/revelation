// Code by Ola Jeppsson @olajep
// From: https://github.com/olajep/esim-test-bins

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int hello = 0;

void foo()
{
    if (!hello) {
	hello = 1;
	printf("Hello\n");
    }
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");
}

void bar()
{
    printf("World\n");
    exit(0);
}

/* Dummy so we can get end of bar */
void baz()
{
}

int main()
{
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    foo();
    memcpy(foo, bar, baz-bar);
    foo();
    /* Should print "Hello\nWorld\n" */
    return 1;
}
