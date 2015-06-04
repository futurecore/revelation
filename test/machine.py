from pydgin.debug import Debug
from epiphany.machine import State
from epiphany.sim import new_memory


def new_state(**args):
    possible_attributes = "AN AZ AC AV AVS BN BZ pc".split()
    state = State(new_memory(), Debug(), **args)
    for attr in possible_attributes:
        if attr in args:
            setattr(state, attr, args[attr])
        else:
            setattr(state, attr, 0b0)
    for arg, value in args.items():
        if arg.startswith("rf"):
            index = int(arg[2:])
            state.set_register(index, value)
    return state


class StateChecker(object):
    """Used only for testing.
    check() tests whether registers and flags of interest are equal to a
    given other state.
    """
    possible_attributes = "AN AZ AC AV AVS BN BZ pc".split()
    def __init__(self, **args):
        self.interesting_state = []
        for attr in self.possible_attributes:
            if attr in args:
                self.interesting_state.append(attr)
                setattr(self, attr, args[attr])
        self.expected_registers = []
        for arg, value in args.items():
            if arg.startswith("rf"):
                index = int(arg[2:])
                if index >= 64:
                    raise ValueError("The Epiphany only has 64 registers cannot set rf[%d]." %
                                     index)
                self.expected_registers.append((index, value))

    def check(self, state):
        for index, expected in self.expected_registers:
            got = state.rf[index]
            if expected != got:
                raise ValueError("Register %s differs. expected: %s got: %s" %
                                 (index, expected, got))
        for attr in self.possible_attributes:
            if attr in self.interesting_state:
                expected = getattr(self, attr)
                got = getattr(state, attr)
                if expected != got:
                    raise ValueError("Flags %s differ. expected: %s got: %s" %
                                     (attr, expected, got))
