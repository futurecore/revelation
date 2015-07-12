from pydgin.utils import trim_32

#-----------------------------------------------------------------------
# ldstrpmd32 - load-store post-modify with displacement.
#-----------------------------------------------------------------------
def execute_ldstrpmd32(s, inst):
    """
    address = RN;
    EITHER:
        RD = memory[address]; (LDR)
    OR:
        memory[address] = RD; (STR)
    RN = RN +/- IMM11 << (log2(size_in_bits/8));
    """
    new_rn = (s.rf[inst.rn] - (inst.imm11 << inst.size) if inst.sub
              else s.rf[inst.rn] + (inst.imm11 << inst.size))
    size = {0:1, 1:2, 2:4, 3:8}[inst.size]  # Size in bytes.
    if inst.s:     # STORE
        s.mem.write(s.rf[inst.rn], size, s.rf[inst.rd])
    else:          # LOAD
        s.rf[inst.rd] = s.mem.read(s.rf[inst.rn], size)
    s.rf[inst.rn] = trim_32(new_rn)
    s.pc += 4


#-----------------------------------------------------------------------
# ldstrdisp16 and ldstrdisp32 - load or store with displacement.
#-----------------------------------------------------------------------
def make_ldstrdisp_executor(is16bit):
    def ldstrdisp(s, inst):
        """
        EITHER:
            address = RN +/- (IMM << (log2(size_in_bits/8))); (LDR)
            RD = memory[address];
        OR:
            address = RN +/- (IMM << (log2(size_in_bits/8))); (STR)
            memory[address] = RD;
        """
        if is16bit:
            inst.bits &= 0xffff
        size = {0:1, 1:2, 2:4, 3:8}[inst.size]  # Size in bytes.
        offset = (inst.imm3 << inst.size) if is16bit else (inst.imm11 << inst.size)
        address = (s.rf[inst.rn] - offset if inst.sub else s.rf[inst.rn] + offset)
        if inst.s:  # STORE
            s.mem.write(address, size, s.rf[inst.rd])
        else:       # LOAD
            s.rf[inst.rd] = trim_32(s.mem.read(address, size))
        s.pc += 2 if is16bit else 4
    return ldstrdisp


#-----------------------------------------------------------------------
# ldstrin16 and ldstrin32 - load or store with index.
# ldstrpm16 and ldstrpm32 - load or store post-modify.
#-----------------------------------------------------------------------
def make_ldstrindpm_executor(is16bit, postmodify):
    def ldstr(s, inst):
        """
        EITHER:
            address = RN +/- RM ;    (LDR)
            RD = memory[address];
            For double data loads, only even RD registers can be used.
            RN = RN +/- RM;          (with postmodify)
        OR:
            address = RN +/- RM ;    (STR)
            memory[address] = RD;
            RN = RN +/- RM;          (with postmodify)
        """
        if is16bit:
            inst.bits &= 0xffff
        address = (s.rf[inst.rn] - s.rf[inst.rm] if inst.sub20
                   else s.rf[inst.rn] + s.rf[inst.rm])
        size = {0:1, 1:2, 2:4, 3:8}[inst.size]  # Size in bytes.
        if inst.s:  # STORE
            s.mem.write(address, size, s.rf[inst.rd])
        else:       # LOAD
            s.rf[inst.rd] = trim_32(s.mem.read(address, size))
        if postmodify:
            s.rf[inst.rn] = trim_32(address)
        s.pc += 2 if is16bit else 4
    return ldstr


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
    address = (s.rf[inst.rn] - s.rf[inst.rm] if inst.sub20
               else s.rf[inst.rn] + s.rf[inst.rm])
    if address <= 0x00100000:
        fail_msg = """testset32 has failed to write to address %s.
The absolute address used for the test and set instruction must be located
within the on-chip local memory and must be greater than 0x00100000 (2^20).
""" % str(hex(address))
        raise ValueError(fail_msg)
    size = {0:1, 1:2, 2:4, 3:8}[inst.size]  # Size in bytes.
    value = s.mem.read(address, size)
    if value:
        s.rf[inst.rd] = value
    else:
        s.mem.write(address, size, s.rf[inst.rd])
        s.rf[inst.rd] = 0
    s.pc += 4
