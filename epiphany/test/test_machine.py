from epiphany.test.machine import StateChecker, new_state
from epiphany.utils import float2bits

import pytest


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
