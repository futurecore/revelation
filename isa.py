# arm-specific utils
from pydgin.utils import (
    trim_32,
#  shifter_operand,
#  condition_passed,
#  not_borrow_from,
#  sext_30,
#  addressing_mode_2,
#  addressing_mode_3,
#  addressing_mode_4,
)

from arm.utils import (
    borrow_from,
    carry_from,
    overflow_from_add,
    overflow_from_sub,
)

from pydgin.misc import create_risc_decoder


#=======================================================================
# Instruction Encodings
#=======================================================================
encodings = [
    ['nop16',    'xxxxxxxxxxxxxxxxxxxxxx0110100010'],
    #---------------------------------------------------------------------
    # Arithmetic
    #---------------------------------------------------------------------
    ['add32', 'xxxxxxxxxxxx1010xxxxxxxxx0011111'],
    ['add32', 'xxxxxxxxxxxxxxxxxxxxxxxxx0011011'], # with immediate
    ['sub32', 'xxxxxxxxxxxx1010xxxxxxxxx0111111'],
    ['sub32', 'xxxxxxxxxxxxxxxxxxxxxxxxx0111011'], # with immediate
]


def reg_or_imm(s, inst):
    if inst.b2 == 1:
        return s.rf[inst.rm]
    else:
        return inst.imm


#-----------------------------------------------------------------------
# nop16
#-----------------------------------------------------------------------
def execute_nop16(s, inst):
    s.pc += 2
    return


#-----------------------------------------------------------------------
# add32 - with or without immediate.
#-----------------------------------------------------------------------
def execute_add32(s, inst):
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
    result = s.rf[inst.rn] + reg_or_imm(s, inst)
    s.rf[inst.rd] = trim_32(result)
    s.AN = (result >> 31) & 1
    s.AZ = trim_32(result) == 0
    s.AC = carry_from(result)
    s.AV = overflow_from_add(s.rf[inst.rn], s.rf[inst.rm], result)
    s.AVS = s.AVS | s.AV
    s.pc += 4


#-----------------------------------------------------------------------
# sub32 - with or without immediate.
#-----------------------------------------------------------------------
def execute_sub32(s, inst):
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
    result = s.rf[inst.rn] - reg_or_imm(s, inst)
    s.rf[inst.rd] = trim_32(result)
    s.AN = (result >> 31) & 1
    s.AC = borrow_from(result)
    s.AZ = trim_32(result) == 0b0
    s.AV = overflow_from_sub(s.rf[inst.rn], s.rf[inst.rm], result)
    s.AVS = s.AVS | s.AV
    s.pc += 4


#=======================================================================
# Create Decoder
#=======================================================================
decode = create_risc_decoder(encodings, globals(), debug=True)
