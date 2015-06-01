#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
#    _virtualizable_ = ['pc', 'ncycles', 'N', 'Z', 'C', 'V']
    def __init__(self, memory, debug, reset_addr=0x400):
        self.pc       = reset_addr
        self.rf       = RegisterFile(constant_zero=False, num_regs=64)
        
        # current program status register (CPSR)
        self.AN    = 0b0      # Negative condition
        self.AZ    = 0b0      # Zero condition
        self.AC    = 0b0      # Carry condition
        self.AV    = 0b0      # Overflow condition
        self.AVS   = 0b0      # Sticky integer overflow flag
   
        # other registers
        self.status        = 0
        self.ncycles       = 0

        # marks if should be running, syscall_exit sets it false
        self.ACTIVE        = True
        
    def fetch_pc( self ):
        return self.pc


