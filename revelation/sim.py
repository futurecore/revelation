from pydgin.debug import Debug
from pydgin.misc import load_program
from pydgin.sim import Sim, init_sim

from revelation.isa import decode, reg_map
from revelation.machine import RevelationMemory, State, RESET_ADDR
from revelation.instruction import Instruction

MEMORY_SIZE = 2**32  # Global on-chip address space.

def new_memory():
    return RevelationMemory(size=MEMORY_SIZE, byte_storage=True)


class Revelation(Sim):

    def __init__(self):
        Sim.__init__(self, "Revelation", jit_enabled=True)
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

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
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
        if ((self.state.rf[reg_map['STATUS']] & (1 << 1)) and
            self.state.pc == self.state.rf[reg_map['LE']]):
            self.state.rf[reg_map['LC']] -= 1
            self.hardware_loop = True

    def post_execute(self):
        # If we are in a hardware loop, and the loop counter is > 0,
        # jump back to the start of the loop.
        if self.hardware_loop and self.state.rf[reg_map['LC']] > 0:
            self.state.pc = self.state.rf[reg_map['LS']]
            self.hardware_loop = False
            return
        # Service interrupts. See: http://blog.alexrp.com/revelation-notes/
        if not (self.state.rf[reg_map['ILAT']] == 0 or
            (self.state.rf[reg_map['STATUS']] & (1 << 1)) or
            self.state.rf[reg_map['DEBUGSTATUS']] == 1):
            self._service_interrupts()

    def _service_interrupts(self):
        # Let N be the interrupt level:
        interrupt_level = 0
        for index in range(10):
            if ((self.state.rf[reg_map['ILAT']] & (1 << index)) and
                not (self.state.rf[reg_map['IMASK']] & (1 << index))):
                interrupt_level = index
                break
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
        memory = new_memory()
        _, _ = load_program(exe_file, memory)
        memory.set_debug(self.debug)
        self.state = State(memory, self.debug, reset_addr=RESET_ADDR)
        # Give the RAM model a reference to the register files. Since the
        # Epiphany has memory-mapped register files, we need to intercept
        # any read / write which should actually go to the registers.
        memory.rf = self.state.rf


init_sim(Revelation())
