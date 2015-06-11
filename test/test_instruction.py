from pydgin.utils import trim_32

from epiphany.instruction import Instruction
from epiphany.isa import decode
from epiphany.test.machine import StateChecker, new_state

import opcode_factory
import pytest


def test_add_register_arguments():
    instr = Instruction(opcode_factory.int_arith32('add', 2, 1, 0), "")
    assert instr.rd == 2
    assert instr.rn == 1
    assert instr.rm == 0
    instr = Instruction(opcode_factory.int_arith32('add', 10, 9, 8), "")
    assert instr.rd == 2 + 8
    assert instr.rn == 1 + 8
    assert instr.rm == 0 + 8


@pytest.mark.parametrize("name,expected", [("add", dict(AZ=0, rf2=92)),
                                           ("sub", dict(AZ=0, AN=0, rf2=2)),
                                          ])
def test_execute_add32sub32(name, expected):
    state = new_state(rf0=45, rf1=47)
    instr = opcode_factory.int_arith32(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=4, **expected)
    expected_state.check(state)


@pytest.mark.parametrize("name,expected", [("add", dict(AZ=0, rf2=7)),
                                           ("sub", dict(AZ=0, AN=0, rf2=3)),
                                          ])
def test_execute_add16sub16(name, expected):
    state = new_state(rf0=2, rf1=5)
    instr = opcode_factory.int_arith16(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=2, **expected)
    expected_state.check(state)


@pytest.mark.parametrize("rn,rm,is16bit", [(-1, 28, True),
                                           (-1, 28, False),
                                           ( 1, 28, True),
                                           ( 1, 28, False)])
def test_logical_shift_right(rn, rm, is16bit):
    rd = 2
    state = new_state(rf0=trim_32(rn), rf1=trim_32(rm))
    instr = (opcode_factory.int_arith16("lsr", rd, 0, 1) if is16bit
             else opcode_factory.int_arith32("lsr", rd, 0, 1))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=(False if rn < 0 else True), # 1 >> 5 == 0
                                  AV=0, AC=0,
                                  pc=(2 if is16bit else 4),
                                  rf2=(0b1111 if rn < 0 else 0))
    expected_state.check(state)


@pytest.mark.parametrize("rn,rm,is16bit", [(-1, 5, True),
                                           (-1, 5, False),
                                           ( 1, 5, True),
                                           ( 1, 5, False)])
def test_arith_shift_right(rn, rm, is16bit):
    rd = 2
    state = new_state(rf0=trim_32(rn), rf1=trim_32(rm))
    instr = (opcode_factory.int_arith16("asr", rd, 0, 1) if is16bit
             else opcode_factory.int_arith32("asr", rd, 0, 1))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=(False if rn < 0 else True), # 1 >> 5 == 0
                                  AV=0, AC=0,
                                  pc=(2 if is16bit else 4),
                                  rf2=(trim_32(-1) if rn < 0 else 0))
    expected_state.check(state)


@pytest.mark.parametrize("name,is16bit", [("lsl", True), ("lsl", False)])
def test_shift_left(name, is16bit):
    state = new_state(rf0=5, rf1=7)
    instr = (opcode_factory.int_arith16(name, 2, 1, 0) if is16bit
             else opcode_factory.int_arith32(name, 2, 1, 0))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AN=0, AC=0, AV=0,
                                  pc=(2 if is16bit else 4),
                                  rf2=7 << 5)
    expected_state.check(state)


@pytest.mark.parametrize("name,expected", [("and", 5 & 7),
                                           ("orr", 5 | 7),
                                           ("eor", 5 ^ 7),
                                          ])
