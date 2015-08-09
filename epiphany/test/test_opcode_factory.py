from opcode_factory import *

import pytest

def test_arith32_immediate():
    #       0bdddnnnxxiiiiiiiidddnnniii0011011 ADD
    instr = 0b00000000010101010010000100011011
    assert add32_immediate(rd=1, rn=0, imm=0b01010101010) == instr
    #       0bdddnnnxxiiiiiiiidddnnniii0111011 SUB
    instr = 0b00000000010101010010000100111011
    assert sub32_immediate(rd=1, rn=0, imm=0b01010101010) == instr


def test_arith16():
    #       0bdddnnnmmm0011010
    instr = 0b0100010000011010
    assert add16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmm0111010
    instr = 0b0100010000111010
    assert sub16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmm1011010
    instr = 0b0100010001011010
    assert and16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmm1111010
    instr = 0b0100010001111010
    assert orr16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmm0001010
    instr = 0b0100010000001010
    assert eor16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmm1101010
    instr = 0b0100010001101010
    assert asr16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmm1001010
    instr = 0b0100010001001010
    assert lsr16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmm0101010
    instr = 0b0100010000101010
    assert lsl16(rd=2, rn=1, rm=0) == instr


def test_bitwise32():
    #       0bdddnnnmmmxxx1010dddnnnmmm0011111
    instr = 0b00000000000010100100010000011111
    assert add32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm0111111
    instr = 0b00000000000010100100010000111111
    assert sub32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm1011111
    instr = 0b00000000000010100100010001011111
    assert and32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm1111111
    instr = 0b00000000000010100100010001111111
    assert orr32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm0001111
    instr = 0b00000000000010100100010000001111
    assert eor32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm1101111
    instr = 0b00000000000010100100010001101111
    assert asr32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm1001111
    instr = 0b00000000000010100100010001001111
    assert lsr32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx1010dddnnnmmm0101111
    instr = 0b00000000000010100100010000101111
    assert lsl32(rd=2, rn=1, rm=0) == instr


def test_bit16_immediate():
    #       0bxxxxxxxxxxxxxxxxdddnnniiiii00110 LSR
    instr = 0b00000000000000001110101111100110
    assert lsr16_immediate(rd=0b111, rn=0b010, imm=0b11111) == instr
    #       0bxxxxxxxxxxxxxxxxdddnnniiiii10110 LSL
    instr = 0b00000000000000001110101111110110
    assert lsl16_immediate(rd=0b111, rn=0b010, imm=0b11111) == instr
    #       0bxxxxxxxxxxxxxxxxdddnnniiiii01110 ASR
    instr = 0b00000000000000001110101111101110
    assert asr16_immediate(rd=0b111, rn=0b010, imm=0b11111) == instr
    #       0bxxxxxxxxxxxxxxxxdddnnniiiii11110 BITR
    instr = 0b00000000000000001110101111111110
    assert bitr16_immediate(rd=0b111, rn=0b010, imm=0b11111) == instr


def test_bit32_immediate():
    #       0bdddnnnxxxxxx0110dddnnniiiii01111 LSR
    instr = 0b10001100000001101000111111101111
    assert lsr32_immediate(rd=0b100100, rn=0b011011, imm=0b11111) == instr
    #       0bdddnnnxxxxxx0110dddnnniiiii11111 LSL
    instr = 0b10001100000001101000111111111111
    assert lsl32_immediate(rd=0b100100, rn=0b011011, imm=0b11111) == instr
    #       0bdddnnnxxxxxx1110dddnnniiiii01111 ASR
    instr = 0b10001100000011101000111111101111
    assert asr32_immediate(rd=0b100100, rn=0b011011, imm=0b11111) == instr
    #       0bdddnnnxxxxxx1110dddnnniiiii11111 BITR
    instr = 0b10001100000011101000111111111111
    assert bitr32_immediate(rd=0b100100, rn=0b011011, imm=0b11111) == instr


def test_jr32():
    #       0bxxxnnnxxxxxx0010xxxnnn0101001111
    instr = 0b00011100000000100001110101001111
    assert jr32(rn=0b111111) == instr


def test_jr16():
    #       0bxxxxxxxxxxxxxxxxxxxnnn0101000010
    instr = 0b00000000000000000001110101000010
    assert jr16(rn=0b111) == instr


def test_jalr32():
    #       0bxxxnnnxxxxxx0010xxxnnn0101011111
    instr = 0b00011100000000100001110101011111
    assert jalr32(rn=0b111111) == instr


def test_jalr16():
    #       0bxxxxxxxxxxxxxxxxxxxnnn0101010010
    instr = 0b00000000000000000001110101010010
    assert jalr16(rn=0b111) == instr


def test_bcond32():
    #       0biiiiiiiiiiiiiiiiiiiiiiiicccc1000
    instr = 0b11100000000000000000000011111000
    assert bcond32(condition=0b1111, imm=0b111000000000000000000000) == instr


