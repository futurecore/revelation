from revelation.sim import Revelation

import os
import os.path
import pytest
import re

elf_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                       'revelation', 'test', 'syscall_layout')

@pytest.mark.parametrize('elf_file,patterns',
    [('stat_test.elf',       ['st_dev\s+2\s+[xabcdef\d]+\s+0x0+\s+[\d]+',
                              'st_ino\s+2\s+[xabcdef\d]+\s+0x2+\s+[\d]+',
                              'st_mode\s+4\s+[xabcdef\d]+\s+0x4+\s+[\d]+',
                              'st_nlink\s+2\s+[xabcdef\d]+\s+0x8+\s+[\d]+',
                              'st_uid\s+2\s+[xabcdef\d]+\s+0xa+\s+[\d]+',
                              'st_gid\s+2\s+[xabcdef\d]+\s+0xc+\s+[\d]+',
                              'st_size\s+4\s+[xabcdef\d]+\s+0x10+\s+[\d]+',
                              'st_atime\s+4\s+[xabcdef\d]+\s+0x14+\s+[\d]+',
                              'st_mtime\s+4\s+[xabcdef\d]+\s+0x1c+\s+[\d]+',
                              'st_ctime\s+4\s+[xabcdef\d]+\s+0x24+\s+[\d]+',
                              'st_blksize\s+4\s+[xabcdef\d]+\s+0x2c+\s+[\d]+',
                              'st_blocks\s+4\s+[xabcdef\d]+\s+0x30+\s+[\d]+']),
     ('fstat_test.elf',      ['st_dev\s+2\s+[xabcdef\d]+\s+0x0+\s+[\d]+',
                              'st_ino\s+2\s+[xabcdef\d]+\s+0x2+\s+[\d]+',
                              'st_mode\s+4\s+[xabcdef\d]+\s+0x4+\s+[\d]+',
                              'st_nlink\s+2\s+[xabcdef\d]+\s+0x8+\s+[\d]+',
                              'st_uid\s+2\s+[xabcdef\d]+\s+0xa+\s+[\d]+',
                              'st_gid\s+2\s+[xabcdef\d]+\s+0xc+\s+[\d]+',
                              'st_size\s+4\s+[xabcdef\d]+\s+0x10+\s+[\d]+',
                              'st_atime\s+4\s+[xabcdef\d]+\s+0x14+\s+[\d]+',
                              'st_mtime\s+4\s+[xabcdef\d]+\s+0x1c+\s+[\d]+',
                              'st_ctime\s+4\s+[xabcdef\d]+\s+0x24+\s+[\d]+',
                              'st_blksize\s+4\s+[xabcdef\d]+\s+0x2c+\s+[\d]+',
                              'st_blocks\s+4\s+[xabcdef\d]+\s+0x30+\s+[\d]+']),
   ])
@pytest.mark.skipif('TRAVIS' in os.environ and os.environ['TRAVIS'] == 'true',
                    reason='This test is long and not CI-friendly.')
@pytest.mark.skip(reason='This test is long and not CI-friendly.')
def test_stat_syscall_layouts(elf_file, patterns, capfd):
    elf_filename = os.path.join(elf_dir, elf_file)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 45000
        revelation.run()
        assert not revelation.states[0].running
        out, err = capfd.readouterr()
        assert err == ''
        for pattern in patterns:
            assert re.search(pattern, out)


@pytest.mark.skipif('TRAVIS' in os.environ and os.environ['TRAVIS'] == 'true',
                    reason='This test is long and not CI-friendly.')
def test_open_close_syscall_layout(capfd):
    with open(os.path.join(os.getcwd(), 'hello.txt') , 'w') as fd:
        fd.write('Hello, world!\n')
    elf_filename = os.path.join(elf_dir, 'open_close_test.elf')
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 7500
        revelation.run()
        assert not revelation.states[0].running
        out, err = capfd.readouterr()
        assert err == ''
        expected = ('open() successful.\nRead: 14 bytes.\nHello, world!\n'
                    'Read: 0 bytes.\nclose() successful.\n')
        expected_full = (('NOTE: Using sparse storage\n'
                          'sparse memory size 400 addr mask 3ff '
                          'block mask fffffc00\n'
                          'Loading program %s on to core 0x808\n' % elf_filename)
                          + expected)
        assert out.startswith(expected_full)
