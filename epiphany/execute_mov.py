from epiphany.condition_codes import condition_passed


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
            inst.bits &= 0xFFFF
        rd = inst.rd
        rn = inst.rn
        if condition_passed(s, inst.cond):
            s.rf[rd] = s.rf[rn]
        s.debug_flags()
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
            inst.bits &= 0xFFFF
        s.rf[inst.rd] = (s.rf[inst.rd] | (inst.imm16 << 16)) if is_t else inst.imm16
        s.pc += 2 if is16bit else 4
    return execute_movimm


#-----------------------------------------------------------------------
# movts16, movts32, movfs16 and movfs32 - move
#-----------------------------------------------------------------------
def make_mov_executor(is16bit, rd_is_special=False, rn_is_special=False):
    # Note that in the MOV 'special' instructions rd and rn are swapped.

    # It says that Rd starts at offset 13. Since this instruction is written as
    # MOVTS <mmr>, <gpr> one might think that Rd is the MMR. This is not the
    # case - the Rd field is the GPR while the Rn field is the MMR. The reason
    # for this encoding is fairly clear: It's how MOVFS is encoded. Still, I
    # think the decode table should be changed to swap the two fields around so
    # it's clear what actually goes where.

    def execute_mov(s, inst):
        """
        RD=RN
        """
        if is16bit:
            inst.bits &= 0xFFFF
        if rd_is_special:
            rd_address = 0xF0400 + (0x4 * inst.rn)
            rn = s.rf[inst.rd]
            s.rf.set_register_by_address(rd_address, rn)
        elif rn_is_special:
            rn_address = 0xF0400 + (0x4 * inst.rn)
            rd = inst.rd
            value = s.rf.get_register_by_address(rn_address)
            s.rf[rd] = value
        s.pc += 2 if is16bit else 4
    return execute_mov
