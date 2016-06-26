from collections import OrderedDict
from pydgin.debug import Debug, pad, pad_hex
from pydgin.jit import elidable, unroll_safe, hint
from pydgin.utils import specialize


#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
def Memory(data=None, size=2**10):
    try:
        from rpython.rlib.objectmodel import we_are_translated
        sparse_storage = not we_are_translated()
    except ImportError:
        sparse_storage = True
    if not sparse_storage:
        return _ByteMemory(data, size)
    else:
        print "NOTE: Using sparse storage"
        return _SparseMemory(_ByteMemory)


#-----------------------------------------------------------------------
# _ByteMemory
#-----------------------------------------------------------------------
class _ByteMemory(object):
    def __init__(self, data=None, size=2**10):
        self.data  = data if data else [' '] * size
        self.size  = len(self.data)
        self.debug = Debug()

    def bounds_check(self, addr):
        # Check if the accessed data is larger than the memory size.
        if addr > self.size:
            print 'WARNING: accessing larger address than memory size. ' + \
                'addr=%s size=%s' % (pad_hex(addr), pad_hex(self.size))
        if addr == 0:
            print 'WARNING: writing null pointer!'
            raise Exception()

    @unroll_safe
    def read(self, start_addr, num_bytes):
        if self.debug.enabled('memcheck'):
            self.bounds_check(start_addr)
        value = 0
        if (self.debug.enabled('mem') and
              (start_addr < 0xf0000 or start_addr > 0xf0718)):
            print ':: RD.MEM[%s] = ' % pad_hex(start_addr),
        for i in range(num_bytes - 1, -1, -1):
            value = value << 8
            value = value | ord(self.data[start_addr + i])
        if self.debug.enabled('mem'):
            print '%s' % pad_hex(value),
        return value

    # this is instruction read, which is otherwise identical to read. The
    # only difference is the elidable annotation, which we assume the
    # instructions are not modified (no side effects, assumes the addresses
    # correspond to the same instructions)
    @elidable
    def iread(self, start_addr, num_bytes):
        value = 0
        for i in range(num_bytes - 1, -1, -1):
            value = value << 8
            value = value | ord(self.data[start_addr + i])
        return value

    @unroll_safe
    def write(self, start_addr, num_bytes, value):
        if self.debug.enabled('memcheck'):
            self.bounds_check(start_addr)
        if (self.debug.enabled('mem') and
              (start_addr < 0xf0000 or start_addr > 0xf0718)):
            print ':: WR.MEM[%s] = %s' % (pad_hex(start_addr), pad_hex(value)),
        for i in range(num_bytes):
            self.data[start_addr + i] = chr(value & 0xff)
            value = value >> 8


