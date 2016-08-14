from revelation.argument_parser import USAGE_TEXT
from revelation.sim import Revelation

import os.path
import pytest

ELF_DIR = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                       'revelation', 'test', 'asm')
ELF_FILE = os.path.join(ELF_DIR, 'nop.elf')


def test_argv_defaults(capfd):
    revelation = Revelation()
    entry_point = revelation.get_entry_point()
    retval = entry_point(('sim.py', ELF_FILE))
    assert retval == 0  # Exit success.
    _, err = capfd.readouterr()
    assert err == ''
    assert revelation.run_from_gdb == False
    assert revelation.rows == 1
    assert revelation.cols == 1
    assert revelation.first_core == 0x808
    assert revelation.ext_base == 0x8e000000
    assert revelation.ext_size == 32
    assert revelation.user_environment == False
    assert revelation.max_insts == 0
    assert revelation.switch_interval == 1
    assert not revelation.collect_times
    assert revelation.logger == None


@pytest.mark.parametrize('argv,expected',
[(('sim.py', '-r', '4', '-c', '4', ELF_FILE),    (('rows', 4), ('cols', 4))),
 (('sim.py', '--rows', '4', ELF_FILE),           (('rows', 4),)),
 (('sim.py', '--cols', '4', ELF_FILE),           (('cols', 4),)),
 (('sim.py', '--first-core', '0x700', ELF_FILE), (('first_core', 0x700),)),
 (('sim.py', '-f', '0x700', ELF_FILE),           (('first_core', 0x700),)),
 (('sim.py', '-b', '0x2', '-s', '64', ELF_FILE), (('ext_base', 2), ('ext_size', 64))),
 (('sim.py', '--ext-base', '0x2',ELF_FILE),      (('ext_base', 2),)),
 (('sim.py', '--ext-size', '64', ELF_FILE),      (('ext_size', 64),)),
 (('sim.py', '--env', 'USER', ELF_FILE),         (('user_environment', True),)),
 (('sim.py', '-e', 'OPERATING', ELF_FILE),       (('user_environment', False),)),
 (('sim.py', '--max-insts', '100000', ELF_FILE), (('max_insts', 100000),)),
 (('sim.py', '--switch', '25', ELF_FILE),        (('switch_interval', 25),)),
])
def test_argv_flags_with_args(argv, expected, capfd):
    revelation = Revelation()
    entry_point = revelation.get_entry_point()
    retval = entry_point(argv)
    assert retval == 0  # Exit success.
    _, err = capfd.readouterr()
    assert err == ''
    for attribute, value in expected:
        assert revelation.__getattribute__(attribute) == value


def test_argv_debug_flags(capfd):
    flags = ('trace', 'rf', 'mem', 'flags', 'syscalls')
    argv = ('sim.py', '-r', '1', '--debug', ','.join(flags), ELF_FILE)
    revelation = Revelation()
    entry_point = revelation.get_entry_point()
    retval = entry_point(argv)
    assert retval == 0  # Exit success.
    _, err = capfd.readouterr()
    assert err == ''
    for flag in flags:
        assert flag in revelation.debug.enabled_flags


@pytest.mark.parametrize('argv,attribute',
[(('sim.py', '--time', ELF_FILE),    'collect_times'),
 (('sim.py', '-t',     ELF_FILE),    'collect_times'),
 (('sim.py', '--profile', ELF_FILE), 'profile'),
 (('sim.py', '-p',     ELF_FILE),    'profile'),
 (('sim.py', '--gdb', ELF_FILE),     'run_from_gdb'),
 (('sim.py', '-g'),                  'run_from_gdb'),
 ])
def test_argv_flags_with_no_args(argv, attribute, capfd):
    revelation = Revelation()
    entry_point = revelation.get_entry_point()
    retval = entry_point(argv)
    assert retval == 0  # Exit success.
    _, err = capfd.readouterr()
    assert err == ''
    assert getattr(revelation, attribute)


@pytest.mark.parametrize('argv,expected',
[(('sim.py', '-r', '1', 'dummy.elf'),    'Could not open file dummy.elf\n'),
 (('sim.py', '-t'),                      'You must supply a file name\n'),
 (('sim.py', '--flibble', 'dummy.elf'),  'Unknown argument --flibble\n'),
 (('sim.py', '--env', '@', 'dummy.elf'), '--env can be OPERATING or USER.\n'),
 (('sim.py', '-e', '@', 'dummy.elf'),    '--env can be OPERATING or USER.\n'),
])
def test_argv_with_errors(argv, expected, capfd):
    revelation = Revelation()
    entry_point = revelation.get_entry_point()
    entry_point(argv)
    out, err = capfd.readouterr()
    assert err == ''
    assert out == expected


@pytest.mark.parametrize('argv', [('sim.py', '--help'), ('sim.py', '-h')])
def test_argv_help(argv, capfd):
    revelation = Revelation()
    expected = (USAGE_TEXT % ('revelation', 'sim.py', 'sim.py', 'sim.py',
                              'sim.py', 'sim.py') + '\n')
    entry_point = revelation.get_entry_point()
    entry_point(argv)
    out, err = capfd.readouterr()
    assert err == ''
    assert out == expected
