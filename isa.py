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
    ['nop16',       'xxxxxxxxxxxxxxxxxxxxxx0110100010'],
    #---------------------------------------------------------------------
    # Arithmetic
    #---------------------------------------------------------------------
    ['add32',       'xxxxxxxxxxxx1010xxxxxxxxx0011111'],
    ['add32',       'xxxxxxxxxxxxxxxxxxxxxxxxx0011011'],  # with immediate.
    ['sub32',       'xxxxxxxxxxxx1010xxxxxxxxx0111111'],
    ['sub32',       'xxxxxxxxxxxxxxxxxxxxxxxxx0111011'],  # with immediate.
    #---------------------------------------------------------------------
    # Bitwise arithmetic
    #---------------------------------------------------------------------
    ['and32',       'xxxxxxxxxxxx1010xxxxxxxxx1011111'],  # AND32
    ['and16',       'xxxxxxxxxxxxxxxxxxxxxxxxx1011010'],  # AND16
    ['orr32',       'xxxxxxxxxxxx1010xxxxxxxxx1111111'],  # ORR32
    ['orr16',       'xxxxxxxxxxxxxxxxxxxxxxxxx1111010'],  # ORR16
    ['eor32',       'xxxxxxxxxxxx1010xxxxxxxxx0001111'],  # EOR32
    ['eor16',       'xxxxxxxxxxxxxxxxxxxxxxxxx0001010'],  # EOR16
    ['asr32',       'xxxxxxxxxxxx1010xxxxxxxxx1101111'],  # ASR32
    ['asr16',       'xxxxxxxxxxxxxxxxxxxxxxxxx1101010'],  # ASR16
    ['lsr32',       'xxxxxxxxxxxx1010xxxxxxxxx1001111'],  # LSR32
    ['lsr16',       'xxxxxxxxxxxxxxxxxxxxxxxxx1001010'],  # LSR16
    ['lsl32',       'xxxxxxxxxxxx1010xxxxxxxxx0101111'],  # LSL32
    ['lsl16',       'xxxxxxxxxxxxxxxxxxxxxxxxx0101010'],  # LSL16
    #--------------------------------------------------------------------
    # Loads and stores
    #---------------------------------------------------------------------
    ['ldstrpmd32',  'xxxxxx1xxxxxxxxxxxxxxxxxxxxx1100'],  # LD or STR combined.
    #---------------------------------------------------------------------
    # Jumps and branch conditions
    #---------------------------------------------------------------------
    ['bcond32',     'xxxxxxxxxxxxxxxxxxxxxxxxxxxx1000'],
    ['jr32',        'xxxxxxxxxxxx0010xxxxxx0101001111'],
    #---------------------------------------------------------------------
    # Move
    #---------------------------------------------------------------------
    ['movcond32',   'xxxxxxxxxxxx0010xxxxxx00xxxx1111'],
]


def reg_or_imm(s, inst):
    if inst.bit2 == 1:
        return s.rf[inst.rm]
    else:
        return inst.imm


def trim_5(value):
    return value & 0b11111


def signed(value, is16bit):
  if is16bit and (value & 0x8000) or not is16bit and (value & 0x80000000):
    twos_complement = ~value + 1
    return -trim_32( twos_complement )
  return value


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


#-----------------------------------------------------------------------
# bit1632 - 16 or 32 bit bitwise arithmetic.
#-----------------------------------------------------------------------
def make_bit_executor(name, is16bit):
    def execute_bit(s, inst):
        """RD = RN <OP> RM
        AN = RD[31]
        AV = 0
        AC = 0
        If ( RD[31:0] == 0 ) { AZ=1 } else { AZ=0 }
        """
        if is16bit:
            inst.bits &= 0xffff
        if name == "and":
            result = s.rf[inst.rn] & s.rf[inst.rm]
        elif name == "orr":
            result = s.rf[inst.rn] | s.rf[inst.rm]
        elif name == "eor":
            result = s.rf[inst.rn] ^ s.rf[inst.rm]
        elif name == "asr":
            result = signed(s.rf[inst.rn], True) >> trim_5(s.rf[inst.rm])
        elif name == "lsr":
            result = s.rf[inst.rn] >> trim_5(s.rf[inst.rm])
        elif name == "lsl":
            result = s.rf[inst.rn] << trim_5(s.rf[inst.rm])
        s.rf[inst.rd] = trim_32(result)
        s.AN = (result >> 31) & 1
        s.AC = 0
        s.AV = 0
        s.AZ = trim_32(result) == 0
        s.pc += 4 if not is16bit else 2
    return execute_bit

