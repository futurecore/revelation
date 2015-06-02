from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.machine import State


def test_add_register_arguments():
    instr = Instruction(0b00000000000010100100010000011111, "")
    assert instr.rd == 2
    assert instr.rn == 1
    assert instr.rm == 0

    instr = Instruction(0b00100100100010100100010000011111, "")
    assert instr.rd == 2 + 8
    assert instr.rn == 1 + 8
    assert instr.rm == 0 + 8


def test_decode_add32():
    instr = 0b00000000000010100100010000011111
    name, _ = decode(instr)
    assert name == "add32"
    instr = 0b00000000010101010010000100011011
    name, _ = decode(instr)
    assert name == "add32"


def test_execute_add32():
    state = State(None, False, 0)
    instr = 0b00000000000010100100010000011111
    name, executefn = decode(instr)
    state.rf[0] = 5
    state.rf[1] = 7
    executefn(state, Instruction(instr, None))
    assert state.rf[2] == 12
    assert state.AZ == 0
    assert state.pc == 4


def test_decode_add32_immediate_argument():
    #                             iiiiiiii      iii
    instr = Instruction(0b00000000010101010010000100011011, "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010


def test_execute_add32_immediate():
    state = State(None, False, 0)
    instr = 0b00000000010101010010000100011011
    name, executefn = decode(instr)
    state.rf[0] = 5
    executefn(state, Instruction(instr, None))
    assert state.rf[1] == 0b01010101010 + 5
    assert state.AZ == 0
    assert state.pc == 4


def test_decode_nop16():
    instr = 0b0000000000000000000000110100010
    name, _ = decode(instr)
    assert name == "nop16"


def test_execute_nop16():
    state = State(None, False, 0)
    instr = 0b0000000000000000000000110100010
    name, executefn = decode(instr)
    save_pc = state.pc
    executefn(state, Instruction(instr, None))
    assert state.pc - save_pc == 2


def test_decode_sub32():
    instr = 0b00000000000010100100010000111111
    name, _ = decode(instr)
    assert name == "sub32"
    instr = 0b00000000010101010010000100111011
    name, _ = decode(instr)
    assert name == "sub32"


def test_sub32_immediate_argument():
    #                             iiiiiiii      iii
    instr = Instruction(0b00000000010101010010000100111011, "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010


def test_execute_sub32():
    state = State(None, False, 0)
    instr = 0b00000000000010100100010000111111
    name, executefn = decode(instr)
    state.rf[0] = 5
    state.rf[1] = 7
    executefn(state, Instruction(instr, None))
    assert state.rf[2] == 2
    assert state.AZ == 0
    assert state.AN == 0  # not Negative
    assert state.pc == 4


def test_execute_sub32_immediate_zero_result():
    from pydgin.utils import trim_32
    state = State(None, False, 0)
    #                 iiiiiiii      iii
    instr = 0b00000000000000000010001010111011
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
    state = State(None, False, 0)
    instr = 0b00000000010101010010000100111011
    name, executefn = decode(instr)
    state.rf[0] = 5
    executefn(state, Instruction(instr, None))
    assert state.rf[1] == trim_32(5 - 0b01010101010)
    assert state.AZ == 0  # Zero
    assert state.AN == 1  # Negative
    assert state.AC == 1  # Borrow, take from utility function. CHECK THIS.
    assert state.pc == 4