#-----------------------------------------------------------------------
# _SparseMemory
#-----------------------------------------------------------------------
class _SparseMemory(object):
    _immutable_fields_ = ['BlockMemory', 'block_size', 'addr_mask', 'block_mask']

    def __init__(self, BlockMemory, block_size=2**10):
        self.BlockMemory = BlockMemory
        self.block_size = block_size
        self.addr_mask  = block_size - 1
        self.block_mask = 0xffffffff ^ self.addr_mask
        self.debug = Debug()
        print 'sparse memory size %x addr mask %x block mask %x' \
              % (self.block_size, self.addr_mask, self.block_mask)
        self.block_dict = {}
        self.debug = Debug()

    def add_block(self, block_addr):
        self.block_dict[block_addr] = self.BlockMemory(size=self.block_size)

    @elidable
    def get_block_mem(self, block_addr):
        if block_addr not in self.block_dict:
            self.add_block(block_addr)
        block_mem = self.block_dict[block_addr]
        return block_mem

    @elidable
    def iread(self, start_addr, num_bytes):
        start_addr = hint(start_addr, promote=True)
        num_bytes  = hint(num_bytes,  promote=True)
        end_addr   = start_addr + num_bytes - 1
        block_addr = self.block_mask & start_addr
        block_mem = self.get_block_mem(block_addr)
        # For mixed-width ISAs, the start_addr is not necessarily
        # word-aligned, and can cross block memory boundaries. If there is
        # such a case, we have two instruction reads and then form the word
        # for it
        block_end_addr = self.block_mask & end_addr
        if block_addr == block_end_addr:
            return block_mem.iread(start_addr & self.addr_mask, num_bytes)
        else:
            num_bytes1 = min(self.block_size - (start_addr & self.addr_mask),
                             num_bytes)
            num_bytes2 = num_bytes - num_bytes1
            block_mem1 = block_mem
            block_mem2 = self.get_block_mem(block_end_addr)
            value1 = block_mem1.iread(start_addr & self.addr_mask, num_bytes1)
            value2 = block_mem2.iread(0, num_bytes2)
            value = value1 | (value2 << (num_bytes1 * 8))
            return value

    def read(self, start_addr, num_bytes):
        if (self.debug.enabled('mem') and
              (start_addr < 0xf0000 or start_addr > 0xf0718)):
            print ':: RD.MEM[%s] = ' % pad_hex(start_addr),
        block_addr = self.block_mask & start_addr
        block_addr = hint(block_addr, promote=True)
        block_mem = self.get_block_mem(block_addr)
        value = block_mem.read(start_addr & self.addr_mask, num_bytes)
        if (self.debug.enabled('mem') and
              (start_addr < 0xf0000 or start_addr > 0xf0718)):
            print '%s' % pad_hex(value),
        return value

    def write(self, start_addr, num_bytes, value):
        if (self.debug.enabled('mem') and
              (start_addr < 0xf0000 or start_addr > 0xf0718)):
            print ':: WR.MEM[%s] = %s' % (pad_hex(start_addr), pad_hex(value)),
        block_addr = self.block_mask & start_addr
        block_addr = hint(block_addr, promote=True)
        block_mem = self.get_block_mem(block_addr)
        block_mem.write(start_addr & self.addr_mask, num_bytes, value)


#-----------------------------------------------------------------------
# MemoryMappedRegisterFile
#-----------------------------------------------------------------------
class MemoryMappedRegisterFile(object):
    """Simulate the memory-mapped registers of a single Epiphany core.
    FIXME: Use correct bit-width for registers whose width is not a
    multiple of 8. Note that memory objects can only read and write
    aligned words.
    """
    def __init__(self, memory):
        self.debug    = Debug()
        self.memory = memory
        self.num_regs = len(_register_map)
        self.debug_nchars = 8
        # All registers hold zero when the simulator starts.
        for index in _register_map:
            self.__setitem__(index, 0)
        return

    def __getitem__(self, index):
        address, nbytes, _ = _register_map[index]
        value = self.memory.read(address, nbytes)
        if self.debug.enabled('rf') and index < 64:
            print (':: RD.RF[%s] = %s' % (pad('%d' % index, 2),
                    pad_hex(value, len=self.debug_nchars))),
        return value

    @specialize.argtype(2)
    def __setitem__(self, index, value):
        address, nbytes, _ = _register_map[index]
        self.memory.write(address, nbytes, value)
        if self.debug.enabled('rf') and index < 64:
            print (':: WR.RF[%s] = %s' % ((pad('%d' % index, 2),
                   pad_hex(value, len=self.debug_nchars)))),

    def print_regs(self, per_row=6):
        """Prints all registers (register dump).
        per_row specifies the number of registers to display per row.
        """
        for col in xrange(0, self.num_regs, per_row):
            line = ''
            for row in xrange(col, min(self.num_regs, col + per_row)):
                _, _, name = _register_map[row]
                value = self.__getitem__(row)
                line += '%s:%s ' % (pad('%s' % name, 2), pad_hex(value))
            print line


def get_address_of_register_by_name(register_name):
    for reg_index in _register_map:
        if _register_map[reg_index][2] == register_name:
            return _register_map[reg_index][0]


