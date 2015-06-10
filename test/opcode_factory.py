def nop16():
    return 0b0000000000000000000000110100010


def idle16():
    return 0b0000000000000000000000110110010


def bkpt16():
    return 0b00000000000000000000000111000010


def gid16():
    return 0b00000000000000000000001110010010


def int_arith32_immediate(name, rd, rn, imm):
    if name == 'add':
        opcode = 0b0011011
    elif name == 'sub':
        opcode = 0b0111011
    else:
        raise NotImplementedError()
    instruction = (opcode | ((imm & 7) << 7) | ((rn & 7) << 10) |
                   ((rd & 7) << 13) | ((imm & (0xFF << 3)) << 13) |
                   ((rn & 56) << 23) | ((rd & 56) << 26))
    return instruction


def int_arith32(name, rd, rn, rm):
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
    instruction = (opcode | ((rm & 7) << 7) | ((rn & 7) << 10) |
                   ((rd & 7) << 13) | (bits_16_20 << 16) |
                   ((rm & 56) << 20) | ((rn & 56) << 23) | ((rd & 56) << 26))
    return instruction


def int_arith16(name, rd, rn, rm):
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
    instruction = (opcode | ((rm & 7) << 7) |
                   ((rn & 7) << 10) | ((rd & 7) << 13))
    return instruction


def int_arith16_immediate(name, rd, rn, imm):
    if name == 'add':
        opcode = 0b0010011
    elif name == 'sub':
        opcode = 0b0110011
    else:
        raise NotImplementedError()
    instruction = (opcode | ((imm & 7) << 7) |
                   ((rn & 7) << 10) | ((rd & 7) << 13))
    return instruction


def jr32(rn):
    opcode = 0b0101001111
    bits_16_20 = 0b0010
    return (opcode | ((rn & 7)) << 7) | (bits_16_20 << 16) | ((rn & 56) << 23)


def jr16(rn):
    opcode = 0b0101000010
    return (opcode | ((rn & 7) << 7))


def bcond_factory(is16bit):
    def bcond(cond, imm):
        opcode = 0b0000 if is16bit else 0b1000
        return (opcode | (cond << 4) | (imm << 8))
    return bcond
bcond32 = bcond_factory(False)
bcond16 = bcond_factory(True)


def movcond32(cond, rd, rn):
    opcode = 0b1111
    bits_16_20 = 0b0010
    instruction = (opcode | (cond << 4) | ((rn & 7) << 10) |
                   ((rd & 7) << 13) | (bits_16_20 << 16) |
                   ((rn & 56) << 23) | ((rd & 56) << 26))
    return instruction


def movcond16(cond, rd, rn):
    opcode = 0b0010
    instruction = (opcode | (cond << 4) |
                   ((rn & 7) << 10) | ((rd & 7) << 13))
    return instruction


def ldstrpmd32(rd, rn, sub, imm, bb, s):
    # Data size
    # 00=byte, 01=half-word, 10=word, 11=double-word
    opcode = 0b1100
    bit25 = 1
    instruction = (opcode | (s << 4) | (bb << 5) | ((imm & 7) << 7) |
                   ((rn & 7) << 10) | ((rd & 7) << 13) |
                   ((imm & (0xFF << 3)) << 13) | (sub << 24) | (bit25 << 25) |
                   ((rn & 56) << 23) | ((rd & 56) << 26))
    return instruction
