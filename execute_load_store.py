#-----------------------------------------------------------------------
# ldstrpmd32 - load-store post-modify with displacement.
#-----------------------------------------------------------------------
def execute_ldstrpmd32(s, inst):
    """
    address=RN;
    EITHER:
        RD=memory[address]; (LD)
    OR:
        memory[address]=RD; (STR)
    RN=RN +/- IMM11 << (log2(size_in_bits/8));
    """
    address = s.rf[inst.rn]
    if inst.s:     # STORE
        s.mem.write(address, 0b1 << inst.size, s.rf[inst.rd])
    else:          # LOAD
        s.rf[inst.rd] = s.mem.read(address, 0b1 << inst.size)
    imm = inst.imm11
    if inst.sub:  # Subtract
        s.rf[inst.rn] = address - (imm << inst.size)
    else:
        s.rf[inst.rn] = address + (imm << inst.size)


#-----------------------------------------------------------------------
# ldstrdisp16 and ldstrdisp32 - load or store with displacement.
#-----------------------------------------------------------------------
def make_ldstrdisp_executor(is16bit):
    def ldstrdisp(s, inst):
        """
        EITHER:
            address= RN +/- IMM << (log2(size_in_bits/8)) ; (LD)
            RD=memory[address];
        OR:
            address = RN +/- IMM << (log2(size_in_bits/8)); (STR)
            memory[address] = RD;
        """
        if is16bit:
            inst.bits &= 0xffff
        address = s.rf[inst.rn]
        if inst.s:  # STORE
            s.mem.write(address, 0b1 << inst.size, s.rf[inst.rd])
        else:       # LOAD
            s.rf[inst.rd] = s.mem.read(address, 0b1 << inst.size)
        if inst.sub:  # Subtract
            s.rf[inst.rn] = address - (inst.imm11 << inst.size)
        else:
            s.rf[inst.rn] = address + (inst.imm11 << inst.size)
    return ldstrdisp
