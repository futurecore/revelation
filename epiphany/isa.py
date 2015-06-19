import epiphany.execute_bitwise    as execute_bitwise
import epiphany.execute_branch     as execute_branch
import epiphany.execute_farith     as execute_farith
import epiphany.execute_iarith     as execute_iarith
import epiphany.execute_interrupt  as execute_interrupts
import epiphany.execute_jump       as execute_jump
import epiphany.execute_load_store as execute_load_store
import epiphany.execute_mov        as execute_mov

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
    ['ldstrdisp16', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx0100'],  # LD or STR combined.
    ['ldstrdisp32', 'xxxxxx0xxxxxxxxxxxxxxxxxxxxx1100'],  # LD or STR combined.
    ['ldstrind16',  'xxxxxxxxxxxxxxxxxxxxxxxxxxxx0001'],  # LD or STR combined.
    ['ldstrind32',  'xxxxxxxxx00xxxxxxxxxxxxxxxxx1001'],  # LD or STR combined.
    ['ldstrpm16',   'xxxxxxxxxxxxxxxxxxxxxxxxxxxx0101'],  # LD or STR combined.
    ['ldstrpm32',   'xxxxxxxxx00xxxxxxxxxxxxxxxxx1101'],  # LD or STR combined.
    ['testset32',   'xxxxxxxxx01xxxxxxxxxxxxxxxx01001'],
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
    ['movts16',     'xxxxxxxxxxxxxxxxxxxxxx0100000010'],
    ['movts32',     'xxxxxxxxxxxx0010xxxxxx0100001111'],
    ['movfs16',     'xxxxxxxxxxxxxxxxxxxxxx0100010010'],
    ['movfs32',     'xxxxxxxxxxxx0010xxxxxx0100011111'],
    #---------------------------------------------------------------------
    # Floating point and integer arithmetic.
    #---------------------------------------------------------------------
    ['fadd16',      'xxxxxxxxxxxxxxxxxxxxxxxxx0000111'],
    ['fsub16',      'xxxxxxxxxxxxxxxxxxxxxxxxx0010111'],
    ['fmul16',      'xxxxxxxxxxxxxxxxxxxxxxxxx0100111'],
    ['fmadd16',     'xxxxxxxxxxxxxxxxxxxxxxxxx0110111'],
    ['fmsub16',     'xxxxxxxxxxxxxxxxxxxxxxxxx1000111'],
    ['float16',     'xxxxxxxxxxxxxxxxxxxxxx0001010111'],
    ['fix16',       'xxxxxxxxxxxxxxxxxxxxxx0001100111'],
    ['fabs16',      'xxxxxxxxxxxxxxxxxxxxxx0001110111'],
    ['fadd32',      'xxxxxxxxxxxx0111xxxxxxxxx0001111'],
    ['fsub32',      'xxxxxxxxxxxx0111xxxxxxxxx0011111'],
    ['fmul32',      'xxxxxxxxxxxx0111xxxxxxxxx0101111'],
    ['fmadd32',     'xxxxxxxxxxxx0111xxxxxxxxx0111111'],
    ['fmsub32',     'xxxxxxxxxxxx0111xxxxxxxxx1001111'],
    ['float32',     'xxxxxxxxxxxx0111xxxxxx0001011111'],
    ['fix32',       'xxxxxxxxxxxx0111xxxxxx0001101111'],
    ['fabs32',      'xxxxxxxxxxxx0111xxxxxx0001111111'],
]


#-----------------------------------------------------------------------
# Branch instructions
#-----------------------------------------------------------------------
execute_bcond32 = execute_branch.make_bcond_executor(False)
execute_bcond16 = execute_branch.make_bcond_executor(True)

#-----------------------------------------------------------------------
# Load / store instructions
#-----------------------------------------------------------------------
execute_ldstrpmd32  = execute_load_store.execute_ldstrpmd32
execute_ldstrdisp16 = execute_load_store.make_ldstrdisp_executor(True)
execute_ldstrdisp32 = execute_load_store.make_ldstrdisp_executor(False)
execute_ldstrind16  = execute_load_store.make_ldstrind_executor(True)
execute_ldstrind32  = execute_load_store.make_ldstrind_executor(False)
execute_ldstrpm16   = execute_load_store.make_ldstrpm_executor(True)
execute_ldstrpm32   = execute_load_store.make_ldstrpm_executor(False)
execute_testset32   = execute_load_store.testset32

#-----------------------------------------------------------------------
# Jump instructions
#-----------------------------------------------------------------------
execute_jr32   = execute_jump.make_jr_executor(False)
execute_jr16   = execute_jump.make_jr_executor(True)
execute_jalr32 = execute_jump.make_jalr_executor(False)
execute_jalr16 = execute_jump.make_jalr_executor(True)

