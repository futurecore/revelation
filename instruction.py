#=======================================================================
# instruction.py
#=======================================================================

class Instruction(object):
    def __init__(self, bits, str):
        self.bits = bits
        self.str  = str

    @property
    def rd(self):
        return ((self.bits >> 13) & 0x7) | ((self.bits >> 26) & 0x38)

    @property
    def rm(self):
        return ((self.bits >> 7) & 0x7) | ((self.bits >> 20) & 0x38)

    @property
    def rn(self):
        return ((self.bits >> 10) & 0x7) | ((self.bits >> 23) & 0x38)

    @property
    def imm(self):
        return ((self.bits >> 7) & 0x7) | ((self.bits >> 13) & (0xFF << 3))

    @property
    def mov_imm(self):
        return ((self.bits >> 5) & 255) | ((self.bits >> 12) & 0xFF00)

    @property
    def bcond(self):
        return (self.bits >> 4) & 15

    @property
    def bcond_imm(self):
        return self.bits >> 8

    @property
    def bits_5_6(self):
        return (self.bits >> 5) & 3

    @property
    def sub_bit24(self):
        return (self.bits >> 24) & 1

    @property
    def bit4(self):
        return (self.bits >> 4) & 1

    @property
    def bit2(self):
        """Get bit 2 of an instruction.
        """
        return (self.bits >> 2) & 1

    @property
    def bit0(self):
        """Get bit 0 of an instruction.
        """
        return self.bits & 1

