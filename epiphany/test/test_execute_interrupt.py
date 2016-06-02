from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.machine import RESET_ADDR
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
    expected_state = StateChecker(pc=(2 + RESET_ADDR))
    expected_state.check(state)


def test_execute_idle16(capsys):
    state = new_state(rfSTATUS=1)
    instr = opcode_factory.idle16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    out, err = capsys.readouterr()
    expected_state = StateChecker(pc=(2 + RESET_ADDR), rfSTATUS=0)
    expected_text = ('IDLE16 does not wait in this simulator. ' +
                     'Moving to next instruction.')
    expected_state.check(state)
    assert expected_text in out
    assert err == ''
    assert state.running


def test_execute_bkpt16():
    state = new_state(rfDEBUGSTATUS=0)
    instr = opcode_factory.bkpt16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rfDEBUGSTATUS=1)
    expected_state.check(state)
    assert not state.running


def test_execute_rti16_no_interrupt():
    state = new_state(rfIRET=224, rfSTATUS=0b00, pc=0)
    instr = opcode_factory.rti16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=224, rfIRET=224, rfSTATUS=0b00)
    expected_state.check(state)


def test_execute_rti16_with_interrupt():
    state = new_state(rfIRET=224, rfSTATUS=0b10, rfIPEND=0b1000000000, pc=0)
    instr = opcode_factory.rti16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=224, rfIRET=224, rfIPEND=0b0, rfSTATUS=0b00)
    expected_state.check(state)


def test_execute_trap16():
    state = new_state()
    instr = opcode_factory.trap16(trap=3)  # Exit.
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    assert not state.running
    # FIXME: Test other syscalls.


def test_execute_trap_warning(capsys):
    state = new_state()
    instr = opcode_factory.trap16(trap=0b11111)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    out, err = capsys.readouterr()
    expected_state = StateChecker(pc=(2 + RESET_ADDR))
    expected_text = ('WARNING: syscall not implemented: 31')
    expected_state.check(state)
    assert expected_text in out
    assert err == ''
    assert state.running


@pytest.mark.parametrize('name,instr', [('mbkpt16',  opcode_factory.mbkpt16()),
                                        ('sync16',   opcode_factory.sync16()),
                                        ('wand16',   opcode_factory.wand16()),
                                       ])
def test_execute_multicore_instructions(name, instr):
    with pytest.raises(NotImplementedError):
        state = new_state()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


def test_execute_unimpl():
    with pytest.raises(NotImplementedError):
        state = new_state()
        instr = opcode_factory.unimpl()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))
