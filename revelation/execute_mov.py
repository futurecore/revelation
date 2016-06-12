from revelation.condition_codes import condition_passed


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
            inst.bits &= 0xffff
        s.rf[inst.rd] = (s.rf[inst.rd] | (inst.imm16 << 16)) if is_t else inst.imm16
        s.pc += 2 if is16bit else 4
    return execute_movimm


#-----------------------------------------------------------------------
# movts16, movts32, movfs16 and movfs32 - move
#-----------------------------------------------------------------------
def make_mov_executor(is16bit, rd_is_special=False, rn_is_special=False):
    # Note that in the MOV 'special' instructions rd and rn are swapped.
    #
    # https://www.parallella.org/forums/viewtopic.php?t=938&p=6027 "It says that
    # Rd starts at offset 13. Since this instruction is written as MOVTS <mmr>,
    # <gpr> one might think that Rd is the MMR. This is not the case - the Rd
    # field is the GPR while the Rn field is the MMR. The reason for this
    # encoding is fairly clear: It's how MOVFS is encoded. Still, I think the
    # decode table should be changed to swap the two fields around so it's clear
    # what actually goes where."
    #
    # ILATST is an alias for the ILAT register that allows bits within the ILAT
    # register to be set individually. Writing a "1" to an individual bit of the
    # ILATST register will set the corresponding ILAT bit to "1". Writing a "0"
    # to an individual bit will have no effect on the ILAT register. The ILATST
    # alias cannot be read.
    #
    # ILATCL is an alias for the ILAT register that allows bits within the ILAT
    # register to be cleared individually. Writing a "1" to an individual bit of
    # the ILATCL register will clear the corresponding ILAT bit to "0". Writing
    # a "0" to an individual bit will have no effect on the ILAT register. The
    # ILATST alias cannot be read.
    #
    def execute_mov(s, inst):
        """
        RD=RN
        """
        if is16bit:
            inst.bits &= 0xffff
        if rd_is_special:
            rd_address = 0xf0400 + (0x4 * inst.rn)
            rn = s.rf[inst.rd]
            if rd_address == 0xf042c:  # ILATST
                value = s.mem.read(rd_address, 4)
                value |= rn
                s.mem.write(rd_address, 4, value)  # Set ILATST.
                ilat = s.mem.read(0xf0428, 4)  # ILAT
                ilat |= rn
                s.mem.write(0xf0428, 4, ilat)
            elif rd_address == rd_address == 0xf0430:  # ILATCL
                value = s.mem.read(rd_address, 4)
                value |= rn
                s.mem.write(rd_address, 4, value)  # Set ILATCL.
                ilat = s.mem.read(0xf0428, 4)  # ILAT
                ilat &= ~rn
                s.mem.write(0xf0428, 4, ilat)
            else:
                s.mem.write(rd_address, 4, rn)
        elif rn_is_special:
            rn_address = 0xf0400 + (0x4 * inst.rn)
            rd = inst.rd
            value = s.mem.read(rn_address, 4)
            s.rf[rd] = value
        s.pc += 2 if is16bit else 4
    return execute_mov
