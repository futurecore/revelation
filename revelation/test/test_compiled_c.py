from revelation.sim import Revelation
from revelation.test.machine import StateChecker

import os.path
import pytest

elf_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                       'revelation', 'test', 'c')


@pytest.mark.parametrize('elf_file,expected',
    [('arithmode.elf',          'a + b = 4.450\na - b = -1.010\na * b = 4.696\n'
                                'd + e = 5\nd - e = -1\nd * e = 6\n'),
     ('clearilat.elf',          'Sync interrupt caused by ILATST (should only '
                                'appear once).\nClearing all ILAT with ILATCL.\n'),
     ('div_by_zero.elf',        'Exception_isr 214023\nEnd.\n'),
     ('get_core_coords.elf',    'Core id: 808 row=32 col=8\n'),
     ('fib_print.elf',          '10946\n'),
     ('hello.elf',              'Hello, world!\n'),
     ('interrupt_fire_all.elf', 'Interrupt E_SW_EXCEPTION ... handler fired.\n'
                                'Interrupt E_MEM_FAULT    ... handler fired.\n'
                                'Interrupt E_TIMER0_INT   ... handler fired.\n'
                                'Interrupt E_TIMER1_INT   ... handler fired.\n'
                                'Interrupt E_MESSAGE_INT  ... handler fired.\n'
                                'Interrupt E_DMA0_INT     ... handler fired.\n'
                                'Interrupt E_DMA1_INT     ... handler fired.\n'
                                'Interrupt E_USER_INT     ... handler fired.\n'),
     ('interrupt_fpu_exceptions.elf',
                                'FPU exception fired.\n'),
     ('interrupt_fpu_exceptions_off.elf',
                                'fpu_handler:\tyou should see this message only'
                                ' once.\nTest complete.\n'),
     ('interrupt_kernel_mode.elf',
                                'fpu_handler:\tyou should see this message only'
                                ' once.\nTest complete.\n'),
     ('interrupt_nested.elf',   'main:\t\ttrigger user interrupt with swi\n'
                                'user_isr:\tbegin\n'
                                'user_isr:\tbefore float overflow\n'
                                'exception_isr:\tbegin\n'
                                'exception_isr:\ttrigger user interrupt with swi.\n'
                                'exception_isr:\tend\n'
                                'user_isr:\tbegin\n'
                                'user_isr:\tagain, will not trigger float exception\n'
                                'user_isr:\tend\n'
                                'user_isr:\tafter float overflow\n'
                                'user_isr:\tend\n'),
     ('interrupt_user.elf',     'User interrupt 1.\nUser interrupt 2.\n'
                                'User interrupt 3.\nUser interrupt 4.\n'
                                'Another user interrupt.\n'),
     ('printf_arg.elf',         '99999\n'),
     ('read_file.elf',          'Hello, world!\n'),
     ('selfmod.elf',            'Hello\nWorld\n'),
     ('selfmod2.elf',           'Hello\nWorld\n'),
     ('setilat.elf',            'User interrupt set by ILATST.\n'),
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
        expected_full = ('NOTE: Using sparse storage\n'
                         'sparse memory size 400 addr mask 3ff '
                         'block mask fffffc00\n') + expected + 'DONE!'
        assert out.startswith(expected_full)


@pytest.mark.parametrize('elf_file,expected',
    [('fib_return.elf',               StateChecker(rf0=10946)),
     ('interrupt_fpu_exceptions.elf', StateChecker(EXCAUSE=0b0011)),
     ('exit5.elf',                    StateChecker(rf0=5)),
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


@pytest.mark.parametrize('elf_file,expected', [('nothing.elf',   250),
                                               ('fib.elf',       461),
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