from pydgin.utils import trim_32
from epiphany.utils import (borrow_from,
                            carry_from,
                            overflow_from_add,
                            overflow_from_sub,
                            reg_or_simm,
                            )

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
        op2 = reg_or_simm(s, inst, is16bit)
        result = (s.rf[inst.rn] + op2 if name == 'add'
                  else s.rf[inst.rn] - op2)
        s.rf[inst.rd] = trim_32(result)
        if name == 'add':
            s.AC = carry_from(result)
            s.AV = bool(overflow_from_add(s.rf[inst.rn], op2, result))
        else:
            s.AC = not borrow_from(result)
            s.AV = bool(overflow_from_sub(s.rf[inst.rn], op2, result))
        s.AN = bool((result >> 31) & 1)
        s.AZ = True if trim_32(result) == 0 else False
        s.AVS = s.AVS or s.AV
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return execute_arith
