from pydgin.debug import Debug, pad, pad_hex
from pydgin.elf import elf_reader
from pydgin.jit import elidable, hint, JitDriver, set_param, set_user_param
from pydgin.sim import Sim, init_sim

from revelation.argument_parser import cli_parser, DoNotInterpretError
from revelation.elf_loader import load_program
from revelation.instruction import Instruction
from revelation.isa import decode
from revelation.logger import Logger
from revelation.machine import State
from revelation.registers import reg_map
from revelation.storage import Memory
from revelation.utils import format_thousands, get_coords_from_coreid
from revelation.utils import  get_coreid_from_coords, zfill

from pydgin.misc import FatalError, NotImplementedInstError

import time

EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_SYNTAX_ERROR = 2
EXIT_FILE_ERROR = 126
EXIT_CTRL_C = 130
LOG_FILENAME = 'r_trace.out'


def new_memory(logger):
    return Memory(block_size=2**20, logger=logger)


def get_printable_location(pc, core, coreid, opcode):
    hex_pc = pad_hex(pc)
    mnemonic, _ = decode(opcode)
    return 'Core ID: 0x%x PC: %s Instruction: %s' % (coreid, hex_pc, mnemonic)


class Revelation(Sim):

    def __init__(self):
        # DO NOT call Sim.__init__() -- Revelation JIT differs from Pydgin.
        self.profile = False
        self.timer = .0
        self.arch_name_human = 'Revelation'
        self.arch_name = self.arch_name_human.lower()
        self.jit_enabled = True
        if self.jit_enabled:
            self.jitdriver = JitDriver(
                greens = ['pc', 'core', 'coreid', 'opcode'],
                reds = ['tick_counter', 'halted_cores', 'idle_cores',
                        'memory', 'sim', 'state', 'start_time'],
                get_printable_location=get_printable_location)
        self.default_trace_limit = 400000
        self.max_insts = 0
        self.logger = None
        self.core = 0    # Index of current core (moved after each instruction).
        self.rows = 1
        self.cols = 1
        self.first_core = 0x808
        self.ext_base = 0x8e000000  # Base address of 'external' memory.
        self.ext_size = 32  # MB.
        self.switch_interval = 1       # TODO: currently ignored.
        self.user_environment = False  # TODO: currently ignored.
        self.collect_times = False
        self.profile = False  # Collect timing data BEFORE main loop.
        self.states = []  # Cores (revelation.machine.State objects).
        self.hardware_loops = []
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

    @elidable
    def next_core(self, core):
        return (core + 1) % (self.rows * self.cols)

    def fetch_latch(self):
        coreid = self.states[self.core].coreid
        address = (coreid << 20) | 0xf0428
        return self.states[self.core].mem.read(address, 4, from_core=coreid)

    def get_entry_point(self):
        def entry_point(argv):
            self.timer = time.time()
            if self.jit_enabled:
                set_param(self.jitdriver, 'trace_limit', self.default_trace_limit)
            try:
                fname, jit, flags = cli_parser(argv, self, Debug.global_enabled)
            except DoNotInterpretError:  # CLI option such as --help or -h.
                return EXIT_SUCCESS
            except (SyntaxError, ValueError):
                return EXIT_SYNTAX_ERROR
            if jit:  # pragma: no cover
                set_user_param(self.jitdriver, jit)
            self.debug = Debug(flags, 0)
            try:
                elf_file = open(fname, 'rb')
            except IOError:
                print 'Could not open file %s' % fname
                return EXIT_FILE_ERROR
            if self.profile:
                timer = time.time()
                print 'CLI parser took: %fs' % (timer - self.timer)
                self.timer = timer
            self.init_state(elf_file, fname, False)
            for state in self.states:
                self.debug.set_state(state)
            elf_file.close()
            try:
                exit_code = self.run()
            except KeyboardInterrupt:
                return EXIT_CTRL_C
            return exit_code
        return entry_point

    def decode(self, bits):
        mnemonic, function = decode(bits)
        if (self.debug.enabled('trace') and self.logger and
              self.states[self.core].is_first_core):
            self.logger.log('%s %s %s %s' %
               (pad('%x' % self.states[self.core].fetch_pc(), 8, ' ', False),
                pad_hex(bits), pad(mnemonic, 12),
                pad('%d' % self.states[self.core].num_insts, 8)))
        return Instruction(bits, mnemonic), function

    def pre_execute(self):
        # Check whether or not we are in a hardware loop, and set registers
        # after the next instruction, as appropriate. See Section 7.9 of the
        # Epiphany Architecture Reference Rev. 14.03.11:
        #     When the program counter (PC) matches the value in LE and the LC
        #     is greater than zero, the PC gets set to the address in LS. The
        #     LC register decrements automatically every time the program
        #     scheduler completes one iteration of the code loop defined by LS
        #     and LE.
        if (self.states[self.core].GID and
              self.states[self.core].pc == self.states[self.core].rf[reg_map['LE']]):
            self.states[self.core].rf[reg_map['LC']] -= 1
            self.hardware_loops[self.core] = True

    def post_execute(self):
        if (self.debug.enabled('trace') and self.logger and
              self.states[self.core].is_first_core):
            self.logger.log('\n')
        # If we are in a hardware loop, and the loop counter is > 0,
        # jump back to the start of the loop.
        if self.hardware_loops[self.core] and self.states[self.core].rf[reg_map['LC']] > 0:
            self.states[self.core].pc = self.states[self.core].rf[reg_map['LS']]
            self.hardware_loops[self.core] = False
            return
        # Service interrupts. See: http://blog.alexrp.com/revelation-notes/
        if (self.states[self.core].rf[reg_map['ILAT']] > 0 and
             not (self.states[self.core].GID or
                  self.states[self.core].rf[reg_map['DEBUGSTATUS']] == 1)):
            self._service_interrupts()

    def _service_interrupts(self):
        # Let N be the interrupt level:
        latched_interrupt = self.states[self.core].get_latched_interrupt()
        pending_interrupt = self.states[self.core].get_pending_interrupt()
        # If there is no interrupt to process, return.
        if latched_interrupt == -1:
            return
        # If a currently pending interrupt is of a higher priority than
        # the latched interrupt, carry on with the pending interrupt.
        elif (pending_interrupt > -1 and latched_interrupt > -1 and
              latched_interrupt > pending_interrupt):
            return
        # Process the currently latched interrupt.
        interrupt_level = latched_interrupt
        #     The PC is saved in IRET.
        self.states[self.core].rf[reg_map['IRET']] = self.states[self.core].pc
        #     Bit N in ILAT is cleared.
        self.states[self.core].rf[reg_map['ILAT']] &= ~(1 << interrupt_level)
        #     Bit N in IPEND is set.
        self.states[self.core].rf[reg_map['IPEND']] |= 1 << interrupt_level
        #     The GID bit in STATUS is set.
        self.states[self.core].GID = True
        #     PC is set to an index into the IVT.
        self.states[self.core].pc = self.ivt[interrupt_level]
        # If core is IDLE, wake up.
        self.states[self.core].ACTIVE = 1

    def run(self):
        """Fetch, decode, execute, service interrupts loop.
        Override Sim.run to provide multicore and close the logger on exit.
        """
        self = hint(self, promote=True)
        memory = hint(self.memory, promote=True)  # Cores share the same memory.
        coreid = 0     # We save these values so that get_location can print
        opcode = 0     # a more meaningful trace in the JIT log.
        tick_counter = 0  # Number of instructions executed by all cores.
        halted_cores, idle_cores = [], []
        old_pc = 0
        start_time, end_time = time.time(), .0

        while True:
            self.jitdriver.jit_merge_point(pc=self.states[self.core].fetch_pc(),
                                           core=self.core,
                                           coreid=coreid,
                                           opcode=opcode,
                                           tick_counter=tick_counter,
                                           halted_cores=halted_cores,
                                           idle_cores=idle_cores,
                                           memory=memory,
                                           sim=self,
                                           state=self.states[self.core],
                                           start_time=start_time)
            # Fetch PC, decode instruction and execute.
            pc = hint(self.states[self.core].fetch_pc(), promote=True)
            coreid = hint(self.states[self.core].coreid, promote=True)
            old_pc = pc
            opcode = memory.iread(pc, 4, from_core=self.states[self.core].coreid)
            try:
                instruction, function = self.decode(opcode)
                self.pre_execute()
                function(self.states[self.core], instruction)
                self.post_execute()
            except (FatalError, NotImplementedInstError) as error:
                mnemonic, _ = decode(opcode)
                print ('Exception in execution of %s (pc: 0x%s), aborting!' %
                       (mnemonic, pad_hex(pc)))
                print 'Exception message: %s' % error.msg
                # Ensure that entry_point() returns correct exit code.
                return EXIT_GENERAL_ERROR   # pragma: no cover
            # Update instruction counters.
            tick_counter += 1
            self.states[self.core].num_insts += 1
            # Halt if we have reached the maximum instruction count or
            # no more cores are running.
            if self.max_insts != 0 and self.states[self.core].num_insts >= self.max_insts:
                print 'Reached the max_insts (%d), exiting.' % self.max_insts
                break
            if not self.states[self.core].running:
                halted_cores.append(self.core)
                if len(halted_cores) == len(self.states):
                    break
            if not self.states[self.core].ACTIVE:
                idle_cores.append(self.core)
            # Switch cores after every instruction. TODO: Switch interval.
            if tick_counter % self.switch_interval == 0 and len(self.states) > 1:
                while True:
                    self.core = hint(self.next_core(self.core), promote=True)
                    if not (self.core in halted_cores or self.core in idle_cores):
                        break
                    # Idle cores can be reactivated by interrupts.
                    elif (self.core in idle_cores and self.fetch_latch() > 0):
                        idle_cores.remove(self.core)
                        self._service_interrupts()
            if self.states[self.core].fetch_pc() < old_pc:
                self.jitdriver.can_enter_jit(pc=self.states[self.core].fetch_pc(),
                                             core=self.core,
                                             coreid=coreid,
                                             opcode=opcode,
                                             tick_counter=tick_counter,
                                             halted_cores=halted_cores,
                                             idle_cores=idle_cores,
                                             memory=memory,
                                             sim=self,
                                             state=self.states[self.core],
                                             start_time=start_time)
        # End of fetch-decode-execute-service interrupts loop.
        if self.collect_times:
            end_time = time.time()
        print 'Total ticks simulated = %s.' % format_thousands(tick_counter)
        for state in self.states:
            row, col = get_coords_from_coreid(state.coreid)
            print ('Core %s (%s, %s) STATUS: 0x%s, Instructions executed: %s' %
                   (hex(state.coreid), zfill(str(row), 2), zfill(str(col), 2),
                    pad_hex(state.rf[reg_map['STATUS']]),
                    format_thousands(state.num_insts)))
        if self.collect_times:
            execution_time = end_time - start_time
            speed = format_thousands(int(tick_counter / execution_time))
            print 'Total execution time: %fs.' % (execution_time)
            print 'Simulator speed:      %s instructions / second.' % speed
        if self.logger:
            self.logger.close()
        return EXIT_SUCCESS

    def init_state(self, elf_file, filename, testbin, is_test=False):
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
        if self.debug.enabled_flags and Debug.global_enabled:
            print 'Trace will be written to: %s.' % LOG_FILENAME
            self.logger = Logger(LOG_FILENAME)
        if self.profile:
            timer = time.time()
            print 'Debugging set up took: %fs' % (timer - self.timer)
            self.timer = timer
        self.memory = new_memory(self.logger)
        if self.profile:
            timer = time.time()
            print 'Memory creation took: %fs' % (timer - self.timer)
            self.timer = timer
        f_row = (self.first_core >> 6) & 0x3f
        f_col = self.first_core & 0x3f
        elf = elf_reader(elf_file, is_64bit=False)
        coreids = []
        for row in xrange(self.rows):
            for col in xrange(self.cols):
                coreid = get_coreid_from_coords(f_row + row, f_col + col)
                coreids.append(coreid)
                print ('Loading program %s on to core %s (%s, %s)' %
                       (filename, hex(coreid), zfill(str(f_row + row), 2),
                        zfill(str(f_col + col), 2)))
                self.hardware_loops.append(False)
                self.states.append(State(self.memory, self.debug,
                                         logger=self.logger, coreid=coreid))
        load_program(elf, self.memory, coreids, ext_base=self.ext_base,
                     ext_size=self.ext_size)
        self.states[0].set_first_core(True)
        if self.profile:
            timer = time.time()
            print 'ELF file loader took: %fs' % (timer - self.timer)
            self.timer = timer


init_sim(Revelation())
