from revelation.sim import Revelation
from revelation.utils import float2bits
from revelation.test.machine import StateChecker

import os.path
import pytest

elf_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                       'revelation', 'test', 'asm')

@pytest.mark.parametrize("elf,expected",
       [('trap.elf',              "Hello, world!"),
        ('trap_undocumented.elf', "Hello, world!"),
       ])
def test_elf_with_stdout(elf, expected, capfd):
    """Test ELF files by checking STDOUT.
    """
    elf_filename = os.path.join(elf_dir, elf)
    revelation = Revelation()
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        assert not revelation.states[0].running
        out, err = capfd.readouterr()
        assert err == ''
        assert expected in out


@pytest.mark.parametrize("elf,expected",
       [('add.elf',          StateChecker(rf1=110, rf2=7, rf3=105)),
        ('and.elf',          StateChecker(rf0=0, rf1=1, rf2=1, rf3=0, rf4=0, rf5=0)),
        ('asr.elf',          StateChecker(rf0=1, rf1=5, rf2=0, rf3=0)),
        ('bcond.elf',        StateChecker(rf0=0, rf1=110)),
        ('bitr.elf',         StateChecker(rf0=0x84c2a6e1)),
        ('bl.elf',           StateChecker(rf0=15, rf1=0, rf2=15)),
        ('coreid.elf',       StateChecker(rf0=0x808)),
        ('ctimer0.elf',      StateChecker(rf16=94, rfCTIMER0=95)),
        ('ctimer1.elf',      StateChecker(rf16=94, rfCTIMER1=95)),
        pytest.mark.xfail(('dma_transfer.elf', StateChecker())),
        ('eor.elf',          StateChecker(rf0=5, rf1=7, rf2=2)),
        ('fix.elf',          StateChecker(rf0=5)),
        ('fstatus.elf',      StateChecker(rf0=0xffffffff, rfFSTATUS=0xffffffff,
                                          rfSTATUS=0xfffffffd)),
        ('gid.elf',          StateChecker(GID=1)),
        ('gie.elf',          StateChecker(GID=0)),
        ('hardware_loop.elf',
                             StateChecker(pc=0x39c, rfSTATUS=0b101,
                                          rf1=0x650, rf2=0x640, rf3=0x640,
                                          rf4=0x640, rf5=0x640, rf6=0x640,
                                          rf7=0x640, rf8=0x640)),
        ('ilatcl.elf',       StateChecker(rf0=0x3ff, rfILATCL=0x3ff, rfILAT=0)),
        ('ilatst.elf',       StateChecker(rfILATST=0x3ff, rfILAT=0x3fe,
                                          rfIPEND=0x1)),
        ('jalr.elf',         StateChecker(rfLR=0x356)),
        ('jr.elf',           StateChecker(rf0=3, rf1=1, rf2=2)),
        ('low_high.elf',     StateChecker(rf3=0xffffffff)),
        ('lsl.elf',          StateChecker(rf0=5, rf1=7, rf2=640, rf3=640)),
        ('lsr.elf',          StateChecker(rf0=3, rf1=1, rf2=1, rf3=1)),
        ('mov_cond.elf',     StateChecker(rf0=0, rf1=15, rf2=15, rf3=15)),
        ('movfs.elf',        StateChecker(rf0=7, rf63=7, rfIRET=7)),
        ('mov_imm.elf',      StateChecker(rf0=25)),
        ('movt.elf',         StateChecker(rf0=2415919104)),
        ('movts.elf',        StateChecker(rf0=7, rfIRET=7)),
        ('nop.elf',          StateChecker(pc=0x354)),
        ('orr.elf',          StateChecker(rf0=5, rf1=7, rf2=7)),
        ('rti.elf',          StateChecker(GID=0)),
        ('rts.elf',          StateChecker(rf1=100, rf2=200, rf3=300, rfLR=0x352)),
        ('special_regs.elf', StateChecker(rf0=1, rf1=2, rf2=3, rf3=4, rf4=5,
                                          rf5=6, rf6=7, rf7=8, rf8=9, rf10=11,
                                          rf11=12,
                                          rfCONFIG=1, rfSTATUS=3,
                                          rfLC=4, rfLS=5, rfLE=6, rfIRET=7,
                                          rfIMASK=8, rfILAT=9, rfILATST=10,
                                          rfILATCL=11, rfIPEND=12)),
        ('sub.elf',          StateChecker(rf0=100, rf1=20, rf2=80, rf3=80)),
        ('swi.elf',          StateChecker(rfILAT=0b10, EXCAUSE=0b0001)),
        ('unimpl.elf',       StateChecker(EXCAUSE=0b0100)),
       ])
def test_elf(elf, expected):
    """Test ELF files that deal in unsigned integers (rather than floats).
    """
    elf_filename = os.path.join(elf_dir, elf)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        expected.check(revelation.states[0])


@pytest.mark.parametrize("elf,expected,memory",
      [('imask.elf', StateChecker(rf0=0x3ff), [((0x808 << 20) | 0xf0424, 3, 0x3ff)]),
      ])
