from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.test.machine import StateChecker, new_state

import opcode_factory
import pytest


@pytest.mark.parametrize('sub,expected', [(1, 8 - 4), (0, 8 + 4)])
def test_execute_ldpmd32(sub, expected):
    state = new_state(rf5=8)
    state.mem.write(8, 4, 42) # Start address, number of bytes, value
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrpmd32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=0)
    assert Instruction(instr, '').s == 0
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=expected)
    expected_state.check(state)


@pytest.mark.parametrize('sub,expected', [(1, 8 - 4), (0, 8 + 4)])
def test_execute_strpmd32(sub, expected):
    state = new_state(rf0=42, rf5=8)
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrpmd32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=expected)
    expected_state.check(state)
    assert 42 == state.mem.read(8, 4) # Start address, number of bytes


def test_execute_ldstrdisp16():
    state = new_state(rf5=8)
    state.mem.write(8, 4, 42) # Start address, number of bytes, value
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrdisp16(rd=0, rn=5, imm=1, bb=0b10, s=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=12)
    expected_state.check(state)
    state = new_state(rf0=42, rf5=8)
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrdisp16(rd=0, rn=5, imm=1, bb=0b10, s=1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=12)
    expected_state.check(state)
    assert 42 == state.mem.read(8, 4) # Start address, number of bytes


@pytest.mark.parametrize('sub,expected', [(1, 8 - 4),
                                          (0, 8 + 4)])
def test_execute_ldstrdisp32(sub, expected):
    state = new_state(rf5=8)
    state.mem.write(8, 4, 42) # Start address, number of bytes, value
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrdisp32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=expected)
    expected_state.check(state)
    state = new_state(rf0=42, rf5=8)
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrdisp32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=expected)
    expected_state.check(state)
    assert 42 == state.mem.read(8, 4) # Start address, number of bytes


@pytest.mark.parametrize('is16bit', [True, False])
def test_ldstrindex(is16bit):
    state = new_state()
    with pytest.raises(NotImplementedError):
        if is16bit:
            instr = opcode_factory.ldstrind16(rd=0, rn=5, rm=7, sub=0, bb=0b10, s=0)
        else:
            instr = opcode_factory.ldstrind32(rd=0, rn=5, rm=7, sub=0, bb=0b10, s=0)
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


@pytest.mark.parametrize('is16bit', [True, False])
def test_ldstrpm(is16bit):
    state = new_state()
    with pytest.raises(NotImplementedError):
        if is16bit:
            instr = opcode_factory.ldstrpm16(rd=0, rn=5, rm=7, sub=0, bb=0b10, s=0)
        else:
            instr = opcode_factory.ldstrpm32(rd=0, rn=5, rm=7, sub=0, bb=0b10, s=0)
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


def test_testset32():
    state = new_state()
    with pytest.raises(NotImplementedError):
        instr = opcode_factory.testset32(rd=0, rn=5, rm=7, sub=0, bb=0b10)
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))