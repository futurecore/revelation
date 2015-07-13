from epiphany.isa import decode
from epiphany.instruction import Instruction

import opcode_factory

import pytest

@pytest.mark.parametrize('name,instr',
                         [('add32',       opcode_factory.add32(rd=0, rn=0, rm=0)),
                          ('add16',       opcode_factory.add16(rd=0, rn=0, rm=0)),
                          ('add32',       opcode_factory.add32(rd=1, rn=1, rm=1)),
                          ('add16',       opcode_factory.add16(rd=1, rn=1, rm=1)),
                          ('sub32',       opcode_factory.sub32(rd=0, rn=0, rm=0)),
                          ('sub16',       opcode_factory.sub16(rd=0, rn=0, rm=0)),
                          ('sub32',       opcode_factory.sub32(rd=1, rn=1, rm=1)),
                          ('sub16',       opcode_factory.sub16(rd=1, rn=1, rm=1)),
                          ('add32',       opcode_factory.add32_immediate(rd=1, rn=0, imm=0b01010101010)),
                          ('add16',       opcode_factory.add16_immediate(rd=1, rn=0, imm=0b0101)),
                          ('sub32',       opcode_factory.sub32_immediate(rd=1, rn=0, imm=0b01010101010)),
                          ('sub16',       opcode_factory.sub16_immediate(rd=1, rn=0, imm=0b0101)),
                          ('and32',       opcode_factory.and32(rd=1, rn=1, rm=1)),
                          ('and16',       opcode_factory.and16(rd=1, rn=1, rm=1)),
                          ('orr32',       opcode_factory.orr32(rd=1, rn=1, rm=1)),
                          ('orr16',       opcode_factory.orr16(rd=1, rn=1, rm=1)),
                          ('eor32',       opcode_factory.eor32(rd=1, rn=1, rm=1)),
                          ('eor16',       opcode_factory.eor16(rd=1, rn=1, rm=1)),
                          ('asr32',       opcode_factory.asr32(rd=1, rn=1, rm=1)),
                          ('asr16',       opcode_factory.asr16(rd=1, rn=1, rm=1)),
                          ('lsr32',       opcode_factory.lsr32(rd=1, rn=1, rm=1)),
                          ('lsr16',       opcode_factory.lsr16(rd=1, rn=1, rm=1)),
                          ('lsl32',       opcode_factory.lsl32(rd=1, rn=1, rm=1)),
                          ('lsl16',       opcode_factory.lsl16(rd=1, rn=1, rm=1)),
                          ('lsrimm16',    opcode_factory.lsr16_immediate(rd=1, rn=1, imm=1)),
                          ('lslimm16',    opcode_factory.lsl16_immediate(rd=1, rn=1, imm=1)),
                          ('asrimm16',    opcode_factory.asr16_immediate(rd=1, rn=1, imm=1)),
                          ('bitrimm16',   opcode_factory.bitr16_immediate(rd=1, rn=1, imm=1)),
                          ('lsrimm32',    opcode_factory.lsr32_immediate(rd=1, rn=1, imm=1)),
                          ('lslimm32',    opcode_factory.lsl32_immediate(rd=1, rn=1, imm=1)),
                          ('asrimm32',    opcode_factory.asr32_immediate(rd=1, rn=1, imm=1)),
                          ('bitrimm32',   opcode_factory.bitr32_immediate(rd=1, rn=1, imm=1)),
                          ('jr32',        opcode_factory.jr32(rn=0)),
                          ('jr16',        opcode_factory.jr16(rn=0)),
                          ('jalr32',      opcode_factory.jalr32(rn=0)),
                          ('jalr16',      opcode_factory.jalr16(rn=0)),
                          ('bcond32',     opcode_factory.bcond32(condition=0b1111, imm=0)),
                          ('bcond16',     opcode_factory.bcond16(condition=0b1111, imm=0)),
                          ('ldstrpmd32',  opcode_factory.ldstrpmd32(rd=1, rn=0, sub=1, imm=0b1010101010, bb=0b11, s=1)),
                          ('ldstrdisp16', opcode_factory.ldstrdisp16(rd=1, rn=0, imm=0b010, bb=0b11, s=1)),
                          ('ldstrdisp32', opcode_factory.ldstrdisp32(rd=1, rn=0, sub=1, imm=0b1010101010, bb=0b11, s=1)),
                          ('ldstrpm16',   opcode_factory.ldstrpm16(rd=1, rn=0, rm=0, bb=0b11, s=1)),
                          ('ldstrpm32',   opcode_factory.ldstrpm32(rd=1, rn=0, rm=0, sub=1, bb=0b11, s=1)),
                          ('ldstrind16',  opcode_factory.ldstrind16(rd=1, rn=0, rm=0, bb=0b11, s=1)),
                          ('ldstrind32',  opcode_factory.ldstrind32(rd=1, rn=0, rm=0, sub=1, bb=0b11, s=1)),
                          ('testset32',   opcode_factory.testset32(rd=1, rn=0, rm=0, sub=1, bb=0b11)),
                          ('fadd16',      opcode_factory.fadd16(rd=1, rn=0, rm=0)),
                          ('fsub16',      opcode_factory.fsub16(rd=1, rn=0, rm=0)),
                          ('fmul16',      opcode_factory.fmul16(rd=1, rn=0, rm=0)),
                          ('fmadd16',     opcode_factory.fmadd16(rd=1, rn=0, rm=0)),
                          ('fmsub16',     opcode_factory.fmsub16(rd=1, rn=0, rm=0)),
                          ('float16',     opcode_factory.float16(rd=1, rn=0, rm=0)),
                          ('fix16',       opcode_factory.fix16(rd=1, rn=0, rm=0)),
                          ('fabs16',      opcode_factory.fabs16(rd=1, rn=0, rm=0)),
                          ('fadd32',      opcode_factory.fadd32(rd=1, rn=0, rm=0)),
                          ('fsub32',      opcode_factory.fsub32(rd=1, rn=0, rm=0)),
                          ('fmul32',      opcode_factory.fmul32(rd=1, rn=0, rm=0)),
                          ('fmadd32',     opcode_factory.fmadd32(rd=1, rn=0, rm=0)),
                          ('fmsub32',     opcode_factory.fmsub32(rd=1, rn=0, rm=0)),
                          ('float32',     opcode_factory.float32(rd=1, rn=0, rm=0)),
                          ('fix32',       opcode_factory.fix32(rd=1, rn=0, rm=0)),
                          ('fabs32',      opcode_factory.fabs32(rd=1, rn=0, rm=0)),
                          ('movcond32',   opcode_factory.movcond32(condition=0b0000, rd=0, rn=0)),
                          ('movcond16',   opcode_factory.movcond16(condition=0b0000, rd=0, rn=0)),
                          ('movtimm32',   opcode_factory.movtimm32(rd=0b1111, imm=0)),
                          ('movimm32',    opcode_factory.movimm32(rd=0b1111, imm=0)),
                          ('movimm16',    opcode_factory.movimm16(rd=0b1111, imm=0)),
                          ('movfs32',     opcode_factory.movfs32(rn=0b110, rd='IRET')),
                          ('movfs16',     opcode_factory.movfs16(rn=0b110, rd='IRET')),
                          ('movts32',     opcode_factory.movts32(rn='IRET', rd=0b011)),
                          ('movts16',     opcode_factory.movts16(rn='IRET', rd=0)),
                          ('gie16',       opcode_factory.gie16()),
                          ('gid16',       opcode_factory.gid16()),
                          ('nop16',       opcode_factory.nop16()),
                          ('idle16',      opcode_factory.idle16()),
                          ('bkpt16',      opcode_factory.bkpt16()),
                          ('mbkpt16',     opcode_factory.mbkpt16()),
                          ('sync16',      opcode_factory.sync16()),
                          ('rti16',       opcode_factory.rti16()),
                          ('wand16',      opcode_factory.wand16()),
                          ('trap16',      opcode_factory.trap16(trap=0b111111)),
                          ('unimpl',      opcode_factory.unimpl()),
                         ])
