from epiphany.condition_codes import should_branch
from epiphany.utils import signed_8, signed_24, sext_8, sext_24

import epiphany.isa

#-----------------------------------------------------------------------
# bcond16 and bcond32 - branch on condition.
#-----------------------------------------------------------------------
def make_bcond_executor(is16bit):
    def execute_bcond(s, inst):
        """
        B<COND>:
            IF (Passed)<COND>)) then
            PC = PC + (SignExtend(SIMM) << 1)
        BL:
            LR = next PC;
            PC = PC + (SignExtend(SIMM) << 1)
        """
        if is16bit:
            inst.bits &= 0xffff
        cond = inst.cond
        imm = inst.bcond_imm
        if cond == 0b1111:  # Branch and link (BL).
            s.rf[epiphany.isa.reg_map['LR']] = s.pc + 2 if is16bit else s.pc + 4
        if should_branch(s, cond):
            s.pc += (sext_8(signed_8(imm)) << 1) if is16bit else (sext_24(signed_24(imm)) << 1)
        else:
            s.pc += 2 if is16bit else 4
    return execute_bcond
