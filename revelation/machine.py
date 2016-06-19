#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine
from pydgin.storage import Memory, RegisterFile

from revelation.isa import reg_map

try:
   from rpython.rlib.rarithmetic import r_uint, intmask
except ImportError:
    r_uint = lambda x : x
    intmask = lambda x : x

RESET_ADDR = 0


#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
class RevelationMemory(object):
    """Since the Epiphany has memory-mapped register files, we need to
    intercept any read / write which should actually go to the registers.

    FIXME: Correctly map address 0xf0408 to the program counter in State.
    """

    def __init__(self, data=None, size=2**32, byte_storage=True):
        self.memory = Memory(data=data, size=size, byte_storage=byte_storage)
        self.rf = None  # Set by Sim.init_state(). Also sets self.fetch_pc()
        self.debug = None  # Set after ELF file loaded.

    def set_debug(self, debug):
        self.debug = debug
        if self.debug.enabled('mem'):
            self.memory.debug.enabled_flags.append('mem')
        if self.debug.enabled('memcheck'):
            self.memory.debug.enabled_flags.append('memcheck')

    def iread(self, address, nbytes=4):
        if 0xf0718 >= address >= 0xf0000:
            _, reg_num = _register_map[r_uint(address)]
            return intmask(self.rf[reg_num])
        else:
            return self.memory.iread(address, nbytes)

    def read(self, address, nbytes=4):
        if 0xf0718 >= address >= 0xf0000:
            _, reg_num = _register_map[r_uint(address)]
            return intmask(self.rf[reg_num])
        else:
            return self.memory.read(address, nbytes)

    def write(self, address, nbytes, value):
        if 0xf0718 >= address >= 0xf0000:
            _, reg_num = _register_map[r_uint(address)]
            self.rf[r_uint(reg_num)] = r_uint(value)
        else:
            self.memory.write(address, nbytes, value)


#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State(Machine):
    _virtualizable_ = ['pc', 'num_insts', 'AN', 'AZ', 'AC', 'AV',
                       'AVS', 'BN', 'BIS', 'BUS', 'BVS', 'BZ']

    def __init__(self, memory, debug, reset_addr=RESET_ADDR):
        Machine.__init__(self,
                         memory,
                         RegisterFile(constant_zero=False, num_regs=107),
                         debug,
                         reset_addr=RESET_ADDR)

        # Epiphany-specific flags.
        self.AN  = False
        self.AZ  = False
        self.AC  = False
        self.AV  = False
        self.AVS = False
        self.BN  = False
        self.BZ  = False
        self.BIS = False
        self.BUS = False
        self.BV  = False
        self.BVS = False

    def fetch_pc(self):
        # Override method from base class. Needed by Pydgin.
        return self.pc

    def debug_flags(self):
        if self.debug.enabled('flags'):
            print ('AN=%s AZ=%s AC=%s AV=%s AVS=%s BN=%s BZ=%s BIS=%s BUS=%s BV=%s BVS=%s ' %
                   (self.AN, self.AZ, self.AC, self.AV, self.AVS,
                    self.BN, self.BZ, self.BIS, self.BUS, self.BV, self.BVS)),


def get_address_of_register_by_name(register_name):
    register_number = reg_map[register_name]
    for address in _register_map:
        if _register_map[address][1] == register_number:
            return address


