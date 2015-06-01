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
    
    
def test_decode_add():
    instr = 0b00000000000010100100010000011111
    name, _ = decode(instr)
    assert name == "add32"
    instr = 0b00000000010101010010000100011011
    name, _ = decode(instr)
    assert name == "add32"
    
def test_execute_add():
    state = State(None, False, 0)
    instr = 0b00000000000010100100010000011111
    name, executefn = decode(instr)
    state.rf[0] = 5
    state.rf[1] = 7
    executefn(state, Instruction(instr, None))
    assert state.rf[2] == 12
    assert state.AZ == 0

    
def test_add_immediate_argument():
    #                             iiiiiiii      iii
    instr = Instruction(0b00000000010101010010000100011011, "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010
    
def test_execute_add_immediate():
    state = State(None, False, 0)
    instr = 0b00000000010101010010000100011011
    name, executefn = decode(instr)
    state.rf[0] = 5
    executefn(state, Instruction(instr, None))
    assert state.rf[1] == 0b01010101010 + 5
    assert state.AZ == 0    

def test_decode_nop():
    instr = 0b0000000000000000000000110100010
    name, _ = decode(instr)
    assert name == "nop"

