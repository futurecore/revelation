from pydgin.utils import trim_32
from epiphany.utils import trim_5, signed

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
            result = signed(s.rf[inst.rn], True) >> trim_5(rm)
        elif name == "lsr":
            result = s.rf[inst.rn] >> trim_5(rm)
        elif name == "lsl":
            result = s.rf[inst.rn] << trim_5(rm)
        elif name == "bitr":
            # The description of this instruction is confused in the ISA
            # reference. The decode table states that the instruction always
            # takes an intermediate, but the description of the instruction
            # states that it does not.
            width = 8 if is16bit else 32  # TODO: Check register sizes.
            result_s = '{:0{width}b}'.format(s.rf[inst.rn], width=width)
            result = int(result_s[::-1], 2)
        s.rf[inst.rd] = trim_32(result)
        s.AN = (result >> 31) & 1
        s.AC = 0
        s.AV = 0
        s.AZ = trim_32(result) == 0
        s.pc += 2 if is16bit else 4
    return execute_bit
