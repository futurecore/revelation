from epiphany.condition_codes import should_branch

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

try:
    from rpython.rlib.objectmodel import we_are_translated
except ImportError:
    we_are_translated = lambda : False

#=======================================================================
# Register Definitions
#=======================================================================
reg_map = {
    'r0'   :  0,   'r1'   :  1,   'r2'   :  2,   'r3'   :  3,
    'r4'   :  4,   'r5'   :  5,   'r6'   :  6,   'r7'   :  7,
    'r8'   :  8,   'r9'   :  9,   'r10'  : 10,   'r11'  : 11,
    'r12'  : 12,   'r13'  : 13,   'r14'  : 14,   'r15'  : 15,
    'r16'  : 16,   'r17'  : 17,   'r18'  : 18,   'r19'  : 19,
    'r20'  : 20,   'r21'  : 21,   'r22'  : 22,   'r23'  : 23,
    'r24'  : 24,   'r25'  : 25,   'r26'  : 26,   'r27'  : 27,
    'r28'  : 28,   'r29'  : 29,   'r30'  : 30,   'r31'  : 31,
    'r32'  : 32,   'r33'  : 33,   'r34'  : 34,   'r35'  : 35,
    'r36'  : 36,   'r37'  : 37,   'r38'  : 38,   'r39'  : 39,
    'r40'  : 40,   'r41'  : 41,   'r42'  : 42,   'r43'  : 43,
    'r48'  : 48,   'r49'  : 49,   'r50'  : 50,   'r51'  : 51,
    'r52'  : 52,   'r53'  : 53,   'r54'  : 54,   'r55'  : 55,
    'r56'  : 56,   'r57'  : 57,   'r58'  : 58,   'r59'  : 59,
    'r60'  : 40,   'r61'  : 61,   'r62'  : 62,   'r63'  : 63,
    # Synonyms.
    'SB' : 9,   # Static base
    'SL' : 10,  # Stack limit
    'FP' : 11,  # Frame pointer
    'SP' : 13,  # Stack pointer
    'LR' : 14,  # Link register
    # Special registers.
    'UNUSED'      : 64,
    'CONFIG'      : 65,  # Core configuration
    'STATUS'      : 66,  # Core status
    'pc'          : 67,  # Program counter
    'DEBUGSTATUS' : 68,  # Debug status
    'LC'          : 69,  # Hardware counter loop
    'LS'          : 70,  # Hardware counter start address
    'LE'          : 71,  # Hardware counter end address
    'IRET'        : 72,  # Interrupt PC return address
    'IMASK'       : 73,  # Interrupt mask
    'ILAT'        : 74,  # Interrupt latch
    'ILATST'      : 75,  # Alias for setting interrupts
    'ILATCL'      : 76,  # Alias for clearing interrupts
    'IPEND'       : 77,  # Interrupt currently in progress
    'FSTATUS'     : 78,  # Alias for writing to all STATUS bits
    'DEBUGCMD'    : 79,  # Debug command register
    'RESETCORE'   : 80,  # Per core software reset
    # Event timer registers
    'CTIMER0'     : 81,  # Core timer 0
    'CTIMER1'     : 82,  # Core timer 1
    # Process control registers
    'MEMSTATUS'   : 83,  # Memory protection status
    'MEMPROTECT'  : 84,  # Memory protection registration
    # DMA registers
    'DMA0CONFIG'  : 85,  # DMA channel 0 configuration
    'DMA0STRIDE'  : 86,  # DMA channel 0 stride
    'DMA0COUNT'   : 87,  # DMA channel 0 count
    'DMA0SRCADDR' : 88,  # DMA channel 0 source address
    'DMA0DSTADDR' : 89,  # DMA channel 0 destination address
    'DMA0AUTO0'   : 90,  # DMA channel 0 slave lower data
    'DMA0AUTO1'   : 91,  # DMA channel 0 slave upper data
    'DMA0STATUS'  : 92,  # DMA channel 0 status
    'DMA1CONFIG'  : 93,  # DMA channel 1 configuration
    'DMA1STRIDE'  : 94,  # DMA channel 1 stride
    'DMA1COUNT'   : 95,  # DMA channel 1 count
    'DMA1SRCADDR' : 96,  # DMA channel 1 source address
    'DMA1DSTADDR' : 97,  # DMA channel 1 destination address
    'DMA1AUTO0'   : 98,  # DMA channel 1 slave lower data
    'DMA1AUTO1'   : 99,  # DMA channel 1 slave upper data
    'DMA1STATUS'  : 100, # DMA channel 1 status
    # Mesh node control registers
    'MESHCONFIG'  : 101, # Mesh node configuration
    'COREID'      : 102, # Processor core ID
    'MULTICAST'   : 103, # Multicast configuration
    'CMESHROUTE'  : 104, # cMesh routing configuration
    'XMESHROUTE'  : 105, # xMesh routing configuration
    'RMESHROUTE'  : 106, # rMesh routing configuration
     }


