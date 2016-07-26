from revelation.instruction import Instruction
from revelation.isa import decode
from revelation.machine import RESET_ADDR
from revelation.test.machine import StateChecker, new_state
from revelation.utils import trim_32

import opcode_factory
import pytest


def test_add_register_arguments():
    instr = Instruction(opcode_factory.add32(rd=2, rn=1, rm=0), '')
    assert instr.rd == 2
    assert instr.rn == 1
    assert instr.rm == 0
    instr = Instruction(opcode_factory.add32(rd=10, rn=9, rm=8), '')
    assert instr.rd == 2 + 8
    assert instr.rn == 1 + 8
    assert instr.rm == 0 + 8


@pytest.mark.parametrize('factory,expected',
                         [(opcode_factory.add32, dict(AZ=0, rf2=92)),
                          (opcode_factory.sub32, dict(AZ=0, AN=0, rf2=2)),
                         ])
def test_execute_add32sub32(factory, expected):
    state = new_state(rf0=45, rf1=47)
    instr = factory(rd=2, rn=1, rm=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=(4 + RESET_ADDR), **expected)
    expected_state.check(state)


@pytest.mark.parametrize('factory,expected',
                         [(opcode_factory.add16, dict(AZ=0, rf2=7)),
                          (opcode_factory.sub16, dict(AZ=0, AN=0, rf2=3)),
                         ])
def test_execute_add16sub16(factory, expected):
    state = new_state(rf0=2, rf1=5)
    instr = factory(rd=2, rn=1, rm=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=(2 + RESET_ADDR), **expected)
    expected_state.check(state)



@pytest.mark.parametrize('opcode,imm,expected',
                         [(opcode_factory.add32_immediate, 0b01010101010,
                           dict(AZ=0, rf1=(0b01010101010 + 5))),
                          (opcode_factory.sub32_immediate, 0b01010101010,
                           dict(AZ=0, AN=1, AC=0, rf1=trim_32(5 - 0b01010101010))),
                          (opcode_factory.sub32_immediate, 0b00000000101,
                           dict(AZ=1, AN=0, AC=1, rf1=0)),
                         ])
def test_execute_arith32_immediate(opcode, imm, expected):
    state = new_state(rf0=5)
    instr = opcode(rd=1, rn=0, imm=imm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(pc=(4 + RESET_ADDR), **expected)
    expected_state.check(state)


def test_sub16_imm():
    state = new_state(rf2=0, rf1=0)
    bits = opcode_factory.sub16_immediate(rd=2, rn=1, imm=0b0)
    name, executefn = decode(bits)
    instr = Instruction(bits, '')
    assert instr.rd == 2
    assert instr.rn == 1
    assert instr.imm3 == 0
    executefn(state, instr)
    expected_state = StateChecker(rf2=0, rf1=0)
    expected_state.check(state)


def test_sub16_neg_imm():
    state = new_state(rf2=0, rf1=0)
    bits = opcode_factory.sub16_immediate(rd=2, rn=1, imm=0b111)
    name, executefn = decode(bits)
    instr = Instruction(bits, '')
    assert instr.rd == 2
    assert instr.rn == 1
    assert instr.imm3 == 0b111
    executefn(state, instr)
    expected_state = StateChecker(rf2=1, rf1=0)
    expected_state.check(state)


def test_sub32_immediate_argument():
    instr = Instruction(opcode_factory.sub32_immediate(rd=1, rn=0, imm=0b01010101010), '')
    assert instr.rd == 1
    assert instr.rn == 0
    assert instr.imm11 == 0b01010101010


@pytest.mark.parametrize('rn,rm,is16bit', [(-1, 28, True),
                                           (-1, 28, False),
                                           ( 1, 28, True),
                                           ( 1, 28, False)])
def test_execute_logical_shift_right(rn, rm, is16bit):
    rd = 2
    state = new_state(rf0=trim_32(rn), rf1=trim_32(rm))
    instr = (opcode_factory.lsr16(rd=rd, rn=0, rm=1) if is16bit
             else opcode_factory.lsr32(rd=rd, rn=0, rm=1))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=(False if rn < 0 else True), # 1 >> 5 == 0
                                  AV=0, AC=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=(0b1111 if rn < 0 else 0))
    expected_state.check(state)


@pytest.mark.parametrize('rn,imm,is16bit', [(-1, 28, True),
                                            (-1, 28, False),
                                            ( 1, 28, True),
                                            ( 1, 28, False)])
def test_execute_logical_shift_right_imm(rn, imm, is16bit):
    rd = 2
    state = new_state(rf0=trim_32(rn))
    instr = (opcode_factory.lsr16_immediate(rd=rd, rn=0, imm=imm) if is16bit
             else opcode_factory.lsr32_immediate(rd=rd, rn=0, imm=imm))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=(False if rn < 0 else True), # 1 >> 5 == 0
                                  AV=0, AC=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=(0b1111 if rn < 0 else 0))
    expected_state.check(state)


