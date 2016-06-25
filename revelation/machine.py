#=======================================================================
# machine.py
#=======================================================================

from pydgin.debug import Debug, pad, pad_hex
from pydgin.machine import Machine
from pydgin.storage import Memory
from pydgin.utils import r_uint, specialize

from revelation.isa import reg_map

try:
    from rpython.rlib.rarithmetic import intmask
except ImportError:
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
# RegisterFile
#-----------------------------------------------------------------------
class RegisterFile( object ):
    def __init__(self, constant_zero=True, num_regs=32, nbits=32):
        self.num_regs = num_regs
        self.regs = [r_uint(0)] * self.num_regs
        self.debug = Debug()
        self.nbits = nbits
        self.debug_nchars = nbits / 4
        # Ignore constant_zero, but keep it here to maintain
        # compatibility with Pydgin.

    def __getitem__(self, idx):
        if self.debug.enabled('rf') and idx < 64:
            print (':: RD.RF[%s] = %s' %
                   (pad('%d' % idx, 2),
                    pad_hex(self.regs[idx], len=self.debug_nchars))),
        return intmask(self.regs[idx])

    @specialize.argtype(2)
    def __setitem__(self, idx, value):
        self.regs[idx] = r_uint(value)
        if self.debug.enabled('rf') and idx < 64:
            print (':: WR.RF[%s] = %s' %
                   (pad('%d' % idx, 2),
                    pad_hex(self.regs[idx], len=self.debug_nchars))),


#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State(Machine):
    _virtualizable_ = ['pc', 'num_insts']

    def __init__(self, memory, debug, reset_addr=RESET_ADDR):
        Machine.__init__(self,
                         memory,
                         RegisterFile(constant_zero=False, num_regs=107),
                         debug,
                         reset_addr=RESET_ADDR)
        # Epiphany III exceptions.
        self.exceptions = { 'UNIMPLEMENTED'  : 0b0100,
                            'SWI'            : 0b0001,
                            'UNALIGNED'      : 0b0010,
                            'ILLEGAL ACCESS' : 0b0101,
                            'FPU EXCEPTION'  : 0b0011,
        }

    def get_pending_interrupt(self):
        ipend_highest_bit = -1
        for index in range(10):
            if (self.rf[reg_map['IPEND']] & (1 << index)):
                ipend_highest_bit = index
                break
        return ipend_highest_bit

    def get_lateched_interrupt(self):
        ilat_highest_bit= -1
        for index in range(10):
            if ((self.rf[reg_map['ILAT']] & (1 << index)) and
                not (self.rf[reg_map['IMASK']] & (1 << index))):
                ilat_highest_bit = index
                break
        return ilat_highest_bit

    def _get_nth_bit_of_register(self, register, n):
        return bool(self.rf[reg_map[register]] & (1 << n))

    def _set_nth_bit_of_register(self, register, n, value):
        if value:
            self.rf[reg_map[register]] |= (1 << n)
        else:
             self.rf[reg_map[register]] &= ~(1 << n)

    @property
    def ACTIVE(self):
        return self._get_nth_bit_of_register('STATUS', 0)

    @ACTIVE.setter
    def ACTIVE(self, value):
        self._set_nth_bit_of_register('STATUS', 0, value)

    @property
    def GID(self):
        return self._get_nth_bit_of_register('STATUS', 1)

    @GID.setter
    def GID(self, value):
        self._set_nth_bit_of_register('STATUS', 1, value)

    @property
    def SUPERUSER(self):
        return self._get_nth_bit_of_register('STATUS', 2)

    @SUPERUSER.setter
    def SUPERUSER(self, value):
        self._set_nth_bit_of_register('STATUS', 2, value)

    @property
    def WAND(self):
        return self._get_nth_bit_of_register('STATUS', 3)

    @WAND.setter
    def WAND(self, value):
        self._set_nth_bit_of_register('STATUS', 3, value)

    @property
    def AZ(self):
        return self._get_nth_bit_of_register('STATUS', 4)

    @AZ.setter
    def AZ(self, value):
        self._set_nth_bit_of_register('STATUS', 4, value)

    @property
    def AN(self):
        return self._get_nth_bit_of_register('STATUS', 5)

    @AN.setter
    def AN(self, value):
        self._set_nth_bit_of_register('STATUS', 5, value)

    @property
    def AC(self):
        return self._get_nth_bit_of_register('STATUS', 6)

    @AC.setter
    def AC(self, value):
        self._set_nth_bit_of_register('STATUS', 6, value)

    @property
    def AV(self):
        return self._get_nth_bit_of_register('STATUS', 7)

    @AV.setter
    def AV(self, value):
        self._set_nth_bit_of_register('STATUS', 7, value)

    @property
    def BZ(self):
        return self._get_nth_bit_of_register('STATUS', 8)

    @BZ.setter
    def BZ(self, value):
        self._set_nth_bit_of_register('STATUS', 8, value)

    @property
    def BN(self):
        return self._get_nth_bit_of_register('STATUS', 9)

    @BN.setter
    def BN(self, value):
        self._set_nth_bit_of_register('STATUS', 9, value)

    @property
    def BV(self):
        return self._get_nth_bit_of_register('STATUS', 10)

    @BV.setter
    def BV(self, value):
        self._set_nth_bit_of_register('STATUS', 10, value)

    @property
    def AVS(self):
        return self._get_nth_bit_of_register('STATUS', 12)

    @AVS.setter
    def AVS(self, value):
        self._set_nth_bit_of_register('STATUS', 12, value)

    @property
    def BIS(self):
        return self._get_nth_bit_of_register('STATUS', 13)

    @BIS.setter
    def BIS(self, value):
        self._set_nth_bit_of_register('STATUS', 13, value)

    @property
    def BVS(self):
        return self._get_nth_bit_of_register('STATUS', 14)

    @BVS.setter
    def BVS(self, value):
        self._set_nth_bit_of_register('STATUS', 14, value)

    @property
    def BUS(self):
        return self._get_nth_bit_of_register('STATUS', 15)

    @BUS.setter
    def BUS(self, value):
        self._set_nth_bit_of_register('STATUS', 15, value)

    @property
    def EXCAUSE(self):
        print 'STATUS', bin(self.rf[reg_map['STATUS']])
        return (self.rf[reg_map['STATUS']] >> 16) & 0xf

    @EXCAUSE.setter
    def EXCAUSE(self, value):
        self._set_nth_bit_of_register('STATUS', 16, value & 0x1)
        self._set_nth_bit_of_register('STATUS', 17, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('STATUS', 18, (value >> 2) & 0x1)
        self._set_nth_bit_of_register('STATUS', 19, (value >> 3) & 0x1)

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
