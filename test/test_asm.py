import os
import os.path
import subprocess
import pytest

asm_dir = os.path.join('epiphany', 'test', 'asm')

@pytest.mark.parametrize("asm,expected_instructions",
                         [('add.elf', 4),
                          ('and.elf', 2),
                          ('asr.elf', 2),
                          pytest.mark.xfail(('bcond.elf', 40)),
                          pytest.mark.xfail(('bitr.elf', 4)),
                          pytest.mark.xfail(('bl.elf', 2)),
                          pytest.mark.xfail(('dma_transfer.elf', 1)),
                          ('eor.elf', 2),
                          pytest.mark.xfail(('fabs.elf', 2)),
                          pytest.mark.xfail(('fadd.elf', 2)),
                          pytest.mark.xfail(('fix.elf', 2)),
                          pytest.mark.xfail(('float.elf', 2)),
                          pytest.mark.xfail(('fmadd.elf', 2)),
                          pytest.mark.xfail(('fmsub.elf', 2)),
                          pytest.mark.xfail(('fmul.elf', 2)),
                          pytest.mark.xfail(('fsub.elf', 2)),
                          ('gid.elf', 2),
                          ('gie.elf', 2),
                          pytest.mark.xfail(('hardware_loop.elf', 18)),
                          pytest.mark.xfail(('iadd.elf', 2)),
                          ('idle.elf', 2),
                          pytest.mark.xfail(('imadd.elf', 2)),
                          pytest.mark.xfail(('imsub.elf', 2)),
                          pytest.mark.xfail(('imul.elf', 2)),
                          pytest.mark.xfail(('isub.elf', 2)),
                          pytest.mark.xfail(('jalr.elf', 3)),
                          pytest.mark.xfail(('jr.elf', 3)),
                          pytest.mark.xfail(('ldr_disp.elf', 3)),
                          pytest.mark.xfail(('ldrdpm.elf', 2)),
                          pytest.mark.xfail(('ldr_index.elf', 3)),
                          pytest.mark.xfail(('ldrpm.elf', 2)),
                          ('lsl.elf', 3),
                          ('lsr.elf', 3),
                          pytest.mark.xfail(('mov_cond.elf', 3)),
                          pytest.mark.xfail(('movfs.elf', 2)),
                          pytest.mark.xfail(('mov_imm.elf', 2)),
                          pytest.mark.xfail(('movt.elf', 2)),
                          pytest.mark.xfail(('movts.elf', 3)),
                          ('nop.elf', 2),
                          ('orr.elf', 2),
                          pytest.mark.xfail(('rti.elf', 2)),
                          pytest.mark.xfail(('rts.elf', 2)),
                          pytest.mark.xfail(('str_disp.elf', 3)),
                          pytest.mark.xfail(('str_dpm.elf', 2)),
                          pytest.mark.xfail(('str_index.elf', 3)),
                          pytest.mark.xfail(('str_pm.elf', 2)),
                          ('sub.elf', 2),
                          pytest.mark.xfail(('testset.elf', 4)),
                          pytest.mark.xfail(('trap.elf', 2)),
                         ])
def test_asm(asm, expected_instructions):
    os.putenv('PYTHONPATH', '.:../../pypy/')
    try:
        output = subprocess.check_output(['python',
                                          'epiphany/sim.py',
                                          '--max-insts',
                                          '100',
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

