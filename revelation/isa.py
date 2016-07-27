import revelation.execute_bitwise    as execute_bitwise
import revelation.execute_branch     as execute_branch
import revelation.execute_farith     as execute_farith
import revelation.execute_interrupt  as execute_interrupts
import revelation.execute_jump       as execute_jump
import revelation.execute_load_store as execute_load_store
import revelation.execute_mov        as execute_mov

from pydgin.misc import create_risc_decoder


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
    'r44'  : 44,   'r45'  : 45,   'r46'  : 46,   'r47'  : 47,
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
    'CONFIG'      : 64,  # Core configuration
    'STATUS'      : 65,  # Core status
    'pc'          : 66,  # Program counter
    'DEBUGSTATUS' : 67,  # Debug status
    'LC'          : 68,  # Hardware counter loop
    'LS'          : 69,  # Hardware counter start address
    'LE'          : 70,  # Hardware counter end address
    'IRET'        : 71,  # Interrupt PC return address
    'IMASK'       : 72,  # Interrupt mask
    'ILAT'        : 73,  # Interrupt latch
    'ILATST'      : 74,  # Alias for setting interrupts
    'ILATCL'      : 75,  # Alias for clearing interrupts
    'IPEND'       : 76,  # Interrupt currently in progress
    'FSTATUS'     : 77,  # Alias for writing to all STATUS bits
    'DEBUGCMD'    : 78,  # Debug command register
    'RESETCORE'   : 79,  # Per core software reset
    # Event timer registers
    'CTIMER0'     : 80,  # Core timer 0
    'CTIMER1'     : 81,  # Core timer 1
    # Process control registers
    'MEMSTATUS'   : 82,  # Memory protection status
    'MEMPROTECT'  : 83,  # Memory protection registration
    # DMA registers
    'DMA0CONFIG'  : 84,  # DMA channel 0 configuration
    'DMA0STRIDE'  : 85,  # DMA channel 0 stride
    'DMA0COUNT'   : 86,  # DMA channel 0 count
    'DMA0SRCADDR' : 87,  # DMA channel 0 source address
    'DMA0DSTADDR' : 88,  # DMA channel 0 destination address
    'DMA0AUTO0'   : 89,  # DMA channel 0 slave lower data
    'DMA0AUTO1'   : 90,  # DMA channel 0 slave upper data
    'DMA0STATUS'  : 91,  # DMA channel 0 status
    'DMA1CONFIG'  : 92,  # DMA channel 1 configuration
    'DMA1STRIDE'  : 93,  # DMA channel 1 stride
    'DMA1COUNT'   : 94,  # DMA channel 1 count
    'DMA1SRCADDR' : 95,  # DMA channel 1 source address
    'DMA1DSTADDR' : 96,  # DMA channel 1 destination address
    'DMA1AUTO0'   : 97,  # DMA channel 1 slave lower data
    'DMA1AUTO1'   : 98,  # DMA channel 1 slave upper data
    'DMA1STATUS'  : 99,  # DMA channel 1 status
    # Mesh node control registers
    'MESHCONFIG'  : 100, # Mesh node configuration
    'COREID'      : 101, # Processor core ID
    'MULTICAST'   : 102, # Multicast configuration
    'CMESHROUTE'  : 103, # cMesh routing configuration, 12 bits
    'XMESHROUTE'  : 104, # xMesh routing configuration, 12 bits
    'RMESHROUTE'  : 105, # rMesh routing configuration, 12 bits
}


