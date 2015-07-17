Contributing to Revelation
==========================

Contributions to Revelation are welcome.
The project source code is available `on GitHub <https://github.com/futurecore/revelation/>`_ and bugs can be reported via the `issue tracker <https://github.com/futurecore/revelation/issues>`_.
If you wish to contribute code, or improvements in this documentation, please fork the project on `on GitHub <https://github.com/futurecore/revelation/>`_ and issue a pull request.
Your pull request will be automatically checked by the `travis continuous integration <https://travis-ci.org/futurecore/revelation>`_ tool before it is merged.

To understand how the Revelation source code is structured, it is a good idea to start by reading about the `Pydgin <https://github.com/cornell-brg/pydgin>`_ framework.

.. seealso:: Derek Lockhart and Berkin Ilbeyi (2015) `Pydgin: Using RPython to Generate Fast Instruction-Set Simulators <http://morepypy.blogspot.co.uk/2015/03/pydgin-using-rpython-to-generate-fast.html>`_ Guest post on the PyPy status blog.

Any changes to the source code should normally be accompanied by unit tests, and should certainly not reduce the current code coverage below 99%.


Running the unit tests locally
------------------------------

Revelation comes with a large number of unit tests, which are intended to be run with the `py.test <http://pytest.org/latest/>`_ framework.
To run the provided tests, first ensure that the required packages are installed:

.. code-block:: bash

    $ pip install -r requirements.txt


Then run the tests themselves:

.. code-block:: bash

    $ py.test -s --cov-report term-missing --cov epiphany epiphany/test/ --no-cov-on-fail -n 4


Structure of the unit tests
---------------------------

All unit tests can be found in the ``epiphany.test`` package.
Most tests are written in pure Python and test the internals of the simulator code, but there are also two directories of C and Assembler code which contain integration tests.

Revelation provides a number of convenience modules which are intended to make it easier to quickly construct unit tests and reduce duplicate code.
It is recommended that anyone adding new tests make uses of these modules, which are described below.

The ``opcode_factory`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Epiphany instructions are 32bit or 16bit binary numbers.
Writing these by hand is error prone and tedious, and loading an ELF file is not appropriate for small unit tests.
The `epiphany.test.opcode_factory <https://github.com/futurecore/revelation/blob/master/epiphany/test/opcode_factory.py>`_ module provides a function to create each instruction in the Epiphany ISA.
Where there are 32bit and 16bit variants of the same instruction, both versions are available.
For example, the following code creates 32 and 16bit versions of the *logical shift left* instruction:

.. code-block:: python

    >>> import epiphany.test.opcode_factory as opcode_factory
    >>> bin(opcode_factory.lsl32(rd=43, rn=42, rm=41))
    '0b10110110100010100110100010101111'
    >>> bin(opcode_factory.lsl16(rd=3, rn=2, rm=1))
    '0b110100010101010'
    >>>

Note that operands to the instruction are passed to the factory function as keyword arguments.
These are named exactly as they are described in the opcode decode table on page 155 of the `Epiphany Architecture Reference Manual <http://adapteva.com/docs/epiphany_arch_ref.pdf>`_.
In the example above, the LSL instruction takes three operands:

* **rd** a destination register
* **rn** an operand register
* **rm** an operand register


The ``new_state`` function
^^^^^^^^^^^^^^^^^^^^^^^^^^

Unit tests for Revelation usually check whether the simulator halts with the expected state (i.e. flags, registers and RAM).
It is often useful to be able to start the simulator in a particular state.
Rather than setting each register or flag individually, Revelation provides the `epiphany.test.machine.new_state <https://github.com/futurecore/revelation/blob/master/epiphany/test/machine.py>`_ function which can accept register and flag values as named parameters.

For example:

.. code-block:: python

    >>> from epiphany.test.machine import new_state
    >>> state = new_state(AZ=1, AN=0, rf0=0xFFFFFFFF, rf1=0xbeef)
    NOTE: Using sparse storage
    sparse memory size 400 addr mask 3ff block mask fffffc00
    >>> hex(state.rf[0])
    '0xffffffff'
    >>> bool(state.AZ)
    True
    >>>


The ``StateChecker`` class
^^^^^^^^^^^^^^^^^^^^^^^^^^

Similarly, it is inconvenient to write separate assertions to check each flag, register or word in RAM .
The `epiphany.test.machine <https://github.com/futurecore/revelation/blob/master/epiphany/test/machine.py>`_ module provides a class called ``StateChecker`` which manages this.
A new ``StateChecker`` takes register and flag values as parameters to its constructor, in exactly the same way as the ``new_state`` function described above.
The ``StateChecker.check`` method takes a state as a parameter, then automatically runs assertions to check that each register or flag of interest is as expected.

For example:

.. code-block:: python

    from epiphany.instruction import Instruction
    from epiphany.isa import decode
    from epiphany.machine import RESET_ADDR
    from epiphany.test.machine import StateChecker, new_state

    import opcode_factory
    import pytest

    @pytest.mark.parametrize('is16bit,val', [(True, 0b111), (False, 0b1111)])
    def test_execute_movcond(is16bit, val):
        """Test that MOV<COND> can move values between registers.
        """
        state = new_state(AZ=1, rf1=val)
        instr = (opcode_factory.movcond16(condition=0b0000, rd=0, rn=1) if is16bit
                 else opcode_factory.movcond32(condition=0b0000, rd=0, rn=1))
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))
        pc_expected = (2 if is16bit else 4) + RESET_ADDR
        expected_state = StateChecker(pc=pc_expected, rf0=val)
        expected_state.check(state)


Note that like most unit tests in Revelation, the example above uses `pytest.mark.parametrize <https://pytest.org/latest/parametrize.html>`_ to avoid duplicating code.


