from pydgin.debug import Debug
from pydgin.sim import init_sim

from revelation.machine import RESET_ADDR
from revelation.sim import Revelation, new_memory
from revelation.test.machine import new_state

class MockRevelation(Revelation):
    """Revelation test harness.
    This class should only be used in unit tests.
    """

    def __init__(self):
        Revelation.__init__(self)
        self.debug = Debug()
        Debug.global_enabled = True

    def init_state(self, instructions, **args):
        """Load the program into a memory object.
        This function should ONLY be called by unit tests.
        """
        self.memory = new_memory(self.debug)
        written_so_far = 0
        for i, (data, width) in enumerate(instructions):
            num_bytes = width / 8
            self.memory.write(RESET_ADDR + written_so_far, num_bytes, data)
            written_so_far += num_bytes
        self.states.append(new_state(mem=self.memory, debug=self.debug, **args))
        self.hardware_loops.append(False)
        self.max_insts = len(instructions)

init_sim(MockRevelation())
