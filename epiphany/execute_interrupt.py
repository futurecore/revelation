import epiphany.isa

#-----------------------------------------------------------------------
# nop16
#-----------------------------------------------------------------------
def execute_nop16(s, inst):
    s.pc += 2


#-----------------------------------------------------------------------
# idle16
#-----------------------------------------------------------------------
def execute_idle16(s, inst):
    """
        STATUS[0]=0
        while(!ILAT){
            PC=PC;
        }
    """
    status = s.rf[epiphany.isa.reg_map['STATUS']]
    mask = 0b1111111111111111111111111110
    status &= mask
    s.rf[epiphany.isa.reg_map['STATUS']] = status
    if not s.rf[epiphany.isa.reg_map['ILAT']]: # TODO: Use threads here?
        pass
    s.pc += 2


#-----------------------------------------------------------------------
# bkpt16 and mbkpt16
#-----------------------------------------------------------------------
def execute_bkpt16(s, inst):
    s.rf[epiphany.isa.reg_map['DEBUGSTATUS']] |= 1
    s.pc += 2
    s.running = False


def execute_mbkpt16(s, inst):
    raise NotImplementedError('Multicore not implemented.')


#-----------------------------------------------------------------------
# gie16 and gid16
#-----------------------------------------------------------------------
def execute_gie16(s, inst):
    """Enables all interrupts in ILAT register, dependent on the per bit
    settings in the IMASK register.
    TODO: Implement interrupts.
        STATUS[1]=0
    """
    s.rf[epiphany.isa.reg_map['STATUS']] &= ~(1 << 1)
    s.pc += 2


def execute_gid16(s, inst):
    """Disable all interrupts.
        STATUS[1]=1
    """
    s.rf[epiphany.isa.reg_map['STATUS']] |= (1 << 1)
    s.pc += 2


#-----------------------------------------------------------------------
# sync16
#-----------------------------------------------------------------------
def execute_sync16(s, inst):
    raise NotImplementedError('Interrupts not implemented.')


#-----------------------------------------------------------------------
# rti16
#-----------------------------------------------------------------------
def execute_rti16(s, inst):
    raise NotImplementedError('Interrupts not implemented.')


#-----------------------------------------------------------------------
# trap16
#-----------------------------------------------------------------------
def execute_trap16(s, inst):
    raise NotImplementedError('Interrupts not implemented.')


#-----------------------------------------------------------------------
# wand16
#-----------------------------------------------------------------------
def execute_wand16(s, inst):
    raise NotImplementedError('Multicore not implemented.')


#-----------------------------------------------------------------------
# unimpl16
#-----------------------------------------------------------------------
def execute_unimpl16(s, inst):
    raise NotImplementedError('UNIMPL16')