encodings = [
    # Branch on condition
    ['bcond32',     'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx1000'],
    ['bcond16',     'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0000'],
    # Loads and stores
    ['ldstrpmd32',  'xxxxxx1x_xxxxxxxx_xxxxxxxx_xxxx1100'],  # LD or STR combined.
    ['ldstrdisp16', 'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0100'],  # LD or STR combined.
    ['ldstrdisp32', 'xxxxxx0x_xxxxxxxx_xxxxxxxx_xxxx1100'],  # LD or STR combined.
    ['ldstrind16',  'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0001'],  # LD or STR combined.
    ['ldstrind32',  'xxxxxxxx_x00xxxxx_xxxxxxxx_xxxx1001'],  # LD or STR combined.
    ['ldstrpm16',   'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxxx0101'],  # LD or STR combined.
    ['ldstrpm32',   'xxxxxxxx_x00xxxxx_xxxxxxxx_xxxx1101'],  # LD or STR combined.
    ['testset32',   'xxxxxxxx_x01xxxxx_xxxxxxxx_xxx01001'],
    # Arithmetic
    ['add32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x0011111'],
    ['add32',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0011011'],  # with immediate.
    ['sub32',       'xxxxxxxx_xxxx1010_xxxxxxxx_x0111111'],
    ['sub32',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0111011'],  # with immediate.
    ['add16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0011010'],
    ['add16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0010011'],  # with immediate.
    ['sub16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0111010'],
    ['sub16',       'xxxxxxxx_xxxxxxxx_xxxxxxxx_x0110011'],  # with immediate.
    # Bitwise arithmetic
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
    # Floating point and signed integer arithmetic.
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
    # Moves.
    ['movcond32',   'xxxxxxxx_xxxx0010_xxxxxx00_xxxx1111'],
    ['movcond16',   'xxxxxxxx_xxxxxxxx_xxxxxx00_xxxx0010'],
    ['movimm32',    'xxx0xxxx_xxxxxxxx_xxxxxxxx_xxx01011'],
    ['movimm16',    'xxxxxxxx_xxxxxxxx_xxxxxxxx_xxx00011'],
    ['movtimm32',   'xxx1xxxx_xxxxxxxx_xxxxxxxx_xxx01011'],
    ['movts16',     'xxxxxxxx_xxxxxxxx_xxxxxx01_00000010'],
    ['movts32',     'xxxxxxxx_xxxx0010_xxxxxx01_00001111'],
    ['movfs16',     'xxxxxxxx_xxxxxxxx_xxxxxx01_00010010'],
    ['movfs32',     'xxxxxxxx_xxxx0010_xxxxxx01_00011111'],
    # Jumps.
    ['jr32',        'xxxxxxxx_xxxx0010_xxxxxx01_01001111'],
    ['jr16',        'xxxxxxxx_xxxxxxxx_xxxxxx01_01000010'],
    ['jalr32',      'xxxxxxxx_xxxx0010_xxxxxx01_01011111'],
    ['jalr16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_01010010'],
    # Interrupts, multicore and control.
    ['nop16',       'xxxxxxxx_xxxxxxxx_xxxxxx01_10100010'],
    ['idle16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_10110010'],
    ['bkpt16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_11000010'],
    ['mbkpt16',     'xxxxxxxx_xxxxxxxx_xxxxxx11_11000010'],
    ['gie16',       'xxxxxxxx_xxxxxxxx_xxxxxx01_10010010'],
    ['gid16',       'xxxxxxxx_xxxxxxxx_xxxxxx11_10010010'],
    ['sync16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_11110010'],
    ['rti16',       'xxxxxxxx_xxxxxxxx_xxxxxx01_11010010'],
    ['swi16',       'xxxxxxxx_xxxxxxxx_xxxxxx01_11100010'],
    ['trap16',      'xxxxxxxx_xxxxxxxx_xxxxxx11_11100010'],
    ['wand16',      'xxxxxxxx_xxxxxxxx_xxxxxx01_10000010'],
    ['unimpl',      'xxxxxxxx_xxxx1111_xxxxxx00_00001111'],
]


# Branch instructions
execute_bcond32 = execute_branch.make_bcond_executor(False)
execute_bcond16 = execute_branch.make_bcond_executor(True)

# Load / store instructions
execute_ldstrpmd32  = execute_load_store.execute_ldstrpmd32
execute_ldstrdisp16 = execute_load_store.make_ldstrdisp_executor(True)
execute_ldstrdisp32 = execute_load_store.make_ldstrdisp_executor(False)
execute_ldstrind16  = execute_load_store.make_ldstrind_executor(True)
execute_ldstrind32  = execute_load_store.make_ldstrind_executor(False)
execute_ldstrpm16   = execute_load_store.make_ldstrpm_executor(True)
execute_ldstrpm32   = execute_load_store.make_ldstrpm_executor(False)
execute_testset32   = execute_load_store.testset32

# Bitwise instructions
execute_sub32     = execute_bitwise.make_addsub_executor(False, 'sub')
execute_sub16     = execute_bitwise.make_addsub_executor(True, 'sub')
execute_add32     = execute_bitwise.make_addsub_executor(False, 'add')
execute_add16     = execute_bitwise.make_addsub_executor(True, 'add')
execute_and16     = execute_bitwise.make_bit_executor("and", True,  False)
execute_orr16     = execute_bitwise.make_bit_executor("orr", True,  False)
execute_eor16     = execute_bitwise.make_bit_executor("eor", True,  False)
execute_asr16     = execute_bitwise.make_bit_executor("asr", True,  False)
execute_lsr16     = execute_bitwise.make_bit_executor("lsr", True,  False)
execute_lsl16     = execute_bitwise.make_bit_executor("lsl", True,  False)
execute_and32     = execute_bitwise.make_bit_executor("and", False, False)
execute_orr32     = execute_bitwise.make_bit_executor("orr", False, False)
execute_eor32     = execute_bitwise.make_bit_executor("eor", False, False)
execute_asr32     = execute_bitwise.make_bit_executor("asr", False, False)
execute_lsr32     = execute_bitwise.make_bit_executor("lsr", False, False)
execute_lsl32     = execute_bitwise.make_bit_executor("lsl", False, False)
execute_lsrimm16  = execute_bitwise.make_bit_executor("lsr",  True, True)
execute_lslimm16  = execute_bitwise.make_bit_executor("lsl",  True, True)
execute_asrimm16  = execute_bitwise.make_bit_executor("asr",  True, True)
execute_bitrimm16 = execute_bitwise.make_bit_executor("bitr", True, True)
execute_lsrimm32  = execute_bitwise.make_bit_executor("lsr",  False, True)
execute_lslimm32  = execute_bitwise.make_bit_executor("lsl",  False, True)
execute_asrimm32  = execute_bitwise.make_bit_executor("asr",  False, True)
execute_bitrimm32 = execute_bitwise.make_bit_executor("bitr", False, True)

# Floating point and integer arithmetic.
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

# Move instructions
execute_movcond32 = execute_mov.make_movcond_executor(False)
execute_movcond16 = execute_mov.make_movcond_executor(True)
execute_movtimm32 = execute_mov.make_movimm_executor(False, True)
execute_movimm32  = execute_mov.make_movimm_executor(False, False)
execute_movimm16  = execute_mov.make_movimm_executor(True,  False)
execute_movts32   = execute_mov.make_mov_executor(False, rd_is_special=True)
execute_movts16   = execute_mov.make_mov_executor(True,  rd_is_special=True)
execute_movfs32   = execute_mov.make_mov_executor(False, rn_is_special=True)
execute_movfs16   = execute_mov.make_mov_executor(True,  rn_is_special=True)

# Jump instructions
execute_jr32   = execute_jump.make_jr_executor(False, save_lr=False)
execute_jr16   = execute_jump.make_jr_executor(True,  save_lr=False)
execute_jalr32 = execute_jump.make_jr_executor(False, save_lr=True)
execute_jalr16 = execute_jump.make_jr_executor(True,  save_lr=True)

# Interrupt and multicore instructions
execute_nop16   = execute_interrupts.execute_nop16
execute_idle16  = execute_interrupts.execute_idle16
execute_bkpt16  = execute_interrupts.execute_bkpt16
execute_mbkpt16 = execute_interrupts.execute_mbkpt16
execute_gie16   = execute_interrupts.execute_gie16
execute_gid16   = execute_interrupts.execute_gid16
execute_sync16  = execute_interrupts.execute_sync16
execute_rti16   = execute_interrupts.execute_rti16
execute_swi16   = execute_interrupts.execute_swi16
execute_wand16  = execute_interrupts.execute_wand16
execute_trap16  = execute_interrupts.execute_trap16
execute_unimpl  = execute_interrupts.execute_unimpl

# Create Decoder
decode = create_risc_decoder(encodings, globals(), debug=True)
