from epiphany.isa import reg_map


def make_zero_operand_factory(opcode):
    def factory():
        return opcode
    return factory

gie16    = make_zero_operand_factory(0b0000000110010010)
gid16    = make_zero_operand_factory(0b0000001110010010)
nop16    = make_zero_operand_factory(0b0000000110100010)
idle16   = make_zero_operand_factory(0b0000000110110010)
bkpt16   = make_zero_operand_factory(0b0000000111000010)
mbkpt16  = make_zero_operand_factory(0b0000001111000010)
sync16   = make_zero_operand_factory(0b0000000111110010)
rti16    = make_zero_operand_factory(0b0000000111010010)
wand16   = make_zero_operand_factory(0b0000000110000010)
unimpl16 = make_zero_operand_factory(0b00000000000011110000000000001111)


def trap16(trap=0):
    return 0b1111100010 | (trap << 10)


def make_arith32_immediate_factory(name):
    def arith32_immediate(rd=0, rn=0, imm=0):
        if name == 'add':
            opcode = 0b0011011
        elif name == 'sub':
            opcode = 0b0111011
        else:
            raise NotImplementedError()
        return (opcode | ((imm & 7) << 7) | ((rn & 7) << 10) |
                ((rd & 7) << 13) | ((imm & (0xFF << 3)) << 13) |
                ((rn & 56) << 23) | ((rd & 56) << 26))
    return arith32_immediate

add32_immediate = make_arith32_immediate_factory('add')
sub32_immediate = make_arith32_immediate_factory('sub')


def make_bitwise32_factory(name):
    def arith32(rd=0, rn=0, rm=0):
        bits_16_20 = 0b1010
        if name == 'add':
            opcode = 0b0011111
        elif name == 'sub':
            opcode = 0b0111111
        elif name == 'and':
            opcode = 0b1011111
        elif name == 'orr':
            opcode = 0b1111111
        elif name == 'eor':
            opcode = 0b0001111
        elif name == 'asr':
            opcode = 0b1101111
        elif name == 'lsr':
            opcode = 0b1001111
        elif name == 'lsl':
            opcode = 0b0101111
        else:
            raise NotImplementedError()
        return (opcode | ((rm & 7) << 7) | ((rn & 7) << 10) |
                ((rd & 7) << 13) | (bits_16_20 << 16) |
                ((rm & 56) << 20) | ((rn & 56) << 23) | ((rd & 56) << 26))
    return arith32

add32 = make_bitwise32_factory('add')
sub32 = make_bitwise32_factory('sub')
and32 = make_bitwise32_factory('and')
orr32 = make_bitwise32_factory('orr')
eor32 = make_bitwise32_factory('eor')
asr32 = make_bitwise32_factory('asr')
lsr32 = make_bitwise32_factory('lsr')
lsl32 = make_bitwise32_factory('lsl')


def make_bitwise32_immediate_factory(name):
    def bit32_immediate(rd=0, rn=0, imm=0):
        if name == 'lsr':
            opcode = 0b01111
            bits_16_20 = 0b0110
        elif name == 'lsl':
            opcode = 0b11111
            bits_16_20 = 0b0110
        elif name == 'asr':
            opcode = 0b01111
            bits_16_20 = 0b1110
        elif name == 'bitr':
            opcode = 0b11111
            bits_16_20 = 0b1110
        else:
            raise NotImplementedError()
        return (opcode | (imm << 5) | ((rn & 7) << 10) | ((rd & 7) << 13) |
                (bits_16_20 << 16) | ((rn & 56) << 23) | ((rd & 56) << 26))
    return bit32_immediate

lsr32_immediate  = make_bitwise32_immediate_factory('lsr')
lsl32_immediate  = make_bitwise32_immediate_factory('lsl')
asr32_immediate  = make_bitwise32_immediate_factory('asr')
bitr32_immediate = make_bitwise32_immediate_factory('bitr')


def make_bitwise16_immediate_factory(name):
    def bit16_immediate(rd=0, rn=0, imm=0):
        if name == 'lsr':
            opcode = 0b00110
        elif name == 'lsl':
            opcode = 0b10110
        elif name == 'asr':
            opcode = 0b01110
        elif name == 'bitr':  # No immediate on pp 81 of reference manual.
            opcode = 0b11110
        else:
            raise NotImplementedError()
        return (opcode | (imm << 5) | (rn  << 10) | (rd << 13))
    return bit16_immediate

lsr16_immediate  = make_bitwise16_immediate_factory('lsr')
lsl16_immediate  = make_bitwise16_immediate_factory('lsl')
asr16_immediate  = make_bitwise16_immediate_factory('asr')
bitr16_immediate = make_bitwise16_immediate_factory('bitr')


