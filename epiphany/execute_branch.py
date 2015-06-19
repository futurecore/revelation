from epiphany.condition_codes import should_branch

#-----------------------------------------------------------------------
# bcond16 and bcond32 - branch on condition.
#-----------------------------------------------------------------------
def make_bcond_executor(is16bit):
    def execute_bcond(s, inst):
        if is16bit:
            inst.bits &= 0xffff
        cond = inst.cond
        imm = inst.bcond_imm
        if should_branch(s, cond):
            s.pc += imm << 1
        else:
            s.pc += 2 if is16bit else 4
    return execute_bcond
