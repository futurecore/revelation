#include <stdlib.h>
#include <stdio.h>

/* Assume the ELF will be simulated from the top-level directory. */
const char *file = "revelation/test/c/hello.txt";

int main() {
    FILE *fp;
    char   buffer[4096];
    size_t nbytes;
    if ((fp = fopen(file, "r")) != 0) {
        while ((nbytes = fread(buffer, sizeof(char), sizeof(buffer), fp)) != 0) {
             fwrite(buffer, sizeof(char), nbytes, stdout);
        }
        fclose(fp);
    }
    return 0;
}
