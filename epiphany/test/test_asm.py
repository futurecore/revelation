from epiphany.machine import RESET_ADDR
from epiphany.sim import Epiphany
from epiphany.utils import float2bits
from epiphany.test.machine import StateChecker

import os.path
import pytest

elf_dir = os.path.join('epiphany', 'test', 'asm')

@pytest.mark.parametrize("elf,expected",
       [('add.elf', StateChecker(pc=(16 + RESET_ADDR), rf1=110, rf2=7, rf3=105)),
        ('and.elf', StateChecker(pc=(14 + RESET_ADDR), rf0=0, rf1=1, rf2=1, rf3=0, rf4=0, rf5=0)),
        ('asr.elf', StateChecker(pc=(10 +  + RESET_ADDR), rf0=1, rf1=5, rf2=0, rf3=0)),
        ('bcond.elf', StateChecker(pc=(12 + RESET_ADDR), rf0=0, rf1=110)),
        ('bitr.elf', StateChecker(pc=(6 + RESET_ADDR), rf0=170, rf1=85)),
        pytest.mark.xfail(('bl.elf', StateChecker(pc=(34 + RESET_ADDR), rf14=15, rf15=0, rf16=15))),
        pytest.mark.xfail(('dma_transfer.elf', StateChecker())),
        ('eor.elf', StateChecker(pc=(8 + RESET_ADDR), rf0=5, rf1=7, rf2=2)),
        ('fix.elf', StateChecker(pc=(8 + RESET_ADDR), rf0=5)),
        ('gid.elf', StateChecker(pc=(6 + RESET_ADDR), rfSTATUS=0b10)),
        ('gie.elf', StateChecker(pc=(6 + RESET_ADDR), rfSTATUS=0b00)),
        ('hardware_loop.elf',
         StateChecker(pc=(68 + RESET_ADDR), rf0=100, rf1=116, rf2=100, rf3=100,
                      rf4=100, rf5=100, rf6=100, rf7=100, rf8=100, rfSTATUS=0b00)),
        ('jalr.elf', StateChecker(pc=(10 + RESET_ADDR), rf3=100, rfLR=0x5c)),
        ('jr.elf', StateChecker(pc=(14 + RESET_ADDR), rf0=3, rf1=1, rf2=2)),
        pytest.mark.xfail(('ldr_disp.elf', StateChecker())),
        pytest.mark.xfail(('ldrdpm.elf', StateChecker())), # TODO
        pytest.mark.xfail(('ldr_index.elf', StateChecker())),
        pytest.mark.xfail(('ldrpm.elf', StateChecker())),
        ('lsl.elf', StateChecker(pc=(10 + RESET_ADDR), rf0=5, rf1=7, rf2=640, rf3=640)),
        ('lsr.elf', StateChecker(pc=(10 + RESET_ADDR), rf0=3, rf1=1, rf2=1, rf3=1)),
        ('mov_cond.elf', StateChecker(pc=(14 + RESET_ADDR), rf0=0, rf1=15, rf2=15, rf3=15)),
        ('movfs.elf', StateChecker(pc=(10 + RESET_ADDR), rf0=7, rf63=7, rfCONFIG=7)),
        ('mov_imm.elf', StateChecker(pc=(4 + RESET_ADDR), rf0=25)),
        ('movt.elf', StateChecker(pc=(6 + RESET_ADDR), rf0=2415919104)),
        ('movts.elf', StateChecker(pc=(6 + RESET_ADDR), rf0=7, rfCONFIG=7)),
        ('nop.elf', StateChecker(pc=(4 + RESET_ADDR))),
        ('orr.elf', StateChecker(pc=(8 + RESET_ADDR), rf0=5, rf1=7, rf2=7)),
        pytest.mark.xfail(('rti.elf', StateChecker())),
        pytest.mark.xfail(('rts.elf', StateChecker())),
        pytest.mark.xfail(('str_disp.elf', StateChecker())),
        pytest.mark.xfail(('str_dpm.elf', StateChecker())), # TODO
        pytest.mark.xfail(('str_index.elf', StateChecker())),
        pytest.mark.xfail(('str_pm.elf', StateChecker())),
        ('sub.elf', StateChecker(pc=(12 + RESET_ADDR), rf0=100, rf1=20, rf2=80, rf3=80)),
        pytest.mark.xfail(('trap.elf', StateChecker(pc=(6 + RESET_ADDR)))),
       ])
def test_elf(elf, expected):
    """Test ELF files that deal in unsigned integers (rather than floats).
    """
    elf_filename = os.path.join(elf_dir, elf)
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        if elf == 'movts.elf': print 'MOVTS'
        epiphany.init_state(elf, elf_filename, '', [], False)
        epiphany.max_insts = 250
        epiphany.run()
        expected.check(epiphany.state)


