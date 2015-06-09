.macro SET_UP

  # gcc needs this to create a valid elf
  .global main
  main:

.endm

.macro TEAR_DOWN

# Terminate the program by calling setting a breakpoint.

  bkpt

  # the pydgin elf loader needs this to find the breakpoint
#  .bss
#  xxx: .word 0

.endm
