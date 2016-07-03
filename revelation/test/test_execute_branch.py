from revelation.instruction import Instruction
from revelation.isa import decode
from revelation.machine import RESET_ADDR
from revelation.test.machine import new_state, StateChecker

import opcode_factory
import pytest

@pytest.mark.parametrize('is16bit,cond,imm,offset',
                         [# BEQ (never branches here).
                          (False, 0b0000, 63,  (63 << 1)),
                          (True,  0b0000, 127, (127 << 1)),
                          (False, 0b0000, pow(2, 24) - 1, (-1 << 1)),
                          (True,  0b0000, pow(2, 8) - 1, (-1 << 1)),
                          # B (unconditional).
                          (False, 0b1110, 63,  (63 << 1)),
                          (True,  0b1110, 127, (127 << 1)),
                          (False, 0b1110, pow(2, 24) - 1, (-1 << 1)),
                          (True,  0b1110, pow(2, 8) - 1, (-1 << 1)),
                          ])
def test_execute_bcond(is16bit, cond, imm, offset):
    state = new_state(AZ=1, pc=90)
    factory = opcode_factory.bcond16 if is16bit else opcode_factory.bcond32
    instr = factory(condition=cond, imm=imm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=(90 + offset), AZ=1)
    expected_state.check(state)


@pytest.mark.parametrize('is16bit', [True, False])
def test_branch_link(is16bit):
    state = new_state()
    cond = 0b1111  # Condition code for branch-and-link
    factory = opcode_factory.bcond16 if is16bit else opcode_factory.bcond32
    instr = factory(condition=cond, imm=0b00011000)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_LR = (2 if is16bit else 4) + RESET_ADDR
    expected = StateChecker(rfLR=expected_LR, pc=(RESET_ADDR + (0b00011000 << 1)))
    expected.check(state)