def test_bcond16():
    #       0bxxxxxxxxxxxxxxxxiiiiiiiicccc0000
    instr = 0b00000000000000001110000011110000
    assert bcond16(condition=0b1111, imm=0b11100000) == instr


def test_farith16():
    #       0bdddnnnmmmxxxxxxxdddnnnmmm0000111
    instr = 0b00000000000000000100010000000111
    assert fadd16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxxxxxxdddnnnmmm0010111
    instr = 0b00000000000000000100010000010111
    assert fsub16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxxxxxxdddnnnmmm0100111
    instr = 0b00000000000000000100010000100111
    assert fmul16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxxxxxxdddnnnmmm0110111
    instr = 0b00000000000000000100010000110111
    assert fmadd16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxxxxxxdddnnnmmm1000111
    instr = 0b00000000000000000100010001000111
    assert fmsub16(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnxxxxxxxxxxdddnnn0001010111
    instr = 0b00000000000000000100010001010111
    assert float16(rd=2, rn=1) == instr
    #       0bdddnnnxxxxxxxxxxdddnnn0001100111
    instr = 0b00000000000000000100010001100111
    assert fix16(rd=2, rn=1) == instr
    #       0bdddnnnxxxxxxxxxxdddnnn0001110111
    instr = 0b00000000000000000100010001110111
    assert fabs16(rd=2, rn=1) == instr


def test_farith32():
    #       0bdddnnnmmmxxx0111dddnnnmmm0001111
    instr = 0b00000000000001110100010000001111
    assert fadd32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx0111dddnnnmmm0011111
    instr = 0b00000000000001110100010000011111
    assert fsub32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx0111dddnnnmmm0101111
    instr = 0b00000000000001110100010000101111
    assert fmul32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx0111dddnnnmmm0111111
    instr = 0b00000000000001110100010000111111
    assert fmadd32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnmmmxxx0111dddnnnmmm1001111
    instr = 0b00000000000001110100010001001111
    assert fmsub32(rd=2, rn=1, rm=0) == instr
    #       0bdddnnnxxxxxx0111dddnnn0001011111
    instr = 0b00000000000001110100010001011111
    assert float32(rd=2, rn=1) == instr
    #       0bdddnnnxxxxxx0111dddnnn0001101111
    instr = 0b00000000000001110100010001101111
    assert fix32(rd=2, rn=1) == instr
    #       0bdddnnnxxxxxx0111dddnnn0001111111
    instr = 0b00000000000001110100010001111111
    assert fabs32(rd=2, rn=1) == instr


def test_movcond32():
    #       0bdddnnnxxxxxx0010dddnnn00cccc1111
    instr = 0b00000000000000100000000001011111
    assert movcond32(condition=0b0101, rd=0, rn=0) == instr


def test_movcond16():
    #       0bxxxxxxxxxxxxxxxxdddnnn00cccc0010
    instr = 0b00000000000000001110100011110010
    assert movcond16(condition=0b1111, rd=0b111, rn=0b010) == instr


def test_movimm16():
    #       0bxxxxxxxxxxxxxxxxdddiiiiiiii00011
    instr = 0b00000000000000001001111111100011
    assert movimm16(rd=0b100, imm=0b11111111) == instr


def test_movimm32():
    #       0bddd0iiiiiiiixxxxdddiiiiiiii01011
    instr = 0b10001111111100001001111111101011
    assert movimm32(rd=0b100100, imm=0b1111111111111111) == instr


def test_movtimm32():
    #       0bddd1iiiiiiiixxxxdddiiiiiiii01011
    instr = 0b10011111111100001001111111101011
    assert movtimm32(rd=0b100100, imm=0b1111111111111111) == instr


def test_movts():
    # Note that in the MOV 'special' instructions rd and rn are swapped.
    assert reg_map['CONFIG'] == 64
    #       0bxxxxxxxxxxxxxxxxdddnnn0100000010
    instr = 0b00000000000000000000000100000010
    assert movts16(rn='CONFIG', rd=0) == instr
    #       0bdddnnnxxxxxx0010dddnnn0100001111
    instr = 0b00000000000000100000000100001111
    assert movts32(rn='CONFIG', rd=0) == instr


def test_movfs():
    # Note that in the MOV 'special' instructions rd and rn are swapped.
    assert reg_map['CONFIG'] == 64
    #       0bdddnnnxxxxxxxxxxdddnnn0100010010
    instr = 0b00000000000000000000000100010010
    assert movfs16(rn=0, rd='CONFIG') == instr
    #       0bdddnnnxxxxxx0010dddnnn0100011111
    instr = 0b00000000000000100000000100011111
    assert movfs32(rn=0, rd='CONFIG') == instr


def test_ldstrpmd32():
    #       0bdddnnn1Siiiiiiiidddnnniiibbs1100
    instr = 0b00000011001010100000011010111100
    assert ldstrpmd32(rd=0, rn=1, sub=0b1, imm=0b00101010101, bb=0b01, s=0b1) == instr
    #       0bdddnnn1Siiiiiiiidddnnniiibbs1100
    instr = 0b00000011001010100000011010101100
    assert ldstrpmd32(rd=0, rn=1, sub=0b1, imm=0b00101010101, bb=0b01, s=0b0) == instr


def test_ldstrdisp32():
    #       0bdddnnn0Siiiiiiiidddnnniiibbs1100
    instr = 0b00000000010101000000110100111100
    assert ldstrdisp32(rd=0, rn=3, sub=0b0, imm=0b01010100010, bb=0b01, s=0b1) == instr
    #       0bdddnnn0Siiiiiiiidddnnniiibbs1100
    instr = 0b00000001001010100000011010101100
    assert ldstrdisp32(rd=0, rn=1, sub=0b1, imm=0b00101010101, bb=0b01, s=0b0) == instr


def test_ldstrind16():
    #       0bxxxxxxxxxxxxxxxxdddnnnmmmbbs0001
    instr = 0b00000000000000001110011010110001
    assert ldstrind16(rd=7, rn=1, rm=5, bb=0b01, s=0b1) == instr
    #       0bxxxxxxxxxxxxxxxxdddnnnmmmbbs0001
    instr = 0b00000000000000001110011010100001
    assert ldstrind16(rd=7, rn=1, rm=5, bb=0b01, s=0b0) == instr


def test_ldstrind32():
    #       0bdddnnnmmm00Sxxxxdddnnnmmmbbs1001
    instr = 0b00000001000000000000111010111001
    assert ldstrind32(rd=0, rn=3, rm=21, sub=0b0, bb=0b01, s=0b1) == instr
    #       0bdddnnnmmm00Sxxxxdddnnnmmmbbs1001
    instr = 0b00000001000100000000011010101001
    assert ldstrind32(rd=0, rn=1, rm=21, sub=0b1, bb=0b01, s=0b0) == instr


def test_ldstrpm16():
    #       0bxxxxxxxxxxxxxxxxdddnnnmmmbbs0101
    instr = 0b00000000000000001110011010110101
    assert ldstrpm16(rd=7, rn=1, rm=5, bb=0b01, s=0b1) == instr
    #       0bxxxxxxxxxxxxxxxxdddnnnmmmbbs0101
    instr = 0b00000000000000001110011010100101
    assert ldstrpm16(rd=7, rn=1, rm=5, bb=0b01, s=0b0) == instr


def test_ldstrpm32():
    #       0bdddnnnmmm00Sxxxxdddnnnmmmbbs1101
    instr = 0b00000001000000000000111010111101
    assert ldstrpm32(rd=0, rn=3, rm=21, sub=0b0, bb=0b01, s=0b1) == instr
    #       0bdddnnnmmm00Sxxxxdddnnnmmmbbs1101
    instr = 0b00000001000100000000011010101101
    assert ldstrpm32(rd=0, rn=1, rm=21, sub=0b1, bb=0b01, s=0b0) == instr


def test_testset32():
    #       0bdddnnnmmm01Sxxxxdddnnnmmmbb01001
    instr = 0b00000001001000000000111010101001
    assert testset32(rd=0, rn=3, rm=21, sub=0b0, bb=0b01) == instr
    #       0bdddnnnmmm01Sxxxxdddnnnmmm0b01001
    instr = 0b00000001001100000000011010101001
    assert testset32(rd=0, rn=1, rm=21, sub=0b1, bb=0b01) == instr


def test_ldstrdisp16():
    #       0bxxxxxxxxxxxxxxxxdddnnniiibbs0100
    instr = 0b00000000000000001110011010110100
    assert ldstrdisp16(rd=7, rn=1, imm=0b101, bb=0b01, s=0b1) == instr
    #       0bxxxxxxxxxxxxxxxxdddnnniiibbs0100
    instr = 0b00000000000000001110011010100100
    assert ldstrdisp16(rd=7, rn=1, imm=0b101, bb=0b01, s=0b0) == instr


def test_trap16():
    #       0bxxxxxxxxxxxxxxxxtttttt1111100000
    instr = 0b00000000000000001111111111100010
    assert trap16(trap=0b111111) == instr


@pytest.mark.parametrize('name,factory,instr',
                         [('gie16',   gie16,    0b00000000000000000000000110010010),
                          ('gid16',   gid16,   0b00000000000000000000001110010010),
                          ('nop16',   nop16,   0b0000000000000000000000110100010),
                          ('idle16',  idle16,  0b0000000000000000000000110110010),
                          ('bkpt16',  bkpt16,  0b00000000000000000000000111000010),
                          ('mbkpt16', mbkpt16, 0b00000000000000000000001111000010),
                          ('sync16',  sync16,  0b00000000000000000000000111110010),
                          ('rti16',   rti16,   0b00000000000000000000000111010010),
                          ('wand16',  wand16,  0b00000000000000000000000110000010),
                          ('unimpl',  unimpl,  0b00000000000011110000000000001111),
                         ])
def test_no_operands(name, factory, instr):
    assert instr == factory()
