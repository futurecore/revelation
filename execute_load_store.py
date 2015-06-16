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
    size_in_bits = inst.size
    if inst.s:     # STORE
        s.mem.write(address, 0b1 << size_in_bits, s.rf[inst.rd])
    else:          # LOAD
        s.rf[inst.rd] = s.mem.read(address, 0b1 << size_in_bits)
    imm = inst.imm11
    if inst.sub:  # Subtract
        s.rf[inst.rn] = address - (imm << size_in_bits)
    else:
        s.rf[inst.rn] = address + (imm << size_in_bits)
