class Instruction(object):
    def __init__(self, bits, name):
        self.bits = bits
        self.name  = name

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
    def imm3(self):
        return (self.bits >> 7) & 0x7

    @property
    def imm5(self):
        return (self.bits >> 5) & 31

    @property
    def imm11(self):
        return ((self.bits >> 7) & 0x7) | ((self.bits >> 13) & (0xff << 3))

    @property
    def imm16(self):
        return ((self.bits >> 5) & 255) | ((self.bits >> 12) & 0xff00)

    @property
    def mmr(self):
        return (self.bits >> 20) & 0x3

    @property
    def t5(self):
        return (self.bits >> 10) & 31

    @property
    def cond(self):
        return (self.bits >> 4) & 15

    @property
    def bcond_imm(self):
        return self.bits >> 8

    @property
    def size(self):
        return (self.bits >> 5) & 3

    @property
    def sub(self):
        return (self.bits >> 24) & 1

    @property
    def sub20(self):
        return (self.bits >> 20) & 1

    @property
    def s(self):
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