@pytest.mark.parametrize('rn,rm,is16bit', [(-1, 5, True),
                                           (-1, 5, False),
                                           ( 1, 5, True),
                                           ( 1, 5, False)])
def test_execute_arith_shift_right(rn, rm, is16bit):
    rd = 2
    state = new_state(rf0=trim_32(rn), rf1=trim_32(rm))
    instr = (opcode_factory.asr16(rd=rd, rn=0, rm=1) if is16bit
             else opcode_factory.asr32(rd=rd, rn=0, rm=1))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=(False if rn < 0 else True), # 1 >> 5 == 0
                                  AV=0, AC=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=(trim_32(-1) if rn < 0 else 0))
    expected_state.check(state)


@pytest.mark.parametrize('rn,imm,is16bit', [(-1, 5, True),
                                            (-1, 5, False),
                                            ( 1, 5, True),
                                            ( 1, 5, False)])
def test_execute_arith_shift_right_imm(rn, imm, is16bit):
    rd = 2
    state = new_state(rf0=trim_32(rn))
    instr = (opcode_factory.asr16_immediate(rd=rd, rn=0, imm=imm) if is16bit
             else opcode_factory.asr32_immediate(rd=rd, rn=0, imm=imm))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=(False if rn < 0 else True), # 1 >> 5 == 0
                                  AV=0, AC=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=(trim_32(-1) if rn < 0 else 0))
    expected_state.check(state)


@pytest.mark.parametrize('rn,imm,is16bit,expected',
                         [(0x49438a1d, 8, False, 0x49438a),
                          (0xffff8000, 0x10, False, 0xffffffff)])
def test_execute_arith_shift_right_imm_from_elf(rn, imm, is16bit, expected):
    rd = 2
    state = new_state(rf0=trim_32(rn))
    instr = (opcode_factory.asr16_immediate(rd=rd, rn=0, imm=imm) if is16bit
             else opcode_factory.asr32_immediate(rd=rd, rn=0, imm=imm))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=False,
                                  AV=0, AC=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize('factory,is16bit',
                         [(opcode_factory.lsl16, True),
                          (opcode_factory.lsl32, False)
                         ])
def test_execute_shift_left(factory, is16bit):
    state = new_state(rf0=5, rf1=7)
    instr = factory(rd=2, rn=1, rm=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AN=0, AC=0, AV=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=7 << 5)
    expected_state.check(state)


@pytest.mark.parametrize('factory,is16bit',
                         [(opcode_factory.lsl16_immediate, True),
                          (opcode_factory.lsl32_immediate, False)
                         ])
def test_execute_shift_left_immediate(factory, is16bit):
    state = new_state(rf1=7)
    instr = factory(rd=2, rn=1, imm=5)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AN=0, AC=0, AV=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=7 << 5)
    expected_state.check(state)


@pytest.mark.parametrize('bits,expected,is16bit',
                         [(0b10101010101010101010101010101010,
                           0b01010101010101010101010101010101,
                           True),
                          (0b01010101010101010101010101010101,
                           0b10101010101010101010101010101010,
                           True),
                          (0b10101010101010101010101010101010,
                           0b01010101010101010101010101010101,
                           False),
                          (0b01010101010101010101010101010101,
                           0b10101010101010101010101010101010,
                           False),
                          ])
def test_execute_bitr(bits, expected, is16bit):
    state = new_state(rf0=0, rf1=bits)
    instr = (opcode_factory.bitr16_immediate(rd=2, rn=1, imm=0) if is16bit
             else opcode_factory.bitr32_immediate(rd=2, rn=1, imm=0))
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AC=0, AV=0,
                                  pc=((2 if is16bit else 4) + RESET_ADDR),
                                  rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize('factory,expected', [(opcode_factory.and32, 5 & 7),
                                              (opcode_factory.orr32, 5 | 7),
                                              (opcode_factory.eor32, 5 ^ 7),
                                          ])
def test_execute_bitwise32(factory, expected):
    state = new_state(rf0=5, rf1=7)
    instr = factory(rd=2, rn=1, rm=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AV=0, AC=0, pc=(4 + RESET_ADDR),
                                  rf2=expected)
    expected_state.check(state)


@pytest.mark.parametrize('factory,expected', [(opcode_factory.and16, 5 & 7),
                                              (opcode_factory.orr16, 5 | 7),
                                              (opcode_factory.eor16, 5 ^ 7),
                                             ])
def test_execute_bitwise16(factory, expected):
    state = new_state(rf0=5, rf1=7)
    instr = factory(rd=2, rn=1, rm=0)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    expected_state = StateChecker(AZ=0, AV=0, AC=0, pc=(2 + RESET_ADDR),
                                  rf2=expected)
    expected_state.check(state)
