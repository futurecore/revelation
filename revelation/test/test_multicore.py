from revelation.sim import Revelation

import os.path
import pytest

elf_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                       'revelation', 'test', 'multicore')


@pytest.mark.parametrize('elf_file,expected',
[('manual_message_pass.elf', 'Received message.\n'),
 ('wake_on_interrupt.elf',   'Core 0x808 woken by interrupt.\n'),
 ])
def test_two_cores_with_output(elf_file, expected, capfd):
    """Test an ELF file that has been compiled from a C function.
    This test checks text printed to STDOUT.
    """
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    revelation.cols = 2  # rows = 1, first_core = 0x808
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        assert (revelation.rows == 1 and revelation.cols == 2 and
                revelation.first_core == 0x808 and len(revelation.states) == 2)
        revelation.max_insts = 100000
        assert True == revelation.states[0x808].is_first_core
        assert True == revelation.states[0x808].rf.is_first_core
        assert False == revelation.states[0x809].is_first_core
        assert False == revelation.states[0x809].rf.is_first_core
        assert 0x808 == revelation.states[0x808].mem.first_core
        revelation.run()
        assert not revelation.states[0x808].running
        assert not revelation.states[0x809].running
        out, err = capfd.readouterr()
        assert err == ''
        expected_full = (('Loading program %s on to core 0x808 (32, 08)\n'
                          'Loading program %s on to core 0x809 (32, 09)\n'
                           % (elf_filename, elf_filename)) + expected)
        assert out.startswith(expected_full)
