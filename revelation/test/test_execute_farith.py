from revelation.instruction import Instruction
from revelation.isa import decode
from revelation.test.machine import new_state, StateChecker
from revelation.utils import float2bits

import opcode_factory
import pytest


@pytest.mark.parametrize('rn,ex',
    [(1, StateChecker(rf0=7, BZ=0, BN=0, BIS=0)),
     (2, StateChecker(rf0=0, BZ=1, BN=0, BIS=0)),
     (3, StateChecker(rf0=0x80000000, BZ=0, BN=1, BIS=0)),
     (4, StateChecker(rf0=0xffffffff, BZ=0, BN=1, BIS=0)),
    ])
def test_execute_fix16(rn, ex):
    state = new_state(rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = opcode_factory.fix16(rd=0, rn=rn)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.check(state)


@pytest.mark.parametrize('rn,ex',
    [(1, StateChecker(rf0=7, BZ=0, BN=0, BIS=0)),
     (2, StateChecker(rf0=0, BZ=1, BN=0, BIS=0)),
     (3, StateChecker(rf0=0x80000000, BZ=0, BN=1, BIS=0)),
     (4, StateChecker(rf0=0xffffffff, BZ=0, BN=1, BIS=0)),
    ])
def test_execute_fix32(rn, ex):
    state = new_state(rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = opcode_factory.fix32(rd=0, rn=rn)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.check(state)


@pytest.mark.parametrize('factory,rn,ex',
    [(opcode_factory.float16, 4, StateChecker(rf0=float2bits(float('nan')), BZ=0, BN=0, BIS=0)),
     (opcode_factory.float16, 6, StateChecker(rf0=float2bits(-1.0), BZ=0, BN=1, BIS=0)),
     (opcode_factory.float16, 7, StateChecker(rf0=float2bits(1.0), BZ=0, BN=0, BIS=0)),
     (opcode_factory.float32, 4, StateChecker(rf0=float2bits(float('nan')), BZ=0, BN=0, BIS=0)),
     (opcode_factory.float32, 6, StateChecker(rf0=float2bits(-1.0), BZ=0, BN=1, BIS=0)),
     (opcode_factory.float32, 7, StateChecker(rf0=float2bits(1.0), BZ=0, BN=0, BIS=0)),
    ])
def test_execute_float16(factory, rn, ex):
    state = new_state(rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = factory(rd=0, rn=rn)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,ex',
    [(opcode_factory.float32, 4, StateChecker(rf0=float2bits(float('nan')), BZ=0, BN=0, BIS=0)),
     (opcode_factory.float32, 6, StateChecker(rf0=float2bits(-1.0), BZ=0, BN=1, BIS=0)),
     (opcode_factory.float32, 7, StateChecker(rf0=float2bits(1.0), BZ=0, BN=0, BIS=0)),
    ])
def test_execute_float32(factory, rn, ex):
    state = new_state(rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = factory(rd=0, rn=rn)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,ex',
     [(opcode_factory.fabs16,  1, StateChecker(rf0=float2bits(7.2), BZ=0, BN=0, BIS=0)),
      (opcode_factory.fabs16,  2, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
      (opcode_factory.fabs16,  3, StateChecker(rf0=float2bits(1.5), BZ=0, BN=0, BIS=0)),
      (opcode_factory.fabs16,  4, StateChecker(rf0=float2bits(float('nan')), BZ=0, BN=0, BIS=1)),
      (opcode_factory.fabs32,  1, StateChecker(rf0=float2bits(7.2), BZ=0, BN=0, BIS=0)),
      (opcode_factory.fabs32,  2, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
      (opcode_factory.fabs32,  3, StateChecker(rf0=float2bits(1.5), BZ=0, BN=0, BIS=0)),
      (opcode_factory.fabs32,  4, StateChecker(rf0=float2bits(float('nan')), BZ=0, BN=0, BIS=1)),
    ])
def test_execute_fabs16(factory, rn, ex):
    state = new_state(rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = factory(rd=0, rn=rn)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,ex',
    [(opcode_factory.fabs32,  1, StateChecker(rf0=float2bits(7.2), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fabs32,  2, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fabs32,  3, StateChecker(rf0=float2bits(1.5), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fabs32,  4, StateChecker(rf0=float2bits(float('nan')), BZ=0, BN=0, BIS=1)),
    ])
def test_execute_fabs32(factory, rn, ex):
    state = new_state(rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = factory(rd=0, rn=rn)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,rm,ex',
    [(opcode_factory.fadd16,  1, 1, StateChecker(rf0=float2bits(14.4), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fadd16,  2, 2, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fadd16,  3, 3, StateChecker(rf0=float2bits(-3.0), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fadd16,  4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fsub16,  1, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fsub16,  2, 1, StateChecker(rf0=float2bits(-7.2), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fsub16,  3, 3, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fsub16,  4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fmul16,  1, 1, StateChecker(rf0=float2bits(51.84), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fmul16,  2, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fmul16,  1, 3, StateChecker(rf0=float2bits(-10.8), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fmul16,  4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fmadd16, 1, 1, StateChecker(rf0=float2bits(51.84), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fmadd16, 2, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fmadd16, 1, 3, StateChecker(rf0=float2bits(-10.8), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fmadd16, 4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fmsub16, 1, 1, StateChecker(rf0=float2bits(-51.84), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fmsub16, 2, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fmsub16, 1, 3, StateChecker(rf0=float2bits(+10.8), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fmsub16, 4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
    ])
def test_execute_farith_binary16(factory, rn, rm, ex):
    state = new_state(rf0=float2bits(0.0),
                      rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = factory(rd=0, rn=rn, rm=rm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,rm,ex',
    [(opcode_factory.fadd32,  1, 1, StateChecker(rf0=float2bits(14.4), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fadd32,  2, 2, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fadd32,  3, 3, StateChecker(rf0=float2bits(-3.0), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fadd32,  4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fsub32,  1, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fsub32,  2, 1, StateChecker(rf0=float2bits(-7.2), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fsub32,  3, 3, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fsub32,  4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fmul32,  1, 1, StateChecker(rf0=float2bits(51.84), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fmul32,  2, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fmul32,  1, 3, StateChecker(rf0=float2bits(-10.8), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fmul32,  4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fmadd32, 1, 1, StateChecker(rf0=float2bits(51.84), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fmadd32, 2, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fmadd32, 1, 3, StateChecker(rf0=float2bits(-10.8), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fmadd32, 4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
     (opcode_factory.fmsub32, 1, 1, StateChecker(rf0=float2bits(-51.84), BZ=0, BN=1, BIS=0)),
     (opcode_factory.fmsub32, 2, 1, StateChecker(rf0=float2bits(0.0), BZ=1, BN=0, BIS=0)),
     (opcode_factory.fmsub32, 1, 3, StateChecker(rf0=float2bits(+10.8), BZ=0, BN=0, BIS=0)),
     (opcode_factory.fmsub32, 4, 2, StateChecker(rf0=float2bits(0xffffffff), BZ=0, BN=0, BIS=1)),
    ])
def test_execute_farith_binary32(factory, rn, rm, ex):
    state = new_state(rf0=float2bits(0.0),
                      rf1=float2bits(7.2), rf2=float2bits(0.0),
                      rf3=float2bits(-1.5), rf4=float2bits(float('nan')),
                      rf5=0, rf6=-1, rf7=1)
    instr = factory(rd=0, rn=rn, rm=rm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,rm,ex',
    [(opcode_factory.fmul16, 1, 1, StateChecker(BV=True, BVS=True, BIS=False, BUS=False)),
     (opcode_factory.fmul16, 2, 2, StateChecker(BV=False, BVS=False, BIS=False, BUS=True)),
    ])
def test_underflow_overflow(factory, rn, rm, ex):
    state = new_state(rf1=float2bits(1.0e+38), rf2=float2bits(1e-19), rf3=1)
    instr = factory(rd=0, rn=rn, rm=rm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,rm,ex',
    [(opcode_factory.fadd16,  1, 1, StateChecker(rf0=14,  BZ=0, BN=0)),
     (opcode_factory.fadd16,  2, 2, StateChecker(rf0=-14, BZ=0, BN=1)),
     (opcode_factory.fadd16,  3, 3, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fsub16,  1, 1, StateChecker(rf0=0,   BZ=1, BN=0)),
     (opcode_factory.fsub16,  2, 1, StateChecker(rf0=-14, BZ=0, BN=1)),
     (opcode_factory.fsub16,  2, 2, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fmul16,  1, 1, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmul16,  2, 2, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmul16,  1, 2, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmul16,  1, 3, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fmadd16, 1, 1, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmadd16, 2, 2, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmadd16, 1, 2, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmadd16, 1, 3, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fmsub16, 1, 1, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmsub16, 2, 2, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmsub16, 1, 2, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmsub16, 1, 3, StateChecker(rf0=0,   BZ=1, BN=0)),
    ])
def test_execute_iarith16(factory, rn, rm, ex):
    state = new_state(rf0=0, rf1=7, rf2=-7,rf3=0, rf4=1,
                      rfCONFIG=0b10000000000000000000)  # Signed Integer mode.
    instr = factory(rd=0, rn=rn, rm=rm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)


@pytest.mark.parametrize('factory,rn,rm,ex',
    [(opcode_factory.fadd32,  1, 1, StateChecker(rf0=14,  BZ=0, BN=0)),
     (opcode_factory.fadd32,  2, 2, StateChecker(rf0=-14, BZ=0, BN=1)),
     (opcode_factory.fadd32,  3, 3, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fsub32,  1, 1, StateChecker(rf0=0,   BZ=1, BN=0)),
     (opcode_factory.fsub32,  2, 1, StateChecker(rf0=-14, BZ=0, BN=1)),
     (opcode_factory.fsub32,  2, 2, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fmul32,  1, 1, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmul32,  2, 2, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmul32,  1, 2, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmul32,  1, 3, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fmadd32, 1, 1, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmadd32, 2, 2, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmadd32, 1, 2, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmadd32, 1, 3, StateChecker(rf0=0,   BZ=1, BN=0)),

     (opcode_factory.fmsub32, 1, 1, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmsub32, 2, 2, StateChecker(rf0=-49, BZ=0, BN=1)),
     (opcode_factory.fmsub32, 1, 2, StateChecker(rf0=49,  BZ=0, BN=0)),
     (opcode_factory.fmsub32, 1, 3, StateChecker(rf0=0,   BZ=1, BN=0)),
    ])
def test_execute_iarith32(factory, rn, rm, ex):
    state = new_state(rf0=0, rf1=7, rf2=-7,rf3=0, rf4=1,
                      rfCONFIG=0b10000000000000000000)  # Signed Integer mode.
    instr = factory(rd=0, rn=rn, rm=rm)
    name, executefn = decode(instr)
    executefn(state, Instruction(instr, None))
    ex.fp_check(state)
