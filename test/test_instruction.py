from pydgin.debug import Debug

from epiphany.instruction import Instruction
from epiphany.isa import decode, should_branch
from epiphany.machine import State
from epiphany.sim import new_memory

import opcode_factory

def new_state():
    return State(new_memory(), Debug())


def test_add_register_arguments():
    instr = Instruction(opcode_factory.int_arith32('add', 2, 1, 0), "")
    assert instr.rd == 2
    assert instr.rn == 1
    assert instr.rm == 0
    instr = Instruction(opcode_factory.int_arith32('add', 10, 9, 8), "")
    assert instr.rd == 2 + 8
    assert instr.rn == 1 + 8
    assert instr.rm == 0 + 8


def test_decode_add32():
    instr = opcode_factory.int_arith32('add', 0, 0, 0)
    name, _ = decode(instr)
    assert name == "add32"
    instr = opcode_factory.int_arith32('add', 1, 1, 1)
    name, _ = decode(instr)
    assert name == "add32"


def test_execute_add32():
    state = new_state()
    instr = opcode_factory.int_arith32('add', 2, 1, 0)
    name, executefn = decode(instr)
    state.rf[0] = 5
    state.rf[1] = 7
    executefn(state, Instruction(instr, None))
    assert state.rf[2] == 12
    assert state.AZ == 0
    assert state.pc == 4


def test_decode_add32_immediate_argument():
    instr = Instruction(opcode_factory.int_arith32_immediate('add', 1, 0, 0b01010101010), "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010


def test_execute_add32_immediate():
    state = new_state()
    instr = opcode_factory.int_arith32_immediate('add', 1, 0, 0b01010101010)
    name, executefn = decode(instr)
    state.rf[0] = 5
    executefn(state, Instruction(instr, None))
    assert state.rf[1] == 0b01010101010 + 5
    assert state.AZ == 0
    assert state.pc == 4


def test_decode_nop16():
    name, _ = decode(opcode_factory.nop16())
    assert name == "nop16"


def test_execute_nop16():
    state = new_state()
    instr = opcode_factory.nop16()
    name, executefn = decode(instr)
    save_pc = state.pc
    executefn(state, Instruction(instr, None))
    assert state.pc - save_pc == 2


def test_decode_sub32():
    instr = opcode_factory.int_arith32('sub', 0, 0, 0)
    name, _ = decode(instr)
    assert name == "sub32"
    instr = opcode_factory.int_arith32('sub', 1, 1, 1)
    name, _ = decode(instr)
    assert name == "sub32"


def test_sub32_immediate_argument():
    instr = Instruction(opcode_factory.int_arith32_immediate('sub', 1, 0, 0b01010101010), "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010


def test_execute_sub32():
    state = new_state()
    instr = opcode_factory.int_arith32('sub', 2, 1, 0)
    name, executefn = decode(instr)
    state.rf[0] = 5
    state.rf[1] = 7
    executefn(state, Instruction(instr, None))
    assert state.rf[2] == 2
    assert state.AZ == 0
    assert state.AN == 0  # not Negative
    assert state.pc == 4


def test_execute_sub32_immediate_zero_result():
    state = new_state()
    instr = opcode_factory.int_arith32_immediate('sub', 1, 0, 0b00000000101)
    name, executefn = decode(instr)
    state.rf[0] = 5
    executefn(state, Instruction(instr, None))
    assert state.rf[1] == 0
    assert state.AZ == 1  # Zero
    assert state.AN == 0  # Negative
    assert state.AC == 0  # Borrow
    assert state.pc == 4


def test_execute_sub32_immediate():
    from pydgin.utils import trim_32
    state = new_state()
    instr = opcode_factory.int_arith32_immediate('sub', 1, 0, 0b01010101010)
    name, executefn = decode(instr)
    state.rf[0] = 5
    executefn(state, Instruction(instr, None))
    assert state.rf[1] == trim_32(5 - 0b01010101010)
    assert state.AZ == 0  # Zero
    assert state.AN == 1  # Negative
    assert state.AC == 1  # Borrow, take from utility function. CHECK THIS.
    assert state.pc == 4


def test_decode_execute_jr32():
    state = new_state()
    instr = opcode_factory.jr32(0)
    name, executefn = decode(instr)
    state.rf[0] = 111
    executefn(state, Instruction(instr, None))
    assert name == "jr32"
    assert state.pc == 111


def test_decode_bcond32():
    instr = opcode_factory.bcond32(0b0000, 0)
    name, executefn = decode(instr)
    assert name == "bcond32"


def test_should_branch():
    state = new_state()
    state.AZ = 1
    assert should_branch(state, 0b0000)
    state.AZ = 0
    assert not should_branch(state, 0b0000)
    # TODO: add more of these.


def test_decode_movcond32():
    instr = opcode_factory.movcond32(0b0000, 0, 0)
    name, executefn = decode(instr)
    assert name == "movcond32"


def test_execute_movcond32():
    state = new_state()
    state.AZ = 1
    instr = opcode_factory.movcond32(0b0000, 0, 1)
    name, executefn = decode(instr)
    assert name == "movcond32"
    state.rf[1] = 111
    executefn(state, Instruction(instr, None))
    assert state.rf[0] == 111
