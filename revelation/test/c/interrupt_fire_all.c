/*
Based on: e_interrupt_test.c Copyright as below.
Copyright (C) 2012 Adapteva, Inc.
Contributed by Wenlin Song <wsong@wpi.edu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program, see the file COPYING. If not, see
<http://www.gnu.org/licenses/>.
*/
#include <stdio.h>
#include "e_lib.h"

void handler() __attribute__ ((interrupt)) __attribute__ ((aligned(8)));
void __attribute__((interrupt)) handler() {
    printf(" ... handler fired.\n");
    return;
}

int main(void) {
    e_coreid_t coreid;
    unsigned row, col, i;
    unsigned irq_priority[8] = { E_SW_EXCEPTION, E_MEM_FAULT, E_TIMER0_INT,
                                 E_TIMER1_INT, E_MESSAGE_INT, E_DMA0_INT,
                                 E_DMA1_INT, E_USER_INT };
    char* irq_name[8] = { "E_SW_EXCEPTION", "E_MEM_FAULT   ", "E_TIMER0_INT  ",
                          "E_TIMER1_INT  ", "E_MESSAGE_INT ", "E_DMA0_INT    ",
                          "E_DMA1_INT    ", "E_USER_INT    " };

    coreid = e_get_coreid();
    e_coords_from_coreid(coreid, &row, &col);

    for (i = 0; i < 8; i++) {
        printf("Interrupt %s", irq_name[i]);
        e_irq_attach(irq_priority[i], (sighandler_t)handler);
        e_irq_mask(irq_priority[i], E_FALSE);
        e_irq_global_mask(E_FALSE);
        e_irq_set(row, col, irq_priority[i]);
        e_irq_mask(irq_priority[i], E_TRUE);
        e_irq_global_mask(E_TRUE);
    }

    return 0;
}
