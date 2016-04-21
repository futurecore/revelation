from epiphany.utils import signed, trim_32

#-----------------------------------------------------------------------
# bit1632 - 16 or 32 bit bitwise arithmetic.
#-----------------------------------------------------------------------
def make_bit_executor(name, is16bit, imm):
    def execute_bit(s, inst):
        """RD = RN <OP> RM
        AN = RD[31]
        AV = 0
        AC = 0
        If ( RD[31:0] == 0 ) { AZ=1 } else { AZ=0 }
        """
        if is16bit:
            inst.bits &= 0xffff
        rm = inst.imm5 if imm else s.rf[inst.rm]
        if name == "and":
            result = s.rf[inst.rn] & rm
        elif name == "orr":
            result = s.rf[inst.rn] | rm
        elif name == "eor":
            result = s.rf[inst.rn] ^ rm
        elif name == "asr":
            result = signed(s.rf[inst.rn]) >> rm
        elif name == "lsr":
            result = s.rf[inst.rn] >> rm
        elif name == "lsl":
            result = s.rf[inst.rn] << rm
        elif name == "bitr":
            # The description of this instruction is confused in the ISA
            # reference. The decode table states that the instruction always
            # takes an intermediate, but the description of the instruction
            # states that it does not.
            result = 0
            for i in range(32):
                if (s.rf[inst.rn] & (1 << i)):
                    result |= (1 << (32 - 1 - i))
        s.rf[inst.rd] = trim_32(result)
        s.AN = bool((result >> 31) & 1)
        s.AC = False
        s.AV = False
        s.AZ = True if trim_32(result) == 0 else False
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return execute_bit
