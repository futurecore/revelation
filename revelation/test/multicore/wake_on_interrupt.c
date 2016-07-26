/* Run on e-sim as:
 *    e-sim -r 1 -c 2 wake_on_interrupt.elf
 */
#include <stdio.h>
#include "e_lib.h"

void interrupt_handler() __attribute__ ((interrupt));
void interrupt_handler() {
    printf("Core 0x808 woken by interrupt.\n");
    __asm__("trap 0x3");
    return;
}

unsigned const PRIORITY = E_USER_INT;  // E_SW_EXCEPTION

int main(void) {
    e_coreid_t coreid = e_get_coreid();

    if (coreid == 0x808) {
        e_irq_attach(PRIORITY, (sighandler_t)interrupt_handler);
        e_irq_mask(PRIORITY, E_FALSE);
        e_irq_global_mask(E_FALSE);
        __asm__("idle");
    }
    else if (coreid == 0x809) {
        unsigned *ilatst;
        unsigned i;
        for (i = 0; i < 10000; i++);
        ilatst = (unsigned *)e_get_global_address(32, 8, (void *)E_REG_ILATST);
        *ilatst |= 1 << PRIORITY;
        return 0;
    }

    return 0;
}
