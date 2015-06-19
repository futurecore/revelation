import epiphany.isa

#-----------------------------------------------------------------------
# jr32 and jr16 - jump.
#-----------------------------------------------------------------------
def make_jr_executor(is16bit):
    def execute_jr(s, inst):
        """
        PC = RN;
        """
        if is16bit:
            inst.bits &= 0xffff
        s.pc = s.rf[inst.rn]
    return execute_jr


#-----------------------------------------------------------------------
# jalr32 and jalr16 - register and link jump.
#-----------------------------------------------------------------------
def make_jalr_executor(is16bit):
    def execute_jalr(s, inst):
        """
        LR = PC;
        PC = RN;
        """
        if is16bit:
            inst.bits &= 0xffff
        s.rf[epiphany.isa.reg_map['LR']] = s.pc
        s.pc = s.rf[inst.rn]
    return execute_jalr
