#include <stdio.h>
#include "e_lib.h"

int main(void) {
    e_coreid_t coreid;
    unsigned row, col, i;

    coreid = e_get_coreid();
    e_coords_from_coreid(coreid, &row, &col);
    printf("Core id: %x row=%u col=%u\n", (unsigned)coreid, row, col);

    return 0;
}
