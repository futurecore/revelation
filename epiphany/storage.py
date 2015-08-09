from collections import OrderedDict
from pydgin.debug import Debug, pad, pad_hex


class EpiphanyRegisterFile(object):
    """Simulate the memory-mapped registers of a single Epiphany core.

    FIXME: Use correct bit-width for registers whose width is not a
    multiple of 8. Note that memory objects can only read and write
    aligned words.
    """
    def __init__(self, memory):
        self.debug    = Debug()
        self.memory = memory
        self.num_regs = len(register_map)
        # All registers hold zero when the simulator starts.
        for index in register_map:
            self.__setitem__(index, 0)
        return

    def __getitem__(self, index):
        address, nbytes, name = register_map[index]
        value = self.memory.read(address, nbytes)
        if self.debug.enabled('rf'):
            print ':: RD.RF[%s] = %s' % (name, pad_hex(value)),
        return value

    def __setitem__(self, index, value):
        address, nbytes, name = register_map[index]
        self.memory.write(address, nbytes, value)
        if self.debug.enabled('rf'):
            print ':: WR.RF[%s] = %s' % (name, pad_hex(value)),

    def get_register_by_address(self, address, nbytes=4):
        value = self.memory.read(address, nbytes)
        if self.debug.enabled('rf'):
            for index in register_map:  # pragma: no cover
                addr, _, name = register_map[index]
                if address == addr:
                    print ':: RD.RF[%s] = %s' % (name, pad_hex(value)),
        return value

    def set_register_by_address(self, address, value, nbytes=4):
        self.memory.write(address, nbytes, value)
        if self.debug.enabled('rf'):
            for index in register_map:  # pragma: no cover
                addr, _, name = register_map[index]
                if address == addr:
                    print ':: WR.RF[%s] = %s' % (name, pad_hex(value)),

    def print_regs(self, per_row=6):
        """Prints all registers (register dump).
        per_row specifies the number of registers to display per row.
        """
        for col in xrange(0, self.num_regs, per_row):
            line = ''
            for row in xrange(col, min(self.num_regs, col + per_row)):
                _, _, name = register_map[row]
                value = self.__getitem__(row)
                line += '%s:%s ' % (pad('%s' % name, 2), pad_hex(value))
            print line


_special_purpose_registers = [
    (0xF0400, 4, 'CONFIG'),       # Core configuration
    (0xF0404, 4, 'STATUS'),       # Core status
    (0xF0408, 4, 'pc'),           # Program counter
    (0xF040C, 4, 'DEBUGSTATUS'),  # Debug status
    (0xF0414, 4, 'LC'),           # Hardware counter loop
    (0xF0418, 4, 'LS'),           # Hardware counter start address
    (0xF041C, 4, 'LE'),           # Hardware counter end address
    (0xF0420, 4, 'IRET'),         # Interrupt PC return address
    (0xF0424, 4, 'IMASK'),        # Interrupt mask
    (0xF0428, 4, 'ILAT'),         # Interrupt latch
    (0xF042C, 4, 'ILATST'),       # Alias for setting interrupts
    (0xF0430, 4, 'ILATCL'),       # Alias for clearing interrupts
    (0xF0434, 4, 'IPEND'),        # Interrupt currently in progress
    (0xF0440, 4, 'FSTATUS'),      # Alias for writing to all STATUS bits
    (0xF0448, 1, 'DEBUGCMD'),     # Debug command register (2 bits)
    (0xF070C, 1, 'RESETCORE'),    # Per core software reset (1 bit)
    # Event timer registers
    (0xF0438, 4, 'CTIMER0'),      # Core timer 0
    (0xF043C, 4, 'CTIMER1'),      # Core timer 1
    # Process control registers
    (0xF0604, 2, 'MEMSTATUS'),    # Memory protection status
                                  # Epiphany IV: 14 bits, III: 1 bit ([2])
    (0xF0608, 2, 'MEMPROTECT'),   # Memory protection registration
                                  # Epiphany IV: 16 bits, III: 8 bits.
    # DMA registers
    (0xF0500, 4, 'DMA0CONFIG'),   # DMA channel 0 configuration
    (0xF0504, 4, 'DMA0STRIDE'),   # DMA channel 0 stride
    (0xF0508, 4, 'DMA0COUNT'),    # DMA channel 0 count
    (0xF050C, 4, 'DMA0SRCADDR'),  # DMA channel 0 source address
    (0xF0510, 4, 'DMA0DSTADDR'),  # DMA channel 0 destination address
    (0xF0514, 4, 'DMA0AUTO0'),    # DMA channel 0 slave lower data
    (0xF0518, 4, 'DMA0AUTO1'),    # DMA channel 0 slave upper data
    (0xF051C, 4, 'DMA0STATUS'),   # DMA channel 0 status
    (0xF0520, 4, 'DMA1CONFIG'),   # DMA channel 1 configuration
    (0xF0524, 4, 'DMA1STRIDE'),   # DMA channel 1 stride
    (0xF0528, 4, 'DMA1COUNT'),    # DMA channel 1 count
    (0xF052C, 4, 'DMA1SRCADDR'),  # DMA channel 1 source address
    (0xF0530, 4, 'DMA1DSTADDR'),  # DMA channel 1 destination address
    (0xF0534, 4, 'DMA1AUTO0'),    # DMA channel 1 slave lower data
    (0xF0538, 4, 'DMA1AUTO1'),    # DMA channel 1 slave upper data
    (0xF053C, 4, 'DMA1STATUS'),   # DMA channel 1 status
    # Mesh node control registers
    (0xF0700, 2, 'MESHCONFIG'),   # Mesh node configuration
    (0xF0704, 3, 'COREID'),       # Processor core ID (12 bits)
    (0xF0708, 4, 'MULTICAST'),    # Multicast configuration
    (0xF0710, 3, 'CMESHROUTE'),   # cMesh routing configuration (12 bits)
    (0xF0714, 3, 'XMESHROUTE'),   # xMesh routing configuration (12 bits)
    (0xF0718, 3, 'RMESHROUTE'),   # rMesh routing configuration (12 bits)
]

register_map = OrderedDict()
# Add general purpose registers to register_map.
for index, address in enumerate(xrange(0xF0000, 0xF0100, 0x4)):
    register_map[index] = (address, 4, 'r%d' % ((address - 0xF0000) / 0x4))
# Add special purpose registers to _register_map.
for index in xrange(len(_special_purpose_registers)):
    register_map[index + 64] = _special_purpose_registers[index]
