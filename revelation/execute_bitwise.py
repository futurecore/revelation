from revelation.utils import (borrow_from,
                              carry_from,
                              overflow_from_add,
                              overflow_from_sub,
                              reg_or_simm,
                              signed,
                              trim_32)

#-----------------------------------------------------------------------
# add32 and add16 -- with or without immediate.
# sub32 and sub16 - with or without immediate.
#-----------------------------------------------------------------------
def make_addsub_executor(is16bit, name):
    def execute_arith(s, inst):
        """
        Operation: RD = RN <OP> <OP2>
        AN = RD[31]
        AC = CARRY OUT (ADD) ~BORROW (SUB)
        if ( RD[31:0] == 0 ) { AZ=1 } else { AZ=0 }
        if (( RD[31] & ~RM[31] & ~RN[31] ) | ( ~RD[31] & RM[31] & RN[31] ))
        { AV=1 }
        else { AV=0 }
        AVS = AVS | AV
        """
        if is16bit:
            inst.bits &= 0xffff
        rn = s.rf[inst.rn]
        op2 = reg_or_simm(s, inst, is16bit)
        result = rn + op2 if name == 'add' else rn - op2
        s.rf[inst.rd] = trim_32(result)
        if name == 'add':
            s.AC = carry_from(result)
            s.AV = bool(overflow_from_add(rn, op2, result))
        else:
            s.AC = not borrow_from(result)
            s.AV = bool(overflow_from_sub(rn, op2, result))
        s.AN = bool((result >> 31) & 1)
        s.AZ = True if trim_32(result) == 0 else False
        s.AVS = s.AVS or s.AV
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return execute_arith


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
        rn = s.rf[inst.rn]
        if name == "and":
            result = rn & rm
        elif name == "orr":
            result = rn | rm
        elif name == "eor":
            result = rn ^ rm
        elif name == "asr":
            result = signed(rn) >> (rm & 0x1f)
        elif name == "lsr":
            result = rn >> (rm & 0x1f)
        elif name == "lsl":
            result = rn << (rm & 0x1f)
        elif name == "bitr":
            # The description of this instruction is confused in the ISA
            # reference. The decode table states that the instruction always
            # takes an intermediate, but the description of the instruction
            # states that it does not.
            result = 0
            for i in range(32):
                if (rn & (1 << i)):
                    result |= (1 << (32 - 1 - i))
        s.rf[inst.rd] = trim_32(result)
        s.AN = bool((result >> 31) & 1)
        s.AC = False
        s.AV = False
        s.AZ = True if trim_32(result) == 0 else False
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return execute_bit
