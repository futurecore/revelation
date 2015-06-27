from epiphany.machine import RESET_ADDR
from epiphany.test.sim import MockEpiphany
from epiphany.test.machine import StateChecker

import opcode_factory

def test_sim_bkpt16():
    instructions = [(opcode_factory.bkpt16(), 16),  # BKPT16
                   ]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(pc=(2 + RESET_ADDR))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_sim_nop16():
    instructions = [(opcode_factory.nop16(),  16),  # NOP16
                    (opcode_factory.bkpt16(), 16),  # BKPT16
                    ]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(pc=(4 + RESET_ADDR))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_single_inst_add32():
    instructions = [(opcode_factory.add32_immediate(rd=1, rn=0, imm=0b01010101010), 32),
                    (opcode_factory.bkpt16(), 16)]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions, rf0=0b01010101010)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(AZ=0, pc=(6 + RESET_ADDR), rf1=(0b01010101010 * 2))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_single_inst_sub32():
    from pydgin.utils import trim_32
    instructions = [(opcode_factory.sub32_immediate(rd=1, rn=0, imm=0b01010101010), 32),
                    (opcode_factory.bkpt16(), 16)]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions, rf0=5)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(AZ=0, AN=1, AC=1,
                                  pc=(6 + RESET_ADDR), rf1=trim_32(5 - 0b01010101010))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_add32_sub32():
    from pydgin.utils import trim_32
    instructions = [(opcode_factory.add32_immediate(rd=1,rn=0, imm=0b01010101010), 32),
    # TODO: Add new instruction to move the result of instruction 1
    # TODO: to rf[0] before instruction 2 is executed.
                    (opcode_factory.sub32_immediate(rd=1, rn=0, imm=0b01010101010), 32),
                    (opcode_factory.bkpt16(), 16),
                    ]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions, rf0=0)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(AZ=0, AN=1, AC=1, pc=(10 + RESET_ADDR),
                                  rf1=trim_32(0 - 0b01010101010))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_bcond32():
    instructions = [(opcode_factory.sub32_immediate(rd=1, rn=0, imm=0b00000000101), 32),
                    (opcode_factory.bcond32(condition=0b0000, imm=0b000000000000000000000100), 32),
                    (opcode_factory.add32_immediate(rd=1, rn=0, imm=0b01010101010), 32),
                    (opcode_factory.bkpt16(), 16),
                    ]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions, rf0=5)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(pc=(14 + RESET_ADDR), rf1=0)
    expected_state.check(epiphany.state)
    assert not epiphany.state.running
    epiphany.init_state(instructions, rf0=8)
    epiphany.run()
    expected_state = StateChecker(pc=(14 + RESET_ADDR), rf1=(8 + 0b01010101010))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_add32_nop16_sub32():
    from pydgin.utils import trim_32
    instructions = [(opcode_factory.add32_immediate(rd=1, rn=0, imm=0b01010101010), 32),
                    (opcode_factory.nop16(), 16),
                    (opcode_factory.sub32_immediate(rd=1, rn=0, imm=0b01010101010), 32),
                    (opcode_factory.bkpt16(), 16),
                    ]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions, rf0=0)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(pc=(12 + RESET_ADDR), AC=1, AN=1, AZ=0,
                                  rf1=trim_32(0 - 0b01010101010))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_sim_idle16():
    instructions = [ (opcode_factory.idle16(), 16),
                     (opcode_factory.bkpt16(), 16),
                   ]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(pc=(4 + RESET_ADDR))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running


def test_sim_all_16bit():
    instructions = [ (opcode_factory.gie16(), 16),
                     (opcode_factory.gid16(), 16),
                     (opcode_factory.idle16(), 16),
                     (opcode_factory.bkpt16(), 16),
                   ]
    epiphany = MockEpiphany()
    epiphany.init_state(instructions)
    assert epiphany.state.running
    epiphany.run()
    expected_state = StateChecker(pc=(8 + RESET_ADDR))
    expected_state.check(epiphany.state)
    assert not epiphany.state.running
