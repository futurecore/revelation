from pydgin.debug import Debug, pad, pad_hex
from pydgin.misc import load_program
from pydgin.sim import Sim, init_sim

from revelation.instruction import Instruction
from revelation.isa import decode, reg_map
from revelation.logger import Logger
from revelation.machine import State, RESET_ADDR
from revelation.storage import Memory

LOG_FILENAME = 'r_trace.out'
MEMORY_SIZE = 2**32  # Global on-chip address space.

def new_memory(logger):
    return Memory(size=MEMORY_SIZE, logger=logger)


class Revelation(Sim):
    """Entry point to the simulator.
    """

    def __init__(self):
        Sim.__init__(self, "Revelation", jit_enabled=True)
        self.logger = None
        self.hardware_loop = False
        self.ivt = {  # Interrupt vector table.
            0 : 0x0,  # Sync hardware signal.
            1 : 0x4,  # Floating-point,invalid instruction or alignment.
            2 : 0x8,  # Memory protection fault.
            3 : 0xc,  # Timer0 has expired.
            4 : 0x10, # Timer1 has expired.
            5 : 0x14, # Message interrupt.
            6 : 0x18, # Local DMA channel-0 finished data transfer.
            7 : 0x1c, # Local DMA channel-1 finished data transfer.
            8 : 0x20, # Wired AND-signal interrupt.
            9 : 0x24, # Software-generate user interrupt.
        }
        Sim.help_message = """Pydgin %s Instruction Set Simulator
usage: %s <args> <sim_exe> <sim_args>

<sim_exe>  the executable to be simulated
<sim_args> arguments to be passed to the simulated executable
<args>     the following optional arguments are supported:

--help,-h       Show this message and exit
--env,-e <NAME>=<VALUE>
                Set an environment variable to be passed to the
                simulated program. Can use multiple --env flags to set
                multiple environment variables.
--debug,-d <flags>[:<start_after>]
                Enable debug flags in a comma-separated form (e.g.
                "--debug syscalls,insts"). If provided, debugs starts
                after <start_after> cycles. The following flags are
                supported:
     trace              cycle-by-cycle instructions, pc and syscalls
     rf                 register file accesses
     mem                memory accesses
     flags              update to arithmetic flags
--max-insts <i> Run until the maximum number of instructions
--jit <flags>   Set flags to tune the JIT (see
                rpython.rlib.jit.PARAMETER_DOCS)
"""

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
        if self.debug.enabled('trace') and self.logger:
            self.logger.log('%s %s %s %s' %
                               (pad('%x' % self.state.fetch_pc(), 8, ' ', False),
                                pad_hex(bits), pad(inst_str, 12),
                                pad('%d' % self.state.num_insts, 8)))
        return Instruction(bits, inst_str), exec_fun

    def pre_execute(self):
        # Check whether or not we are in a hardware loop, and set registers
        # after the next instruction, as appropriate. See Section 7.9 of the
        # Epiphany Architecture Reference Rev. 14.03.11:
        #     When the program counter (PC) matches the value in LE and the LC
        #     is greater than zero, the PC gets set to the address in LS. The
        #     LC register decrements automatically every time the program
        #     scheduler completes one iteration of the code loop defined by LS
        #     and LE.
        if (self.state.GID and self.state.pc == self.state.rf[reg_map['LE']]):
            self.state.rf[reg_map['LC']] -= 1
            self.hardware_loop = True

    def post_execute(self):
        if self.debug.enabled('trace') and self.logger:
            self.logger.log('\n')
        # If we are in a hardware loop, and the loop counter is > 0,
        # jump back to the start of the loop.
        if self.hardware_loop and self.state.rf[reg_map['LC']] > 0:
            self.state.pc = self.state.rf[reg_map['LS']]
            self.hardware_loop = False
            return
        # Service interrupts. See: http://blog.alexrp.com/revelation-notes/
        if (self.state.rf[reg_map['ILAT']] > 0 and
             not (self.state.GID or self.state.rf[reg_map['DEBUGSTATUS']] == 1)):
            self._service_interrupts()

    def run(self):
        """Override Sim.run to close the logger on exit.
        """
        Sim.run(self)
        if self.logger:
            self.logger.close()

    def _service_interrupts(self):
        # Let N be the interrupt level:
        latched_interrupt = self.state.get_latched_interrupt()
        pending_interrupt = self.state.get_pending_interrupt()
        # If there is no interrupt to process, return.
        if latched_interrupt == pending_interrupt == -1:
            return
        # If a currently pending interrupt is of a higher priority than
        # the latched interrupt, carry on with the pending interrupt.
        elif (pending_interrupt > -1 and latched_interrupt > -1 and
              latched_interrupt > pending_interrupt):
            return
        # Process the currently latched interrupt.
        interrupt_level = latched_interrupt
        #     The PC is saved in IRET.
        self.state.rf[reg_map['IRET']] = self.state.pc
        #     Bit N in ILAT is cleared.
        self.state.rf[reg_map['ILAT']] &= ~(1 << interrupt_level)
        #     Bit N in IPEND is set.
        self.state.rf[reg_map['IPEND']] |= 1 << interrupt_level
        #     The GID bit in STATUS is set.
        self.state.GID = True
        #     PC is set to an index into the IVT.
        self.state.pc = self.ivt[interrupt_level]

    def init_state(self, exe_file, filename, run_argv, envp, testbin,
                   is_test=False):
        """Revelation has custom logging infrastructure that differs from the
        default provided by Pydgin. This matches e-sim, in that log messages are
        written to a file rather than to STDOUT. This prevents some specious
        differences in the two traces; e.g. the mode of an fstat object
        differing between Revelation and e-sim when the Revelation log is
        redirected from STDOUT to a file. This makes scripts/diff_trace.py much
        more useful.
        """
        if is_test:
            self.debug = Debug()
            Debug.global_enabled = True
        if self.debug.enabled_flags:
            print 'Trace will be written to: %s.' % LOG_FILENAME
            self.logger = Logger(LOG_FILENAME)
        memory = new_memory(self.logger)
        _, _ = load_program(exe_file, memory)
        self.state = State(memory, self.debug, logger=self.logger,
                           coreid=0x808, reset_addr=RESET_ADDR)


init_sim(Revelation())
