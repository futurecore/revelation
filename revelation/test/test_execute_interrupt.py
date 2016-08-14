from revelation.instruction import Instruction
from revelation.isa import decode
from revelation.machine import RESET_ADDR
from revelation.test.machine import StateChecker, new_state

from pydgin.misc import FatalError, NotImplementedInstError

import opcode_factory
import pytest


def test_execute_gid16():
    state = new_state(rfSTATUS=0)
    instr = opcode_factory.gid16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(GID=True)
    expected_state.check(state)


def test_execute_gie16():
    state = new_state(rfSTATUS=0b10)
    instr = opcode_factory.gie16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(GID=False)
    expected_state.check(state)


def test_execute_nop16():
    state = new_state()
    instr = opcode_factory.nop16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=(2 + RESET_ADDR))
    expected_state.check(state)


def test_execute_idle16():
    state = new_state(ACTIVE=True)
    instr = opcode_factory.idle16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=RESET_ADDR, ACTIVE=False)
    expected_state.check(state)


def test_execute_bkpt16():
    state = new_state()
    instr = opcode_factory.bkpt16()
    name, executefn = decode(instr)
    expected_state = StateChecker(pc=(RESET_ADDR + 2), ACTIVE=False,
                                  rfDEBUGSTATUS=1)
    executefn(state, Instruction(instr, None))
    expected_state.check(state)


def test_execute_rti16_no_interrupt():
    state = new_state(rfIRET=224, rfSTATUS=0b00, pc=0)
    instr = opcode_factory.rti16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=224, rfIRET=224, GID=0)
    expected_state.check(state)


def test_execute_rti16_with_interrupt():
    state = new_state(rfIRET=224, GID=1, rfIPEND=0b1000000000, pc=0)
    instr = opcode_factory.rti16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=224, rfIRET=224, rfIPEND=0b0, GID=0)
    expected_state.check(state)


def test_execute_swi16():
    state = new_state(rfSTATUS=0b0, rfILAT=0b0, pc=0)
    instr = opcode_factory.swi16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rfILAT=0b10, EXCAUSE=0b0001)
    expected_state.check(state)


def test_execute_trap16_exit():
    state = new_state()
    instr = opcode_factory.trap16(trap=3)  # Exit.
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    assert not state.running


def test_execute_trap16_assert_success():
    state = new_state()
    instr = opcode_factory.trap16(trap=4)  # Assert success.
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=1)
    expected_state.check(state)


def test_execute_trap16_assert_failure():
    state = new_state()
    instr = opcode_factory.trap16(trap=5)  # Assert failure.
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0)
    expected_state.check(state)


def test_execute_trap_warning():
    state = new_state()
    instr = opcode_factory.trap16(trap=0b11111)
    name, executefn = decode(instr)
    with pytest.raises(FatalError) as exninfo:
        executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=RESET_ADDR)
    expected_text = ('Unknown argument to trap instruction: 31')
    expected_state.check(state)
    assert expected_text == exninfo.value.msg


@pytest.mark.parametrize('name,instr', [('mbkpt16',  opcode_factory.mbkpt16()),
                                        ('sync16',   opcode_factory.sync16()),
                                        ('wand16',   opcode_factory.wand16()),
                                       ])
def test_execute_multicore_instructions(name, instr):
    with pytest.raises(NotImplementedInstError):
        state = new_state()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


def test_execute_unimpl32():
    state = new_state()
    instr = opcode_factory.unimpl32()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(EXCAUSE=0b0100)
    expected_state.check(state)
