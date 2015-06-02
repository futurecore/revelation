# arm-specific utils
from pydgin.utils import (
    trim_32,
#  shifter_operand,
#  condition_passed,
#  borrow_from,
#  not_borrow_from,
#  overflow_from_sub,
#  sext_30,
#  addressing_mode_2,
#  addressing_mode_3,
#  addressing_mode_4,
)

from arm.utils import (
    carry_from,
    overflow_from_add,
)

from pydgin.misc import create_risc_decoder


#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [
    ['nop',    'xxxxxxxxxxxxxxxxxxxxxx0110100010'],
    #---------------------------------------------------------------------
    # Arithmetic
    #---------------------------------------------------------------------
    ['add32', 'xxxxxxxxxxxx1010xxxxxxxxx0011111'],
    ['add32', 'xxxxxxxxxxxxxxxxxxxxxxxxx0011011'], # with immediate
]


def reg_or_imm(s, inst):
    if inst.b2 == 1:
        return s.rf[inst.rm]
    else:
        return inst.imm


#-----------------------------------------------------------------------
# nop
#-----------------------------------------------------------------------
def execute_nop(s, inst):
    s.pc += 2
    return


#-----------------------------------------------------------------------
# add32
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
    s.pc += 4
    s.AN = (result >> 31) & 1
    s.AZ = trim_32(result) == 0
    s.AC = carry_from( result )
    s.OV = overflow_from_add(s.rf[inst.rn], s.rf[inst.rm], result)
    s.AVS = s.AVS | s.AV



#=======================================================================
# Create Decoder
#=======================================================================

decode = create_risc_decoder(encodings, globals(), debug=True)
