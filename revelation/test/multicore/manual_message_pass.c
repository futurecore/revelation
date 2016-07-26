/* Run on e-sim as:
 *    e-sim -r 1 -c 2 manual_message_pass.elf
 */
#include <stdio.h>
#include "e_lib.h"

int main(void) {
    e_coreid_t coreid = e_get_coreid();
    unsigned i;

    if (coreid == 0x808) {
        volatile int *p;
        p = (int *) 0x80880000;
        while ((*p) == 0);  /* Wait until message has been written. */
        printf("Received message.\n");
        return 0;
    }
    else {
        int i;
        int *p;
        p = (int *) 0x80880000;
        *p = 0;
        for (i = 0; i < 1000; i++);
        *p = (int)coreid;
        return 0;
    }

    return 0;
}