_special_purpose_registers = [
    (0xf0400, 4, 'CONFIG'),       # Core configuration
    (0xf0404, 4, 'STATUS'),       # Core status
    (0xf0408, 4, 'pc'),           # Program counter
    (0xf040c, 4, 'DEBUGSTATUS'),  # Debug status
    (0xf0414, 4, 'LC'),           # Hardware counter loop
    (0xf0418, 4, 'LS'),           # Hardware counter start address
    (0xf041c, 4, 'LE'),           # Hardware counter end address
    (0xf0420, 4, 'IRET'),         # Interrupt PC return address
    (0xf0424, 4, 'IMASK'),        # Interrupt mask
    (0xf0428, 4, 'ILAT'),         # Interrupt latch
    (0xf042c, 4, 'ILATST'),       # Alias for setting interrupts
    (0xf0430, 4, 'ILATCL'),       # Alias for clearing interrupts
    (0xf0434, 4, 'IPEND'),        # Interrupt currently in progress
    (0xf0440, 4, 'FSTATUS'),      # Alias for writing to all STATUS bits
    (0xf0448, 1, 'DEBUGCMD'),     # Debug command register (2 bits)
    (0xf070c, 1, 'RESETCORE'),    # Per core software reset (1 bit)
    # Event timer registers
    (0xf0438, 4, 'CTIMER0'),      # Core timer 0
    (0xf043c, 4, 'CTIMER1'),      # Core timer 1
    # Process control registers
    (0xf0604, 2, 'MEMSTATUS'),    # Memory protection status
                                  # Epiphany IV: 14 bits, III: 1 bit ([2])
    (0xf0608, 2, 'MEMPROTECT'),   # Memory protection registration
                                  # Epiphany IV: 16 bits, III: 8 bits.
    # DMA registers
    (0xf0500, 4, 'DMA0CONFIG'),   # DMA channel 0 configuration
    (0xf0504, 4, 'DMA0STRIDE'),   # DMA channel 0 stride
    (0xf0508, 4, 'DMA0COUNT'),    # DMA channel 0 count
    (0xf050c, 4, 'DMA0SRCADDR'),  # DMA channel 0 source address
    (0xf0510, 4, 'DMA0DSTADDR'),  # DMA channel 0 destination address
    (0xf0514, 4, 'DMA0AUTO0'),    # DMA channel 0 slave lower data
    (0xf0518, 4, 'DMA0AUTO1'),    # DMA channel 0 slave upper data
    (0xf051c, 4, 'DMA0STATUS'),   # DMA channel 0 status
    (0xf0520, 4, 'DMA1CONFIG'),   # DMA channel 1 configuration
    (0xf0524, 4, 'DMA1STRIDE'),   # DMA channel 1 stride
    (0xf0528, 4, 'DMA1COUNT'),    # DMA channel 1 count
    (0xf052c, 4, 'DMA1SRCADDR'),  # DMA channel 1 source address
    (0xf0530, 4, 'DMA1DSTADDR'),  # DMA channel 1 destination address
    (0xf0534, 4, 'DMA1AUTO0'),    # DMA channel 1 slave lower data
    (0xf0538, 4, 'DMA1AUTO1'),    # DMA channel 1 slave upper data
    (0xf053c, 4, 'DMA1STATUS'),   # DMA channel 1 status
    # Mesh node control registers
    (0xf0700, 2, 'MESHCONFIG'),   # Mesh node configuration
    (0xf0704, 3, 'COREID'),       # Processor core ID (12 bits)
    (0xf0708, 4, 'MULTICAST'),    # Multicast configuration
    (0xf0710, 3, 'CMESHROUTE'),   # cMesh routing configuration (12 bits)
    (0xf0714, 3, 'XMESHROUTE'),   # xMesh routing configuration (12 bits)
    (0xf0718, 3, 'RMESHROUTE'),   # rMesh routing configuration (12 bits)
]


# Register number -> (memory address, num bytes, name)
_register_map = OrderedDict()
# Add general purpose registers to register_map.
for index, address in enumerate(xrange(0xf0000, 0xf0100, 0x4)):
    _register_map[index] = (address, 4, 'r%d' % ((address - 0xf0000) / 0x4))
# Add special purpose registers to _register_map.
for index in xrange(len(_special_purpose_registers)):
    _register_map[index + 64] = _special_purpose_registers[index]
