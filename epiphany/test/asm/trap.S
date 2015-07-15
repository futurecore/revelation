#include "epiphany-macros.h"
.global _main
_main:
    trap 0 ; Halt processor to prepare for write
TEAR_DOWN
