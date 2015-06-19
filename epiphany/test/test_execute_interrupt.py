from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.test.machine import StateChecker, new_state

import opcode_factory
import pytest


def test_execute_gid16():
    state = new_state(rfSTATUS=0)
    instr = opcode_factory.gid16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rfSTATUS=0b10)
    expected_state.check(state)


def test_execute_gie16():
    state = new_state(rfSTATUS=0b10)
    instr = opcode_factory.gie16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rfSTATUS=0b00)
    expected_state.check(state)


def test_execute_nop16():
    state = new_state()
    instr = opcode_factory.nop16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=2)
    expected_state.check(state)


def test_execute_idle16():
    state = new_state(rfSTATUS=1)
    instr = opcode_factory.idle16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=2, rfSTATUS=0)
    expected_state.check(state)
    assert state.running


def test_execute_bkpt16():
    state = new_state(rfDEBUGSTATUS=0)
    instr = opcode_factory.bkpt16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rfDEBUGSTATUS=1)
    expected_state.check(state)
    assert not state.running


@pytest.mark.parametrize('name,instr', [('rti16',  opcode_factory.rti16()),
                                        ('trap16', opcode_factory.trap16(0b111111))])
def test_execute_interrupt_instructions(name, instr):
    with pytest.raises(NotImplementedError):
        state = new_state()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


@pytest.mark.parametrize('name,instr', [('mbkpt16',  opcode_factory.mbkpt16()),
                                        ('sync16',   opcode_factory.sync16()),
                                        ('wand16',   opcode_factory.wand16()),
                                       ])
def test_execute_multicore_instructions(name, instr):
    with pytest.raises(NotImplementedError):
        state = new_state()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


def test_execute_unimpl16():
    with pytest.raises(NotImplementedError):
        state = new_state()
        instr = opcode_factory.unimpl16()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))