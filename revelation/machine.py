#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine

from revelation.isa import reg_map
from revelation.storage import RevelationRegisterFile

RESET_ADDR = 0

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State(Machine):
    _virtualizable_ = ['pc', 'num_insts', 'AN', 'AZ', 'AC', 'AV',
                       'AVS', 'BN', 'BIS', 'BUS', 'BVS', 'BZ']

    def __init__(self, memory, debug, reset_addr=RESET_ADDR):
        self.rf = RevelationRegisterFile(memory)
        Machine.__init__(self,
                         memory,
                         self.rf,
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

    @property
    def pc(self):
        return self.rf[reg_map['pc']]

    @pc.setter
    def pc(self, value):
        self.rf[reg_map['pc']] = value

    def fetch_pc(self):
        # Override method from base class. Needed by Pydgin.
        return self.rf[reg_map['pc']]

    def debug_flags(self):
        if self.debug.enabled('flags'):
            print ('AN=%s AZ=%s AC=%s AV=%s AVS=%s BN=%s BZ=%s BIS=%s BUS=%s BV=%s BVS=%s ' %
                   (self.AN, self.AZ, self.AC, self.AV, self.AVS,
                    self.BN, self.BZ, self.BIS, self.BUS, self.BV, self.BVS)),
