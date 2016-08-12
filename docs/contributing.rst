Contributing to Revelation
==========================

Contributions to Revelation are welcome, particularly bug reports.
The project source code is available `on GitHub <https://github.com/futurecore/revelation/>`_ and bugs can be reported via the `issue tracker <https://github.com/futurecore/revelation/issues>`_.
If you wish to contribute code, or improvements in this documentation, please fork the project on `on GitHub <https://github.com/futurecore/revelation/>`_ and issue a pull request.
Your pull request will be automatically checked by the `travis continuous integration <https://travis-ci.org/futurecore/revelation>`_ tool before it is merged.

To understand how the Revelation source code is structured, it is a good idea to start by reading about the `Pydgin <https://github.com/cornell-brg/pydgin>`_ framework.

.. seealso:: Derek Lockhart and Berkin Ilbeyi (2015) `Pydgin: Using RPython to Generate Fast Instruction-Set Simulators <https://morepypy.blogspot.co.uk/2015/03/pydgin-using-rpython-to-generate-fast.html>`_ Guest post on the PyPy status blog.

Any changes to the source code should normally be accompanied by unit tests, and should certainly not reduce the current code coverage below 100%.


Running Revelation un-translated
---------------------------------

When working with the Revelation source code, it is easiest to run and test the simulator un-translated, until your changes are stable.
Translating Revelation is relatively slow, however it is easy (albeit slower) to run the simulator without translating it, e.g.:

.. code-block:: bash

    $ pypy revelation/sim.py revelation/test/c/hello.elf  # Use pypy or python2 here
    Loading program revelation/test/c/hello.elf on to core 0x808 (32, 08)
    Hello, world!
    Done! Total ticks simulated = 1951
    Core 0x808 (32, 08): STATUS=0x00000005, Instructions executed=1951

To work with the code here you need a copy of Pydgin, which you can obtain a copy from the `Pydgin project page <https://github.com/cornell-brg/pydgin>`_.
Pydgin is a framework for writing functional simulators as `just in time interpreters <https://en.wikipedia.org/wiki/Just-in-time_compilation>`_.


Structure of the code
---------------------

To understand the Revelation source code, it is helpful to read about Pydgin, and have a copy of the `Epiphany Architecture Reference Manual <http://adapteva.com/docs/epiphany_arch_ref.pdf>`_ to hand.
However, there are a number of mistakes in that document, many of which are `listed on the Parallella discussion forum <https://parallella.org/forums/viewtopic.php?f=8&t=43>`_.
This `set of notes <http://blog.alexrp.com/epiphany-notes/>`_ from Alex Rønne Petersen is also extremely helpful, as is the `Epiphany GDB code <https://github.com/adapteva/epiphany-gdb>`_.

Revelation is structured as follows:

- `revelation/argument_parser.py <https://github.com/futurecore/revelation/blob/master/revelation/argument_parser.py>`_ simple argument parser (RPtyhon projects do not use `argparse` or similar).
- `revelation/condition_codes.py <https://github.com/futurecore/revelation/blob/master/revelation/condition_codes.py>`_ condition codes for branch instructions.
- `revelation/elf_loader.py <https://github.com/futurecore/revelation/blob/master/revelation/elf_loader.py>`_ function to load an ELF file onto an individual Epiphany core.
- `revelation/execute_bitwise.py <https://github.com/futurecore/revelation/blob/master/revelation/execute_bitwise.py>`_ semantics of bitwise instructions.
- `revelation/execute_branch.py <https://github.com/futurecore/revelation/blob/master/revelation/execute_branch.py>`_ semantics of branch instructions.
- `revelation/execute_farith.py <https://github.com/futurecore/revelation/blob/master/revelation/execute_farith.py>`_ FPU model.
- `revelation/execute_interrupt.py <https://github.com/futurecore/revelation/blob/master/revelation/execute_interrupt.py>`_ semantics of instructions relating to interrupts (``rti``, ``trap``, etc.).
- `revelation/execute_jump.py <https://github.com/futurecore/revelation/blob/master/revelation/execute_jump.py>`_ semantics of ``jr`` and ``jalr`` instructions.
- `revelation/execute_load_store.py <https://github.com/futurecore/revelation/blob/master/revelation/execute_load_store.py>`_ semantics of load and store instructions.
- `revelation/execute_mov.py <https://github.com/futurecore/revelation/blob/master/revelation/execute_mov.py>`_ semantics of move instructions.
- `revelation/instruction.py <https://github.com/futurecore/revelation/blob/master/revelation/instruction.py>`_ simple model of an instruction, with methods to retrieve operands.
- `revelation/isa.py <https://github.com/futurecore/revelation/blob/master/revelation/isa.py>`_ instruction encodings.
- `revelation/logger.py <https://github.com/futurecore/revelation/blob/master/revelation/logger.py>`_ an object for logging ``--debug`` strings to ``r_trace.out``.
- `revelation/machine.py <https://github.com/futurecore/revelation/blob/master/revelation/machine.py>`_ model of a single Epiphany core, including flags.
- `revelation/registers.py <https://github.com/futurecore/revelation/blob/master/revelation/registers.py>`_ dictionaries and functions for finding named registers and their sizes.
- `revelation/sim.py <https://github.com/futurecore/revelation/blob/master/revelation/sim.py>`_ entry point to simulator.
- `revelation/storage.py <https://github.com/futurecore/revelation/blob/master/revelation/storage.py>`_ RAM model.
- `revelation/utils.py <https://github.com/futurecore/revelation/blob/master/revelation/utils.py>`_ bit manipulation utilities.


Running the unit tests
----------------------

Revelation comes with a large number of unit tests, which are intended to be run with the `py.test <http://docs.pytest.org/en/latest/>`_ framework.
To run the provided tests, first ensure that the required packages are installed:

.. code-block:: bash

    $ pip install -r requirements.txt

Then run the tests themselves:

.. code-block:: bash

    $ py.test --cov-report term-missing --cov revelation revelation/test/

Note that the tests may take some time to run, particularly those that load an ELF file.


Structure of the unit tests
---------------------------

All unit tests can be found in the `revelation.test <https://github.com/futurecore/revelation/tree/master/revelation/test>`_ package.
Most tests are written in pure Python and test the internals of the simulator code.
Revelation provides a number of convenience modules which are intended to make it easier to quickly construct unit tests and reduce duplicate code.
It is recommended that anyone adding new tests make uses of these modules, which are described below.


The ``opcode_factory`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Epiphany instructions are 32bit or 16bit binary numbers.
Writing these by hand is error prone and tedious, and loading an ELF file is not always appropriate for small unit tests.
The `revelation.test.opcode_factory <https://github.com/futurecore/revelation/blob/master/revelation/test/opcode_factory.py>`_ module provides a function to create every instruction in the Epiphany ISA.
Where there are 32bit and 16bit variants of the same instruction, both versions are available.
For example, the following code creates 32 and 16bit versions of the *logical shift left* instruction:

.. code-block:: python

    >>> import revelation.test.opcode_factory as opcode_factory
    >>> bin(opcode_factory.lsl32(rd=43, rn=42, rm=41))
    '0b10110110100010100110100010101111'
    >>> bin(opcode_factory.lsl16(rd=3, rn=2, rm=1))
    '0b110100010101010'
    >>>

Note that operands to the instruction are passed to the factory function as keyword arguments.
These are named exactly as they are described in the opcode decode table on page 155 of the `Epiphany Architecture Reference Manual <http://adapteva.com/docs/epiphany_arch_ref.pdf>`_.
In the example above, the LSL instruction takes three operands:

  - **rd** a destination register
  - **rn** an operand register
  - **rm** an operand register


The ``new_state`` function
^^^^^^^^^^^^^^^^^^^^^^^^^^

Unit tests for Revelation usually check whether the simulator halts with the expected state (i.e. flags, registers and RAM).
It is often useful to be able to start the simulator in a particular state.
Rather than setting each register or flag individually, Revelation provides the `epiphany.test.machine.new_state <https://github.com/futurecore/revelation/blob/master/revelation/test/machine.py>`_ function which can accept register and flag values as named parameters.

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
The `epiphany.test.machine <https://github.com/futurecore/revelation/blob/master/revelation/test/machine.py>`_ module provides a class called ``StateChecker`` which manages this.
A new ``StateChecker`` takes register and flag values as parameters to its constructor, in exactly the same way as the ``new_state`` function described above.
The ``StateChecker.check`` method takes a state as a parameter, then automatically runs assertions to check that each register or flag of interest is as expected.