@pytest.mark.parametrize("elf,expected",
                         [('fabs.elf', StateChecker(pc=(24 + RESET_ADDR),
                                                    rf0=float2bits(5.0),
                                                    rf1=float2bits(0.0),
                                                    rf2=float2bits(-5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(0.0),
                                                    rf5=float2bits(5.0),
                                                    )),
                          ('float.elf', StateChecker(pc=(6 + RESET_ADDR),
                                                     rf1=float2bits(25.0))),
                          ('fadd.elf', StateChecker(pc=(18 + RESET_ADDR),
                                                    rf0=float2bits(15.0),
                                                    rf1=float2bits(5.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(10.0),
                                                    rf4=float2bits(0.0))),
                          ('fsub.elf', StateChecker(pc=(20 + RESET_ADDR),
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(3.0),
                                                    rf5=float2bits(-3.0))),
                          ('fmul.elf', StateChecker(pc=(18 + RESET_ADDR),
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(0.0),
                                                    rf4=float2bits(10.0))),
                          ('fmadd.elf', StateChecker(pc=(26 + RESET_ADDR),
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(17.0),
                                                     rf4=float2bits(7.0))),
                          ('fmsub.elf', StateChecker(pc=(26 + RESET_ADDR),
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(-3.0),
                                                     rf4=float2bits(7.0))),
                          ('iadd.elf', StateChecker(pc=(18 + RESET_ADDR),
                                                    rf0=float2bits(15.0),
                                                    rf1=float2bits(5.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(10.0),
                                                    rf4=float2bits(0.0))),
                          ('isub.elf', StateChecker(pc=(20 + RESET_ADDR),
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(3.0),
                                                    rf5=float2bits(-3.0))),
                          ('imul.elf', StateChecker(pc=(18 + RESET_ADDR),
                                                    rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(0.0),
                                                    rf4=float2bits(10.0))),
                          ('imadd.elf', StateChecker(pc=(26 + RESET_ADDR),
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(17.0),
                                                     rf4=float2bits(7.0))),
                          ('imsub.elf', StateChecker(pc=(26 + RESET_ADDR),
                                                     rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(-3.0),
                                                     rf4=float2bits(7.0))),
                         ])
def test_fp_elf(elf, expected):
    """Check that floating point instructions operate correctly.
    These ELF files are tested separately using the fp_check method.
    This means that test failures will be reported so that the contents of
    registers are printed as floats, rather than as unsigned integers.
    """
    elf_filename = os.path.join(elf_dir, elf)
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        epiphany.init_state(elf, elf_filename, '', [], False)
        epiphany.max_insts = 250
        epiphany.run()
        expected.fp_check(epiphany.state)


def test_execute_idle16(capsys):
    """Check that the idle16 prints out the correct warning on STDOUT.
    """
    elf_filename = os.path.join(elf_dir, 'idle.elf')
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        epiphany.init_state(elf, elf_filename, '', [], False)
        epiphany.state.rfSTATUS = 1
        epiphany.max_insts = 250
        epiphany.run()
        out, err = capsys.readouterr()
        expected_state = StateChecker(pc=(4 + RESET_ADDR), rfSTATUS=0)
        expected_text = ('IDLE16 does not wait in this simulator. ' +
                         'Moving to next instruction.')
        expected_state.check(epiphany.state)
        assert expected_text in out
        assert err == ''
        assert not epiphany.state.running  # Set by bkpt16 instruction.


def test_testset32():
    elf_filename = os.path.join(elf_dir, 'testset.elf')
    epiphany = Epiphany()
    with open(elf_filename, 'rb') as elf:
        if elf == 'movts.elf': print 'MOVTS'
        epiphany.init_state(elf, elf_filename, '', [], False)
        epiphany.state.mem.write(0x100004, 4, 0x0)
        epiphany.max_insts = 10
        epiphany.run()
        expected = StateChecker(pc=(22 + RESET_ADDR), AZ=1, rf0=0, rf1=0x100001, rf2=0x3)
        expected.check(epiphany.state, memory=[(0x100004, 4, 0xFFFF)])


def test_testset32_fail():
    """Check that the testset32 instruction fails if the memory address it
    is given is too low..
    """
    elf_filename = os.path.join(elf_dir, 'testset_fail.elf')
    expected_text = """testset32 has failed to write to address %s.
The absolute address used for the test and set instruction must be located
within the on-chip local memory and must be greater than 0x00100000 (2^20).
""" % str(hex(0x4))
    with pytest.raises(ValueError) as expected_exn:
        epiphany = Epiphany()
        with open(elf_filename, 'rb') as elf:
            epiphany.init_state(elf, elf_filename, '', [], False)
            epiphany.max_insts = 10
            epiphany.run()
    assert expected_text == expected_exn.value.message


def test_unimpl():
    """Check that the unimpl instruction throws a NotImplementedError.
    """
    elf_filename = os.path.join(elf_dir, 'unimpl.elf')
    with pytest.raises(NotImplementedError):
        epiphany = Epiphany()
        with open(elf_filename, 'rb') as elf:
            epiphany.init_state(elf, elf_filename, '', [], False)
            epiphany.run()
