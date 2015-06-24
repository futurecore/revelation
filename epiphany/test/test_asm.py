from epiphany.sim import Epiphany
from epiphany.test.machine import StateChecker

import os.path
import pytest

elf_dir = os.path.join('epiphany', 'test', 'asm')

@pytest.mark.parametrize("elf,expected",
                         [('add.elf', StateChecker(pc=16, rf1=110, rf2=7, rf3=105)),
                          ('and.elf', StateChecker(pc=4)),
                          ('asr.elf', StateChecker(pc=4)),
                          ('bcond.elf', StateChecker(pc=12, rf0=0, rf1=110)),
                          pytest.mark.xfail(('bitr.elf', StateChecker())),
                          ('bl.elf', StateChecker(pc=34, rf14=15, rf15=0, rf16=15)),
                          pytest.mark.xfail(('dma_transfer.elf', StateChecker())),
                          ('eor.elf', StateChecker(pc=4)),
                          pytest.mark.xfail(('fabs.elf', StateChecker())),
                          pytest.mark.xfail(('fadd.elf', StateChecker())),
                          pytest.mark.xfail(('fix.elf', StateChecker())),
                          pytest.mark.xfail(('float.elf', StateChecker())),
                          pytest.mark.xfail(('fmadd.elf', StateChecker())),
                          pytest.mark.xfail(('fmsub.elf', StateChecker())),
                          pytest.mark.xfail(('fmul.elf', StateChecker())),
                          pytest.mark.xfail(('fsub.elf', StateChecker())),
                          ('gid.elf', StateChecker(pc=4)),
                          ('gie.elf', StateChecker(pc=4)),
                          pytest.mark.xfail(('hardware_loop.elf', StateChecker())),
                          pytest.mark.xfail(('iadd.elf', StateChecker())),
                          ('idle.elf', StateChecker(pc=4)),
                          pytest.mark.xfail(('imadd.elf', StateChecker())),
                          pytest.mark.xfail(('imsub.elf', StateChecker())),
                          pytest.mark.xfail(('imul.elf', StateChecker())),
                          pytest.mark.xfail(('isub.elf', StateChecker())),
                          pytest.mark.xfail(('jalr.elf', StateChecker())),
                          pytest.mark.xfail(('jr.elf', StateChecker())),
                          pytest.mark.xfail(('ldr_disp.elf', StateChecker())),
                          pytest.mark.xfail(('ldrdpm.elf', StateChecker())),
                          pytest.mark.xfail(('ldr_index.elf', StateChecker())),
                          pytest.mark.xfail(('ldrpm.elf', StateChecker())),
                          ('lsl.elf', StateChecker(pc=6)),
                          ('lsr.elf', StateChecker(pc=6)),
                          pytest.mark.xfail(('mov_cond.elf', StateChecker())),
                          pytest.mark.xfail(('movfs.elf', StateChecker())),
                          ('mov_imm.elf', StateChecker(pc=4, rf0=25)),
                          pytest.mark.xfail(('movt.elf', StateChecker())),
                          pytest.mark.xfail(('movts.elf', StateChecker())),
                          ('nop.elf', StateChecker(pc=4)),
                          ('orr.elf', StateChecker(pc=4)),
                          pytest.mark.xfail(('rti.elf', StateChecker())),
                          pytest.mark.xfail(('rts.elf', StateChecker())),
                          pytest.mark.xfail(('str_disp.elf', StateChecker())),
                          pytest.mark.xfail(('str_dpm.elf', StateChecker())),
                          pytest.mark.xfail(('str_index.elf', StateChecker())),
                          pytest.mark.xfail(('str_pm.elf', StateChecker())),
                          ('sub.elf', StateChecker(pc=4)),
                          pytest.mark.xfail(('testset.elf', StateChecker())),
                          pytest.mark.xfail(('trap.elf', StateChecker(pc=6))),
                          pytest.mark.xfail(('trap.elf', StateChecker(pc=6))),
                         ])
def test_elf(elf, expected):
    elf_filename = os.path.join(elf_dir, elf)
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        epiphany.init_state(elf, elf_filename, '', [], False)
        epiphany.max_insts = 250
        epiphany.run()
        expected.check(epiphany.state)


def test_unimpl():
    elf_filename = os.path.join(elf_dir, 'unimpl.elf')
    with pytest.raises(NotImplementedError):
        epiphany = Epiphany()
        with open(elf_filename, 'rb') as elf:
            epiphany.init_state(elf, elf_filename, '', [], False)
            epiphany.run()
