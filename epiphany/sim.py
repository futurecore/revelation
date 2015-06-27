from pydgin.misc import load_program
from pydgin.sim import Sim, init_sim
from pydgin.storage import Memory
from pydgin.debug import Debug

from epiphany.isa import decode
from epiphany.machine import State
from epiphany.instruction import Instruction

memory_size = 2**18  # 2^8 x 2^10 == 32kB.

def new_memory():
    return Memory(size=memory_size, byte_storage=True)


class Epiphany(Sim):

    def __init__(self):
        Sim.__init__(self, "Epiphany", jit_enabled=True)

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
        return Instruction(bits, inst_str), exec_fun

    def init_state(self, exe_file, filename, run_argv, envp, testbin):
        mem = new_memory()
        entrypoint, breakpoint = load_program(exe_file, mem)
        self.state = State(mem, Debug(), reset_addr=0x58)


init_sim(Epiphany())
