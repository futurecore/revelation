#include <stdio.h>
#include <stdint.h>

int main() {
    float a = 1.72;
    float b = 2.73;
    float c = 0.0;

    int d = 2;
    int e = 3;
    int f = 0;

    c = a + b;
    printf("a + b = %.3f\n", c);
    c = a - b;
    printf("a - b = %.3f\n", c);
    c = a * b;
    printf("a * b = %.3f\n", c);

    f = d + e;
    printf("d + e = %d\n", f);
    f = d - e;
    printf("d - e = %d\n", f);
    f = d * e;
    printf("d * e = %d\n", f);

    return 0;
}
