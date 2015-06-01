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

    
def test_execute_add():
    state = State(None, False, 0)
    instr = 0b00000000000010100100010000011111
    name, executefn = decode(instr)
    state.rf[0] = 5
    state.rf[1] = 7
    executefn(state, Instruction(instr, None))
    assert state.rf[2] == 12
    assert state.AZ == 0
