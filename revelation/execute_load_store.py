from revelation.utils import trim_32


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
        if size == 8:  # 64 bit store.
            s.mem.write(s.rf[inst.rn],     4, s.rf[inst.rd], from_core=s.coreid)
            s.mem.write(s.rf[inst.rn] + 4, 4, s.rf[inst.rd + 1], from_core=s.coreid)
        else:
            s.mem.write(s.rf[inst.rn], size, s.rf[inst.rd], from_core=s.coreid)
    else:          # LOAD
        if size == 8:  # 64 bit load.
            value = s.mem.read(s.rf[inst.rn], size, from_core=s.coreid)
            s.rf[inst.rd + 1] = (value >> 32) & 0xffffffff
            s.rf[inst.rd] = (value & 0xffffffff)
        else:
            s.rf[inst.rd] = s.mem.read(s.rf[inst.rn], size, from_core=s.coreid)
    s.rf[inst.rn] = trim_32(new_rn)
    s.pc += 4


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
            if size == 8:  # 64 bit store.
                s.mem.write(address,     4, s.rf[inst.rd], from_core=s.coreid)
                s.mem.write(address + 4, 4, s.rf[inst.rd + 1], from_core=s.coreid)
            else:
                s.mem.write(address, size, s.rf[inst.rd], from_core=s.coreid)
        else:       # LOAD
            if size == 8:  # 64 bit load.
                value = s.mem.read(address, size, from_core=s.coreid)
                s.rf[inst.rd + 1] = (value >> 32) & 0xffffffff
                s.rf[inst.rd] = (value & 0xffffffff)
            else:
                s.rf[inst.rd] = s.mem.read(address, size, from_core=s.coreid)
        s.pc += 2 if is16bit else 4
    return ldstrdisp


def make_ldstrind_executor(is16bit):
    def ldstrind(s, inst):
        """
        EITHER:
            address = RN +/- RM ;    (LDR)
            RD = memory[address];
            For double data loads, only even RD registers can be used.
        OR:
            address = RN +/- RM ;    (STR)
            memory[address] = RD;
        """
        if is16bit:
            inst.bits &= 0xffff
        address = (s.rf[inst.rn] - s.rf[inst.rm] if inst.sub20
                   else s.rf[inst.rn] + s.rf[inst.rm])
        size = {0:1, 1:2, 2:4, 3:8}[inst.size]  # Size in bytes.
        if inst.s:  # STORE
            if size == 8:  # 64 bit store.
                s.mem.write(address,     4, s.rf[inst.rd], from_core=s.coreid)
                s.mem.write(address + 4, 4, s.rf[inst.rd + 1], from_core=s.coreid)
            else:
                s.mem.write(address, size, s.rf[inst.rd], from_core=s.coreid)
        else:       # LOAD
            if size == 8:  # 64 bit load.
                value = s.mem.read(address, size, from_core=s.coreid)
                s.rf[inst.rd + 1] = (value >> 32) & 0xffffffff
                s.rf[inst.rd] = (value & 0xffffffff)
            else:
                s.rf[inst.rd] = s.mem.read(address, size, from_core=s.coreid)
        s.pc += 2 if is16bit else 4
    return ldstrind


def make_ldstrpm_executor(is16bit):
    def ldstrpm(s, inst):
        """
        EITHER:
            address = RN +/- RM ;    (LDR)
            RD = memory[address];
            For double data loads, only even RD registers can be used.
            RN = RN +/- RM;
        OR:
            address = RN +/- RM ;    (STR)
            memory[address] = RD;
            RN = RN +/- RM;
        """
        if is16bit:
            inst.bits &= 0xffff
        address = s.rf[inst.rn]
        index = s.rf[inst.rm]
        size = {0:1, 1:2, 2:4, 3:8}[inst.size]  # Size in bytes.
        if inst.s:  # STORE
            if size == 8:  # 64 bit store.
                s.mem.write(address,     4, s.rf[inst.rd], from_core=s.coreid)
                s.mem.write(address + 4, 4, s.rf[inst.rd + 1], from_core=s.coreid)
            else:
                s.mem.write(address, size, s.rf[inst.rd], from_core=s.coreid)
        else:       # LOAD
            if size == 8:  # 64 bit load.
                value = s.mem.read(address, size, from_core=s.coreid)
                s.rf[inst.rd + 1] = (value >> 32) & 0xffffffff
                s.rf[inst.rd] = (value & 0xffffffff)
            else:
                s.rf[inst.rd] = s.mem.read(address, size, from_core=s.coreid)
        postmodify = address - index if inst.sub20 else address + index
        s.rf[inst.rn] = trim_32(postmodify)
        s.pc += 2 if is16bit else 4
    return ldstrpm


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
    value = s.mem.read(address, size, from_core=s.coreid)
    if value:
        s.rf[inst.rd] = value
    else:
        s.mem.write(address, size, s.rf[inst.rd], from_core=s.coreid)
        s.rf[inst.rd] = 0
    s.pc += 4
