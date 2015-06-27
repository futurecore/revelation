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


#-----------------------------------------------------------------------
# ldstrin16 and ldstrin32 - load or store with index.
#-----------------------------------------------------------------------
def make_ldstrind_executor(is16bit):
    def ldstrind(s, inst):
        raise NotImplementedError
    return ldstrind


#-----------------------------------------------------------------------
# ldstrpm16 and ldstrpm32 - load or store post-modify.
#-----------------------------------------------------------------------
def make_ldstrpm_executor(is16bit):
    def ldstrind(s, inst):
        raise NotImplementedError
    return ldstrind


#-----------------------------------------------------------------------
# testset32
#-----------------------------------------------------------------------
def testset32(s, inst):
    """From the Epiphany Architecture Reference Manual (c) Adapteva Inc:

    The TESTSET instruction does an atomic "test-if-not-zero", then
    conditionally writes on any memory location within the Epiphany
    architecture. The absolute address used for the test and set instruction
    must be located within the on-chip local memory and must be greater than
    0x00100000 (2^20).

    The instruction tests the value of a specific memory location
    and if that value is zero, writes in a new value from the local register
    file. If the value at the memory location was already set to a non-zero
    value, then the value is returned to the register file, but the memory
    location is left unmodified.

    if ([RN+/-RM]) {
        RD = ([RN+/-RM]);
    }
    else{
        ([RN+/-RM]) = RD
        RD = 0;
    }
    """
    address = (s.rf[inst.rn] + s.rf[inst.rm] if inst.sub == 0
               else s.rf[inst.rn] - s.rf[inst.rm])
    if address <= 0x00100000:
        fail_msg = """testset32 has failed to write to address %s.
The absolute address used for the test and set instruction must be located
within the on-chip local memory and must be greater than 0x00100000 (2^20).
""" % str(hex(address))
        raise ValueError(fail_msg)
    size = {0:1, 2:4, 3:8, 4:16}[inst.size]  # Size in bytes.
    value = s.mem.read(address, size)
    if value == 0:
        s.mem.write(address, size, s.rf[inst.rd])
        s.rf[inst.rd] = 0
    else:
        s.rf[inst.rd] = value
    s.pc += 4
