import revelation.execute_bitwise    as execute_bitwise
import revelation.execute_branch     as execute_branch
import revelation.execute_farith     as execute_farith
import revelation.execute_interrupt  as execute_interrupts
import revelation.execute_jump       as execute_jump
import revelation.execute_load_store as execute_load_store
import revelation.execute_mov        as execute_mov

from pydgin.misc import create_risc_decoder


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
    ['unimpl32',    'xxxxxxxx_xxxx1111_xxxxxx00_00001111'],
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
execute_float16 = execute_farith.make_float_executor(True)
execute_fix16   = execute_farith.make_fix_executor(True)
execute_fabs16  = execute_farith.make_fabs_executor(True)
execute_fadd32  = execute_farith.make_farith_executor('add', False)
execute_fsub32  = execute_farith.make_farith_executor('sub', False)
execute_fmul32  = execute_farith.make_farith_executor('mul', False)
execute_fmadd32 = execute_farith.make_farith_executor('madd', False)
execute_fmsub32 = execute_farith.make_farith_executor('msub', False)
execute_float32 = execute_farith.make_float_executor(False)
execute_fix32   = execute_farith.make_fix_executor(False)
execute_fabs32  = execute_farith.make_fabs_executor(False)

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
execute_nop16    = execute_interrupts.execute_nop16
execute_idle16   = execute_interrupts.execute_idle16
execute_bkpt16   = execute_interrupts.execute_bkpt16
execute_mbkpt16  = execute_interrupts.execute_mbkpt16
execute_gie16    = execute_interrupts.execute_gie16
execute_gid16    = execute_interrupts.execute_gid16
execute_sync16   = execute_interrupts.execute_sync16
execute_rti16    = execute_interrupts.execute_rti16
execute_swi16    = execute_interrupts.execute_swi16
execute_wand16   = execute_interrupts.execute_wand16
execute_trap16   = execute_interrupts.execute_trap16
execute_unimpl32 = execute_interrupts.execute_unimpl32

# Create Decoder
decode = create_risc_decoder(encodings, globals(), debug=True)
