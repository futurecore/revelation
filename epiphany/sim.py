from pydgin.debug import Debug
from pydgin.misc import load_program
from pydgin.sim import Sim, init_sim
from pydgin.storage import Memory

from epiphany.isa import decode
from epiphany.machine import State, RESET_ADDR
from epiphany.instruction import Instruction

MEMORY_SIZE = 2**18  # 2^8 x 2^10 == 32kB.

def new_memory():
    return Memory(size=MEMORY_SIZE, byte_storage=True)


class Epiphany(Sim):

    def __init__(self):
        Sim.__init__(self, "Epiphany", jit_enabled=True)

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
        return Instruction(bits, inst_str), exec_fun

    def init_state(self, exe_file, filename, run_argv,
                   envp, testbin, is_test=False):
        if is_test:
            self.debug = Debug()
            Debug.global_enabled = True
        mem = new_memory()
        _, _ = load_program(exe_file, mem)
        self.state = State(mem, self.debug, reset_addr=RESET_ADDR)


init_sim(Epiphany())
