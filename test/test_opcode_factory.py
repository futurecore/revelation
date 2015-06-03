from opcode_factory import *

def test_int_arith32_immediate():
    #       0bdddnnnxxiiiiiiiidddnnniii0011011 ADD
    instr = 0b00000000010101010010000100011011
    assert int_arith32_immediate('add', 1, 0, 0b01010101010) == instr
    #       0bdddnnnxxiiiiiiiidddnnniii0111011 SUB
    instr = 0b00000000010101010010000100111011
    assert int_arith32_immediate('sub', 1, 0, 0b01010101010) == instr



def test_int_arith32():
    #       0bdddnnnmmmxxx1010dddnnnmmm0011111
    instr = 0b00000000000010100100010000011111
    assert int_arith32('add', 2, 1, 0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm0111111
    instr = 0b00000000000010100100010000111111
    assert int_arith32('sub', 2, 1, 0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm1011111
    instr = 0b00000000000010100100010001011111
    assert int_arith32('and', 2, 1, 0) == instr
#
def test_jr32():
    #       0bxxxnnnxxxxxx0010xxxnnn0101011111
    instr = 0b00000000000000100000000101001111
    rn = 0
    assert jr32(rn) == instr


def test_bcond32():
    #       0biiiiiiiiiiiiiiiiiiiiiiiicccc1000
    instr = 0b00000000000000000000000011111000
    assert bcond32(0b1111, 0) == instr


def test_movcond32():
    #       0bdddnnnxxxxxx0010dddnnn00cccc1111
    instr = 0b00000000000000100000000001011111
    assert movcond32(0b0101, 0, 0) == instr


def test_ldstrpmd32():
    #       0bdddnnn1Siiiiiiiidddnnniiibbs1100
    instr = 0b00000011001010100000011010111100
    # (rd, rn, sub, imm, bb, s):
    assert ldstrpmd32(0, 1, 0b1, 0b00101010101, 0b01, 0b1) == instr
    #       0bdddnnn1Siiiiiiiidddnnniiibbs1100
    instr = 0b00000011001010100000011010101100
    # (rd, rn, sub, imm, bb, s):
    assert ldstrpmd32(0, 1, 0b1, 0b00101010101, 0b01, 0b0) == instr
