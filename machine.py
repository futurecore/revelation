#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile

DONT_CARE = 'x'


#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State(object):
#    _virtualizable_ = ['pc', 'ncycles', 'N', 'Z', 'C', 'V']
    def __init__(self, memory, debug, reset_addr=0x0):
        self.pc       = reset_addr
        self.rf       = RegisterFile(constant_zero=False, num_regs=64)
        self.mem      = memory

        self.running   = True
        self.debug     = debug
        self.rf.debug  = debug
        self.mem.debug = debug

        # current program status register (CPSR)
        self.AN    = 0b0      # Negative condition
        self.AZ    = 0b0      # Zero condition
        self.AC    = 0b0      # Carry condition
        self.AV    = 0b0      # Overflow condition
        self.AVS   = 0b0      # Sticky integer overflow flag
        self.BN    = 0b0      # FP zero
        self.BZ    = 0b0      # FP negative

        # other registers
        self.status        = 0
        self.ncycles       = 0
        self.stats_en      = False

        # marks if should be running, syscall_exit sets it false
        self.running       = True

    def fetch_pc( self ):
        return self.pc


class TestState(object):
    """Used only for testing.
    __equals__ tests whether registers and flags of interest are equal to a
    given other state.
    """
    possible_attributes = "AN AZ AC AV AVS pc".split()
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
                self.expected_registers.append((index, value))

        # TODO: Registers

    def check(self, state):
        for attr in self.possible_attributes:
            if attr in self.interesting_state:
                expected = getattr(self, attr)
                got = getattr(state, attr)
                if expected != got:
                    raise ValueError("attrs %s differ. expected: %s got: %s" %
                                         (attr, expected, got))
        for index, expected in self.expected_registers:
            got = state.rf[index]
            if expected != got:
                raise ValueError("register %s differs. expected: %s got: %s" %
                                     (index, expected, got))
