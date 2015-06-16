from epiphany.instruction import Instruction


def test_rd():
    #      0bdddxxxxxxxxxxxxxdddxxxxxxxxxxxxx
    bits = 0b11100000000000001110000000000000
    inst = Instruction(bits, '')
    assert 63 == inst.rd
    #      0bdddxxxxxxxxxxxxxdddxxxxxxxxxxxxx
    bits = 0b00011111111111110001111111111111
    inst = Instruction(bits, '')
    assert 0 == inst.rd


def test_rn():
    #      0bxxxnnnxxxxxxxxxxxxxnnnxxxxxxxxxx
    bits = 0b00011100000000000001110000000000
    inst = Instruction(bits, '')
    assert 63 == inst.rn
    #      0bxxxnnnxxxxxxxxxxxxxnnnxxxxxxxxxx
    bits = 0b11100011111111111110001111111111
    inst = Instruction(bits, '')
    assert 0 == inst.rn

def test_rm():
    #      0bxxxxxxmmmxxxxxxxxxxxxxmmmxxxxxxx
    bits = 0b00000011100000000000001110000000
    inst = Instruction(bits, '')
    assert 63 == inst.rm
    #      0bxxxxxxmmmxxxxxxxxxxxxxmmmxxxxxxx
    bits = 0b11111100011111111111110001111111
    inst = Instruction(bits, '')
    assert 0 == inst.rm


def test_imm3():
    #      0bxxxxxxxxxxxxxxxxxxxxxiiixxxxxxxx
    bits = 0b00000000000000000000011100000000
    inst = Instruction(bits, '')
    assert 7 == inst.imm3
    #      0bxxxxxxxxxxxxxxxxxxxxxiiixxxxxxxx
    bits = 0b11111111111111111111100011111111
    inst = Instruction(bits, '')
    assert 0 == inst.imm3



def test_imm5():
    #      0bxxxxxxxxxxxxxxxxxxxxxxiiiiixxxxx
    bits = 0b00000000000000000000001111100000
    inst = Instruction(bits, '')
    assert 31 == inst.imm5
    #      0bxxxxxxxxxxxxxxxxxxxxxxiiiiixxxxx
    bits = 0b11111111111111111111110000011111
    inst = Instruction(bits, '')
    assert 0 == inst.imm5


def test_imm11():
    #      0bxxxxxxxxiiiiiiiixxxxxxiiixxxxxxx
    bits = 0b00000000111111110000001110000000
    inst = Instruction(bits, '')
    assert 2047 == inst.imm11
    #      0bxxxxxxxxiiiiiiiixxxxxxiiixxxxxxx
    bits = 0b11111111000000001111110001111111
    inst = Instruction(bits, '')
    assert 0 == inst.imm11


def test_imm16():
    #      0bxxxxiiiiiiiixxxxxxxiiiiiiiixxxxx
    bits = 0b00001111111100000001111111100000
    inst = Instruction(bits, '')
    assert 65535 == inst.imm16
    #      0bxxxxiiiiiiiixxxxxxxiiiiiiiixxxxx
    bits = 0b11110000000011111110000000011111
    inst = Instruction(bits, '')
    assert 0 == inst.imm16


def test_cond():
    #      0bxxxxxxxxxxxxxxxxxxxxxxxxccccxxxx
    bits = 0b00000000000000000000000011110000
    inst = Instruction(bits, '')
    assert 15 == inst.cond
    #      0bxxxxxxxxxxxxxxxxxxxxxxxxccccxxxx
    bits = 0b11111111111111111111111100001111
    inst = Instruction(bits, '')
    assert 0 == inst.cond


def test_bcond_imm():
    #      0biiiiiiiiiiiiiiiiiiiiiiiixxxxxxxx
    bits = 0b11111111111111111111111100000000
    inst = Instruction(bits, '')
    assert 16777215 == inst.bcond_imm
    #      0biiiiiiiiiiiiiiiiiiiiiiiixxxxxxxx
    bits = 0b00000000000000000000000011111111
    inst = Instruction(bits, '')
    assert 0 == inst.bcond_imm


def test_sub():
    #      0bxxxxxxxSxxxxxxxxxxxxxxxxxxxxxxxx
    bits = 0b00000001000000000000000000000000
    inst = Instruction(bits, '')
    assert 1 == inst.sub
    #      0bxxxxxxxSxxxxxxxxxxxxxxxxxxxxxxxx
    bits = 0b11111110111111111111111111111111
    inst = Instruction(bits, '')
    assert 0 == inst.sub


def test_size():
    #      0bxxxxxxxxxxxxxxxxxxxxxxxxxbbxxxxx
    bits = 0b00000000000000000000000001100000
    inst = Instruction(bits, '')
    assert 3 == inst.size
    #      0bxxxxxxxxxxxxxxxxxxxxxxxxxbbxxxxx
    bits = 0b11111111111111111111111110011111
    inst = Instruction(bits, '')
    assert 0 == inst.size


def test_s():
    bits = 0b00000000000000000000000000010000
    inst = Instruction(bits, '')
    assert 1 == inst.s
    bits = 0b11111111111111111111111111101111
    inst = Instruction(bits, '')
    assert 0 == inst.s


def test_bit2():
    bits = 0b00000000000000000000000000000100
    inst = Instruction(bits, '')
    assert 1 == inst.bit2
    bits = 0b11111111111111111111111111111011
    inst = Instruction(bits, '')
    assert 0 == inst.bit2


def test_bit0():
    bits = 0b00000000000000000000000000000001
    inst = Instruction(bits, '')
    assert 1 == inst.bit0
    bits = 0b11111111111111111111111111111110
    inst = Instruction(bits, '')
    assert 0 == inst.bit0
