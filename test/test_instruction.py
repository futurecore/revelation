from pydgin.debug import Debug

from epiphany.instruction import Instruction
from epiphany.isa import decode, should_branch
from epiphany.machine import State, StateChecker
from epiphany.sim import new_memory

import opcode_factory

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
    expected_state = StateChecker(AZ=0, pc=4, rf2=12)
    expected_state.check(state)


def test_execute_and32():
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32('and', 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=4, rf2=(5 & 7))
    expected_state.check(state)


def test_execute_and16():
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith16('and', 2, 1, 0) | (0xffff << 16)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=2, rf2=(5 & 7))
    expected_state.check(state)


def test_execute_orr32():
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32('orr', 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=4, rf2=(5 | 7))
    expected_state.check(state)


def test_execute_orr16():
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith16('orr', 2, 1, 0) | (0xffff << 16)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=2, rf2=(5 | 7))
    expected_state.check(state)


def test_execute_eor32():
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32('eor', 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=4, rf2=(5 ^ 7))
    expected_state.check(state)


def test_execute_eor16():
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith16('eor', 2, 1, 0) | (0xffff << 16)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=2, rf2=(5 ^ 7))
    expected_state.check(state)


def test_decode_add32_immediate_argument():
    instr = Instruction(opcode_factory.int_arith32_immediate('add', 1, 0, 0b01010101010), "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010


def test_execute_add32_immediate():
    state = new_state(rf0=5)
    instr = opcode_factory.int_arith32_immediate('add', 1, 0, 0b01010101010)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, pc=4, rf1=(0b01010101010 + 5))
    expected_state.check(state)


def test_decode_nop16():
    name, _ = decode(opcode_factory.nop16())
    assert name == "nop16"


def test_execute_nop16():
    state = new_state()
    instr = opcode_factory.nop16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=2)
    expected_state.check(state)


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
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32('sub', 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=4, AZ=0, AN=0, rf2=2)
    expected_state.check(state)


def test_execute_sub32_immediate_zero_result():
    state = new_state(rf0=5)
    instr = opcode_factory.int_arith32_immediate('sub', 1, 0, 0b00000000101)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=4, AZ=1, AN=0, AC=0, rf1=0)
    expected_state.check(state)


def test_execute_sub32_immediate():
    from pydgin.utils import trim_32
    state = new_state(rf0=5)
    instr = opcode_factory.int_arith32_immediate('sub', 1, 0, 0b01010101010)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=4, AZ=0, AN=1, AC=1,
                                  rf1=trim_32(5 - 0b01010101010))
    expected_state.check(state)


def test_decode_execute_jr32():
    state = new_state(rf0=111)
    instr = opcode_factory.jr32(0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    assert name == "jr32"
    expected_state = StateChecker(pc=111)
    expected_state.check(state)


def test_decode_bcond32():
    instr = opcode_factory.bcond32(0b0000, 0)
    name, executefn = decode(instr)
    assert name == "bcond32"
    # TODO: test execute


def test_should_branch():
    state = new_state(AZ=1)
    assert should_branch(state, 0b0000)
    state.AZ = 0
    assert not should_branch(state, 0b0000)
    # TODO: add more of these.


def test_decode_movcond32():
    instr = opcode_factory.movcond32(0b0000, 0, 0)
    name, executefn = decode(instr)
    assert name == "movcond32"


def test_execute_movcond32():
    state = new_state(AZ=1, rf1=111)
    instr = opcode_factory.movcond32(0b0000, 0, 1)
    name, executefn = decode(instr)
    assert name == "movcond32"
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=111)
    expected_state.check(state)


def test_decode_ldstrpmd32():
    instr = opcode_factory.ldstrpmd32(1, 0, 1, 0b1010101010, 0b11, 1)
    name, executefn = decode(instr)
    assert name == "ldstrpmd32"
    assert Instruction(instr, "").sub_bit24 == 1
    assert Instruction(instr, "").bit4 == 1
    assert Instruction(instr, "").bits_5_6 == 0b11


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
