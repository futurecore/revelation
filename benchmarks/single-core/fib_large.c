/* Long Fibonacci loop -- the result overflows, but this is just enough to
 * trigger the JIT.
 */
#include <stdlib.h>
#include <stdio.h>
int main() {
    unsigned long a = 1, b = 1, i = 0, temp = 0;
    for(i = 0; i < 10000; i++) {
        temp = a;
        a = b;
        b += temp;
    }
    printf("%lu\n", a);
    return 0;
}
