from pydgin.utils import trim_32

import epiphany.isa

#-----------------------------------------------------------------------
# nop16
#-----------------------------------------------------------------------
def execute_nop16(s, inst):
    """The instruction does nothing, but holds an instruction slot.
    """
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
    """The BKPT instruction causes the processor to halt and wait for external
    inputs. The instruction is only be used by the debugging tools such as
    GDB and should not be user software. The instruction is included here
    only for the purpose of reference.
    """
    s.rf[epiphany.isa.reg_map['DEBUGSTATUS']] |= 1
    s.pc += 2
    s.running = False


def execute_mbkpt16(s, inst):
    """Halts all cores within the group (sets DEBUGSTATUS[0] to 1).
    """
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
    """Sets the ILAT[0] of all cores within a work group to 1.
    """
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
    """The TRAP instruction causes the processor to halt and wait for external
    inputs. The immediate field within the instruction opcode is not processed
    by the hardware but can be used by software such as a debugger or
    operating system to find out the reason for the TRAP instruction.
    """
    import pydgin.syscalls
    syscall_funcs = {
        2:  pydgin.syscalls.syscall_open,
        3:  pydgin.syscalls.syscall_close,
        4:  pydgin.syscalls.syscall_read,
        5:  pydgin.syscalls.syscall_write,
        6:  pydgin.syscalls.syscall_lseek,
        7:  pydgin.syscalls.syscall_unlink,
        10: pydgin.syscalls.syscall_fstat,
        15: pydgin.syscalls.syscall_stat,
#       19: get_time_of_day,  # TODO r0 = time pointer, r1 = timezone pointer
        21: pydgin.syscalls.syscall_link,
    }
    # Undocumented traps: 0, 1, 2, 6. These are listed as "Reserved" in
    # the reference manual, but have been reported to appear in real programs.
    if inst.t5 == 0 or inst.t5 == 1 or inst.t5 == 2 or inst.t5 == 6:
        if inst.t5 == 0:  # Write.
            syscall_handler = syscall_funcs[5]
        elif inst.t5 == 1:  # Read.
            syscall_handler = syscall_funcs[4]
        elif inst.t5 == 2:  # Open.
            syscall_handler = syscall_funcs[2]
        else:  # Close.
            syscall_handler = syscall_funcs[3]
        retval, errno = syscall_handler(s, s.rf[0], s.rf[1], s.rf[2])
        s.rf[0] = trim_32(retval)
        s.rf[3] = errno
    elif inst.t5 == 3:  # Exit.
        syscall_handler = pydgin.syscalls.syscall_exit
        retval, errno = syscall_handler(s, s.rf[0], s.rf[1], s.rf[2])
    elif inst.t5 == 4:
        if s.debug.enabled('syscalls'):
            print 'TRAP: Assertion SUCCEEDED.'
    elif inst.t5 == 5:
        if s.debug.enabled('syscalls'):
            print 'TRAP: Assertion FAILED.'
    elif inst.t5 == 7: # Initiate system call.
        syscall_handler = syscall_funcs[s.rf[3]]
        retval, errno = syscall_handler(s, s.rf[0], s.rf[1], s.rf[2])
        # Undocumented:
        s.rf[0] = trim_32(retval)
        s.rf[3] = errno
    else:
        print ('WARNING: syscall not implemented: %d. Should be unreachable' %
               inst.t5)
    s.pc += 2


#-----------------------------------------------------------------------
# wand16
#-----------------------------------------------------------------------
def execute_wand16(s, inst):
    """
    STATUS[3] = 1
    """
    raise NotImplementedError('Multicore not implemented.')


#-----------------------------------------------------------------------
# unimpl
#-----------------------------------------------------------------------
def execute_unimpl(s, inst):
    """Not implemented.
    """
    raise NotImplementedError('UNIMPL')
