#include <e-lib.h>
#include <stdio.h>

void timer_handler();
void __attribute__((interrupt)) timer_handler() {
    printf("CTIMER0 has expired.\n");
    return;
}

int main() {
    float a = 1., b = 2., c = 0.;
    int i = 0;

    /* Attach and set-up timer interrupt. */
    e_irq_attach(E_TIMER0_INT, timer_handler);
    e_irq_mask(E_TIMER0_INT, E_FALSE);
    e_irq_global_mask(E_FALSE);

    /* Set and start the timer. */
    e_ctimer_set(E_CTIMER_0, 10);
    e_ctimer_start(E_CTIMER_0, E_CTIMER_FPU_INST);

    for (i = 0; i < 15; i++) {
        c = a + b;
    }
    /* Interrupt should be triggered here. */

    return 0;
}
