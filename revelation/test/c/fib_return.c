#include <stdlib.h>
int main() {
    unsigned int a = 1, b = 1, i = 0, temp = 0;
    for(i = 0; i < 20; i++) {
        temp = a;
        a = b;
        b += temp;
    }
    return a;
}
