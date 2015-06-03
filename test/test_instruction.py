from pydgin.debug import Debug
from pydgin.utils import trim_32

from epiphany.instruction import Instruction
from epiphany.isa import decode, should_branch
from epiphany.machine import State, StateChecker
from epiphany.sim import new_memory

import opcode_factory
import pytest

def new_state(**args):
    return State(new_memory(), Debug(), **args)


def test_add_register_arguments():
    instr = Instruction(opcode_factory.int_arith32('add', 2, 1, 0), "")
    assert instr.rd == 2
    assert instr.rn == 1
    assert instr.rm == 0
    instr = Instruction(opcode_factory.int_arith32('add', 10, 9, 8), "")
    assert instr.rd == 2 + 8
    assert instr.rn == 1 + 8
    assert instr.rm == 0 + 8


@pytest.mark.parametrize("name,expected", [("add", {'AZ':0, 'rf2':12}),
                                           ("sub", {'AZ':0, 'AN':0, 'rf2':2}),
                                          ])
def test_execute_add32(name, expected):
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=4, **expected)
    expected_state.check(state)

@pytest.mark.parametrize("name,expected", [("asr", 5 >> 7),
                                          ])
def test_shifts32(name, expected):
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=1, pc=4, rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize("name,expected", [("asr", 5 >> 7),
                                          ])
def test_shifts16(name, expected):
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith16(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=1, pc=2, rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize("name,expected", [("and", 5 & 7),
                                           ("orr", 5 | 7),
                                           ("eor", 5 ^ 7),
                                          ])
def test_bitwise32(name, expected):
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=4, rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize("name,expected", [("and", 5 & 7),
                                           ("orr", 5 | 7),
                                           ("eor", 5 ^ 7),
                                          ])
def test_bitwise16(name, expected):
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith16(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=2, rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize("name,imm,expected",
                         [("add", 0b01010101010, {'AZ':0, 'rf1':(0b01010101010 + 5)}),
                          ("sub", 0b01010101010, {'AZ':0, 'AN':1, 'AC':1,
                                   'rf1':trim_32(5 - 0b01010101010)}),
                          ("sub", 0b00000000101, {'AZ':1, 'AN':0, 'AC':0, 'rf1':0}),
                         ])
def test_execute_arith32_immediate(name, imm, expected):
    state = new_state(rf0=5)
    instr = opcode_factory.int_arith32_immediate(name, 1, 0, imm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=4, **expected)
    expected_state.check(state)


def test_execute_nop16():
    state = new_state()
    instr = opcode_factory.nop16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=2)
    expected_state.check(state)


def test_sub32_immediate_argument():
    instr = Instruction(opcode_factory.int_arith32_immediate('sub', 1, 0, 0b01010101010), "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010


def test_should_branch():
    state = new_state(AZ=1)
    assert should_branch(state, 0b0000)
    state.AZ = 0
    assert not should_branch(state, 0b0000)
    # TODO: add more of these.


def test_execute_movcond32():
    state = new_state(AZ=1, rf1=111)
    instr = opcode_factory.movcond32(0b0000, 0, 1)
    name, executefn = decode(instr)
    assert name == "movcond32"
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=111)
    expected_state.check(state)


def test_execute_ldpmd32():
    state = new_state(rf5=8)
    state.mem.write(8, 4, 42) # Start address, number of bytes, value
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    #       opcode_factory.ldstrpmd32(rd, rn, sub, imm, bb, s):
    instr = opcode_factory.ldstrpmd32(0,   5,   1,   1, 0b10, 0)
    assert Instruction(instr, "").bit4 == 0
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=4)
    expected_state.check(state)


def test_execute_strpmd32():
    state = new_state(rf0=42, rf5=8)
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    #       opcode_factory.ldstrpmd32(rd, rn, sub, imm, bb, s):
    instr = opcode_factory.ldstrpmd32(0,   5,   1,   1, 0b10, 1)
    assert Instruction(instr, "").bit4 == 1
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=4)
    expected_state.check(state)
    assert 42 == state.mem.read(8, 4) # Start address, number of bytes


def test_execute_jr32():
    state = new_state(rf0=111)
    instr = opcode_factory.jr32(0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=111)
    expected_state.check(state)

# TODO: test bcond32
