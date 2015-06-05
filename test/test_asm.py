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
    os.putenv('PYTHONPATH', '.:../../pypy/')
    try:
        output = subprocess.check_output(['python',
                                          'epiphany/sim.py',
                                          '--debug',
                                          'insts,mem,rf,regdump',
                                          os.path.join(asm_dir, asm)],
                                         stderr=subprocess.PIPE,
                                         shell=False)
    except subprocess.CalledProcessError as excn:
        assert False, ("Simulator exit with non-zero return code " +
                       "return code: {0}, cmd: {1}".format(excn.returncode, excn.cmd))
    assert output, "Output of simulating {0} was empty".format(os.path.join(asm_dir, asm))
    for line in output.split('\n'):
        if line.startswith("Instructions"):
            assert expected.pc == int(line.split()[-1])
