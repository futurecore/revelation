from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.test.machine import StateChecker, new_state

import opcode_factory
import pytest


@pytest.mark.parametrize('is16bit,val', [(True, 0b111), (False, 0b1111)])
def test_execute_movcond(is16bit, val):
    state = new_state(AZ=1, rf1=val)
    instr = (opcode_factory.movcond16(condition=0b0000, rd=0, rn=1) if is16bit
             else opcode_factory.movcond32(condition=0b0000, rd=0, rn=1))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    pc_expected = 2 if is16bit else 4
    expected_state = StateChecker(pc=pc_expected, rf0=val)
    expected_state.check(state)


@pytest.mark.parametrize('is16bit,is_to,imm', [(True, False, 0b11111111),
                                               (False, True, 0b0000000011111111),
                                               (False, False, 0b1111111111111111)])
def test_execute_movimm(is16bit, is_to, imm):
    state = new_state(AZ=1, rf2=0)
    if is_to:
        instr = opcode_factory.movtimm32(rd=2, imm=imm)
    elif is16bit:
        instr = opcode_factory.movimm16(rd=2, imm=imm)
    else:
        instr = opcode_factory.movimm32(rd=2, imm=imm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_t = 2 | (imm << 16)
    pc_expected = 2 if is16bit else 4
    expected_state = StateChecker(pc=pc_expected, rf2=expected_t) if is_to else StateChecker(pc=pc_expected, rf2=imm)
    expected_state.check(state)


@pytest.mark.parametrize('is16bit,is_from,', [(True,  False),
                                              (True,  True),
                                              (False, False),
                                              (False, True)
                                           ])
def test_execute_mov_special(is16bit, is_from):
    state = new_state(rf0=5, rf1=3, rfSP=7, rfSTATUS=11)
    if is_from and is16bit:
        instr = opcode_factory.movfs16(rd=0, rn='r1')
        expected_state = StateChecker(pc=2, rf0=3, rf1=3, rfSP=7, rfSTATUS=11)
    elif is_from and (not is16bit):
        instr = opcode_factory.movfs32(rd=0, rn='SP')
        expected_state = StateChecker(pc=4, rf0=7, rf1=3, rfSP=7, rfSTATUS=11)
    elif (not is_from) and is16bit:
        instr = opcode_factory.movts16(rd='r1', rn=0)
        expected_state = StateChecker(pc=2, rf0=5, rf1=5, rfSP=7, rfSTATUS=11)
    elif (not is_from) and (not is16bit):
        instr = opcode_factory.movts32(rd='SP', rn=0)
        expected_state = StateChecker(pc=4, rf0=5, rf1=3, rfSP=5, rfSTATUS=11)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state.check(state)


