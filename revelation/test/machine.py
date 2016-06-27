from pydgin.debug import Debug
from revelation.machine import State
from revelation.sim import new_memory
from revelation.isa import reg_map
from revelation.utils import bits2float

flags = 'ACTIVE GID KERNEL WAND AN AZ AC AV AVS BN BV BIS BVS BUS BZ EXCAUSE pc'.split()


def new_state(mem=None, debug=Debug(), **args):
    if mem is None:
        mem = new_memory()
    state = State(mem, debug)
    for attr in flags:
        if attr in args:
            setattr(state, attr, args[attr])
    for arg, value in args.items():
        if arg in flags:
            continue
        elif arg.startswith('rf') and arg[2].isdigit():
            index = int(arg[2:])
            if index >= 107:
                raise ValueError('The Adapteva Epiphany only has 107 registers cannot set rf[%d]. ' %
                                 index)
            state.rf[index] = value
        elif arg.startswith('rf') and arg[2:] in reg_map:
            state.rf[reg_map[arg[2:]]] = value
        else:
            raise KeyError('No such register: {0}'.format(arg[2:]))
    return state


class StateChecker(object):
    """Used only for testing.
    check() tests whether registers and flags of interest are equal to a
    given other state.
    """
    epsilon = 0.0001
    def __init__(self, **args):
        self.interesting_state = []
        for attr in flags:
            if attr in args:
                self.interesting_state.append(attr)
                setattr(self, attr, args[attr])
        self.expected_registers = []
        for arg, value in args.items():
            if arg in flags:
                continue
            elif arg.startswith('rf') and arg[2].isdigit():
                index = int(arg[2:])
                if index >= 107:
                    raise ValueError('The Revelation only has 107 registers cannot set rf[%d]. ' %
                                     index)
                self.expected_registers.append((index, value))
            elif arg.startswith('rf') and arg[2:] in reg_map:
                self.expected_registers.append((reg_map[arg[2:]], value))
            else:
                raise KeyError('No such register: {0}'.format(arg[2:]))

    def check_flags(self, state):
        """Check all machine flags against an expected state.
        """
        for attr in flags:
            if attr in self.interesting_state:
                expected = getattr(self, attr)
                got = getattr(state, attr)
                if expected != got:
                    raise ValueError('Flag %s differs. Expected: %s got: %s' %
                                     (attr, expected, got))

    def check_memory(self, memory, state):
        """Check whether locations in memory are set as expected.
        The 'memory' argument should be an iterable containing 3-tuples of
        address, size (in number of bytes), and expected value.
        """
        if memory is None or memory == []:
            return
        for (location, size, expected) in memory:
            got = state.mem.read(location, size)
            if expected != got:
                    raise ValueError('Memory location %s differs; expected: %s got: %s. ' %
                                     (location, hex(expected), hex(got)))

    def check(self, state, memory=[]):
        """Check all registers and flags against an expected state.
        """
        reg_errors = ''
        for index, expected in sorted(self.expected_registers, key=lambda x: x[0]):
            got = state.rf[index]
            if index > 63:
                reg_name = (key for key, value in reg_map.items() if value==index).next()
            else:
                reg_name = index
            if expected != got:
                reg_errors += ('Register %s differs; expected: %s got: %s. ' %
                                 (reg_name, hex(expected), hex(got)))
        if reg_errors:
            raise ValueError(reg_errors)
        self.check_flags(state)
        self.check_memory(memory, state)

    def fp_check(self, state, memory=[]):
        """Check all registers and flags against an expected state.
        For registers, convert the contents to a Python float and check that
        the state and expected state do not differ by more than self.epsilon.
        """
        for index, expected in self.expected_registers:
            got = state.rf[index]
            if index > 63:
                reg_name = (key for key, value in reg_map.items() if value==index).next()
            else:
                reg_name = index
            if abs(bits2float(expected) - bits2float(got)) > self.epsilon:
                raise ValueError('Register %s differs by more than %.4f; expected: %s got: %s. ' %
                                 (reg_name, self.epsilon,
                                  bits2float(expected), bits2float(got)))
        self.check_flags(state)
        self.check_memory(memory, state)