def test_decode(name, instr):
    decoded_name, _ = decode(instr)
    assert decoded_name == name


def test_bit32_imm():
    instr = Instruction(opcode_factory.bitr32_immediate(rd=0b110110, rn=0b101101, imm=0b11111),
                        None)
    assert instr.imm5 == 0b11111
    assert instr.rd == 0b110110
    assert instr.rn == 0b101101
    instr = Instruction(opcode_factory.lsr32_immediate(rd=0, rn=0, imm=0b01011),
                        None)
    assert instr.imm5 == 0b01011


def test_bit16_imm():
    instr = Instruction(opcode_factory.bitr16_immediate(rd=0b110, rn=0b101, imm=0b11111),
                        None)
    assert instr.imm5 == 0b11111
    assert instr.rd == 0b110
    assert instr.rn == 0b101
    instr = Instruction(opcode_factory.lsr16_immediate(rd=0, rn=0, imm=0b01011),
                        None)
    assert instr.imm5 == 0b01011


def test_decode_ldstrpmd32():
    instr = opcode_factory.ldstrpmd32(rd=1, rn=0, sub=1, imm=0b1010101010, bb=0b11, s=1)
    name, executefn = decode(instr)
    assert Instruction(instr, '').sub == 1
    assert Instruction(instr, '').s == 1
    assert Instruction(instr, '').size == 0b11


def test_decode_add32_immediate_argument():
    instr = Instruction(opcode_factory.add32_immediate(rd=1, rn=0, imm=0b01010101010), '')
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm11 == 0b01010101010


def test_mov_special_registers():
    # Note that in the MOV 'special' instructions rd and rn are swapped.
    instr = Instruction(opcode_factory.movfs16(rn=0, rd='CONFIG'), '')
    assert instr.rd == 1  # 65 - 64
    assert instr.rn == 0
    instr = Instruction(opcode_factory.movfs32(rn=0, rd='pc'), '')
    assert instr.rd == 3  # 67 - 64
    assert instr.rn == 0
    instr = Instruction(opcode_factory.movts16(rn='CONFIG', rd=0), '')
    assert instr.rd == 0
    assert instr.rn == 1  # 65 - 64
    instr = Instruction(opcode_factory.movts32(rn='pc', rd=0), '')
    assert instr.rd == 0
    assert instr.rn == 3  # 67 -64
