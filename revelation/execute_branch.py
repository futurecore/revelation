from revelation.condition_codes import condition_passed
from revelation.utils import signed, sext_8, sext_24, trim_32

import revelation.isa

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
        if cond == 0 and imm == 0:
            raise RuntimeError(('Revelation simulator caught infinite loop at runtime. ' +
                                'Instruction at pc=%s is attempting to ' +
                                'branch unconditionally to itself.') % hex(s.pc))
        if cond == 0b1111:  # Branch and link (BL).
            s.rf[revelation.isa.reg_map['LR']] = s.pc + (2 if is16bit else 4)
        if condition_passed(s, cond):
            offset = (signed(sext_8(imm)) << 1) if is16bit else (signed(sext_24(imm)) << 1)
            s.pc = trim_32(s.pc + offset)
        else:
            s.pc += 2 if is16bit else 4
        s.debug_flags()
    return execute_bcond
