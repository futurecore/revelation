from pydgin.debug import Debug
from epiphany.machine import State
from epiphany.sim import new_memory
from epiphany.isa import reg_map


def new_state(mem=None, **args):
    possible_attributes = "AN AZ AC AV AVS BN BZ pc".split()
    if mem is None:
        mem = new_memory()
    state = State(mem, Debug(), reset_addr=0x00)
    for attr in possible_attributes:
        if attr in args:
            setattr(state, attr, args[attr])
        else:
            setattr(state, attr, 0b0)
    for arg, value in args.items():
        if arg in possible_attributes:
            continue
        elif arg.startswith("rf") and arg[2].isdigit():
            index = int(arg[2:])
            if index >= 107:
                raise ValueError("The Epiphany only has 107 registers cannot set rf[%d]." %
                                 index)
            state.set_register(index, value)
        elif arg.startswith("rf") and arg[2:] in reg_map:
            state.set_register(reg_map[arg[2:]], value)
        else:
            raise KeyError('No such register: {0}'.format(arg[2:]))
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
            if arg in self.possible_attributes:
                continue
            elif arg.startswith("rf") and arg[2].isdigit():
                index = int(arg[2:])
                if index >= 107:
                    raise ValueError("The Epiphany only has 107 registers cannot set rf[%d]." %
                                     index)
                self.expected_registers.append((index, value))
            elif arg.startswith("rf") and arg[2:] in reg_map:
                self.expected_registers.append((reg_map[arg[2:]], value))
            else:
                raise KeyError('No such register: {0}'.format(arg[2:]))

    def check(self, state):
        for index, expected in self.expected_registers:
            got = state.rf[index]
            if index > 63:
                reg_name = (key for key, value in reg_map.items() if value==index).next()
            else:
                reg_name = index
            if expected != got:
                raise ValueError("Register %s differs. expected: %s got: %s" %
                                 (reg_name, expected, got))
        for attr in self.possible_attributes:
            if attr in self.interesting_state:
                expected = getattr(self, attr)
                got = getattr(state, attr)
                if expected != got:
                    raise ValueError("Flags %s differ. expected: %s got: %s" %
                                     (attr, expected, got))