def make_bitwise16_factory(name):
    def bit16(rd=0, rn=0, rm=0):
        assert rd <= 0b111
        assert rn <= 0b111
        assert rm <= 0b111
        if name == 'add':
            opcode = 0b0011010
        elif name == 'sub':
            opcode = 0b0111010
        elif name == 'and':
            opcode = 0b1011010
        elif name == 'orr':
            opcode = 0b1111010
        elif name == 'eor':
            opcode = 0b0001010
        elif name == 'asr':
            opcode = 0b1101010
        elif name == 'lsr':
            opcode = 0b1001010
        elif name == 'lsl':
            opcode = 0b0101010
        else:
            raise NotImplementedError()
        return (opcode | ((rm & 7) << 7) | ((rn & 7) << 10) | ((rd & 7) << 13))
    return bit16

add16 = make_bitwise16_factory('add')
sub16 = make_bitwise16_factory('sub')
and16 = make_bitwise16_factory('and')
orr16 = make_bitwise16_factory('orr')
eor16 = make_bitwise16_factory('eor')
asr16 = make_bitwise16_factory('asr')
lsr16 = make_bitwise16_factory('lsr')
lsl16 = make_bitwise16_factory('lsl')


def make_arith16_immediate_factory(name):
    def arith16_immediate(rd=0, rn=0, imm=0):
        if name == 'add':
            opcode = 0b0010011
        elif name == 'sub':
            opcode = 0b0110011
        else:
            raise NotImplementedError()
        return (opcode | ((imm & 7) << 7) | ((rn & 7) << 10) | ((rd & 7) << 13))
    return arith16_immediate

add16_immediate = make_arith16_immediate_factory('add')
sub16_immediate = make_arith16_immediate_factory('sub')


def make_jump32_factory(and_link):
    def jump(rn=0):
        opcode = 0b0101011111 if and_link else 0b0101001111
        bits_16_20 = 0b0010
        return (opcode | ((rn & 7) << 10) | (bits_16_20 << 16) | ((rn & 56) << 23))
    return jump

jr32   = make_jump32_factory(False)
jalr32 = make_jump32_factory(True)


def make_jump16_factory(and_link):
    def jump(rn=0):
        opcode = 0b0101010010 if and_link else 0b0101000010
        return (opcode | (rn << 10))
    return jump

jr16   = make_jump16_factory(False)
jalr16 = make_jump16_factory(True)


def bcond_factory(is16bit):
    def bcond(condition=0, imm=0):
        opcode = 0b0000 if is16bit else 0b1000
        return (opcode | (condition << 4) | (imm << 8))
    return bcond

bcond32 = bcond_factory(False)
bcond16 = bcond_factory(True)


def movcond32(condition=0, rd=0, rn=0):
    opcode = 0b1111
    bits_16_20 = 0b0010
    return (opcode | (condition << 4) | ((rn & 7) << 10) |
            ((rd & 7) << 13) | (bits_16_20 << 16) |
            ((rn & 56) << 23) | ((rd & 56) << 26))


def movcond16(condition, rd=0, rn=0):
    opcode = 0b0010
    bits_9_10 = 0b00
    return (opcode | (condition << 4) | (bits_9_10 << 8) | (rn << 10) | (rd << 13))


def make_movimm32(is_t):
    def mov32_immediate(rd=0, imm=0):
        opcode = 0b01011
        bit28 = 1 if is_t else 0
        return (opcode | ((imm & 255) << 5) | ((rd & 7) << 13) |
                ((imm & 65280) << 12) | (bit28 << 28) | ((rd & 56) << 26))
    return mov32_immediate

movimm32  = make_movimm32(False)
movtimm32 = make_movimm32(True)


def make_mov_factory(is16bit, is_from):
    # TODO: Find out what M0 and M1 are for.
    def mov(rd=0, rn=0):
        rn = reg_map[rn] if is_from else rn
        rd = reg_map[rd] if not is_from else rd
        if is16bit and is_from:
            opcode = 0b0100010010
        elif is16bit and not is_from:
            opcode = 0b0100000010
        elif not is16bit and is_from:
            opcode = 0b0100011111
        elif not is16bit and not is_from:
            opcode = 0b0100001111
        bits_16_20 = 0b0000 if is16bit else 0b0010
        return (opcode | ((rn & 7) << 10) |
                ((rd & 7) << 13) | (bits_16_20 << 16) |
                ((rn & 56) << 23) | ((rd & 56) << 26))
    return mov

movts16  = make_mov_factory(True,  False)
movts32  = make_mov_factory(False, False)
movfs16  = make_mov_factory(True,  True)
movfs32  = make_mov_factory(False, True)


def movimm16(rd=0, imm=0):
    opcode = 0b00011
    return (opcode | (imm << 5) | (rd << 13))


def ldstrpmd32(rd=0, rn=0, sub=0, imm=0, bb=0, s=0):
    # Data size
    # 00=byte, 01=half-word, 10=word, 11=double-word
    opcode = 0b1100
    bit25 = 1
    return (opcode | (s << 4) | (bb << 5) | ((imm & 7) << 7) |
            ((rn & 7) << 10) | ((rd & 7) << 13) |
            ((imm & (0xFF << 3)) << 13) | (sub << 24) | (bit25 << 25) |
            ((rn & 56) << 23) | ((rd & 56) << 26))
