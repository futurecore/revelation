from revelation.test.machine import StateChecker, new_state


def test_coreid_read_only():
    state = new_state(rfCOREID=0x808)
    # Change by writing to register.
    state.rf[0x65] = 0x100
    expected_state = StateChecker(rfCOREID=0x808)
    expected_state.check(state)
    # Change by writing to memory.
    # This _is_ possible, because we need to be able to write the COREID
    # location when the state is initially constructed.
    state.mem.write(0x808f0704, 12, 0x100)
    expected_state = StateChecker(rfCOREID=0x100)
    expected_state.check(state)