#=======================================================================
# Instruction Encodings
#=======================================================================
encodings = [
    ['nop16',       'xxxxxxxxxxxxxxxxxxxxxx0110100010'],
    ['idle16',      'xxxxxxxxxxxxxxxxxxxxxx0110110010'],
    ['bkpt16',      'xxxxxxxxxxxxxxxxxxxxxx0111000010'],
    ['mbkpt16',     'xxxxxxxxxxxxxxxxxxxxxx1111000010'],
    ['gie16',       'xxxxxxxxxxxxxxxxxxxxxx0110010010'],
    ['gid16',       'xxxxxxxxxxxxxxxxxxxxxx1110010010'],
    ['sync16',      'xxxxxxxxxxxxxxxxxxxxxx0111110010'],
    ['rti16',       'xxxxxxxxxxxxxxxxxxxxxx0111010010'],
    ['wand16',      'xxxxxxxxxxxxxxxxxxxxxx0110000010'],
    ['trap16',      'xxxxxxxxxxxxxxxxxxxxxx1111100010'],
    ['unimpl16',    'xxxxxxxxxxxx1111xxxxxx0000001111'],
    #---------------------------------------------------------------------
    # Arithmetic
    #---------------------------------------------------------------------
    ['add32',       'xxxxxxxxxxxx1010xxxxxxxxx0011111'],
    ['add32',       'xxxxxxxxxxxxxxxxxxxxxxxxx0011011'],  # with immediate.
    ['sub32',       'xxxxxxxxxxxx1010xxxxxxxxx0111111'],
    ['sub32',       'xxxxxxxxxxxxxxxxxxxxxxxxx0111011'],  # with immediate.
    ['add16',       'xxxxxxxxxxxxxxxxxxxxxxxxx0011010'],
    ['add16',       'xxxxxxxxxxxxxxxxxxxxxxxxx0010011'],  # with immediate.
    ['sub16',       'xxxxxxxxxxxxxxxxxxxxxxxxx0111010'],
    ['sub16',       'xxxxxxxxxxxxxxxxxxxxxxxxx0110011'],  # with immediate.
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
    ['lsrimm32',    'xxxxxxxxxxxx0110xxxxxxxxxxx01111'],  # LSRIMM32
    ['lslimm32',    'xxxxxxxxxxxx0110xxxxxxxxxxx11111'],  # LSLIMM32
    ['asrimm32',    'xxxxxxxxxxxx1110xxxxxxxxxxx01111'],  # ASRIMM32
    ['bitrimm32',   'xxxxxxxxxxxx1110xxxxxxxxxxx11111'],  # BITRIMM32
    ['lsrimm16',    'xxxxxxxxxxxxxxxxxxxxxxxxxxx00110'],  # LSRIMM16
    ['lslimm16',    'xxxxxxxxxxxxxxxxxxxxxxxxxxx10110'],  # LSLIMM16
    ['asrimm16',    'xxxxxxxxxxxxxxxxxxxxxxxxxxx01110'],  # ASRIMM16
    ['bitrimm16',   'xxxxxxxxxxxxxxxxxxxxxxxxxxx11110'],  # BITRIMM16
    #--------------------------------------------------------------------
    # Loads and stores
    #---------------------------------------------------------------------
    ['ldstrpmd32',  'xxxxxx1xxxxxxxxxxxxxxxxxxxxx1100'],  # LD or STR combined.
    #---------------------------------------------------------------------
    # Jumps and branch conditions
    #---------------------------------------------------------------------
    ['bcond32',     'xxxxxxxxxxxxxxxxxxxxxxxxxxxx1000'],
    ['bcond16',     'xxxxxxxxxxxxxxxxxxxxxxxxxxxx0000'],
    ['jr32',        'xxxxxxxxxxxx0010xxxxxx0101001111'],
    ['jr16',        'xxxxxxxxxxxxxxxxxxxxxx0101000010'],
    ['jalr32',      'xxxxxxxxxxxx0010xxxxxx0101011111'],
    ['jalr16',      'xxxxxxxxxxxxxxxxxxxxxx0101010010'],
    #---------------------------------------------------------------------
    # Moves
    #---------------------------------------------------------------------
    ['movcond32',   'xxxxxxxxxxxx0010xxxxxx00xxxx1111'],
    ['movcond16',   'xxxxxxxxxxxxxxxxxxxxxx00xxxx0010'],
    ['movimm32',    'xxx0xxxxxxxxxxxxxxxxxxxxxxx01011'],
    ['movimm16',    'xxxxxxxxxxxxxxxxxxxxxxxxxxx00011'],
    ['movtimm32',   'xxx1xxxxxxxxxxxxxxxxxxxxxxx01011'],
]


