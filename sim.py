from pydgin.sim import Sim, init_sim
from pydgin.storage import Memory
from pydgin.debug import Debug
from epiphany.isa import decode
from epiphany.machine import State
from epiphany.instruction import Instruction

memory_size = 2**18  # 2^8 x 2^10 == 32kB.

def new_memory():
    return Memory(size=memory_size, byte_storage=False)


class Epiphany(Sim):

    def __init__(self):
        Sim.__init__(self, "Epiphany", jit_enabled=True)

    def decode(self, bits):
        inst_str, exec_fun = decode(bits)
        return Instruction(bits, inst_str), exec_fun

    def init_test_state(self, instructions):
        """Load the program into a memory object.
        This function should be called by unit tests.
        Assume 32bit instructions.
        TODO: 16bit instructions.
        """
        mem = new_memory()
        for i, data in enumerate(instructions):
            mem.write(i * 4, 4, data)
        self.state = State(mem, Debug(), reset_addr=0x0)


init_sim(Epiphany())