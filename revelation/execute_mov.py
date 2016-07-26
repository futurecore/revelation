from revelation.condition_codes import condition_passed
from revelation.utils import get_mmr_address


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


def make_movimm_executor(is16bit, is_t):
    def execute_movimm(s, inst):
        """
        RD=<imm>
        """
        if is16bit:
            inst.bits &= 0xffff
        if is_t:
            s.rf[inst.rd] = ((s.rf[inst.rd] & 0xffff) | (inst.imm16 << 16))
        else:
            s.rf[inst.rd] = inst.imm16
        s.pc += 2 if is16bit else 4
    return execute_movimm


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
            rd_address, _ = get_mmr_address(inst.rn, inst.mmr)
            rn = s.rf[inst.rd]
            s.mem.write(rd_address, 4, rn, from_core=s.coreid)
        elif rn_is_special:
            rn_address, _ = get_mmr_address(inst.rn, inst.mmr)
            value = s.mem.read(rn_address, 4, from_core=s.coreid)
            s.rf[inst.rd] = value
        s.pc += 2 if is16bit else 4
    return execute_mov
