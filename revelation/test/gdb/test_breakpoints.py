from revelation.sim import Revelation
from revelation.gdb.breakpoints import BreakPointManager, BKPT16, NOP16

import os.path
import pytest

COREID = 0x808

elf_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                       'revelation', 'test', 'gdb', 'elfs')


@pytest.mark.parametrize('elf_file,address',
    [('nothing.elf', 0x350),  # str fp,[sp],-0x4  - 32 bit
     ('nothing.elf', 0x366),  # nop               - 16 bit
     ('hello.elf', 0x370),    # add sp,sp,16      - 32 bit
     ('hello.elf', 0x380),    # ldr r1,[r2]       - 16 bit
    ])
def test_set_breakpoint(elf_file, address):
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    bkpts = BreakPointManager(revelation)
    global_address = (COREID << 20) | address
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
    bkpts.set_breakpoint(address)
    assert BKPT16 == revelation.memory.iread(global_address, 2)
    assert global_address in bkpts.breakpoints
    opcode, size = bkpts.breakpoints[global_address]
    if size == 4:
        assert NOP16 == revelation.memory.iread(global_address + 2, 2)


@pytest.mark.parametrize('elf_file,address',
    [('nothing.elf', 0x350),  # str fp,[sp],-0x4  - 32 bit
     ('nothing.elf', 0x366),  # nop               - 16 bit
     ('hello.elf', 0x370),    # add sp,sp,16      - 32 bit
     ('hello.elf', 0x380),    # ldr r1,[r2]       - 16 bit
    ])
def test_remove_breakpoint(elf_file, address):
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    bkpts = BreakPointManager(revelation)
    global_address = (COREID << 20) | address
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
    original_32bits = revelation.memory.iread(global_address, 4)
    bkpts.set_breakpoint(address)
    assert BKPT16 == revelation.memory.iread(global_address, 2)
    assert global_address in bkpts.breakpoints
    opcode, size = bkpts.breakpoints[global_address]
    if size == 4:
        assert NOP16 == revelation.memory.iread(global_address + 2, 2)
    bkpts.remove_breakpoint(global_address)
    assert not global_address in bkpts.breakpoints
    assert opcode == revelation.memory.iread(global_address, size)
    assert original_32bits == revelation.memory.iread(global_address, 4)


@pytest.mark.parametrize('elf_file,address',
    [('nothing.elf', 0x350),  # str fp,[sp],-0x4  - 32 bit
     ('nothing.elf', 0x366),  # nop               - 16 bit
     ('hello.elf', 0x370),    # add sp,sp,16      - 32 bit
     ('hello.elf', 0x380),    # ldr r1,[r2]       - 16 bit
    ])
def test_remove_breakpoint_invalid(elf_file, address):
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    bkpts = BreakPointManager(revelation)
    global_address = (COREID << 20) | address
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
    bkpts.set_breakpoint(address)
    assert BKPT16 == revelation.memory.iread(global_address, 2)
    assert global_address in bkpts.breakpoints
    opcode, size = bkpts.breakpoints[global_address]
    if size == 4:
        assert NOP16 == revelation.memory.iread(global_address + 2, 2)
    original_dict = bkpts.breakpoints
    bkpts.remove_breakpoint(global_address + 2)  # Not a breakpoint!
    for address in original_dict:
        assert address in bkpts.breakpoints
        assert original_dict[address] == bkpts.breakpoints[address]


@pytest.mark.parametrize('elf_file,address',
    [('nothing.elf', 0x350),  # str fp,[sp],-0x4  - 32 bit
     ('nothing.elf', 0x366),  # nop               - 16 bit
     ('hello.elf', 0x370),    # add sp,sp,16      - 32 bit
     ('hello.elf', 0x380),    # ldr r1,[r2]       - 16 bit
    ])
def test_is_breakpoint_set(elf_file, address):
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    bkpts = BreakPointManager(revelation)
    global_address = (COREID << 20) | address
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
    bkpts.set_breakpoint(address)
    assert bkpts.is_breakpoint_set(global_address)
    assert not bkpts.is_breakpoint_set(global_address - 4)
    assert not bkpts.is_breakpoint_set(global_address - 2)
    assert not bkpts.is_breakpoint_set(global_address + 2)
    assert not bkpts.is_breakpoint_set(global_address + 4)
