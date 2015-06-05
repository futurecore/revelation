import os
import subprocess
import pytest


@pytest.mark.parametrize("asm", ['epiphany/test/asm/nop.elf',
                                 'epiphany/test/asm/add.elf'])
def test_asm_nop(asm):
    assert '/home/snim2/Desktop/working/futurecore/pydgin' == os.getcwd()
    os.putenv('PYTHONPATH', '.')
    child = subprocess.Popen(['python',
                             'epiphany/sim.py',
                              '--debug',
                              'insts,mem,rf,regdump',
                              asm],
                             stdout=subprocess.PIPE)
    child.communicate()[0]
    assert 0 == child.returncode
