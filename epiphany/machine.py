#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine
from pydgin.storage import RegisterFile

RESET_ADDR = 0

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
        self.AN  = False
        self.AZ  = False
        self.AC  = False
        self.AV  = False
        self.AVS = False
        self.BN  = False
        self.BZ  = False
        self.BIS = False
        self.BUS = False
        self.BV  = False
        self.BVS = False

    def set_register(self, index, value):
        self.rf[index] = value

    def fetch_pc(self):
        return self.pc

    def debug_flags(self):
        if self.debug.enabled('flags'):
            print ('AN=%s AZ=%s AC=%s AV=%s AVS=%s BN=%s BZ=%s BIS=%s BUS=%s BV=%s BVS=%s ' %
                   (self.AN, self.AZ, self.AC, self.AV, self.AVS,
                    self.BN, self.BZ, self.BIS, self.BUS, self.BV, self.BVS)),
