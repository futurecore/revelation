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
    'CMESHROUTE'  : 104, # cMesh routing configuration, 12 bits
    'XMESHROUTE'  : 105, # xMesh routing configuration, 12 bits
    'RMESHROUTE'  : 106, # rMesh routing configuration, 12 bits
    # Other control registers
    'RESETCORE'   : 107, # Write-only, 1 bit
     }


#=======================================================================
# Instruction Encodings
#=======================================================================
encodings = [
    #---------------------------------------------------------------------
    # Branch on condition
    #---------------------------------------------------------------------
    ['bcond32',     'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx1000'],
    ['bcond16',     'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0000'],
    #--------------------------------------------------------------------
    # Loads and stores
    #---------------------------------------------------------------------
    ['ldstrpmd32',  'xxxxxx1x_xxxxxxxx_xxxxxxxx_xxxx1100'],  # LD or STR combined.
    ['ldstrdisp16', 'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0100'],  # LD or STR combined.
    ['ldstrdisp32', 'xxxxxx0x_xxxxxxxx_xxxxxxxx_xxxx1100'],  # LD or STR combined.
    ['ldstrind16',  'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0001'],  # LD or STR combined.
    ['ldstrind32',  'xxxxxxxx_x00xxxxx_xxxxxxxx_xxxx1001'],  # LD or STR combined.
    ['ldstrpm16',   'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0101'],  # LD or STR combined.
    ['ldstrpm32',   'xxxxxxxx_x00xxxxx_xxxxxxxx_xxxx1101'],  # LD or STR combined.
    ['testset32',   'xxxxxxxx_x01xxxxx_xxxxxxxx_xxx01001'],
    #---------------------------------------------------------------------
    # Arithmetic
    #---------------------------------------------------------------------
    ['add32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x0011111'],
    ['add32',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0011011'],  # with immediate.
    ['sub32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x0111111'],
    ['sub32',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0111011'],  # with immediate.
    ['add16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0011010'],
    ['add16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0010011'],  # with immediate.
    ['sub16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0111010'],
    ['sub16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0110011'],  # with immediate.
    #---------------------------------------------------------------------
    # Bitwise arithmetic
    #---------------------------------------------------------------------
    ['and32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x1011111'],  # AND32
    ['and16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x1011010'],  # AND16
    ['orr32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x1111111'],  # ORR32
    ['orr16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x1111010'],  # ORR16
    ['eor32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x0001111'],  # EOR32
    ['eor16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0001010'],  # EOR16
    ['asr32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x1101111'],  # ASR32
    ['asr16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x1101010'],  # ASR16
    ['lsr32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x1001111'],  # LSR32
    ['lsr16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x1001010'],  # LSR16
    ['lsl32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x0101111'],  # LSL32
    ['lsl16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0101010'],  # LSL16
    ['lsrimm32',    'xxxxxxxx_xxxx0110_xxxxxxxx_xxx01111'],  # LSRIMM32
    ['lslimm32',    'xxxxxxxx_xxxx0110_xxxxxxxx_xxx11111'],  # LSLIMM32
    ['asrimm32',    'xxxxxxxx_xxxx1110_xxxxxxxx_xxx01111'],  # ASRIMM32
    ['bitrimm32',   'xxxxxxxx_xxxx1110_xxxxxxxx_xxx11111'],  # BITRIMM32
    ['lsrimm16',    'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxx00110'],  # LSRIMM16
    ['lslimm16',    'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxx10110'],  # LSLIMM16
    ['asrimm16',    'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxx01110'],  # ASRIMM16
    ['bitrimm16',   'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxx11110'],  # BITRIMM16
    #---------------------------------------------------------------------
    # Floating point and integer arithmetic.
    #---------------------------------------------------------------------
    ['fadd16',      'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0000111'],
    ['fsub16',      'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0010111'],
    ['fmul16',      'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0100111'],
    ['fmadd16',     'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0110111'],
    ['fmsub16',     'xxxxxxxx_xxxxxxxx_xxxxxxxx_x1000111'],
    ['float16',     'xxxxxxxx_xxxxxxxx_xxxxxx00_01010111'],
    ['fix16',       'xxxxxxxx_xxxxxxxx_xxxxxx00_01100111'],
    ['fabs16',      'xxxxxxxx_xxxxxxxx_xxxxxx00_01110111'],
    ['fadd32',      'xxxxxxxx_xxxx0111_xxxxxxxx_x0001111'],
    ['fsub32',      'xxxxxxxx_xxxx0111_xxxxxxxx_x0011111'],
    ['fmul32',      'xxxxxxxx_xxxx0111_xxxxxxxx_x0101111'],
    ['fmadd32',     'xxxxxxxx_xxxx0111_xxxxxxxx_x0111111'],
    ['fmsub32',     'xxxxxxxx_xxxx0111_xxxxxxxx_x1001111'],
    ['float32',     'xxxxxxxx_xxxx0111_xxxxxx00_01011111'],
    ['fix32',       'xxxxxxxx_xxxx0111_xxxxxx00_01101111'],
    ['fabs32',      'xxxxxxxx_xxxx0111_xxxxxx00_01111111'],
    #---------------------------------------------------------------------
    # Moves.
    #---------------------------------------------------------------------
    ['movcond32',   'xxxxxxxx_xxxx0010_xxxxxx00_xxxx1111'],
    ['movcond16',   'xxxxxxxx_xxxxxxxx_xxxxxx00_xxxx0010'],
    ['movimm32',    'xxx0xxxx_xxxxxxxx_xxxxxxxx_xxx01011'],
    ['movimm16',    'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxx00011'],
    ['movtimm32',   'xxx1xxxx_xxxxxxxx_xxxxxxxx_xxx01011'],
    ['movts16',     'xxxxxxxx_xxxxxxxx_xxxxxx01_00000010'],
    ['movts32',     'xxxxxxxx_xxxx0010_xxxxxx01_00001111'],
    ['movfs16',     'xxxxxxxx_xxxxxxxx_xxxxxx01_00010010'],
    ['movfs32',     'xxxxxxxx_xxxx0010_xxxxxx01_00011111'],
    #---------------------------------------------------------------------
    # Jumps.
    #---------------------------------------------------------------------
    ['jr32',        'xxxxxxxx_xxxx0010_xxxxxx01_01001111'],
    ['jr16',        'xxxxxxxx_xxxxxxxx_xxxxxx01_01000010'],
    ['jalr32',      'xxxxxxxx_xxxx0010_xxxxxx01_01011111'],
    ['jalr16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_01010010'],
    #---------------------------------------------------------------------
    # Interrupts, multicore and control.
    #---------------------------------------------------------------------
    ['nop16',       'xxxxxxxx_xxxxxxxx_xxxxxx01_10100010'],
    ['idle16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_10110010'],
    ['bkpt16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_11000010'],
    ['mbkpt16',     'xxxxxxxx_xxxxxxxx_xxxxxx11_11000010'],
    ['gie16',       'xxxxxxxx_xxxxxxxx_xxxxxx01_10010010'],
    ['gid16',       'xxxxxxxx_xxxxxxxx_xxxxxx11_10010010'],
    ['sync16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_11110010'],
    ['rti16',       'xxxxxxxx_xxxxxxxx_xxxxxx01_11010010'],
    ['wand16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_10000010'],
    ['trap16',      'xxxxxxxx_xxxxxxxx_xxxxxx11_11100010'],
    ['unimpl',      'xxxxxxxx_xxxx1111_xxxxxx00_00001111'],
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
execute_ldstrind16  = execute_load_store.make_ldstrindpm_executor(True,  False)
execute_ldstrind32  = execute_load_store.make_ldstrindpm_executor(False, False)
execute_ldstrpm16   = execute_load_store.make_ldstrindpm_executor(True,  True)
execute_ldstrpm32   = execute_load_store.make_ldstrindpm_executor(False, True)
execute_testset32   = execute_load_store.testset32

#-----------------------------------------------------------------------
# Integer arithmetic instructions
#-----------------------------------------------------------------------
execute_sub32 = execute_iarith.make_sub_executor(False)
execute_sub16 = execute_iarith.make_sub_executor(True)
execute_add32 = execute_iarith.make_add_executor(False)
execute_add16 = execute_iarith.make_add_executor(True)

#-----------------------------------------------------------------------
# Bitwise instructions
#-----------------------------------------------------------------------
# 16 bit instructions without immediate.
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
# Move instructions
#-----------------------------------------------------------------------
execute_movcond32 = execute_mov.make_movcond_executor(False)
execute_movcond16 = execute_mov.make_movcond_executor(True)
execute_movtimm32 = execute_mov.make_movimm_executor(False, True)
execute_movimm32  = execute_mov.make_movimm_executor(False, False)
execute_movimm16  = execute_mov.make_movimm_executor(True,  False)
execute_movts32   = execute_mov.make_mov_executor(False, rd_is_special=True)
execute_movts16   = execute_mov.make_mov_executor(True,  rd_is_special=True)
execute_movfs32   = execute_mov.make_mov_executor(False, rn_is_special=True)
execute_movfs16   = execute_mov.make_mov_executor(True,  rn_is_special=True)

#-----------------------------------------------------------------------
# Jump instructions
#-----------------------------------------------------------------------
execute_jr32   = execute_jump.make_jr_executor(False, save_lr=False)
execute_jr16   = execute_jump.make_jr_executor(True,  save_lr=False)
execute_jalr32 = execute_jump.make_jr_executor(False, save_lr=True)
execute_jalr16 = execute_jump.make_jr_executor(True,  save_lr=True)

#-----------------------------------------------------------------------
# Interrupt and multicore instructions
#-----------------------------------------------------------------------
execute_nop16   = execute_interrupts.execute_nop16
execute_idle16  = execute_interrupts.execute_idle16
execute_bkpt16  = execute_interrupts.execute_bkpt16
execute_mbkpt16 = execute_interrupts.execute_mbkpt16
execute_gie16   = execute_interrupts.execute_gie16
execute_gid16   = execute_interrupts.execute_gid16
execute_sync16  = execute_interrupts.execute_sync16
execute_rti16   = execute_interrupts.execute_rti16
execute_wand16  = execute_interrupts.execute_wand16
execute_trap16  = execute_interrupts.execute_trap16
execute_unimpl  = execute_interrupts.execute_unimpl

#=======================================================================
# Create Decoder
#=======================================================================
decode = create_risc_decoder(encodings, globals(), debug=True)
