import os
import os.path
import subprocess
import pytest

pytestmark = pytest.mark.skipif(True,
                                reason=("Pydgin needs a .bss section in ELF " +
                                        "files, but e-as cannot compile .bss.")
                                )

asm_dir = os.path.join('epiphany', 'test', 'asm')

@pytest.mark.parametrize("asm,expected_instructions",
                         [('nop.elf', 2),
                          ('add.elf', 2),
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
            assert expected_instructions == int(line.split()[-1])
