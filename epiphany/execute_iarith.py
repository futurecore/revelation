from pydgin.utils import trim_32
from epiphany.utils import (borrow_from,
                            carry_from,
                            overflow_from_add,
                            overflow_from_sub,
                            reg_or_imm,
                            signed,
                            )

#-----------------------------------------------------------------------
# add32 and add16 -- with or without immediate.
#-----------------------------------------------------------------------
def make_add_executor(is16bit):
    def execute_add(s, inst):
        """
        Operation: RD = RN + <OP2>
        AN = RD[31]
        AC = CARRY OUT
        if ( RD[31:0] == 0 ) { AZ=1 } else { AZ=0 }
        if (( RD[31] & ~RM[31] & ~RN[31] ) | ( ~RD[31] & RM[31] & RN[31] ))
        { OV=1 }
        else { OV=0 }
        AVS = AVS | AV
        """
        if is16bit:
            inst.bits &= 0xffff
        result = signed(s.rf[inst.rn]) + reg_or_imm(s, inst, is16bit)
        s.rf[inst.rd] = trim_32(result)
        s.AN = bool((result >> 31) & 1)
        s.AZ = True if trim_32(result) == 0 else False
        s.AC = carry_from(result)
        s.AV = bool(overflow_from_add(s.rf[inst.rn], s.rf[inst.rm], result))
        s.AVS = s.AVS or s.AV
        s.pc += 2 if is16bit else 4
    return execute_add


#-----------------------------------------------------------------------
# sub32 and sub16 - with or without immediate.
#-----------------------------------------------------------------------
def make_sub_executor(is16bit):
    def execute_sub(s, inst):
        """
        RD = RN - <OP2>
        AN = RD[31]
        AC = BORROW
        if (RD[31:0]==0) { AZ=1 } else { AZ=0}
        if ((RD[31] & ~RM[31] & RN[31]) | (RD[31] & ~RM[31] & RN[31]) )
        { AV=1 }
        else { AV=0 }
        AVS = AVS | AV
        """
        if is16bit:
            inst.bits &= 0xffff
        result = signed(s.rf[inst.rn]) - reg_or_imm(s, inst, is16bit)
        s.rf[inst.rd] = trim_32(result)
        s.AN = bool((result >> 31) & 1)
        s.AC = not borrow_from(result)
        s.AZ = True if trim_32(result) == 0 else False
        s.AV = bool(overflow_from_sub(s.rf[inst.rn], s.rf[inst.rm], result))
        s.AVS = s.AVS or s.AV
        s.pc += 2 if is16bit else 4
    return execute_sub