def reg_or_imm(s, inst, is16bit):
    if is16bit:
        val = s.rf[inst.rm] if inst.bit0 == 0 else inst.imm
    else:
        val = s.rf[inst.rm] if inst.bit2 == 1 else inst.imm
    return val


def trim_5(value):
    return value & 0b11111


def signed(value, is16bit):
  if is16bit and (value & 0x8000) or not is16bit and (value & 0x80000000):
    twos_complement = ~value + 1
    return -trim_32(twos_complement)
  return value


#-----------------------------------------------------------------------
# nop16
#-----------------------------------------------------------------------
def execute_nop16(s, inst):
    s.pc += 2


#-----------------------------------------------------------------------
# idle16
#-----------------------------------------------------------------------
def execute_idle16(s, inst):
    """
        STATUS[0]=0
        while(!ILAT){
            PC=PC;
        }
    """
    status = s.rf[reg_map['STATUS']]
    mask = 0b1111111111111111111111111110
    status &= mask
    s.rf[reg_map['STATUS']] = status
    if not s.rf[reg_map['ILAT']]: # TODO: Use threads here?
        pass
    s.pc += 2


#-----------------------------------------------------------------------
# bkpt16 and mbkpt16
#-----------------------------------------------------------------------
def execute_bkpt16(s, inst):
    s.rf[reg_map['DEBUGSTATUS']] |= 1
    s.pc += 2
    s.running = False


def execute_mbkpt16(s, inst):
    raise NotImplementedError('Multicore not implemented.')


#-----------------------------------------------------------------------
# gie16 and gid16
#-----------------------------------------------------------------------
def execute_gie16(s, inst):
    """Enables all interrupts in ILAT register, dependent on the per bit
    settings in the IMASK register.
    TODO: Implement interrupts.
        STATUS[1]=0
    """
    s.rf[reg_map['STATUS']] &= ~(1 << 1)
    s.pc += 2


def execute_gid16(s, inst):
    """Disable all interrupts.
        STATUS[1]=1
    """
    s.rf[reg_map['STATUS']] |= (1 << 1)
    s.pc += 2


#-----------------------------------------------------------------------
# sync16
#-----------------------------------------------------------------------
def execute_sync16(s, inst):
    raise NotImplementedError('Interrupts not implemented.')


#-----------------------------------------------------------------------
# rti16
#-----------------------------------------------------------------------
def execute_rti16(s, inst):
    raise NotImplementedError('Interrupts not implemented.')


#-----------------------------------------------------------------------
# trap16
#-----------------------------------------------------------------------
def execute_trap16(s, inst):
    raise NotImplementedError('Interrupts not implemented.')


#-----------------------------------------------------------------------
# wand16
#-----------------------------------------------------------------------
def execute_wand16(s, inst):
    raise NotImplementedError('Multicore not implemented.')


#-----------------------------------------------------------------------
# unimpl16
#-----------------------------------------------------------------------
def execute_unimpl16(s, inst):
    raise NotImplementedError('UNIMPL16')


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
        result = s.rf[inst.rn] + reg_or_imm(s, inst, is16bit)
        s.rf[inst.rd] = trim_32(result)
        s.AN = (result >> 31) & 1
        s.AZ = trim_32(result) == 0
        s.AC = carry_from(result)
        s.AV = overflow_from_add(s.rf[inst.rn], s.rf[inst.rm], result)
        s.AVS = s.AVS | s.AV
        s.pc += 2 if is16bit else 4
    return execute_add

execute_add32 = make_add_executor(False)
execute_add16 = make_add_executor(True)


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
        result = s.rf[inst.rn] - reg_or_imm(s, inst, is16bit)
        s.rf[inst.rd] = trim_32(result)
        s.AN = (result >> 31) & 1
        s.AC = borrow_from(result)
        s.AZ = trim_32(result) == 0b0
        s.AV = overflow_from_sub(s.rf[inst.rn], s.rf[inst.rm], result)
        s.AVS = s.AVS | s.AV
        s.pc += 2 if is16bit else 4
    return execute_sub