def test_elf_writes_to_memory(elf, expected, memory):
    """Test ELF files that deal in unsigned integers (rather than floats).
    """
    elf_filename = os.path.join(elf_dir, elf)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        expected.check(revelation.states[0], memory)



@pytest.mark.parametrize("elf,expected",
                         [('fabs.elf', StateChecker(rf0=float2bits(5.0),
                                                    rf1=float2bits(0.0),
                                                    rf2=float2bits(-5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(0.0),
                                                    rf5=float2bits(5.0),
                                                    )),
                          ('float.elf', StateChecker(rf1=float2bits(25.0))),
                          ('fadd.elf', StateChecker(rf0=float2bits(15.0),
                                                    rf1=float2bits(5.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(10.0),
                                                    rf4=float2bits(0.0))),
                          ('fsub.elf', StateChecker(rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(3.0),
                                                    rf5=float2bits(-3.0))),
                          ('fmul.elf', StateChecker(rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(0.0),
                                                    rf4=float2bits(10.0))),
                          ('fmadd.elf', StateChecker(rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(17.0),
                                                     rf4=float2bits(7.0))),
                          ('fmsub.elf', StateChecker(rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(-3.0),
                                                     rf4=float2bits(7.0))),
                          ('iadd.elf', StateChecker(rf0=float2bits(15.0),
                                                    rf1=float2bits(5.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(10.0),
                                                    rf4=float2bits(0.0))),
                          ('isub.elf', StateChecker(rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(5.0),
                                                    rf4=float2bits(3.0),
                                                    rf5=float2bits(-3.0))),
                          ('imul.elf', StateChecker(rf0=float2bits(0.0),
                                                    rf1=float2bits(2.0),
                                                    rf2=float2bits(5.0),
                                                    rf3=float2bits(0.0),
                                                    rf4=float2bits(10.0))),
                          ('imadd.elf', StateChecker(rf0=float2bits(0.0),
                                                     rf1=float2bits(2.0),
                                                     rf2=float2bits(5.0),
                                                     rf3=float2bits(17.0),
                                                     rf4=float2bits(7.0))),
                          ('imsub.elf', StateChecker(rf0=float2bits(0.0),
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
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        expected.fp_check(revelation.states[0])


@pytest.mark.parametrize("elf,expected",
       [('ldr_disp.elf',    StateChecker(rf0=0xffffffff, rf1=0x00100000)),
        ('ldr_disp_pm.elf', StateChecker(rf0=0xffffffff, rf1=0x00100004)),
        ('ldr_index.elf',   StateChecker(rf0=0xffffffff, rf1=0x00100004, rf2=0)),
       ])
def test_load(elf, expected):
    """Test ELF files that load values from memory into a register.
    """
    elf_filename = os.path.join(elf_dir, elf)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.states[0].mem.write(0x00100004, 4, 0xffffffff)
        revelation.max_insts = 10000
        revelation.run()
        expected.check(revelation.states[0])


@pytest.mark.parametrize("elf,expected",
       [('str_disp.elf', StateChecker(rf0=0xffffffff, rf1=0x00100000)),
        ('str_disp_pm.elf', StateChecker(rf0=0xffffffff, rf1=0x00100004)),
        ('str_index.elf', StateChecker(rf0=0xffffffff, rf1=0x00100004, rf2=0)),
       ])
def test_store(elf, expected):
    """Test ELF files that transfer data from registers to memory.
    """
    elf_filename = os.path.join(elf_dir, elf)
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        expected.check(revelation.states[0], memory=[(0x00100004, 4, 0xffffffff)])


def test_elf_load_pm():
    elf_filename = os.path.join(elf_dir, 'ldr_pm.elf')
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.states[0].mem.write(0x80002, 4, 0xffffffff)
        revelation.max_insts = 10000
        revelation.run()
        expected = StateChecker(rf0=0xffffffff, rf1=0x100004, rf2=0x80002)
        expected.check(revelation.states[0])


def test_elf_store_pm():
    """Test ELF files that transfer data from registers to memory.
    """
    elf_filename = os.path.join(elf_dir, 'str_pm.elf')
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.max_insts = 10000
        revelation.run()
        expected = StateChecker(rf0=0xffffffff, rf1=0x00100004, rf2=4)
        expected.check(revelation.states[0], memory=[(0x100000, 4, 0xffffffff)])


def test_testset32():
    elf_filename = os.path.join(elf_dir, 'testset.elf')
    revelation = Revelation()
    with open(elf_filename, 'rb') as elf:
        revelation.init_state(elf, elf_filename, False, is_test=True)
        revelation.states[0].mem.write(0x100004, 4, 0x0)
        revelation.max_insts = 100000
        revelation.run()
        expected = StateChecker(AZ=1, rf0=0, rf1=0x100000, rf2=0x4)
        expected.check(revelation.states[0], memory=[(0x100004, 4, 0xffff)])


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
        revelation = Revelation()
        with open(elf_filename, 'rb') as elf:
            revelation.init_state(elf, elf_filename, False, is_test=True)
            revelation.max_insts = 100000
            revelation.run()
    assert expected_text == expected_exn.value.message
