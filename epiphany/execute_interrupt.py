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
        print 'IDLE16 does not wait in this simulator.',
        print 'Moving to next instruction.'
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
    """
    IPEND[_i_] = 0; where _i_ is the current interrupt level being serviced
    STATUS[1] = 0;
    PC = IRET;
    <execute instruction at PC>
    """
    # FIXME: Set IPEND.
    mask = 0xFFFFFFFD
    s.rf[epiphany.isa.reg_map['STATUS']] &= mask
    s.pc = s.rf[epiphany.isa.reg_map['IRET']]


#-----------------------------------------------------------------------
# trap16
#-----------------------------------------------------------------------
def execute_trap16(s, inst):
    import pydgin.syscalls
    syscall_funcs = {
        2: pydgin.syscalls.syscall_open,
        3: pydgin.syscalls.syscall_close,
        4: pydgin.syscalls.syscall_read,
        5: pydgin.syscalls.syscall_write,
        6: pydgin.syscalls.syscall_lseek,
        7: pydgin.syscalls.syscall_unlink,
       10: pydgin.syscalls.syscall_fstat,
       15: pydgin.syscalls.syscall_stat,
    }
    if inst.t5 == 3:  # Exit.
        syscall_handler = pydgin.syscalls.syscall_exit
    elif inst.t5 == 7:
        syscall_handler = syscall_funcs[s.rf[3]]
    else:
        print 'WARNING: syscall not implemented: %d' % inst.t5
        s.pc += 2
        return
    retval, errno = syscall_handler(s, s.rf[0], s.rf[1], s.rf[2])
    s.pc += 2


#-----------------------------------------------------------------------
# wand16
#-----------------------------------------------------------------------
def execute_wand16(s, inst):
    raise NotImplementedError('Multicore not implemented.')


#-----------------------------------------------------------------------
# unimpl
#-----------------------------------------------------------------------
def execute_unimpl(s, inst):
    raise NotImplementedError('UNIMPL')