#-----------------------------------------------------------------------
# Bitwise instructions
#-----------------------------------------------------------------------
# 16 bit instructions with immediate.
execute_and16     = execute_bitwise.make_bit_executor("and", True,  False)
execute_orr16     = execute_bitwise.make_bit_executor("orr", True,  False)
execute_eor16     = execute_bitwise.make_bit_executor("eor", True,  False)
execute_asr16     = execute_bitwise.make_bit_executor("asr", True,  False)
execute_lsr16     = execute_bitwise.make_bit_executor("lsr", True,  False)
execute_lsl16     = execute_bitwise.make_bit_executor("lsl", True,  False)
# 32 bit instructions without immediate.
execute_and32     = execute_bitwise.make_bit_executor("and", False, False)
execute_orr32     = execute_bitwise.make_bit_executor("orr", False, False)
execute_eor32     = execute_bitwise.make_bit_executor("eor", False, False)
execute_asr32     = execute_bitwise.make_bit_executor("asr", False, False)
execute_lsr32     = execute_bitwise.make_bit_executor("lsr", False, False)
execute_lsl32     = execute_bitwise.make_bit_executor("lsl", False, False)
# 16 bit instructions with immediate.
execute_lsrimm16  = execute_bitwise.make_bit_executor("lsr",  True, True)
execute_lslimm16  = execute_bitwise.make_bit_executor("lsl",  True, True)
execute_asrimm16  = execute_bitwise.make_bit_executor("asr",  True, True)
execute_bitrimm16 = execute_bitwise.make_bit_executor("bitr", True, True)
# 32 bit instructions with immediate.
execute_lsrimm32  = execute_bitwise.make_bit_executor("lsr",  False, True)
execute_lslimm32  = execute_bitwise.make_bit_executor("lsl",  False, True)
execute_asrimm32  = execute_bitwise.make_bit_executor("asr",  False, True)
execute_bitrimm32 = execute_bitwise.make_bit_executor("bitr", False, True)

#-----------------------------------------------------------------------
# Integer arithmetic instructions
#-----------------------------------------------------------------------
execute_sub32 = execute_iarith.make_sub_executor(False)
execute_sub16 = execute_iarith.make_sub_executor(True)
execute_add32 = execute_iarith.make_add_executor(False)
execute_add16 = execute_iarith.make_add_executor(True)

#-----------------------------------------------------------------------
# Move instructions
#-----------------------------------------------------------------------
execute_movcond32 = execute_mov.make_movcond_executor(False)
execute_movcond16 = execute_mov.make_movcond_executor(True)
execute_movtimm32 = execute_mov.make_movimm_executor(False, True)
execute_movimm32  = execute_mov.make_movimm_executor(False, False)
execute_movimm16  = execute_mov.make_movimm_executor(True, False)
execute_movts32   = execute_mov.make_mov_executor(False)
execute_movts16   = execute_mov.make_mov_executor(True)
execute_movfs32   = execute_mov.make_mov_executor(False)
execute_movfs16   = execute_mov.make_mov_executor(True)

#---------------------------------------------------------------------
# Floating point and integer arithmetic.
#---------------------------------------------------------------------
execute_fadd16  = execute_farith.make_farith_executor('add', True)
execute_fsub16  = execute_farith.make_farith_executor('sub', True)
execute_fmul16  = execute_farith.make_farith_executor('mul', True)
execute_fmadd16 = execute_farith.make_farith_executor('madd', True)
execute_fmsub16 = execute_farith.make_farith_executor('msub', True)
execute_float16 = execute_farith.make_farith_executor('float', True)
execute_fix16   = execute_farith.make_farith_executor('fix', True)
execute_fabs16  = execute_farith.make_farith_executor('abs', True)
execute_fadd32  = execute_farith.make_farith_executor('add', False)
execute_fsub32  = execute_farith.make_farith_executor('sub', False)
execute_fmul32  = execute_farith.make_farith_executor('mul', False)
execute_fmadd32 = execute_farith.make_farith_executor('madd', False)
execute_fmsub32 = execute_farith.make_farith_executor('msub', False)
execute_float32 = execute_farith.make_farith_executor('float', False)
execute_fix32   = execute_farith.make_farith_executor('fix', False)
execute_fabs32  = execute_farith.make_farith_executor('abs', False)

#-----------------------------------------------------------------------
# Interrupt and multicore instructions
#-----------------------------------------------------------------------
execute_nop16     = execute_interrupts.execute_nop16
execute_idle16    = execute_interrupts.execute_idle16
execute_bkpt16    = execute_interrupts.execute_bkpt16
execute_mbkpt16   = execute_interrupts.execute_mbkpt16
execute_gie16     = execute_interrupts.execute_gie16
execute_gid16     = execute_interrupts.execute_gid16
execute_sync16    = execute_interrupts.execute_sync16
execute_rti16     = execute_interrupts.execute_rti16
execute_wand16    = execute_interrupts.execute_wand16
execute_trap16    = execute_interrupts.execute_trap16
execute_unimpl16  = execute_interrupts.execute_unimpl16

#=======================================================================
# Create Decoder
#=======================================================================
decode = create_risc_decoder(encodings, globals(), debug=True)
