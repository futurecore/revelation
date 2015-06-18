import os
import os.path
import subprocess
import pytest

asm_dir = os.path.join('epiphany', 'test', 'asm')

@pytest.mark.parametrize("asm,expected_instructions",
                         [('nop.elf', 2),
                          ('add.elf', 4),
                         ])
def test_asm(asm, expected_instructions):
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
            print line
            assert expected_instructions == int(line.split()[-1])


def test_unimpl():
    os.putenv('PYTHONPATH', '.:../../pypy/')
    asm_file = os.path.join(asm_dir, 'unimpl.elf')
    try:
        child = subprocess.Popen(['python',
                                  'epiphany/sim.py',
                                  '--debug',
                                  'insts,mem,rf,regdump',
                                  asm_file],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=False)
        output, error_output = child.communicate()
    except subprocess.CalledProcessError as excn:
        # Expect to exit with non-zero return code.
        assert True, ("Simulator exit with non-zero return code " +
                       "return code: {0}, cmd: {1}".format(excn.returncode, excn.cmd))
        assert 'NotImplementedError: UNIMPL16' in error_output

