from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.machine import RESET_ADDR
from epiphany.test.machine import StateChecker, new_state

import opcode_factory
import pytest


@pytest.mark.parametrize('is16bit,val', [(True, 0b111), (False, 0b111111)])
def test_execute_jump(is16bit, val):
    state = new_state(rf0=val)
    instr = opcode_factory.jr16(rn=0) if is16bit else opcode_factory.jr32(0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=val)
    expected_state.check(state)


@pytest.mark.parametrize('is16bit,val', [(True, 0b111), (False, 0b111111)])
def test_execute_jump_and_link(is16bit, val):
    state = new_state(rf0=val)
    instr = opcode_factory.jalr16(rn=0) if is16bit else opcode_factory.jalr32(0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_lr = RESET_ADDR + (2 if is16bit else 4)
    expected_state = StateChecker(pc=val, rfLR=expected_lr)
    expected_state.check(state)