execute_and32 = make_bit_executor("and", False)
execute_and16 = make_bit_executor("and", True)
execute_orr32 = make_bit_executor("orr", False)
execute_orr16 = make_bit_executor("orr", True)
execute_eor32 = make_bit_executor("eor", False)
execute_eor16 = make_bit_executor("eor", True)
execute_asr32 = make_bit_executor("asr", False)
execute_asr16 = make_bit_executor("asr", True)
execute_lsr32 = make_bit_executor("lsr", False)
execute_lsr16 = make_bit_executor("lsr", True)
execute_lsl32 = make_bit_executor("lsl", False)
execute_lsl16 = make_bit_executor("lsl", True)


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
    size_in_bits = inst.bits_5_6
    if inst.bit4:  # STORE
        s.mem.write(address, 0b1 << size_in_bits, s.rf[inst.rd])
    else:          # LOAD
        s.rf[inst.rd] = s.mem.read(address, 0b1 << size_in_bits)
    imm = inst.imm
    if inst.sub_bit24:  # Subtract
        s.rf[inst.rn] = address - (imm << size_in_bits)
    else:
        s.rf[inst.rn] = address + (imm << size_in_bits)


#-----------------------------------------------------------------------
# jr32 - jump.
#-----------------------------------------------------------------------
def execute_jr32(s, inst):
    """
    PC = RN;
    """
    s.pc = s.rf[inst.rn]


#-----------------------------------------------------------------------
# bcond32 - branch on condition.
#-----------------------------------------------------------------------
def should_branch(s, cond):
    if cond == 0b0000:
        return s.AZ
    elif cond == 0b0001:
        return ~s.AZ
    elif cond == 0b0010:
        return ~s.AZ & s.AC
    elif cond == 0b0011:
        return s.AC
    elif cond == 0b0100:
        return s.AZ | ~s.AC
    elif cond == 0b0101:
        return ~s.AC
    elif cond == 0b0110:
        return ~s.AZ & (s.AV == s.AN)
    elif cond == 0b0111:
        return s.AV == s.AN
    elif cond == 0b1000:
        return s.AV != s.AN
    elif cond == 0b1001:
        return s.AZ | (s.AV != s.AN)
    elif cond == 0b1010:
        return s.BZ
    elif cond == 0b1011:
        return ~s.BZ
    elif cond == 0b1100:
        return s.BN & ~s.BZ
    elif cond == 0b1101:
        return s.BN | s.BZ
    elif cond == 0b1110:
        return True
    elif cond == 0b1111:
        return True  # Branch and link
    else:
        raise ValueError('Invalid condition, should be unreachable: ' +
                         str(bin(cond)))


def execute_bcond32(s, inst):
    cond = inst.bcond
    imm = inst.bcond32_imm
    if should_branch(s, cond):
        s.pc += imm << 1
    else:
        s.pc += 4


#-----------------------------------------------------------------------
# movcond32 - move on condition.
#-----------------------------------------------------------------------
def execute_movcond32(s, inst):
    rd = inst.rd
    rn = inst.rn
    if should_branch(s, inst.bcond):
        s.rf[rd] = s.rf[rn]


#=======================================================================
# Create Decoder
#=======================================================================
decode = create_risc_decoder(encodings, globals(), debug=True)
