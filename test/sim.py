from pydgin.sim import init_sim
from pydgin.debug import Debug

from epiphany.machine import State
from epiphany.sim import Epiphany, new_memory

class MockEpiphany(Epiphany):

    def init_test_state(self, instructions):
        """Load the program into a memory object.
        This function should ONLY be called by unit tests.
        Assume 32bit instructions.
        TODO: 16bit instructions.
        """
        mem = new_memory()
        for i, data in enumerate(instructions):
            mem.write(i * 4, 4, data)
        self.state = State(mem, Debug(), reset_addr=0x0)

init_sim(MockEpiphany())
