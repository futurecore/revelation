from epiphany.sim import Epiphany

import opcode_factory

def test_single_inst_add32():
    instructions = [opcode_factory.int_arith32_immediate('add', 1, 0, 0b01010101010)]
    epiphany = Epiphany()
    epiphany.init_test_state(instructions)
    epiphany.state.rf[0] = 0b01010101010
    epiphany.run()
    assert epiphany.state.rf[1] == 0b01010101010 * 2
    assert epiphany.state.AZ == 0
    assert epiphany.state.pc == 4


def test_single_inst_sub32():
    from pydgin.utils import trim_32
    instructions = [opcode_factory.int_arith32_immediate('sub', 1, 0, 0b01010101010)]
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
    instructions = [opcode_factory.int_arith32_immediate('add', 1,0, 0b01010101010),
    # TODO: Add new instruction to move the result of instruction 1
    # TODO: to rf[0] before instruction 2 is executed.
                    opcode_factory.int_arith32_immediate('sub', 1, 0, 0b01010101010),
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


def test_bcond32():#
    instructions = [opcode_factory.int_arith32_immediate('sub', 1, 0, 0b00000000101),
                    opcode_factory.bcond32(0b0000, 0b000000000000000000000100),
                    opcode_factory.int_arith32_immediate('add', 1,0, 0b01010101010), # ADD 0b01010101010
                    ]
    epiphany = Epiphany()
    epiphany.init_test_state(instructions)
    epiphany.state.rf[0] = 5
    epiphany.run()
    assert epiphany.state.pc == 12
    assert epiphany.state.rf[1] == 0
    epiphany.init_test_state(instructions)
    epiphany.state.rf[0] = 8
    epiphany.run()
    assert epiphany.state.rf[1] == 8 + 0b01010101010
    assert epiphany.state.pc == 12
