from revelation.condition_codes import condition_passed
from revelation.test.machine import new_state

import pytest


def test_condition_passed():
    state = new_state(AZ=1)
    assert condition_passed(state, 0b0000)
    state.AZ = 0
    assert condition_passed(state, 0b0001)
    state.AZ = 0
    state.AC = 1
    assert condition_passed(state, 0b0010)
    state.AC = 1
    assert condition_passed(state, 0b0011)
    state.AZ = 1
    state.AC = 0
    assert condition_passed(state, 0b0100)
    state.AC = 0
    assert condition_passed(state, 0b0101)
    state.AZ = 0
    state.AV = state.AN = 2
    assert condition_passed(state, 0b0110)
    state.AZ = 1
    state.AV = state.AN = 3
    assert condition_passed(state, 0b0111)
    state.AV = 4
    state.AN = 3
    assert condition_passed(state, 0b1000)
    state.AZ = 1
    state.AV = 3
    state.AN = 4
    assert condition_passed(state, 0b1001)
    state.BZ = 1
    assert condition_passed(state, 0b1010)
    state.BZ = 0
    assert condition_passed(state, 0b1011)
    state.BN = 1
    state.BZ = 0
    assert condition_passed(state, 0b1100)
    state.BN = 1
    state.BZ = 1
    assert condition_passed(state, 0b1101)
    assert condition_passed(state, 0b1110)
    assert condition_passed(state, 0b1111)
    with pytest.raises(ValueError):
        condition_passed(state, 0b11111)
