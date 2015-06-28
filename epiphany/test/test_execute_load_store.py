from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.test.machine import StateChecker, new_state

import opcode_factory
import pytest


@pytest.mark.parametrize('sub,address', [(1, 8 - 4),
                                         (0, 8 + 4),
                                         (1, 8 - 4),
                                         (0, 8 + 4)])
def test_execute_ldr_disp_pm(sub, address):
    # Load.
    state = new_state(rf5=8)
    state.mem.write(address, 4, 42) # Start address, number of bytes, value
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrpmd32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=address)
    expected_state.check(state)


@pytest.mark.parametrize('sub,expected', [(1, 8 - 4),
                                          (0, 8 + 4),
                                          (1, 8 - 4),
                                          (0, 8 + 4)])
def test_execute_str_disp_pm(sub, expected):
    # Store.
    state = new_state(rf0=0xFFFFFFFF, rf5=8)
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    instr = opcode_factory.ldstrpmd32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    address = 8 - (1 << 2) if sub else 8 + (1 << 2)
    expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=address)
    expected_state.check(state, memory=[(address, 4, 0xFFFFFFFF)])


@pytest.mark.parametrize('is16bit,sub,address', [(False, 1, 8 - (1 << 2)),
                                                 (False, 0, 8 + (1 << 2)),
                                                 (True,  0, 8 + (1 << 2))])
def test_execute_ldr_disp(is16bit, sub, address):
    # Load.
    state = new_state(rf0=0, rf5=8)
    state.mem.write(address, 4, 0xFFFFFFFF) # Start address, number of bytes, value
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    if is16bit:
        instr = opcode_factory.ldstrdisp16(rd=0, rn=5, imm=1, bb=0b10, s=0)
    else:
        instr = opcode_factory.ldstrdisp32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=8)
    expected_state.check(state)


@pytest.mark.parametrize('is16bit,sub,expected', [(False, 1, 8 - (1 << 2)),
                                                  (False, 0, 8 + (1 << 2)),
                                                  (True,  0, 8 + (1 << 2))])
def test_execute_str_disp(is16bit, sub, expected):
    # Store.
    state = new_state(rf0=0xFFFFFFFF, rf5=8)
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    if is16bit:
        instr = opcode_factory.ldstrdisp16(rd=0, rn=5, imm=1, bb=0b10, s=1)
    else:
        instr = opcode_factory.ldstrdisp32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    address = 8 - (1 << 2) if sub else 8 + (1 << 2)
    expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=8)
    expected_state.check(state, memory=[(address, 4, 0xFFFFFFFF)])


@pytest.mark.parametrize('is16bit', [True, False])
def test_ldr_index(is16bit):
    # Load.
    state = new_state(rf0=0, rf5=8, rf6=8)
    state.mem.write(16, 4, 0xFFFFFFFF)
    if is16bit:
        instr = opcode_factory.ldstrind16(rd=0, rn=5, rm=6, bb=0b10, s=0)
    else:
        instr = opcode_factory.ldstrind32(rd=0, rn=5, rm=6, sub=0, bb=0b10, s=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=8, rf6=8)
    expected_state.check(state)


@pytest.mark.parametrize('is16bit', [True, False])
def test_str_index(is16bit):
    # Store.
    state = new_state(rf0=0xFFFFFFFF, rf5=8, rf6=8)
    if is16bit:
        instr = opcode_factory.ldstrind16(rd=0, rn=5, rm=6, bb=0b10, s=1)
    else:
        instr = opcode_factory.ldstrind32(rd=0, rn=5, rm=6, sub=0, bb=0b10, s=1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=8, rf6=8)
    expected_state.check(state, memory=[(16, 4, 0xFFFFFFFF)])


@pytest.mark.parametrize('is16bit', [True, False])
def test_ldr_pm(is16bit):
    # Load.
    state = new_state(rf0=0, rf5=8, rf6=8)
    state.mem.write(16, 4, 0xFFFFFFFF)
    if is16bit:
        instr = opcode_factory.ldstrpm16(rd=0, rn=5, rm=6, bb=0b10, s=0)
    else:
        instr = opcode_factory.ldstrpm32(rd=0, rn=5, rm=6, sub=0, bb=0b10, s=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=16, rf6=8)
    expected_state.check(state)


@pytest.mark.parametrize('is16bit', [True, False])
def test_str_pm(is16bit):
    # Store.
    state = new_state(rf0=0xFFFFFFFF, rf5=8, rf6=8)
    if is16bit:
        instr = opcode_factory.ldstrpm16(rd=0, rn=5, rm=6, bb=0b10, s=1)
    else:
        instr = opcode_factory.ldstrpm32(rd=0, rn=5, rm=6, sub=0, bb=0b10, s=1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=16, rf6=8)
    expected_state.check(state, memory=[(16, 4, 0xFFFFFFFF)])


def test_testset32_zero():
    state = new_state(rf0=0xFFFF, rf1=0x80002, rf2=0x80002)
    size = 0b10  # Word
    state.mem.write(0x00100004, 4, 0x0)
    instr = opcode_factory.testset32(rd=0, rn=1, rm=2, sub=0, bb=size)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0, rf1=0x80002, rf2=0x80002)
    expected_state.check(state, memory=[(0x00100004, 4, 0xFFFF)])


def test_testset32_nonzero():
    state = new_state(rf0=0, rf1=0x80002, rf2=0x80002)
    size = 0b10  # Word
    state.mem.write(0x00100004, 4, 0xFFFF)
    instr = opcode_factory.testset32(rd=0, rn=1, rm=2, sub=0, bb=size)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=0xFFFF, rf1=0x80002, rf2=0x80002,)
    expected_state.check(state, memory=[(0x00100004, 4, 0xFFFF)])


def test_testset32_fail():
    expected_text = """testset32 has failed to write to address %s.
The absolute address used for the test and set instruction must be located
within the on-chip local memory and must be greater than 0x00100000 (2^20).
""" % str(hex(0x4))
    state = new_state(rf0=0, rf1=0x2, rf2=0x2)
    size = 0b10  # Word
    state.mem.write(0x00100004, 4, 0xFFFF)
    instr = opcode_factory.testset32(rd=0, rn=1, rm=2, sub=0, bb=size)
    name, executefn = decode(instr)
    with pytest.raises(ValueError) as exninfo:
        executefn(state, Instruction(instr, None))
    assert expected_text == exninfo.value.message
