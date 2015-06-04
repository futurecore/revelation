from epiphany.test.machine import StateChecker
from epiphany.machine import State
from epiphany.sim import new_memory

from pydgin.debug import Debug

import pytest

def test_register_out_of_range():
    with pytest.raises(ValueError):
        StateChecker(rf65=0)


def test_registers_differ():
    expected = StateChecker(rf0=0)
    got = State(new_memory(), Debug())
    got.rf[0] = 1
    with pytest.raises(ValueError):
        expected.check(got)


def test_flags_differ():
    expected = StateChecker(AZ=0)
    got = State(new_memory(), Debug())
    got.AZ = 1
    with pytest.raises(ValueError):
        expected.check(got)
