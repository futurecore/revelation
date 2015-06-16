from epiphany.isa import decode
from epiphany.instruction import Instruction

import opcode_factory

import pytest

@pytest.mark.parametrize('name,instr',
                         [('add32',      opcode_factory.add32(rd=0, rn=0, rm=0)),
                          ('add16',      opcode_factory.add16(rd=0, rn=0, rm=0)),
                          ('add32',      opcode_factory.add32(rd=1, rn=1, rm=1)),
                          ('add16',      opcode_factory.add16(rd=1, rn=1, rm=1)),
                          ('sub32',      opcode_factory.sub32(rd=0, rn=0, rm=0)),
                          ('sub16',      opcode_factory.sub16(rd=0, rn=0, rm=0)),
                          ('sub32',      opcode_factory.sub32(rd=1, rn=1, rm=1)),
                          ('sub16',      opcode_factory.sub16(rd=1, rn=1, rm=1)),
                          ('add32',      opcode_factory.add32_immediate(rd=1, rn=0, imm=0b01010101010)),
                          ('add16',      opcode_factory.add16_immediate(rd=1, rn=0, imm=0b0101)),
                          ('sub32',      opcode_factory.sub32_immediate(rd=1, rn=0, imm=0b01010101010)),
                          ('sub16',      opcode_factory.sub16_immediate(rd=1, rn=0, imm=0b0101)),
                          ('and32',      opcode_factory.and32(rd=1, rn=1, rm=1)),
                          ('and16',      opcode_factory.and16(rd=1, rn=1, rm=1)),
                          ('orr32',      opcode_factory.orr32(rd=1, rn=1, rm=1)),
                          ('orr16',      opcode_factory.orr16(rd=1, rn=1, rm=1)),
                          ('eor32',      opcode_factory.eor32(rd=1, rn=1, rm=1)),
                          ('eor16',      opcode_factory.eor16(rd=1, rn=1, rm=1)),
                          ('asr32',      opcode_factory.asr32(rd=1, rn=1, rm=1)),
                          ('asr16',      opcode_factory.asr16(rd=1, rn=1, rm=1)),
                          ('lsr32',      opcode_factory.lsr32(rd=1, rn=1, rm=1)),
                          ('lsr16',      opcode_factory.lsr16(rd=1, rn=1, rm=1)),
                          ('lsl32',      opcode_factory.lsl32(rd=1, rn=1, rm=1)),
                          ('lsl16',      opcode_factory.lsl16(rd=1, rn=1, rm=1)),
                          ('lsrimm16',   opcode_factory.lsr16_immediate(rd=1, rn=1, imm=1)),
                          ('lslimm16',   opcode_factory.lsl16_immediate(rd=1, rn=1, imm=1)),
                          ('asrimm16',   opcode_factory.asr16_immediate(rd=1, rn=1, imm=1)),
                          ('bitrimm16',  opcode_factory.bitr16_immediate(rd=1, rn=1, imm=1)),
                          ('lsrimm32',   opcode_factory.lsr32_immediate(rd=1, rn=1, imm=1)),
                          ('lslimm32',   opcode_factory.lsl32_immediate(rd=1, rn=1, imm=1)),
                          ('asrimm32',   opcode_factory.asr32_immediate(rd=1, rn=1, imm=1)),
                          ('bitrimm32',  opcode_factory.bitr32_immediate(rd=1, rn=1, imm=1)),
                          ('jr32',       opcode_factory.jr32(rn=0)),
                          ('jr16',       opcode_factory.jr16(rn=0)),
                          ('jalr32',     opcode_factory.jalr32(rn=0)),
                          ('jalr16',     opcode_factory.jalr16(rn=0)),
                          ('bcond32',    opcode_factory.bcond32(condition=0b1111, imm=0)),
                          ('bcond16',    opcode_factory.bcond16(condition=0b1111, imm=0)),
                          ('ldstrpmd32', opcode_factory.ldstrpmd32(rd=1, rn=0, sub=1, imm=0b1010101010, bb=0b11, s=1)),
                          ('movcond32',  opcode_factory.movcond32(condition=0b0000, rd=0, rn=0)),
                          ('movcond16',  opcode_factory.movcond16(condition=0b0000, rd=0, rn=0)),
                          ('movtimm32',  opcode_factory.movtimm32(rd=0b1111, imm=0)),
                          ('movimm32',   opcode_factory.movimm32(rd=0b1111, imm=0)),
                          ('movimm16',   opcode_factory.movimm16(rd=0b1111, imm=0)),
                          ('movfs32',    opcode_factory.movfs32(rd=0b110, rn='LR')),
                          ('movfs16',    opcode_factory.movfs16(rd=0b110, rn='r1')),
                          ('movts32',    opcode_factory.movts32(rd='LR', rn=0b011)),
                          ('movts16',    opcode_factory.movts16(rd='r1', rn=0)),
                          ('gie16',      opcode_factory.gie16()),
                          ('gid16',      opcode_factory.gid16()),
                          ('nop16',      opcode_factory.nop16()),
                          ('idle16',     opcode_factory.idle16()),
                          ('bkpt16',     opcode_factory.bkpt16()),
                          ('mbkpt16',    opcode_factory.mbkpt16()),
                          ('sync16',     opcode_factory.sync16()),
                          ('rti16',      opcode_factory.rti16()),
                          ('wand16',     opcode_factory.wand16()),
                          ('trap16',     opcode_factory.trap16(trap=0b111111)),
                          ('unimpl16',   opcode_factory.unimpl16()),
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


def test_mov_registers():
    from epiphany.isa import reg_map
    instr = Instruction(opcode_factory.movfs16(rd=0, rn='SP'), '')
    assert instr.rd == 0
    assert instr.rn == reg_map['SP']
    instr = Instruction(opcode_factory.movfs32(rd=0, rn='SP'), '')
    assert instr.rd == 0
    assert instr.rn == reg_map['SP']
    instr = Instruction(opcode_factory.movts16(rd='r1', rn=0), '')
    assert instr.rd == reg_map['r1']
    assert instr.rn == 0
    instr = Instruction(opcode_factory.movts16(rd='SP', rn=0), '')
    assert instr.rd == reg_map['SP']
    assert instr.rn == 0
    instr = Instruction(opcode_factory.movts32(rd='SP', rn=0), '')
    assert instr.rd == reg_map['SP']
    assert instr.rn == 0

