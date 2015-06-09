from epiphany.isa import decode
from epiphany.instruction import Instruction

import opcode_factory

def test_decode_add32():
    instr = opcode_factory.int_arith32('add', 0, 0, 0)
    name, _ = decode(instr)
    assert name == "add32"
    instr = opcode_factory.int_arith32('add', 1, 1, 1)
    name, _ = decode(instr)
    assert name == "add32"


def test_decode_nop16():
    name, _ = decode(opcode_factory.nop16())
    assert name == "nop16"


def test_decode_idle16():
    name, _ = decode(opcode_factory.idle16())
    assert name == "idle16"


def test_decode_sub32():
    instr = opcode_factory.int_arith32('sub', 0, 0, 0)
    name, _ = decode(instr)
    assert name == "sub32"
    instr = opcode_factory.int_arith32('sub', 1, 1, 1)
    name, _ = decode(instr)
    assert name == "sub32"


def test_decode_execute_jr32():
    instr = opcode_factory.jr32(0)
    name, executefn = decode(instr)
    assert name == "jr32"


def test_decode_bcond32():
    instr = opcode_factory.bcond32(0b0000, 0)
    name, executefn = decode(instr)
    assert name == "bcond32"


def test_decode_ldstrpmd32():
    instr = opcode_factory.ldstrpmd32(1, 0, 1, 0b1010101010, 0b11, 1)
    name, executefn = decode(instr)
    assert name == "ldstrpmd32"
    assert Instruction(instr, "").sub_bit24 == 1
    assert Instruction(instr, "").bit4 == 1
    assert Instruction(instr, "").bits_5_6 == 0b11


def test_decode_movcond32():
    instr = opcode_factory.movcond32(0b0000, 0, 0)
    name, executefn = decode(instr)
    assert name == "movcond32"


def test_decode_add32_immediate_argument():
    instr = Instruction(opcode_factory.int_arith32_immediate('add', 1, 0, 0b01010101010), "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010
