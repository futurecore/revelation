Quickstart guide
================

In order to use Revelation, you need to obtain a native binary build of the simulator.
Intel / GNU-Linux builds are available from the `revelation-bins repository <https://github.com/futurecore/revelation-bins>`_.
You should normally use the JITed version of the simulator, ``pydgin-revelation-jit`` or ``pydgin-revelation-jit-debug``.
The ``--debug`` options is enabled in the ``pydgin-revelation-jit-debug`` build.
For other platforms, you will need to translate Revelation yourself (instructions are below).

To run the simulator, pass it an Epiphany ELF file on the command line:

.. code-block:: bash

    $ ./pydgin-revelation-jit revelation/test/c/hello.elf
    Loading program revelation/test/c/hello.elf on to core 0x808 (32, 08)
    Hello, world!
    Total ticks simulated = 1,951.
    Core 0x808 (32, 08) STATUS: 0x00000005, Instructions executed: 1,951
    $

In the above example, an ELF file from the Revelation repository was simulated.
To compile your own binaries for the Epiphany platform, you will need the `Adapteva eSDK <https://github.com/adapteva/epiphany-sdk>`_.


Command line options
---------------------

By default, Revelation will be configured to simulate a single-core version of the Epiphany.
Like ``e-sim``, the default core has ID ``0x808`` and lies at row ``32`` and column ``8`` of of the memory map.
You can configure this at the command line:

.. code-block:: bash

    $ ./pydgin-revelation-jit -r 1 -c 2 -f 0x808 revelation/test/multicore/manual_message_pass.elf
    Loading program revelation/test/multicore/manual_message_pass.elf on to core 0x808 (32, 08)
    Loading program revelation/test/multicore/manual_message_pass.elf on to core 0x809 (32, 09)
    Received message.
    Total ticks simulated = 14,193.
    Core 0x808 (32, 08) STATUS: 0x00000005, Instructions executed: 7,894
    Core 0x809 (32, 09) STATUS: 0x00000055, Instructions executed: 6,299


The ``-f`` switch selects the first core, and must always be written in hex.

The full list of command-line options is:

.. code-block:: bash


    $ ./pydgin-revelation-jit --help
    Pydgin revelation Instruction Set Simulator
    Usage: ./pydgin-revelation-jit [OPTIONS] [ELFFILE]
    Simulate the execution of ELFFILE.

    The following OPTIONS are supported:
        --help, -h               Show this message and exit
        --rows, -r ROWS          Number of rows (default: 1)
        --cols, -c COLS          Number of columns (default: 1)
        --first-core, -f COREID  Coreid, in hex, of North West core (default: 0x808)
        --ext-base, -b COREID    Base address of external RAM (default: 0x8e000000)
        --ext-size, -s SIZE      Size of external RAM in MB (default: 32)
        --env, -e ENVIRONMENT    Either USER or OPERATING (ignored)
        --max-insts NUM          Halt after executing NUM instructions
        --switch N               Switch cores every N instructions (ignored)
        --time, -t               Print approximate timing information
        --jit FLAGS              Set flags to tune the JIT (see
                                     rpython.rlib.jit.PARAMETER_DOCS)
        --debug,-d FLAGS        Enable debug flags in a comma-separated form. The
                                following flags are supported:
                                     trace     pc, decoded instructions
                                     rf        register file accesses
                                     mem       memory accesses
                                     flags     update to CPU flags
                                     syscalls  system call information

    EXAMPLES:
        $ ./pydgin-revelation-jit -r 1 -c 2 -f 0x808 program.elf
        $ ./pydgin-revelation-jit -r 1 -c 2 --max-insts 20000 program.elf
        $ ./pydgin-revelation-jit --time program.elf
        $ ./pydgin-revelation-jit --debug trace,rf,mem,flags program.elf


Debugging an Epiphany program with Revelation
---------------------------------------------

You can learn more about how Revelation simulates your ELF file with the ``--debug`` options.
These options will write a trace of simulator operations to a file called ``r_trace.out`` in your current working directory.
You can optionally choose to trace instructions, register reads/writes, memory reads/writes, CPU flags and/or system calls.
For example:

