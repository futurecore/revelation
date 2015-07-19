Mistakes and ambiguities in v14.03.11 of the Epiphany Architecture Reference Manual
-----------------------------------------------------------------------------------

These notes are for anyone wishing to contribute to Revelation.
The `Epiphany Architecture Reference Manual <http://adapteva.com/docs/epiphany_arch_ref.pdf>`_ is the definitive reference for the architecture.
Revelation was originally based on v14.03.11 of this manual and v2015.1 of the eSDK.
This page documents a list of issues and potential misunderstandings with that version of the manual.


Issues with the decode table (pp 155)
=====================================

* In ``LD/STR(INDEX)(32)`` and ``RM`` should be ``RN``
* The ``BITR`` instruction has a 5-bit immediate integer, according to the decode table on page 155, but on page 81, the instruction only takes operands from registers.
* ``FLOAT``, ``FIX`` and ``FABS`` have some extra bits in the decode table for an ``RM`` operand, even though these instructions are unary
* In the last row of the decode table, the ``UNIMPL`` instruction is marked as 16 bit but cannot fit into 16 bits, this should be written as ``UNIMPL(32)``


Issues in Appendix A
=====================
* ``BCOND`` example on pp 80 ``add r1,r1#1    ; some operation`` should be ``add r1,r1,#1``
* In description of ``ADD`` and ``SUB`` (pp 76 and 108) flag ``OV`` should be ``AV``
* In description of ``JALR`` (pp 100) ``LR = PC;`` should be ``LR = PC + 2 (16 bit), PC + 4 (32 bit)`` -- i.e. the jump should save the address of the *next* instruction, to prevent infinite loops
* The DMA transfer example on pp 72 fails to compile with this error: ``dma_transfer.s:7: Error: unrecognised instruction `_1d_descr'``
* All ``ldrs`` and ``strs`` should be ``ldrh`` and ``strh``:
  * The ``LDR (POSTMODIFY)`` example on pp 103 fails to compile with the error ``ldrdpm.s:3: Error: unrecognised form of instruction 'ldrs r31,[r2],#1'``
  * The ``LDR (DISPLACEMENT-POSTMODIFY)`` example on pp 105 fails to compile with the error ``ldrpm.s:3: Error: unrecognised form of instruction 'ldrs r31,[r2],r1'``
  * The ``STR (POSTMODIFY)`` example on pp 121 fails to compile with the error ``str_pm.s:3: Error: unrecognised form of instruction 'strs r31,[r2],r1'``
  * The ``STR (DISPLACEMENT-POSTMODIFY)`` example on pp 122 fails to compile with the error ``str_dpm.s:3: Error: unrecognised form of instruction 'strs r31,[r2],#2'``
* In the ``SUB`` instruction on page 118, ``AC = BORROW`` should say ``AC = ~BORROW``.
* In the ``MOVTS`` and ``MOVFS`` operations, the code the compiler produces swaps ``rd`` and ``rn``, which is not mentioned in Appendix A. The code on page 81 says:

.. code-block:: asm

    MOV R0,%low(x87654321) ;
    MOV R0,%high(x87654321) ;
    BITR R0,R0 ; R0 gets 0x84C2A6B1


which does not compile, and isn't correct in any case. This should say:

.. code-block:: asm

    MOV R0,%low(0x87654321) ;
    MOVT R0,%high(0x87654321) ;
    BITR R0,R0 ; R0 gets 0x84C2A6E1


Ambiguities
===========
* In the ``SUB`` instruction on page 118, the carry flag, ``AC``, is not used in the subtraction. i.e. should the operation be: ``Rd = Rn - Rm - ~(AC)``? The same applies to ``ADD``.
* In the ``TRAP`` instruction on page 124, each system call will produce a return value and an error number, but the manual does not say whether these are saved in registers.
* In the ``RTI`` instruction on page 116, the **Operation** section says ``IPEND[i]=0; where i is the current interrupt level being serviced``, but it is not clear how the current interrupt level is set.


Typographical mistakes
=======================
* In Appendix A, pp 81 the ``BITR`` instruction does not have a section heading (or the heading has the wrong styling), so ``BITR`` does not appear in the Table of Contents.
* pp 109: Too many right parentheses in **Operation** section.


Would-be-nice-to-have improvements
==================================

* Instruction descriptions contain pseudo-code for each ISA instruction, but do not deal with incrementing ``COUNTER0`` and ``COUNTER1``. Ideally it would be nice for each instruction in Appendix A to state clearly whether and when counters are updated.
