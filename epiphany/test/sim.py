from pydgin.debug import Debug
from pydgin.sim import init_sim

from epiphany.machine import RESET_ADDR
from epiphany.sim import Epiphany, new_memory
from epiphany.test.machine import new_state

class MockEpiphany(Epiphany):
    """Epiphany test harness.
    This class should only be used in unit tests.
    """

    def __init__(self):
        Epiphany.__init__(self)
        self.debug = Debug()
        Debug.global_enabled = True

    def init_state(self, instructions, **args):
        """Load the program into a memory object.
        This function should ONLY be called by unit tests.
        """
        mem = new_memory()
        written_so_far = 0
        for i, (data, width) in enumerate(instructions):
            num_bytes = width / 8
            mem.write(RESET_ADDR + written_so_far, num_bytes, data)
            written_so_far += num_bytes
        self.state = new_state(mem=mem, debug=self.debug, **args)
        self.max_insts = len(instructions)

init_sim(MockEpiphany())
