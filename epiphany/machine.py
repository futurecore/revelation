#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine
from pydgin.storage import RegisterFile

RESET_ADDR = 0x58

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State(Machine):
    _virtualizable_ = ['pc', 'num_insts', 'AN', 'AZ', 'AC', 'AV',
                       'AVS', 'BN', 'BIS', 'BUS', 'BVS', 'BZ']

    def __init__(self, memory, debug, reset_addr=RESET_ADDR):
        Machine.__init__(self,
                         memory,
                         RegisterFile(constant_zero=False, num_regs=107),
                         debug,
                         reset_addr=RESET_ADDR)

        # Epiphany-specific flags.
        self.AN  = 0b0
        self.AZ  = 0b0
        self.AC  = 0b0
        self.AV  = 0b0
        self.AVS = 0b0
        self.BN  = 0b0
        self.BZ  = 0b0
        self.BIS = 0b0
        self.BUS = 0b0
        self.BV  = 0b0
        self.BVS = 0b0

    def set_register(self, index, value):
        self.rf[index] = value

    def fetch_pc( self ):
        return self.pc