execute_sub32 = make_sub_executor(False)
execute_sub16 = make_sub_executor(True)


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

# 16 bit instructions with immediate.
execute_and16     = make_bit_executor("and", True,  False)
execute_orr16     = make_bit_executor("orr", True,  False)
execute_eor16     = make_bit_executor("eor", True,  False)
execute_asr16     = make_bit_executor("asr", True,  False)
execute_lsr16     = make_bit_executor("lsr", True,  False)
execute_lsl16     = make_bit_executor("lsl", True,  False)
# 32 bit instructions without immediate.
execute_and32     = make_bit_executor("and", False, False)
execute_orr32     = make_bit_executor("orr", False, False)
execute_eor32     = make_bit_executor("eor", False, False)
execute_asr32     = make_bit_executor("asr", False, False)
execute_lsr32     = make_bit_executor("lsr", False, False)
execute_lsl32     = make_bit_executor("lsl", False, False)
# 16 bit instructions with immediate.
execute_lsrimm16  = make_bit_executor("lsr",  True, True)
execute_lslimm16  = make_bit_executor("lsl",  True, True)
execute_asrimm16  = make_bit_executor("asr",  True, True)
execute_bitrimm16 = make_bit_executor("bitr", True, True)
# 32 bit instructions with immediate.
execute_lsrimm32  = make_bit_executor("lsr",  False, True)
execute_lslimm32  = make_bit_executor("lsl",  False, True)
execute_asrimm32  = make_bit_executor("asr",  False, True)
execute_bitrimm32 = make_bit_executor("bitr", False, True)


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
# jr32 and jr16 - jump.
#-----------------------------------------------------------------------
def make_jr_executor(is16bit):
    def execute_jr(s, inst):
        """
        PC = RN;
        """
        if is16bit:
            inst.bits &= 0xffff
        s.pc = s.rf[inst.rn]
    return execute_jr

execute_jr32 = make_jr_executor(False)
execute_jr16 = make_jr_executor(True)


#-----------------------------------------------------------------------
# jalr32 and jalr16 - register and link jump.
#-----------------------------------------------------------------------
def make_jalr_executor(is16bit):
    def execute_jalr(s, inst):
        """
        LR = PC;
        PC = RN;
        """
        if is16bit:
            inst.bits &= 0xffff
        s.rf[reg_map['LR']] = s.pc
        s.pc = s.rf[inst.rn]
    return execute_jalr

execute_jalr32 = make_jalr_executor(False)
execute_jalr16 = make_jalr_executor(True)


#-----------------------------------------------------------------------
# bcon16 and bcond32 - branch on condition.
#-----------------------------------------------------------------------
def make_bcond_executor(is16bit):
    def execute_bcond(s, inst):
        if is16bit:
            inst.bits &= 0xffff
        cond = inst.bcond
        imm = inst.bcond_imm
        if should_branch(s, cond):
            s.pc += imm << 1
        else:
            s.pc += 2 if is16bit else 4
    return execute_bcond

execute_bcond32 = make_bcond_executor(False)
execute_bcond16 = make_bcond_executor(True)


#-----------------------------------------------------------------------
# movcond32 and movcond16 - move on condition.
#-----------------------------------------------------------------------
def make_movcond_executor(is16bit):
    def execute_movcond(s, inst):
        """
        IF (Passed) <COND> then
            RD = RN
        """
        if is16bit:
            inst.bits &= 0xffff
        rd = inst.rd
        rn = inst.rn
        if should_branch(s, inst.bcond):
            s.rf[rd] = s.rf[rn]
    return execute_movcond

execute_movcond32 = make_movcond_executor(False)
execute_movcond16 = make_movcond_executor(True)


#-----------------------------------------------------------------------
# movimm32, movtimm32 and movimm16 - move with immediate
#-----------------------------------------------------------------------
def make_movimm_executor(is16bit, is_t):
    def execute_movimm(s, inst):
        """
        RD=<imm>
        """
        if is16bit:
            inst.bits &= 0xffff
        imm = inst.mov_imm
        rd = inst.rd
        s.rf[rd] = (rd | (imm << 16)) if is_t else imm
    return execute_movimm

execute_movtimm32 = make_movimm_executor(False, True)
execute_movimm32  = make_movimm_executor(False, False)
execute_movimm16  = make_movimm_executor(True, False)


#=======================================================================
# Create Decoder
#=======================================================================
decode = create_risc_decoder(encodings, globals(), debug=True)
