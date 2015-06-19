from epiphany.test.machine import StateChecker, new_state

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
    expected = StateChecker(rf0=0)
    got = new_state(rf0=1)
    with pytest.raises(ValueError):
        expected.check(got)


def test_flags_differ():
    expected = StateChecker(AZ=0)
    got = new_state(AZ=1)
    with pytest.raises(ValueError):
        expected.check(got)
