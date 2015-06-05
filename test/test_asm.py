import os
import os.path
import subprocess
import pytest

from epiphany.test.machine import StateChecker

asm_dir = os.path.join('epiphany', 'test', 'asm')

@pytest.mark.parametrize("asm,expected",
                         [('nop.elf', StateChecker(pc=2)),
                           pytest.mark.xfail(('add.elf', StateChecker(pc=4)))])
def test_asm_nop(asm, expected):
    assert os.getcwd().endswith('pydgin')
    os.putenv('PYTHONPATH', '.')
    child = subprocess.Popen(['python',
                             'epiphany/sim.py',
                              '--debug',
                              'insts,mem,rf,regdump',
                              os.path.join(asm_dir, asm)],
                             stdout=subprocess.PIPE)
    out = child.communicate()[0]
    assert 0 == child.returncode
    for line in out.split('\n'):
      if line.startswith("Instructions"):
        pc = int(line.split()[-1])
        assert expected.pc == pc
