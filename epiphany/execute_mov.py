from epiphany.condition_codes import should_branch


#-----------------------------------------------------------------------
# movcond32 and movcond16 - move on condition.
#-----------------------------------------------------------------------
def make_movcond_executor(is16bit):
    def execute_movcond(s, inst):
        """
        IF (Passed) <COND> then
            RD = RN
        """
        if is16bit:
            inst.bits &= 0xffff
        rd = inst.rd
        rn = inst.rn
        if should_branch(s, inst.cond):
            s.rf[rd] = s.rf[rn]
        s.pc += 2 if is16bit else 4
    return execute_movcond


#-----------------------------------------------------------------------
# movimm32, movtimm32 and movimm16 - move with immediate
#-----------------------------------------------------------------------
def make_movimm_executor(is16bit, is_t):
    def execute_movimm(s, inst):
        """
        RD=<imm>
        """
        if is16bit:
            inst.bits &= 0xffff
        imm = inst.imm16
        rd = inst.rd
        s.rf[rd] = (rd | (imm << 16)) if is_t else imm
        s.pc += 2 if is16bit else 4
    return execute_movimm


#-----------------------------------------------------------------------
# movts16, movts32, movfs16 and movfs32 - move
#-----------------------------------------------------------------------
def make_mov_executor(is16bit):
    def execute_mov(s, inst):
        """
        RD=RN
        """
        if is16bit:
            inst.bits &= 0xffff
        s.rf[inst.rd] = s.rf[inst.rn]
        s.pc += 2 if is16bit else 4
    return execute_mov
