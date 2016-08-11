from revelation.registers import reg_map
from revelation.utils import trim_32

from pydgin.misc import FatalError, NotImplementedInstError


def execute_nop16(s, inst):
    """The instruction does nothing, but holds an instruction slot.
    """
    s.pc += 2


def execute_idle16(s, inst):
    """
        STATUS[0]=0
        while(!ILAT){
            PC=PC;
        }
    """
    s.ACTIVE = False


def execute_bkpt16(s, inst):
    """The BKPT instruction causes the processor to halt and wait for external
    inputs. The instruction is only be used by the debugging tools such as
    GDB and should not be user software. The instruction is included here
    only for the purpose of reference.
    """
    raise NotImplementedInstError('bkpt instruction not implemented.')


def execute_mbkpt16(s, inst):
    """Halts all cores within the group (sets DEBUGSTATUS[0] to 1).
    """
    raise NotImplementedInstError('mbkpt instruction not implemented.')


def execute_gie16(s, inst):
    """Enables all interrupts in ILAT register, dependent on the per bit
    settings in the IMASK register.
        STATUS[1]=0
    """
    for index in range(10):
        if not (s.rf[reg_map['IMASK']] & (1 << index)):
            s.rf[reg_map['ILAT']] &= ~(1 << index)
    s.GID = 0
    s.pc += 2


def execute_gid16(s, inst):
    """Disable all interrupts.
        STATUS[1]=1
    """
    s.GID = 1
    s.pc += 2


def execute_sync16(s, inst):
    """Sets the ILAT[0] of all cores within a work group to 1.
    """
    raise NotImplementedInstError('sync instruction not implemented.')


def execute_rti16(s, inst):
    """
    IPEND[_i_] = 0; where _i_ is the current interrupt level being serviced
    STATUS[1] = 0;
    PC = IRET;
    <execute instruction at PC>

    If an RTI instruction is issued outside of an interrupt, the RTI
    proceeds as if there were an interrupt to service:
    https://parallella.org/forums/viewtopic.php?f=23&t=818&hilit=interrupt#p5185
    """
    # Let N be the interrupt level.
    interrupt_level = s.get_pending_interrupt()
    #     Bit N of IPEND is cleared.
    if interrupt_level >= 0:
        s.rf[reg_map['IPEND']] &= ~(1 << interrupt_level)
    #     The GID bit in STATUS is cleared.
    s.GID = 0
    #     PC is set to IRET.
    s.pc = s.rf[reg_map['IRET']]


def execute_swi16(s, inst):
    # http://blog.alexrp.com/revelation-notes/
    # The architecture has an undocumented SWI instruction which raises a software
    # exception. It sets bit 1 of ILAT and sets the EXCAUSE bits in STATUS to
    # 0b0001 (for Epiphany III) or 0b1110 (for Epiphany IV).
    s.rf[reg_map['ILAT']] |= (1 << 1)
    s.EXCAUSE = s.exceptions['SWI']
    s.pc += 2


def execute_trap16(s, inst):
    """The TRAP instruction causes the processor to halt and wait for external
    inputs. The immediate field within the instruction opcode is not processed
    by the hardware but can be used by software such as a debugger or
    operating system to find out the reason for the TRAP instruction.
    """
    import pydgin.syscalls
    undocumented_syscall_funcs = {
        0:  pydgin.syscalls.syscall_write,
        1:  pydgin.syscalls.syscall_read,
        2:  pydgin.syscalls.syscall_open,
        6:  pydgin.syscalls.syscall_close,
    }
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
    if inst.t5 in undocumented_syscall_funcs:
        syscall_handler = undocumented_syscall_funcs[inst.t5]
        retval, errno = syscall_handler(s, s.rf[0], s.rf[1], s.rf[2])
        s.rf[0] = trim_32(retval)
        s.rf[3] = errno
    elif inst.t5 == 3:  # Exit.
        syscall_handler = pydgin.syscalls.syscall_exit
        exit_code = s.rf[0]
        if s.debug.enabled('syscalls') and s.is_first_core:  # pragma: no cover
            s.logger.log(' syscall_exit(status=%x)' % exit_code)
        retval, errno = syscall_handler(s, exit_code, s.rf[1], s.rf[2])
    elif inst.t5 == 4:
        s.rf[0] = 1
        if s.debug.enabled('syscalls') and s.is_first_core:
            s.logger.log(' TRAP: Assertion SUCCEEDED.')
    elif inst.t5 == 5:
        s.rf[0] = 0
        if s.debug.enabled('syscalls') and s.is_first_core:
            s.logger.log(' TRAP: Assertion FAILED.')
    elif inst.t5 == 7: # Initiate system call.
        syscall = s.rf[3]
        syscall_handler = syscall_funcs[syscall]
        arg0, arg1, arg2 = s.rf[0], s.rf[1], s.rf[2]
        if s.debug.enabled('syscalls') and s.is_first_core:  # pragma: no cover
            _debug_syscalls(syscall, arg0, arg1, arg2, s.logger)
        # Map any buffers to core-local addresses, where necessary.
        if syscall in (4, 5, 10, 15):
            if (arg1 >> 20) == 0x0:
                arg1 = s.map_address_to_core_local(arg1)
        retval, errno = syscall_handler(s, arg0, arg1, arg2)
        # Undocumented:
        s.rf[0] = trim_32(retval)
        s.rf[3] = errno
    else:
        raise FatalError('Unknown argument to trap instruction: %d' % inst.t5)
    s.pc += 2


def _debug_syscalls(syscall, arg0, arg1, arg2, logger):
    if syscall == 2:  # pragma: no cover
        logger.log(' syscall_open(filename=%x, flags=%x, mode=%x)' % \
                     (arg0, arg1, arg2))
    elif syscall == 3:  # pragma: no cover
        logger.log(' syscall_close(fd=%x)' % arg0)
    elif syscall == 4:  # pragma: no cover
        logger.log(' syscall_read(fd=%x, buf=%x, count=%x)' % \
                     (arg0, arg1, arg2))
    elif syscall == 5:  # pragma: no cover
        logger.log(' syscall_write(fd=%x, buf=%x, count=%x)' % \
                     (arg0, arg1, arg2))
    elif syscall == 6:  # pragma: no cover
        logger.log(' syscall_lseek(fd=%x, pos=%x, how=%x)' % \
                     (arg0, arg1, arg2))
    elif syscall == 7:  # pragma: no cover
        logger.log(' syscall_unlink(path=%x)' % arg0)
    elif syscall == 10:  # pragma: no cover
        logger.log(' syscall_fstat(fd=%x, buf=%x)' % (arg0, arg1))
    elif syscall == 15:  # pragma: no cover
        logger.log('syscall_stat(path=%x, buf=%x)' % (arg0, arg1))
    elif syscall == 21:  # pragma: no cover
        logger.log('syscall_link(src=%x, link=%x)' % (arg0, arg1))


def execute_wand16(s, inst):
    """
    STATUS[3] = 1
    """
    raise NotImplementedInstError('wand instruction not implemented.')


def execute_unimpl(s, inst):
    """Not implemented exception.
    STATUS[16-19] = 0100  [Epiphany III]
    STATUS[16-19] = 1111  [Epiphany IV]
    """
    s.EXCAUSE = s.exceptions['UNIMPLEMENTED']
    s.pc += 4
