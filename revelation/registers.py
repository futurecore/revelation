from collections import OrderedDict

LOCAL_PC_ADDRESS = 0xf0408


def get_address_of_register_by_name(register_name):
    for reg_index in reg_memory_map:  # reg_memory_map at end of file.
        if reg_memory_map[reg_index][2] == register_name:
            return reg_memory_map[reg_index][0]


def get_register_size_by_address(register_address):
    """Returns size of register in bits.
    """
    size = 32  # __special_purpose_registers at end of file.
    for address, size, _ in _special_purpose_registers:
        if address == register_address:
            break
    return size


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


_special_purpose_registers = [
    (0xf0400, 32, 'CONFIG'),       # Core configuration
    (0xf0404, 32, 'STATUS'),       # Core status
    (0xf0408, 32, 'pc'),           # Program counter
    (0xf040c, 32, 'DEBUGSTATUS'),  # Debug status
    (0xf0414, 32, 'LC'),           # Hardware counter loop
    (0xf0418, 32, 'LS'),           # Hardware counter start address
    (0xf041c, 32, 'LE'),           # Hardware counter end address
    (0xf0420, 32, 'IRET'),         # Interrupt PC return address
    (0xf0424, 10, 'IMASK'),        # Interrupt mask
    (0xf0428, 10, 'ILAT'),         # Interrupt latch
    (0xf042c, 10, 'ILATST'),       # Alias for setting interrupts
    (0xf0430, 10, 'ILATCL'),       # Alias for clearing interrupts
    (0xf0434, 10, 'IPEND'),        # Interrupt currently in progress
    (0xf0440, 32, 'FSTATUS'),      # Alias for writing to all STATUS bits
    (0xf0448, 2, 'DEBUGCMD'),     # Debug command register (2 bits)
    (0xf070c, 1, 'RESETCORE'),    # Per core software reset (1 bit)
    # Event timer registers
    (0xf0438, 32, 'CTIMER0'),      # Core timer 0
    (0xf043c, 32, 'CTIMER1'),      # Core timer 1
    # Process control registers
    (0xf0604, 3, 'MEMSTATUS'),    # Memory protection status
                                  # Epiphany IV: 14 bits, III: 1 bit ([2])
    (0xf0608, 8, 'MEMPROTECT'),   # Memory protection registration
                                  # Epiphany IV: 16 bits, III: 8 bits.
    # DMA registers
    (0xf0500, 32, 'DMA0CONFIG'),   # DMA channel 0 configuration
    (0xf0504, 32, 'DMA0STRIDE'),   # DMA channel 0 stride
    (0xf0508, 32, 'DMA0COUNT'),    # DMA channel 0 count
    (0xf050c, 32, 'DMA0SRCADDR'),  # DMA channel 0 source address
    (0xf0510, 32, 'DMA0DSTADDR'),  # DMA channel 0 destination address
    (0xf0514, 32, 'DMA0AUTO0'),    # DMA channel 0 slave lower data
    (0xf0518, 32, 'DMA0AUTO1'),    # DMA channel 0 slave upper data
    (0xf051c, 32, 'DMA0STATUS'),   # DMA channel 0 status
    (0xf0520, 32, 'DMA1CONFIG'),   # DMA channel 1 configuration
    (0xf0524, 32, 'DMA1STRIDE'),   # DMA channel 1 stride
    (0xf0528, 32, 'DMA1COUNT'),    # DMA channel 1 count
    (0xf052c, 32, 'DMA1SRCADDR'),  # DMA channel 1 source address
    (0xf0530, 32, 'DMA1DSTADDR'),  # DMA channel 1 destination address
    (0xf0534, 32, 'DMA1AUTO0'),    # DMA channel 1 slave lower data
    (0xf0538, 32, 'DMA1AUTO1'),    # DMA channel 1 slave upper data
    (0xf053c, 32, 'DMA1STATUS'),   # DMA channel 1 status
    # Mesh node control registers
    (0xf0700, 16, 'MESHCONFIG'),   # Mesh node configuration
    (0xf0704, 12, 'COREID'),       # Processor core ID (12 bits)
    (0xf0708, 12, 'MULTICAST'),    # Multicast configuration
    (0xf0710, 12, 'CMESHROUTE'),   # cMesh routing configuration (12 bits)
    (0xf0714, 12, 'XMESHROUTE'),   # xMesh routing configuration (12 bits)
    (0xf0718, 12, 'RMESHROUTE'),   # rMesh routing configuration (12 bits)
]


# Register number -> (memory address, num bytes, name)
reg_memory_map = OrderedDict()
# Add general purpose registers to register_map.
for index, address in enumerate(xrange(0xf0000, 0xf0100, 0x4)):
    reg_memory_map[index] = (address, 32, 'r%d' % ((address - 0xf0000) / 0x4))
# Add special purpose registers to _register_map.
for index in xrange(len(_special_purpose_registers)):
    reg_memory_map[index + 64] = _special_purpose_registers[index]