def test_bitwise32(name, expected):
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith32(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AV=0, AC=0, pc=4, rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize("name,expected", [("and", 5 & 7),
                                           ("orr", 5 | 7),
                                           ("eor", 5 ^ 7),
                                          ])
def test_bitwise16(name, expected):
    state = new_state(rf0=5, rf1=7)
    instr = opcode_factory.int_arith16(name, 2, 1, 0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AV=0, AC=0, pc=2, rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize("name,imm,expected",
                         [("add", 0b01010101010, dict(AZ=0, rf1=(0b01010101010 + 5))),
                          ("sub", 0b01010101010, dict(AZ=0, AN=1, AC=1,
                                                      rf1=trim_32(5 - 0b01010101010))),
                          ("sub", 0b00000000101, dict(AZ=1, AN=0, AC=0, rf1=0)),
                         ])
def test_execute_arith32_immediate(name, imm, expected):
    state = new_state(rf0=5)
    instr = opcode_factory.int_arith32_immediate(name, 1, 0, imm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=4, **expected)
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


def test_sub32_immediate_argument():
    instr = Instruction(opcode_factory.int_arith32_immediate('sub', 1, 0, 0b01010101010), "")
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm == 0b01010101010


@pytest.mark.parametrize("is16bit,val", [(True, 0b111), (False, 0b1111)])
def test_execute_movcond(is16bit, val):
    state = new_state(AZ=1, rf1=val)
    instr = opcode_factory.movcond16(0b0000, 0, 1) if is16bit else opcode_factory.movcond32(0b0000, 0, 1)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=val)
    expected_state.check(state)


@pytest.mark.parametrize("is16bit,is_t,imm", [(True, False, 0b11111111),
                                              (False, True, 0b0000000011111111),
                                              (False, False, 0b1111111111111111)])
def test_execute_movimm(is16bit, is_t, imm):
    state = new_state(AZ=1, rf2=0)
    if is_t:
        instr = opcode_factory.movtimm32(2, imm)
    elif is16bit:
        instr = opcode_factory.movimm16(2, imm)
    else:
        instr = opcode_factory.movimm32(2, imm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_t = 2 | (imm << 16)
    expected_state = StateChecker(rf2=expected_t) if is_t else StateChecker(rf2=imm)
    expected_state.check(state)


@pytest.mark.parametrize("sub,expected", [(1, 8 - 4), (0, 8 + 4)])
def test_execute_ldpmd32(sub, expected):
    state = new_state(rf5=8)
    state.mem.write(8, 4, 42) # Start address, number of bytes, value
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    #       opcode_factory.ldstrpmd32(rd, rn, sub, imm, bb, s):
    instr = opcode_factory.ldstrpmd32(0,   5, sub,   1, 0b10, 0)
    assert Instruction(instr, "").bit4 == 0
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=expected)
    expected_state.check(state)


@pytest.mark.parametrize("sub,expected", [(1, 8 - 4), (0, 8 + 4)])
def test_execute_strpmd32(sub, expected):
    state = new_state(rf0=42, rf5=8)
    # bb: 00=byte, 01=half-word, 10=word, 11=double-word
    #       opcode_factory.ldstrpmd32(rd, rn, sub, imm, bb, s):
    instr = opcode_factory.ldstrpmd32(0,   5, sub,   1, 0b10, 1)
    assert Instruction(instr, "").bit4 == 1
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rf0=42, rf5=expected)
    expected_state.check(state)
    assert 42 == state.mem.read(8, 4) # Start address, number of bytes


@pytest.mark.parametrize("is16bit,val", [(True, 0b111), (False, 0b1111)])
def test_execute_jr32(is16bit, val):
    state = new_state(rf0=val)
    instr = opcode_factory.jr16(0) if is16bit else opcode_factory.jr32(0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=val)
    expected_state.check(state)


@pytest.mark.parametrize("is16bit,imm,expected_pc",
                         [(False, 0b01111111,  254),
                          (True,  0b011111111, 510)])
def test_bcond(is16bit, imm, expected_pc):
    state = new_state(AZ=1, pc=0)
    instr = opcode_factory.bcond16(0b0000, imm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=expected_pc, AZ=1)
    expected_state.check(state)


def test_execute_bkpt16():
    state = new_state(rfDEBUGSTATUS=0)
    instr = opcode_factory.bkpt16()
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(rfDEBUGSTATUS=1)
    expected_state.check(state)
    assert not state.running


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


@pytest.mark.parametrize("name,instr", [('rti16',  opcode_factory.rti16()),
                                        ('trap16', opcode_factory.trap16(0b111111))])
def test_interrupt_instructions(name, instr):
    with pytest.raises(NotImplementedError):
        state = new_state()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


@pytest.mark.parametrize("name,instr", [('mbkpt16',  opcode_factory.mbkpt16()),
                                        ('sync16',   opcode_factory.sync16()),
                                        ('wand16',   opcode_factory.wand16()),
                                       ])
def test_multicore_instructions(name, instr):
    with pytest.raises(NotImplementedError):
        state = new_state()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))


def test_unimpl16():
    with pytest.raises(NotImplementedError):
        state = new_state()
        instr = opcode_factory.unimpl16()
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))
