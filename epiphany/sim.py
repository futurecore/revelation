from pydgin.debug import Debug
from pydgin.misc import load_program
from pydgin.sim import Sim, init_sim
from pydgin.storage import Memory

from epiphany.isa import decode, reg_map
from epiphany.machine import State, RESET_ADDR
from epiphany.instruction import Instruction

MEMORY_SIZE = 2**32  # Global on-chip address space.

def new_memory():
    return Memory(size=MEMORY_SIZE, byte_storage=True)


class Epiphany(Sim):

    def __init__(self):
        Sim.__init__(self, "Epiphany", jit_enabled=True)
        self.ivt = {  # Interrupt vector table.
            0 : 0x0,  # Sync hardware signal.
            1 : 0x4,  # Floating-point,invalid instruction or alignment.
            2 : 0x8,  # Memory protection fault.
            3 : 0xC,  # Timer0 has expired.
            4 : 0x10, # Timer1 has expired.
            5 : 0x14, # Message interrupt.
            6 : 0x18, # Local DMA channel-0 finished data transfer.
            7 : 0x1C, # Local DMA channel-1 finished data transfer.
            8 : 0x20, # Wired AND-signal interrupt.
            9 : 0x24, # Software-generate user interrupt.
        }

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
        return Instruction(bits, inst_str), exec_fun

    def post_execute(self):
        # Service interrupts. See: http://blog.alexrp.com/epiphany-notes/
        if (self.state.rf[reg_map['ILAT']] == 0 or
            (self.state.rf[reg_map['STATUS']] & (1 << 1)) or
            self.state.rf[reg_map['DEBUGSTATUS']] == 1 or
            self.state.rf[reg_map['IPEND']] > 0):
            return
        # Let N be the interrupt level:
        interrupt_level = 0
        for index in range(10):
            if (self.state.rf[reg_map['ILAT']] & (1 << index)):
                interrupt_level = index
                break
        if self.state.rf[reg_map['IMASK']] & (1 << interrupt_level):
            return
        #     The PC is saved in IRET.
        self.state.rf[reg_map['IRET']] = self.state.pc
        #     Bit N in ILAT is cleared.
        self.state.rf[reg_map['ILAT']] &= ~(1 << interrupt_level)
        #     Bit N in IPEND is set.
        self.state.rf[reg_map['IPEND']] |= (1 << interrupt_level)
        #     The GID bit in STATUS is set.
        self.state.rf[reg_map['STATUS']] |= (1 << 1)
        #     PC is set to an index into the IVT.
        self.state.pc = self.ivt[interrupt_level]

    def init_state(self, exe_file, filename, run_argv,
                   envp, testbin, is_test=False):
        if is_test:
            self.debug = Debug()
            Debug.global_enabled = True
        mem = new_memory()
        _, _ = load_program(exe_file, mem)
        self.state = State(mem, self.debug, reset_addr=RESET_ADDR)


init_sim(Epiphany())
