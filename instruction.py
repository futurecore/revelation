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