.. code-block:: bash

    $ ./pydgin-revelation-jit-debug --debug trace,rf,mem,flags revelation/test/c/hello.elf
    Trace will be written to: r_trace.out.
    Loading program revelation/test/c/hello.elf on to core 0x808 (32, 08)
    Hello, world!
    Done! Total ticks simulated = 1951
    Core 0x808 (32, 08): STATUS=0x00000005, Instructions executed=1951

    $ cat r_trace.out

           0 000080e8 bcond32      0        AN=0 AZ=0 AC=0 AV=0 AVS=0 BN=0 BZ=0 BIS=0 BUS=0 BV=0 BVS=0
         100 0012660b movimm32     1        :: WR.RF[3 ] = 00000130
         104 1002600b movtimm32    2        :: RD.RF[3 ] = 00000130 :: WR.RF[3 ] = 00000130
         108 00000d52 jalr16       3        :: WR.RF[14] = 0000010a :: RD.RF[3 ] = 00000130
         130 27f2be0b movimm32     4        :: WR.RF[13] = 00007ff0
         134 3002a00b movtimm32    5        :: RD.RF[13] = 00007ff0 :: WR.RF[13] = 00007ff0
         138 2002e00b movimm32     6        :: WR.RF[15] = 00000000
         13c 00020b0b movimm32     7        :: WR.RF[0 ] = 00000058
         140 1002000b movtimm32    8        :: RD.RF[0 ] = 00000058 :: WR.RF[0 ] = 00000058
         144 202b0044 ldstrdisp16  9        :: RD.RF[0 ] = 00000058 :: WR.RF[0 ] = 00000000
         146 0002202b movimm32     10       :: WR.RF[1 ] = 00000001
         14a 1002200b movtimm32    11       :: RD.RF[1 ] = 00000001 :: WR.RF[1 ] = 00000001
         14e 111000da and16        12       :: RD.RF[1 ] = 00000001 :: RD.RF[0 ] = 00000000 :: WR.RF[0 ] = 00000000 AN=0 AZ=1 AC=0 AV=0 AVS=0 BN=0 BZ=0 BIS=0 BUS=0 BV=0 BVS=0
         150 1d0b1110 bcond16      13       AN=0 AZ=1 AC=0 AV=0 AVS=0 BN=0 BZ=0 BIS=0 BUS=0 BV=0 BVS=0
         ...


The left-most column represents the program counter, the next column shows the opcode being simulated, next is the Revelation name for the opcode, then how many instructions have been executed so far.
On the right you can see register, memory and flag reads and writes.
The Revelation name for each instruction will not look exactly like the equivalent assembler code (e.g. ``bcond32`` could be a ``blt`` or ``beq``).
Each instruction name will end in ``32`` or ``16``, depending on whether the compiler has produced a 32-bit or 16-bit version of the instruction.

If you are simulating a multi-core program, then **only** the first (south-west) core is traced.


Translating Revelation
----------------------

Revelation is written in RPython, a statically typed version of Python.
"Translating" is the process of converting RPython code here into C, and compiling that to a native executable.
To translate the simulator, you need to first clone (or download) a recent version of the `PyPy toolchain <https://bitbucket.org/pypy/pypy>`_.
The ``rpython`` directory from PyPy needs to be included in your ``PYTHONPATH`` environment variable.
You will also need a copy of `the Pydgin framework <https://github.com/cornell-brg/pydgin>`_, which should also be on your ``PYTHONPATH``.
If you are in any doubt about this, the Revelation `Travis configuration <https://github.com/futurecore/revelation/blob/master/.travis.yml>`_ contains a script which translates the simulator.

You can translate versions of Revelation with and without the just-in-time component of the simulator.
The JITed version of the simulator will be faster, especially for long-running programs.

To translate *without* a JIT:

.. code-block:: bash

    $ PATH_TO_PYPY/rpython/bin/rpython -O2 revelation/sim.py


To translate the simulator *with* a JIT:

.. code-block:: bash

    $ PATH_TO_PYPY/rpython/bin/rpython -Ojit revelation/sim.py


To translate the simulator *with* a JIT and debug support, so that you can use the ``--debug`` command-line option:

.. code-block:: bash

    $ PATH_TO_PYPY/rpython/bin/rpython -Ojit revelation/sim.py --debug

To translate with RPython debug support (e.g. to run the simulator through GDB whilst debugging):

.. code-block:: bash

    $ PATH_TO_PYPY/rpython/bin/rpython -Ojit --lldebug revelation/sim.py --debug


.. toctree::
  :maxdepth: 2
  :hidden:
