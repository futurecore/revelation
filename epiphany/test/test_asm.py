from epiphany.sim import Epiphany
from epiphany.utils import float2bits
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
                          ('fix.elf', StateChecker(pc=8, rf0=5)),
                          ('gid.elf', StateChecker(pc=4)),
                          ('gie.elf', StateChecker(pc=4)),
                          pytest.mark.xfail(('hardware_loop.elf', StateChecker())),
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


@pytest.mark.parametrize("elf,expected",
                         [('fabs.elf', StateChecker(pc=24,
                                                    rf0=float2bits(5.0),
                                                    rf1=float2bits(0.0),
                                                    rf2=float2bits(-5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(0.0),
                                                    rf5=float2bits(5.0),
                                                    )),
                          ('float.elf', StateChecker(pc=6, rf1=float2bits(25.0))),
                          ('fadd.elf', StateChecker(pc=18,
                                                    rf0=float2bits(15.0),
                                                    rf1=float2bits(5.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(10.0),
                                                    rf4=float2bits(0.0))),
                          ('fsub.elf', StateChecker(pc=20,
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(3.0),
                                                    rf5=float2bits(-3.0))),
                          ('fmul.elf', StateChecker(pc=18,
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(0.0),
                                                    rf4=float2bits(10.0))),
                          ('fmadd.elf', StateChecker(pc=26,
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(17.0),
                                                     rf4=float2bits(7.0))),
                          ('fmsub.elf', StateChecker(pc=26,
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(-3.0),
                                                     rf4=float2bits(7.0))),
                          ('iadd.elf', StateChecker(pc=18,
                                                    rf0=float2bits(15.0),
                                                    rf1=float2bits(5.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(10.0),
                                                    rf4=float2bits(0.0))),
                          ('isub.elf', StateChecker(pc=20,
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(3.0),
                                                    rf5=float2bits(-3.0))),
                          ('imul.elf', StateChecker(pc=18,
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(0.0),
                                                    rf4=float2bits(10.0))),
                          ('imadd.elf', StateChecker(pc=26,
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(17.0),
                                                     rf4=float2bits(7.0))),
                          ('imsub.elf', StateChecker(pc=26,
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(-3.0),
                                                     rf4=float2bits(7.0))),
                         ])
def test_fp_elf(elf, expected):
    elf_filename = os.path.join(elf_dir, elf)
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        epiphany.init_state(elf, elf_filename, '', [], False)
        epiphany.max_insts = 250
        epiphany.run()
        expected.fp_check(epiphany.state)


def test_execute_idle16(capsys):
    elf_filename = os.path.join(elf_dir, 'idle.elf')
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        epiphany.init_state(elf, elf_filename, '', [], False)
        epiphany.state.rfSTATUS = 1
        epiphany.max_insts = 250
        epiphany.run()
        out, err = capsys.readouterr()
        expected_state = StateChecker(pc=4, rfSTATUS=0)
        expected_text = ('IDLE16 does not wait in this simulator. ' +
                         'Moving to next instruction.')
        expected_state.check(epiphany.state)
        assert expected_text in out
        assert err == ''
        assert not epiphany.state.running  # Set by bkpt16 instruction.


def test_unimpl():
    elf_filename = os.path.join(elf_dir, 'unimpl.elf')
    with pytest.raises(NotImplementedError):
        epiphany = Epiphany()
        with open(elf_filename, 'rb') as elf:
            epiphany.init_state(elf, elf_filename, '', [], False)
            epiphany.run()
