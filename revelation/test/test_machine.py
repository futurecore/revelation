from revelation.test.machine import StateChecker, new_state
from revelation.utils import float2bits

import pytest

def test_check_memory():
    expected = StateChecker()
    got = new_state()
    got.mem.write(4, 4, 0xFFFF)
    got.mem.write(0, 4, 0x0)
    expected.check(got, memory=[(0x4, 4, 0xFFFF)])
    with pytest.raises(ValueError):
        expected.check(got, memory=[(0x0, 4, 0xFFFF)])


def test_register_out_of_range():
    with pytest.raises(ValueError):
        StateChecker(rf108=0)
    with pytest.raises(ValueError):
        new_state(rf108=0)


def test_register_does_not_exist():
    with pytest.raises(KeyError):
        StateChecker(rfNONSENSE=0)
    with pytest.raises(KeyError):
        new_state(rfNONSENSE=0)


def test_registers_differ():
    expected = StateChecker(rf0=0, rf1=float2bits(5.2), rfLR=0, rfDEBUGSTATUS=1)
    got = new_state(rf0=1)
    with pytest.raises(ValueError):
        expected.check(got)
    got = new_state(rf1=float2bits(5.200000001), rfDEBUGSTATUS=1)
    expected.fp_check(got)
    got = new_state(rf1=float2bits(5.3), rfLR=0, rfDEBUGSTATUS=1)
    with pytest.raises(ValueError):
        expected.fp_check(got)


def test_flags_differ():
    expected = StateChecker(AZ=0, rfLR=0)
    got = new_state(AZ=1, rfLR=0)
    with pytest.raises(ValueError):
        expected.check(got)
    with pytest.raises(ValueError):
        expected.fp_check(got)
