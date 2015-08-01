from epiphany.sim import Epiphany

import os.path
import pytest

elf_dir = os.path.join('epiphany', 'test', 'c')


@pytest.mark.parametrize("elf_file,expected", [('nothing.elf',   236),
                                               ('fib.elf',       441),
                                              ])
def test_compiled_c(elf_file, expected, capsys):
    """Test an ELF file that has been compiled from a C function.
    This test checks that the correct number of instructions have been executed.
    """
    elf_filename = os.path.join(elf_dir, elf_file)
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        epiphany.init_state(elf, elf_filename, '', [], False, is_test=True)
        epiphany.max_insts = 10000
        epiphany.run()
        out, err = capsys.readouterr()
        expected_text = 'Instructions Executed = ' + str(expected)
        assert expected_text in out
        assert err == ''
        assert not epiphany.state.running
