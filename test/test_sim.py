from epiphany.sim import Epiphany

def test_single_inst_add32():
    instructions = [0b00000000010101010010000100011011]
    epiphany = Epiphany()
    epiphany.init_test_state(instructions)
    epiphany.state.rf[0] = 0b01010101010
    epiphany.run()
    assert epiphany.state.rf[1] == 0b01010101010 * 2
    assert epiphany.state.AZ == 0
    assert epiphany.state.pc == 4


def test_single_inst_sub32():
    from pydgin.utils import trim_32
    instructions = [0b00000000010101010010000100111011]
    epiphany = Epiphany()
    epiphany.init_test_state(instructions)
    epiphany.state.rf[0] = 5
    epiphany.run()
    assert epiphany.state.rf[1] == trim_32(5 - 0b01010101010)
    assert epiphany.state.AZ == 0  # Zero
    assert epiphany.state.AN == 1  # Negative
    assert epiphany.state.AC == 1  # Borrow, take from utility function. CHECK THIS.
    assert epiphany.state.pc == 4


def test_add32_sub32():
    from pydgin.utils import trim_32
    instructions = [0b00000000010101010010000100011011, # ADD 0b01010101010
    # TODO: Add new instruction to move the result of instruction 1
    # TODO: to rf[0] before instruction 2 is executed.
                    0b00000000010101010010000100111011, # SUB 0b01010101010
                    ]
    epiphany = Epiphany()
    epiphany.init_test_state(instructions)
    epiphany.state.rf[0] = 0
    epiphany.run()
    assert epiphany.state.rf[1] == trim_32(0 - 0b01010101010)
    assert epiphany.state.AZ == 0  # Zero
    assert epiphany.state.AN == 1  # Negative
    assert epiphany.state.AC == 1  # Borrow, take from utility function. CHECK THIS.
    assert epiphany.state.pc == 8
