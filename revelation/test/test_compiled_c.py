from revelation.sim import Revelation
from revelation.test.machine import StateChecker

import os.path
import pytest

elf_dir = os.path.join('revelation', 'test', 'c')


@pytest.mark.parametrize('elf_file,expected',
                         [('clearilat.elf',       'Sync interrupt caused by ILATST (should only appear once).\n'
                                                  'Clearing all ILAT with ILATCL.\n'
                                                  'DONE! Status = 0\n'),
                          pytest.mark.skip(('div_by_zero.elf',     'Exception_isr 214023\nEnd.\nDONE! Status = 1')),
                          ('hello.elf',           'Hello, world!\n'),
                          pytest.mark.skip(('fib_print.elf',       '10946')),
                          pytest.mark.skip(('printf_arg.elf',       '99999')),
                          pytest.mark.skip(('read_file.elf',       'Hello, world!')),
                          ('selfmod.elf',         'Hello\nWorld\n'),
                          ('selfmod2.elf',        'Hello\nWorld\n'),
                          ('setilat.elf',         'User interrupt set by ILATST.\n'
                                                  'DONE! Status = 0'),
                          ('user_interrupt1.elf', ('User interrupt 1.\n'
                                                   'User interrupt 2.\n'
                                                   'User interrupt 3.\n'
                                                   'User interrupt 4.\n'
                                                   'Another user interrupt.\n')),
                          pytest.mark.skip(('user_interrupt2.elf',
                           ('main:    trigger user interrupt with swi\n'
                            'user_isr:  begin\n'
                            'user_isr:  before float overflow\n'
                            'exception_isr:  begin\n'
                            'exception_isr:  trigger user interrupt with swi.\n'
                            'exception_isr:  end\n'
                            'user_isr:  begin\n'
                            'user_isr:  again, will not trigger float exception\n'
                            'user_isr:  end\n'
                            'user_isr:  after float overflow\n'
                            'user_isr:  end\n'))),
                         ])
def test_compiled_c_with_output(elf_file, expected, capfd):
    """Test an ELF file that has been compiled from a C function.
    This test checks text printed to STDOUT.
    """
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, '', [], False, is_test=True)
        revelation.max_insts = 100000
        revelation.run()
        assert not revelation.state.running
        out, err = capfd.readouterr()
        assert err == ''
        assert expected in out


@pytest.mark.parametrize('elf_file,expected',
                         [('fib_return.elf', StateChecker(rf0=10946)),
                          ('exit5.elf',      StateChecker(rf0=5)),
                         ])
def test_compiled_c_with_return(elf_file, expected):
    """Test an ELF file that has been compiled from a C function.
    This test checks the state of the simulator after exit.
    """
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, '', [], False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        expected.check(revelation.state)
        assert not revelation.state.running


@pytest.mark.parametrize('elf_file,expected', [('nothing.elf',   236),
                                               ('fib.elf',       441),
                                              ])
def test_compiled_c(elf_file, expected, capsys):
    """Test an ELF file that has been compiled from a C function.
    This test checks that the correct number of instructions have been executed.
    """
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, '', [], False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        out, err = capsys.readouterr()
        expected_text = 'Instructions Executed = ' + str(expected)
        assert expected_text in out
        assert err == ''
        assert not revelation.state.running
