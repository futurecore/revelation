from pydgin.debug import Debug, pad, pad_hex
from pydgin.elf import elf_reader
from pydgin.jit import JitDriver, set_param, set_user_param
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
IVT = {  # Interrupt vector table.
    0 : 0x0,   # Sync hardware signal.
    1 : 0x4,   # Floating-point,invalid instruction or alignment.
    2 : 0x8,   # Memory protection fault.
    3 : 0xc,   # Timer0 has expired.
    4 : 0x10,  # Timer1 has expired.
    5 : 0x14,  # Message interrupt.
    6 : 0x18,  # Local DMA channel-0 finished data transfer.
    7 : 0x1c,  # Local DMA channel-1 finished data transfer.
    8 : 0x20,  # Wired AND-signal interrupt.
    9 : 0x24,  # Software-generate user interrupt.
}


def new_memory(logger):
    return Memory(block_size=2**20, logger=logger)


def get_printable_location(pc):
    """Printed in PYPYLOG while tracing."""
    return 'PC: %s' % pad_hex(pc)


class Revelation(Sim):

    def __init__(self):
        # DO NOT call Sim.__init__() -- Revelation JIT differs from Pydgin.
        self.arch_name_human = 'Revelation'
        self.arch_name = self.arch_name_human.lower()
        self.jit_enabled = True
        if self.jit_enabled:
            self.jitdriver = JitDriver(
                greens = ['pc', ],
                reds = ['core', 'tick_counter', 'coreids', 'sim', 'state',],
                get_printable_location=get_printable_location)
        self.default_trace_limit = 400000
        self.max_insts = 0             # --max-insts.
        self.logger = None             # --debug output: self.logger.log().
        self.rows = 1                  # --rows, -r.
        self.cols = 1                  # --cols, -c.
        self.states = {}               # coreid -> revelation.machine.State.
        self.first_core = 0x808        # --first-core, -f.
        self.ext_base = 0x8e000000     # Base address of 'external' memory.
        self.ext_size = 32             # Size of 'external' memory in MB.
        self.switch_interval = 1       # --switch. TODO: currently ignored.
        self.user_environment = False  # Superuser mode. TODO: currently ignored.
        self.collect_times = False     # --time, -t option.
        self.start_time = .0           # --time, -t option.
        self.end_time = .0             # --time, -t option.
        self.profile = False  # Undocumented --profile option.
        self.timer = .0       # Undocumented --profile option.

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
            for coreid in self.states:
                self.debug.set_state(self.states[coreid])
            elf_file.close()
            try:
                exit_code, tick_counter = self.run()
            except KeyboardInterrupt:
                exit_code = EXIT_CTRL_C
                tick_counter = -1
            if self.collect_times:
                self.end_time = time.time()
            if self.logger:
                self.logger.close()
            self._print_summary_statistics(tick_counter)
            return exit_code
        return entry_point

    def run(self):
        """Fetch, decode, execute, service interrupts loop.
        Override Sim.run to provide multicore and close the logger on exit.
        """
        coreids = self.states.keys()
        core = coreids[0]      # Key to self.states dictionary.
        state = self.states[core]  # revelation.machine.State object.
        pc = state.fetch_pc()  # Program counter.
        tick_counter = 0       # Number of instructions executed by all cores.
        old_pc = 0
        self.start_time = time.time()

        while True:
            self.jitdriver.jit_merge_point(pc=pc,
                                           core=core,
                                           tick_counter=tick_counter,
                                           coreids=coreids,
                                           sim=self,
                                           state=state,)
            # Fetch next instruction.
            opcode = state.mem.iread(pc, 4, from_core=state.coreid)
            try:
                # Decode instruction.
                mnemonic, function = decode(opcode)
                instruction = Instruction(opcode, mnemonic)
                # --debug
                if (state.is_first_core and self.logger and
                      state.debug.enabled('trace')):
                    state.logger.log('%s %s %s %s' %
                        (pad('%x' % pc, 8, ' ', False),
                         pad_hex(opcode), pad(instruction.name, 12),
                         pad('%d' % state.num_insts, 8)))
                # Check whether or not we are in a hardware loop, and set
                # registers after the next instruction, as appropriate. See
                # Section 7.9 of the Architecture Reference Rev. 14.03.11.
                if (state.GID and state.pc == state.rf[reg_map['LE']]):
                    state.rf[reg_map['LC']] -= 1
                    state.is_in_hardware_loop = True
                # Execute next instruction.
                function(state, instruction)
                # --debug
                if (state.is_first_core and state.logger and
                      state.debug.enabled('trace')):
                    state.logger.log('\n')
                # Check hardware loop registers.
                if state.is_in_hardware_loop and state.rf[reg_map['LC']] > 0:
                    state.pc = state.rf[reg_map['LS']]
                    state.is_in_hardware_loop = False
                # Service interrupts.
                if (state.rf[reg_map['ILAT']] > 0 and not (state.GID or
                       state.rf[reg_map['DEBUGSTATUS']] == 1)):
                    interrupt_level = state.get_latched_interrupt()
                    if interrupt_level > -1:  # Interrupt to process.
                        # If a pending interrupt is of a higher priority than
                        # the latched interrupt, carry on with the pending
                        # interrupt.
                        pending_interrupt = state.get_pending_interrupt()
                        if (pending_interrupt == -1 or
                              (pending_interrupt > -1 and
                              interrupt_level <= pending_interrupt)):
                            state.rf[reg_map['IRET']] = state.pc
                            state.rf[reg_map['ILAT']] &= ~(1 << interrupt_level)
                            state.rf[reg_map['IPEND']] |= 1 << interrupt_level
                            state.GID = True  # Set global interrupt disabled bit.
                            state.pc = IVT[interrupt_level]
                            state.ACTIVE = 1  # Wake up IDLE cores.
            except (FatalError, NotImplementedInstError) as error:
                mnemonic, _ = decode(opcode)
                print ('Exception in execution of %s (pc: 0x%s), aborting!' %
                       (mnemonic, pad_hex(pc)))
                print 'Exception message: %s' % error.msg
                return EXIT_GENERAL_ERROR, tick_counter  # pragma: no cover
            # Update instruction counters.
            tick_counter += 1
            state.num_insts += 1
            # Halt if we have reached the maximum instruction count.
            if self.max_insts != 0 and state.num_insts >= self.max_insts:
                print 'Reached the max_insts (%d), exiting.' % self.max_insts
                break
            # Check whether state has halted.
            if not state.running:
                if len(coreids) == 1:  # Last running core has halted.
                    break
                old_core = core
                core = coreids[(coreids.index(core) + 1) % len(coreids)]
                state = self.states[core]
                coreids.remove(old_core)
            # Switch cores after every instruction. TODO: Honour switch interval.
            elif len(coreids) > 1 and tick_counter % self.switch_interval == 0:
                while True:
                    core = coreids[(coreids.index(core) + 1) % len(coreids)]
                    if self.states[core].ACTIVE == 1:
                        break
                    # Idle cores can be made active by interrupts.
                    elif (self.states[core].ACTIVE == 0 and
                            self.states[core].rf[reg_map['ILAT']] > 0):
                        interrupt_level = self.states[core].get_latched_interrupt()
                        self.states[core].rf[reg_map['IRET']] = self.states[core].pc
                        self.states[core].rf[reg_map['ILAT']] &= ~(1 << interrupt_level)
                        self.states[core].rf[reg_map['IPEND']] |= 1 << interrupt_level
                        self.states[core].GID = True  # Set global interrupt disabled bit.
                        self.states[core].pc = IVT[interrupt_level]
                        self.states[core].ACTIVE = 1  # Wake up IDLE cores.
                        break
                state = self.states[core]
            # Move program counter to next instruction.
            old_pc = pc
            pc = state.fetch_pc()
            if pc < old_pc:
                self.jitdriver.can_enter_jit(pc=pc,
                                             core=core,
                                             tick_counter=tick_counter,
                                             coreids=coreids,
                                             sim=self,
                                             state=state,)
        return EXIT_SUCCESS, tick_counter

    def _print_summary_statistics(self, ticks):
        """Print timing information. If simulation was interrupted by the user
        pressing Ctrl+c, 'ticks' will be -1.
        """
        if ticks > -1:
            print 'Total ticks simulated = %s.' % format_thousands(ticks)
        for coreid in self.states:
            row, col = get_coords_from_coreid(coreid)
            print ('Core %s (%s, %s) STATUS: 0x%s, Instructions executed: %s' %
                   (hex(coreid), zfill(str(row), 2), zfill(str(col), 2),
                    pad_hex(self.states[coreid].rf[reg_map['STATUS']]),
                    format_thousands(self.states[coreid].num_insts)))
        if self.collect_times:
            execution_time = self.end_time - self.start_time
            print 'Total execution time: %fs.' % (execution_time)
            if ticks > -1:
                speed = format_thousands(int(ticks / execution_time))
                print 'Simulator speed:      %s instructions / second.' % speed

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
                self.states[coreid] = State(self.memory, self.debug,
                                            logger=self.logger, coreid=coreid)
        load_program(elf, self.memory, coreids, ext_base=self.ext_base,
                     ext_size=self.ext_size)
        self.states[coreids[0]].set_first_core(True)
        if self.profile:
            timer = time.time()
            print 'ELF file loader took: %fs' % (timer - self.timer)
            self.timer = timer


init_sim(Revelation())
