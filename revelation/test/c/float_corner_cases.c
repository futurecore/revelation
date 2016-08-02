/* Some floating point corner cases. */
#include <float.h>
#include <stdio.h>
#include <stdint.h>

int main() {
    int val_i = 0xffffffff;
    float val_f = 0xffffffff;
    float convert_f = (float)val_i;
    int convert_i = (int)val_f;
    printf("Signed integer value = %d, %x\n", val_i, val_i);
    printf("Float value = %.*e\n", DECIMAL_DIG, val_f);
    printf("Convert float to signed integer: %d, %x\n", convert_i, convert_i);
    printf("Convert signed integer to float = %.*e\n", DECIMAL_DIG, convert_f);
    return 0;
}
