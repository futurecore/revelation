from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.test.machine import new_state

import opcode_factory
import pytest


@pytest.mark.parametrize('factory,expected', [(opcode_factory.fadd16,  5 + 7),
                                              (opcode_factory.fsub16,  5 - 7),
                                              (opcode_factory.fmul16,  5 * 7),
                                              (opcode_factory.fmadd16, 5 * 7),
                                              (opcode_factory.fmsub16, 5 * 7),
                                              (opcode_factory.float16, 12),
                                              (opcode_factory.fix16,   100),
                                              (opcode_factory.fabs16,  -100.5),
                                          ])
def test_execute_farith16(factory, expected):
    state = new_state(rf0=5, rf1=7)
    instr = factory(rd=2, rn=1, rm=0)
    name, executefn = decode(instr)
    with pytest.raises(NotImplementedError):
        executefn(state, Instruction(instr, None))


@pytest.mark.parametrize('factory,expected', [(opcode_factory.fadd32,  5 + 7),
                                              (opcode_factory.fsub32,  5 - 7),
                                              (opcode_factory.fmul32,  5 * 7),
                                              (opcode_factory.fmadd32, 5 * 7),
                                              (opcode_factory.fmsub32, 5 * 7),
                                              (opcode_factory.float32, 12),
                                              (opcode_factory.fix32,   100),
                                              (opcode_factory.fabs32,  -100.5),
                                          ])
def test_execute_farith32(factory, expected):
    state = new_state(rf0=5, rf1=7)
    instr = factory(rd=2, rn=1, rm=0)
    name, executefn = decode(instr)
    with pytest.raises(NotImplementedError):
        executefn(state, Instruction(instr, None))