Checking the contents of RAM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the examples above, unit tests have checked the contents of registers and flags.
It is also possible to check that a word in RAM has the correct contents, by passing a list of expected memory locations to the ``StateChecker.check`` method.

For example:

.. code-block:: python

    @pytest.mark.parametrize('sub,new_rn', [(1, 8 - 4), ... (0, 8 + 4)])
    def test_execute_str_disp_pm(sub, new_rn):
        state = new_state(rf0=0xFFFFFFFF, rf5=8)
        # We can set the contents of a word in memory here:
        # state.mem.write(8, 4, 42) # Start address, number of bytes, value
        instr = opcode_factory.ldstrpmd32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=1)
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))
        expected_state = StateChecker(rf0=0xFFFFFFFF, rf5=new_rn)
        # Check the contents of the half-word starting at address 8:
        expected_state.check(state, memory=[(8, 4, 0xFFFFFFFF)])


The ``MockEpiphany`` class
^^^^^^^^^^^^^^^^^^^^^^^^^^

In the examples above, each unit test executed exactly one Epiphany instruction.
It is possible to execute a list of instructions, using the `epiphany.test.sim.MockEpiphany <https://github.com/futurecore/revelation/blob/master/epiphany/test/sim.py>`_ class.
This allows you to write a simple "program" using the opcode factory to construct each instruction, without having to compile an ELF file.

The following example tests that the ``bkpt16`` instruction correctly advances the program counter and halts the simulator:

.. code-block:: python

    from epiphany.machine import RESET_ADDR
    from epiphany.test.sim import MockEpiphany
    from epiphany.test.machine import StateChecker

    import opcode_factory

    def test_sim_nop16_bkpt16():
        instructions = [(opcode_factory.nop16(),  16),
                        (opcode_factory.bkpt16(), 16),
                        ]
        epiphany = MockEpiphany()
        epiphany.init_state(instructions)
        assert epiphany.state.running
        epiphany.run()
        expected_state = StateChecker(pc=(4 + RESET_ADDR))
        expected_state.check(epiphany.state)
        assert not epiphany.state.running


Integration tests that run ELF files
-------------------------------------

Tests that load and execute ELF files are structured differently to the unit tests above.
Instead of using the mocking framework that Revelation provides, integration tests need to load ELF files into memory and run the simulator as if it had been invoked on the command line.
Assertions can then use the `epiphany.test.machine.StateMachine <https://github.com/futurecore/revelation/blob/master/epiphany/test/machine.py>`_ class, or can use the `capsys <https://pytest.org/latest/capture.html>`_ fixture provided by `py.test <http://pytest.org/latest/>`_.

For example, this simple piece of C can be found in the file `epiphany/test/c/nothing.c <https://github.com/futurecore/revelation/blob/master/epiphany/test/c/nothing.c>`_:

.. code-block:: c

    int main() {
       return 0;
    }


The code is compiled with a `Makefile <https://github.com/futurecore/revelation/blob/master/epiphany/test/c/Makefile>`_ which can be found in the same directory as the C code.

Each ELF file which has been compiled from C code has a corresponding Python unit test which can be found in `epiphany/test/test_compiled_c.py <https://github.com/futurecore/revelation/blob/master/epiphany/test/test_compiled_c.py>`_.
These tests are normally parametrized, to avoid duplicate code.
For example:

.. code-block:: python

    import os.path
    import pytest

    elf_dir = os.path.join('epiphany', 'test', 'c')

    @pytest.mark.parametrize("elf_file,expected", [('nothing.elf',   176),
                                                   ...
                                                  ])
    def test_compiled_c(elf_file, expected, capsys):
        """Test an ELF file that has been compiled from a C function.
        This test checks that the correct number of instructions have been executed.
        """
        elf_filename = os.path.join(elf_dir, elf_file)
        epiphany = Epiphany()
        with open(elf_filename, 'rb') as elf:
            epiphany.init_state(elf, elf_filename, '', [], False, is_test=True)
            epiphany.max_insts = 10000
            epiphany.run()
            out, err = capsys.readouterr()
            expected_text = 'Instructions Executed = ' + str(expected)
            assert expected_text in out
            assert err == ''
            assert not epiphany.state.running


Similarly, the `epiphany/test/asm/ <https://github.com/futurecore/revelation/blob/master/epiphany/test/asm/>`_ directory contains an assembler file for each opcode in the Epiphany ISA.
Unit tests for the resulting ELF files can be found in `epiphany/test/test_asm.py <https://github.com/futurecore/revelation/blob/master/epiphany/test/test_asm.py>`_.


Compiling your own ELF files
----------------------------

In order to recompile the ELF files in the Revelation repository, or create new ELFs, you will need to install the `official Epiphany SDK <https://github.com/adapteva/epiphany-sdk>`_ provided by Adapteva.
If you do not wish to install the Adapteva toolchain on your own machine, we have provided a `Docker image <https://registry.hub.docker.com/u/snim2/parallella-devenv/>`_ which has the Epiphany toolchain pre-installed.


Compiling the simulator
-----------------------

To compile the simulator to a native executable, you need to first clone (or download) a recent version of the `PyPy toolchain <https://bitbucket.org/pypy/pypy>`_.
The ``rpython`` directory from PyPy needs to be included in your ``PYTHONPATH`` environment variable.

To compile *without* a JIT:

.. code-block:: bash

    $ PYTHONPATH=. .../pypy/rpython/bin/rpython -Ojit epiphany/sim.py


To compile the simulator *with* a JIT:

.. code-block:: bash

    $ PYTHONPATH=. ../../pypy/rpython/bin/rpython -Ojit epiphany/sim.py


.. toctree::
  :maxdepth: 2
  :hidden:
