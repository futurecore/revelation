from pydgin.debug import Debug, pad, pad_hex

from revelation.registers import reg_memory_map


def is_local_address(address):
    return (address >> 20) == 0x0


def is_register_address(address):
    return address >= 0xf0000 and address <= 0xf0718


class _BlockMemory(object):
    """32MB block of memory, initialised to zero.
    """

    def __init__(self, size=2**10, logger=None):
        """Initialise all memory to zero, as we don't know which memory.
        segments might hold memory-mapped registers.
        """
        self.data = ['\0'] * size
        self.size = len(self.data)

    def read(self, start_addr, num_bytes):
        value = 0
        for i in range(num_bytes - 1, -1, -1):
            value = value << 8
            value = value | ord(self.data[start_addr + i])
        return value

    def iread(self, start_addr, num_bytes):
        """This is instruction read, which is otherwise identical to read. The
        only difference is the elidable annotation, which we assume the
        instructions are not modified (no side effects, assumes the addresses
        correspond to the same instructions).
        """
        value = 0
        for i in range(num_bytes - 1, -1, -1):
            value = value << 8
            value = value | ord(self.data[start_addr + i])
        return value

    def write(self, start_addr, num_bytes, value, from_core=0x808):
        for i in range(num_bytes):
            self.data[start_addr + i] = chr(value & 0xff)
            value = value >> 8


class Memory(object):
    """Sparse memory model adapted from Pydgin.
    """

    def __init__(self, block_size=2**20, logger=None):
        self.block_size = block_size
        self.debug = Debug()
        self.logger = logger
        self.first_core = 0x808
        self.addr_mask  = block_size - 1
        self.block_mask = 0xffffffff ^ self.addr_mask
        self.block_dict = {}
        self.code_blocks = []

    def add_block(self, block_addr):
        self.block_dict[block_addr] = _BlockMemory(size=self.block_size)

    def get_block_mem(self, block_addr):
        if block_addr not in self.block_dict:
            self.add_block(block_addr)
        block_mem = self.block_dict[block_addr]
        return block_mem

    def iread(self, start_addr, num_bytes, from_core=0x808):
        if is_local_address(start_addr):
            start_addr |= (from_core << 20)
        end_addr   = start_addr + num_bytes - 1
        block_addr = self.block_mask & start_addr
        block_mem = self.get_block_mem(block_addr)
        # For mixed-width ISAs, the start_addr is not necessarily
        # word-aligned, and can cross block memory boundaries. If there is
        # such a case, we have two instruction reads and then form the word
        # for it.
        block_end_addr = self.block_mask & end_addr
        if block_addr == block_end_addr:
            value = block_mem.iread(start_addr & self.addr_mask, num_bytes)
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

    def read(self, start_addr, num_bytes, from_core=0x808):
        if is_local_address(start_addr):
            start_addr |= (from_core << 20)
        block_addr = self.block_mask & start_addr
        block_mem = self.get_block_mem(block_addr)
        masked_addr = 0xfffff & start_addr
        value = block_mem.read(start_addr & self.addr_mask, num_bytes)
        if (self.debug.enabled('mem') and self.logger and
              not is_register_address(masked_addr) and
              (start_addr >> 20) == self.first_core):
            if start_addr >> 20 == from_core:
                start_addr = start_addr & 0xfffff
            self.logger.log(' :: RD.MEM[%s] = %s' % \
                              (pad_hex(start_addr), pad_hex(value)))
        return value

    def write(self, start_addr, num_bytes, value, from_core=0x808, quiet=False):
        """Deal with register writes that are aliases to other locations. Better
        not to put these in the instruction semantics, as the aliased
        registers may be written to by a variety of instructions, and accessed
        as either registers or memory locations.
        """
        if is_local_address(start_addr):
            start_addr |= (from_core << 20)
        coreid_mask = start_addr & 0xfff00000
        for start, end in self.code_blocks:
            if start_addr >= start and (start_addr + num_bytes) <= end:
                print 'WARNING: self-modifying code @', pad_hex(start_addr)
        if start_addr & 0xfffff == 0xf042c:  # ILATST
            ilat = self.read(coreid_mask | 0xf0428, 4) & 0x3ff
            ilat |= (value & ((2 << 10) - 1))
            self.write(coreid_mask | 0xf0428, 4, ilat)
        elif start_addr & 0xfffff == 0xf0430:  # ILATCL
            ilat = self.read(coreid_mask | 0xf0428, 4) & 0x3ff
            ilat &= ~(value &  ((2 << 10) - 1))
            self.write(coreid_mask | 0xf0428, 4, ilat)
        elif start_addr & 0xfffff == 0xf0440:  # FSTATUS
            status = self.read(coreid_mask | 0xf0404, 4)
            status |= (value & 0xfffffffc)  # Can't write to lowest 2 bits.
            self.write(coreid_mask | 0xf0404, 4, status)
        elif start_addr & 0xfffff == 0xf0438 and value == 0:  # CTIMER0 expired.
            ilat = self.read(coreid_mask | 0xf0428, 4) & 0x3ff
            ilat |= 0x8
            self.write(coreid_mask | 0xf0428, 4, ilat)
        elif start_addr & 0xfffff == 0xf043c and value == 0:  # CTIMER1 expired.
            ilat = self.read(coreid_mask | 0xf0428, 4) & 0x3ff
            ilat |= 0x10
            self.write(coreid_mask | 0xf0428, 4, ilat)
        block_addr = self.block_mask & start_addr
        block_mem = self.get_block_mem(block_addr)
        block_mem.write(start_addr & self.addr_mask, num_bytes, value)
        masked_addr = 0xfffff & start_addr
        if (self.debug.enabled('mem') and self.logger and not quiet and
              not is_register_address(masked_addr) and
              (start_addr >> 20) == self.first_core):
            if start_addr >> 20 == from_core:
                start_addr = start_addr & 0xfffff
            self.logger.log(' :: WR.MEM[%s] = %s' % \
                              (pad_hex(start_addr), pad_hex(value)))


class MemoryMappedRegisterFile(object):
    """Simulate the memory-mapped registers of a single Epiphany core.
    Note that memory objects can only read and write aligned words.
    """

    def __init__(self, memory, coreid, logger):
        self.debug = Debug()
        self.logger = logger
        self.memory = memory
        self.coreid = coreid
        self.coreid_mask = coreid << 20
        self.is_first_core = False
        self.memory.write(self.coreid_mask | 0xf0704, 4, coreid & 0xfff,
                          from_core=coreid, quiet=True)
        self.num_regs = len(reg_memory_map)
        self.debug_nchars = 8

    def __getitem__(self, index):
        address, bitsize, _ = reg_memory_map[index]
        mask = (1 << bitsize) - 1
        value = self.memory.iread(address, 4, from_core=self.coreid) & mask
        if (self.debug.enabled('rf') and self.logger and index < 64 and
              self.is_first_core):
            self.logger.log(' :: RD.RF[%s] = %s' % (pad('%d' % index, 2),
                              pad_hex(value, len=self.debug_nchars)))
        return value

    def __setitem__(self, index, value):
        if index == 0x65:  # COREID register. Read only. Other Read/Write only
            return         # registers need to be accessed by instructions.
        address, bitsize, _ = reg_memory_map[index]  # Lower 20 bits of address.
        mask = (1 << bitsize) - 1
        self.memory.write(self.coreid_mask | address, 4, value & mask,
                                 from_core=self.coreid, quiet=True)
        if (self.debug.enabled('rf') and self.logger and index < 64 and
              self.is_first_core):
            self.logger.log(' :: WR.RF[%s] = %s' % ((pad('%d' % index, 2),
                              pad_hex(value, len=self.debug_nchars))))
