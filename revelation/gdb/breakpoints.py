from revelation.isa import decode

BKPT16 = 0b0000000111000010
NOP16 = 0b0000000110100010


class BreakPointManager(object):
    """Manage breakpoints during GDB execution.
    """

    def __init__(self, simulator):
        self.target = simulator
        self.breakpoints = {}  # Address -> (opcode, size in bytes)

    def _get_global_address(self, address, coreid=0x808):
        """Remap any local addresses to global address.
        """
        if (address >> 20) == 0x0:
            return (coreid << 20) | address
        return address

    def is_breakpoint_set(self, address):
        return address in self.breakpoints

    def set_breakpoint(self, address, coreid=0x080):
        """Set a breakpoint at a given address.
        1. Read 32 bit current instructions at address, save in dictionary.
        2. If current instruction is 16 bit, replace with bkpt16.
        3. If current instruction is 32 bit, replace with bkpt16, nop16.
        """
        global_address = self._get_global_address(address, coreid)
        opcode = self.target.memory.iread(global_address, 4)
        mnemonic, _ = decode(opcode)
        if mnemonic.endswith('16'):
            self.breakpoints[global_address] = (opcode & 0xffff, 2)
            self.target.memory.write(global_address, 2, BKPT16)
        else:
            self.breakpoints[global_address] = (opcode, 4)
            self.target.memory.write(global_address, 2, BKPT16)
            self.target.memory.write(global_address + 2, 2, NOP16)

    def remove_breakpoint(self, address, coreid=0x808):
        """Remove a breakpoint at a given address."""
        global_address = self._get_global_address(address, coreid)
        opcode, size = self.breakpoints[global_address]
        self.target.memory.write(global_address, size, opcode)
