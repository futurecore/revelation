def nop16():
    return 0b0000000000000000000000110100010



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


def int_arith32(name, rd, rm, rn):
    bits_16_20 = 0b1010
    if name == 'add':
        opcode = 0b0011111
    elif name == 'sub':
        opcode = 0b0111111
    else:
        raise NotImplementedError()
    instruction = 'foobar'