For example:

.. code-block:: python

    from revelation.instruction import Instruction
    from revelation.isa import decode
    from revelation.machine import RESET_ADDR
    from revelation.test.machine import StateChecker, new_state

    import revelation.test.opcode_factory as opcode_factory
    import pytest

    @pytest.mark.parametrize('is16bit,val', [(True, 0b111), (False, 0b1111)])
    def test_execute_movcond(is16bit, val):
        state = new_state(AZ=1, rf1=val)
        instr = (opcode_factory.movcond16(condition=0b0000, rd=0, rn=1) if is16bit
                 else opcode_factory.movcond32(condition=0b0000, rd=0, rn=1))
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))
        pc_expected = (2 if is16bit else 4) + RESET_ADDR
        expected_state = StateChecker(pc=pc_expected, rf0=val)
        expected_state.check(state)


Note that like most unit tests in Revelation, the example above uses `pytest.mark.parametrize <http://docs.pytest.org/en/latest/parametrize.html>`_ to avoid duplicating code.


Checking the contents of RAM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the examples above, unit tests have checked the contents of registers and flags.
It is also possible to check that a word in RAM has the correct contents, by passing a list of expected memory locations to the ``StateChecker.check`` method.

For example:

.. code-block:: python

    @pytest.mark.parametrize('sub,new_rn', [(1, 8 - 4),
                                            (0, 8 + 4),
                                            (1, 8 - 4),
                                            (0, 8 + 4)])
    def test_execute_str_disp_pm(sub, new_rn):
        # Store.
        state = new_state(rf0=0xffffffff, rf5=8)
        # bb: 00=byte, 01=half-word, 10=word, 11=double-word
        instr = opcode_factory.ldstrpmd32(rd=0, rn=5, sub=sub, imm=1, bb=0b10, s=1)
        name, executefn = decode(instr)
        executefn(state, Instruction(instr, None))
        expected_state = StateChecker(rf0=0xffffffff, rf5=new_rn)
        expected_state.check(state, memory=[(8, 4, 0xffffffff)])


The ``MockEpiphany`` class
^^^^^^^^^^^^^^^^^^^^^^^^^^

In the examples above, each unit test executed exactly one Epiphany instruction.
It is possible to execute a list of instructions, using the `epiphany.test.sim.MockEpiphany <https://github.com/futurecore/revelation/blob/master/revelation/test/sim.py>`_ class.
This allows you to write a simple "program" using the opcode factory to construct each instruction, without having to compile an ELF file.

The following example tests that the ``trap16(3)`` instruction correctly halts the simulator:

.. code-block:: python

    from revelation.machine import RESET_ADDR
    from revelation.test.sim import MockRevelation
    from revelation.test.machine import StateChecker
    from revelation.test.opcode_factory as opcode_factory

    def test_sim_trap16_3():
        instructions = [(opcode_factory.trap16(3), 16)]
        revelation = MockRevelation()
        revelation.init_state(instructions)
        assert revelation.states[0].running
        exit_code, ticks = revelation.run()
        expected_state = StateChecker(pc=(2 + RESET_ADDR))
        expected_state.check(revelation.states[0])
        assert EXIT_SUCCESS == exit_code
        assert len(instructions) == ticks
        assert not revelation.states[0].running


Integration tests that run ELF files
-------------------------------------

Many tests use compiled ELF files, which should be compiled with the `2016.3.1 version of the eSDK <https://github.com/adapteva/epiphany-sdk>`_ and checked into the repository.
Makefiles are provided in all relevant directories.

You can find compiled ELF files, and the source that generated them, in the following directories:

- ``revelation/test/asm`` Assembler files compiled to Epiphany ELF format (intended to run on a single-core).
- ``revelation/test/c`` C files compiled to Epiphany ELF format (intended to run on a single-core).
- ``revelation/test/multicore`` C files compiled to Epiphany ELF format (intended to run on more than one core).
- ``revelation/test/syscall-layout`` C files compiled to Epiphany ELF format.
- ``revelation/test/zigzag`` C files compiled to Epiphany ELF format (intended to run on more than one core).

The `asm` directory contains at least one assembler file for each Epiphany instruction, most test cases are taken from the `Epiphany Architecture Reference Manual <http://adapteva.com/docs/epiphany_arch_ref.pdf>`_.
The `c` and `multicore` directories contain more complex test cases (e.g. testing interrupts and system calls).

The ``syscall-layout`` and ``zigzag`` directories are different to the others.
``syscall-layout`` tests write out the format of ``stat`` and ``fstat`` objects, this is intended to help debugging Revelation syscalls on a new platform.
``zigzag`` contains a complex multicore test case written by Ola Jeppsson, you can find the original in the `esim-test-bins <https://github.com/olajep/esim-test-bins>`_ repository.

Where test cases are written by other authors, they should contain all relevant copyright notices and attributions.

Tests that load and execute ELF files are structured differently to the pure-Python unit tests.
Instead of using the mocking framework that Revelation provides, integration tests need to load ELF files into memory and run the simulator as if it had been invoked on the command line.
Assertions can then use the `revelation.test.machine.StateMachine <https://github.com/futurecore/revelation/blob/master/revelation/test/machine.py>`_ class, or can use the `capsys <http://docs.pytest.org/en/latest//capture.html>`_ fixture provided by `py.test <http://docs.pytest.org/en/latest/>`_.

For example, this simple piece of C can be found in the file `epiphany/test/c/hello.c <https://github.com/futurecore/revelation/blob/master/revelation/test/c/hello.c>`_:

.. code-block:: c

    #include <stdlib.h>
    #include <stdio.h>
    int main() {
        printf("Hello, world!\n");
    }


The code is compiled with a `Makefile <https://github.com/futurecore/revelation/blob/master/revelation/test/c/Makefile>`_ which can be found in the same directory as the C code.

Each ELF file which is in the ``revelation/test/c/`` directory has a corresponding Python unit test which can be found in `revelation/test/test_compiled_c.py <https://github.com/futurecore/revelation/blob/master/revelation/test/test_compiled_c.py>`_.
These tests are normally parametrized, to avoid duplicate code.
For example:

.. code-block:: python

    from revelation.sim import EXIT_SUCCESS, Revelation
    from revelation.test.machine import StateChecker

    import os.path
    import pytest

    elf_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                           'revelation', 'test', 'c')


    @pytest.mark.parametrize('elf_file,expected',
        [('hello.elf',              'Hello, world!\n'),
         ...
        ])
    def test_compiled_c_with_output(elf_file, expected, capfd):
        """Test an ELF file that has been compiled from a C function.
        This test checks text printed to STDOUT.
        """
        elf_filename = os.path.join(elf_dir, elf_file)
        revelation = Revelation()
        with open(elf_filename, 'rb') as elf:
            revelation.init_state(elf, elf_filename, False, is_test=True)
            revelation.max_insts = 100000
            revelation.run()
            assert not revelation.states[0].running
            out, err = capfd.readouterr()
            assert err == ''
            expected_full = (('Loading program %s on to core 0x808 (32, 08)\n' % elf_filename)
                              + expected)
            assert out.startswith(expected_full)


Similarly, the `epiphany/test/asm/ <https://github.com/futurecore/revelation/tree/master/revelation/test/asm/>`_ directory contains an assembler file for each opcode in the Epiphany ISA.
Unit tests for the resulting ELF files can be found in `epiphany/test/test_asm.py <https://github.com/futurecore/revelation/tree/master/revelation/test/asm>`_.


Compiling your own ELF files
----------------------------

In order to recompile the ELF files in the Revelation repository, or create new ELFs, you will need to install version 2016.3.1 of the `official Epiphany SDK <https://github.com/adapteva/epiphany-sdk>`_ provided by Adapteva.


.. toctree::
  :maxdepth: 2
  :hidden:
