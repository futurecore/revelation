#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State(object):
#    _virtualizable_ = ['pc', 'ncycles', 'N', 'Z', 'C', 'V']
    possible_attributes = "AN AZ AC AV AVS BN BZ pc".split()

    def __init__(self, memory, debug, reset_addr=0x0, **args):
        self.pc       = reset_addr
        self.rf       = RegisterFile(constant_zero=False, num_regs=64)
        self.mem      = memory

        self.running   = True
        self.debug     = debug
        self.rf.debug  = debug
        self.mem.debug = debug

        for attr in self.possible_attributes:
            if attr in args:
                setattr(self, attr, args[attr])
            else:
                setattr(self, attr, 0b0)
        for arg, value in args.items():
            if arg.startswith("rf"):
                index = int(arg[2:])
                self.set_register(index, value)

        # other registers
        self.status   = 0
        self.ncycles  = 0
        self.stats_en = False

        # marks if should be running, syscall_exit sets it false
        self.running = True

    def set_register(self, index, value):
        self.rf[index] = value

    def fetch_pc( self ):
        return self.pc