_register_map = {
    # Memory location -> (size, register number)
    0xf0400 : (4, reg_map['CONFIG']),       # Core configuration
    0xf0404 : (4, reg_map['STATUS']),       # Core status
    0xf0408 : (4, reg_map['pc']),           # Program counter
    0xf040c : (4, reg_map['DEBUGSTATUS']),  # Debug status
    0xf0414 : (4, reg_map['LC']),           # Hardware counter loop
    0xf0418 : (4, reg_map['LS']),           # Hardware counter start address
    0xf041c : (4, reg_map['LE']),           # Hardware counter end address
    0xf0420 : (4, reg_map['IRET']),         # Interrupt PC return address
    0xf0424 : (4, reg_map['IMASK']),        # Interrupt mask
    0xf0428 : (4, reg_map['ILAT']),         # Interrupt latch
    0xf042c : (4, reg_map['ILATST']),       # Alias for setting interrupts
    0xf0430 : (4, reg_map['ILATCL']),       # Alias for clearing interrupts
    0xf0434 : (4, reg_map['IPEND']),        # Interrupt currently in progress
    0xf0440 : (4, reg_map['FSTATUS']),      # Alias for writing to all STATUS bits
    0xf0448 : (1, reg_map['DEBUGCMD']),     # Debug command register (2 bits)
    0xf070c : (1, reg_map['RESETCORE']),    # Per core software reset (1 bit)
    # Event timer registers
    0xf0438 : (4, reg_map['CTIMER0']),      # Core timer 0
    0xf043c : (4, reg_map['CTIMER1']),      # Core timer 1
    # Process control registers
    0xf0604 : (2, reg_map['MEMSTATUS']),    # Memory protection status
                                  # Epiphany IV: 14 bits, III: 1 bit ([2])
    0xf0608 : (2, reg_map['MEMPROTECT']),   # Memory protection registration
                                  # Epiphany IV: 16 bits, III: 8 bits.
    # DMA registers
    0xf0500 : (4, reg_map['DMA0CONFIG']),   # DMA channel 0 configuration
    0xf0504 : (4, reg_map['DMA0STRIDE']),   # DMA channel 0 stride
    0xf0508 : (4, reg_map['DMA0COUNT']),    # DMA channel 0 count
    0xf050c : (4, reg_map['DMA0SRCADDR']),  # DMA channel 0 source address
    0xf0510 : (4, reg_map['DMA0DSTADDR']),  # DMA channel 0 destination address
    0xf0514 : (4, reg_map['DMA0AUTO0']),    # DMA channel 0 slave lower data
    0xf0518 : (4, reg_map['DMA0AUTO1']),    # DMA channel 0 slave upper data
    0xf051c : (4, reg_map['DMA0STATUS']),   # DMA channel 0 status
    0xf0520 : (4, reg_map['DMA1CONFIG']),   # DMA channel 1 configuration
    0xf0524 : (4, reg_map['DMA1STRIDE']),   # DMA channel 1 stride
    0xf0528 : (4, reg_map['DMA1COUNT']),    # DMA channel 1 count
    0xf052c : (4, reg_map['DMA1SRCADDR']),  # DMA channel 1 source address
    0xf0530 : (4, reg_map['DMA1DSTADDR']),  # DMA channel 1 destination address
    0xf0534 : (4, reg_map['DMA1AUTO0']),    # DMA channel 1 slave lower data
    0xf0538 : (4, reg_map['DMA1AUTO1']),    # DMA channel 1 slave upper data
    0xf053c : (4, reg_map['DMA1STATUS']),   # DMA channel 1 status
    # Mesh node control registers
    0xf0700 : (2, reg_map['MESHCONFIG']),   # Mesh node configuration
    0xf0704 : (3, reg_map['COREID']),       # Processor core ID (12 bits)
    0xf0708 : (4, reg_map['MULTICAST']),    # Multicast configuration
    0xf0710 : (3, reg_map['CMESHROUTE']),   # cMesh routing configuration (12 bits)
    0xf0714 : (3, reg_map['XMESHROUTE']),   # xMesh routing configuration (12 bits)
    0xf0718 : (3, reg_map['RMESHROUTE']),   # rMesh routing configuration (12 bits)
}

# Add general purpose registers to register_map.
for index, address in enumerate(xrange(0xf0000, 0xf0100, 0x4)):
    _register_map[address] = (4, reg_map['r%d' % ((address - 0xf0000) / 0x4)])
