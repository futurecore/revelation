Quickstart guide
================

Revelation can be run either as a Python program or as a native executable.
A compiled version of the simulator will include a just in time compiler, and will therefore simulate long running programs much faster.
However, the simulator is invoked in the same way, with the same command-line switches, whether you have compiled it or not.
See below for instructions on how to compile the code to an executable.

Simulating an Epiphany ELF file
-------------------------------

If you are running Revelation as a Python script, you need to have the `Pydgin module <https://github.com/cornell-brg/pydgin>`_ available on your ``PYTHONPATH``.
At present, Pydgin is not available on PyPI, so you have to do this by hand:

.. code-block:: bash

  $ cd $HOME
  $ wget https://github.com/cornell-brg/pydgin/archive/master.zip
  $ unzip master.zip
  $ mv pydgin-master/ pydgin
  $ export PYTHONPATH=${PYTHONPATH}:$HOME/pydgin/:.


You may want to add the last line to your ``~/.bashrc`` or similar.


The file `epiphany/sim.py <https://github.com/futurecore/revelation/blob/master/epiphany/sim.py>`_ is the entry point to the simulator:

.. code-block:: bash

    $ python epiphany/sim.py epiphany/test/c/nothing.elf
    NOTE: Using sparse storage
    sparse memory size 400 addr mask 3ff block mask fffffc00
    DONE! Status = 0
    Instructions Executed = 176


Full command line options to the simulator are as follows:

.. code-block:: bash

    $ python epiphany/sim.py --help

      Pydgin Epiphany Instruction Set Simulator
      usage: epiphany/sim.py <args> <sim_exe> <sim_args>

      <sim_exe>  the executable to be simulated
      <sim_args> arguments to be passed to the simulated executable
      <args>     the following optional arguments are supported:

        --help,-h       Show this message and exit
        --test          Run in testing mode (for running asm tests)
        --env,-e <NAME>=<VALUE>
                        Set an environment variable to be passed to the
                        simulated program. Can use multiple --env flags to set
                        multiple environment variables.
        --debug,-d <flags>[:<start_after>]
                        Enable debug flags in a comma-separated form (e.g.
                        "--debug syscalls,insts"). If provided, debugs starts
                        after <start_after> cycles. The following flags are
                        supported:
             insts              cycle-by-cycle instructions
             rf                 register file accesses
             mem                memory accesses
             regdump            register dump
             syscalls           syscall information
             bootstrap          initial stack and register state

        --max-insts <i> Run until the maximum number of instructions
        --jit <flags>   Set flags to tune the JIT (see
                        rpython.rlib.jit.PARAMETER_DOCS)


The ``--debug`` flags can be used to give a more detailed trace of a simulation:

.. code-block:: bash

    $ python epiphany/sim.py --debug insts,rf epiphany/test/c/nothing.elf
    NOTE: Using sparse storage
    sparse memory size 400 addr mask 3ff block mask fffffc00
         0 00002ce8 bcond32  0
        58 0002720b movimm32 1        :: WR.RF[3 ] = 00000090
        5c 1002600b movtimm32 2        :: RD.RF[3 ] = 00000090 :: WR.RF[3 ] = 00000090
        60 00000d52 jalr16   3        :: WR.RF[14] = 00000062 :: RD.RF[3 ] = 00000090
        90 27f2be0b movimm32 4        :: WR.RF[13] = 00007ff0
        94 3002a00b movtimm32 5        :: RD.RF[13] = 00007ff0 :: WR.RF[13] = 00007ff0
        98 2002600b movimm32 6        :: WR.RF[11] = 00000000
        9c 0022190b movimm32 7        :: WR.RF[0 ] = 000002c8
       ...
       8e0005c8 ffe80fe2 trap16   175      :: RD.RF[0 ] = 00000000 :: RD.RF[1 ] = 8e0005c8 :: RD.RF[2 ] = 00000000
        DONE! Status = 0
        Instructions Executed = 176


Compiling Revelation
--------------------

To compile Revelation to a native executable, you need to first clone (or download) a recent version of the `PyPy toolchain <https://bitbucket.org/pypy/pypy>`_.
The ``rpython`` directory from PyPy needs to be included in your ``PYTHONPATH`` environment variable.

To compile *without* a JIT:

.. code-block:: bash

    $ PYTHONPATH=. .../pypy/rpython/bin/rpython -Ojit epiphany/sim.py


To compile the simulator *with* a JIT:

.. code-block:: bash

    $ PYTHONPATH=. ../../pypy/rpython/bin/rpython -Ojit epiphany/sim.py


Support
-------

Revelation is currently under active development, it is not yet able to simulate full, multicore, Epiphany programs.
However, if you do try Revelation, please do report any bugs you find on the project `issue tracker <https://github.com/futurecore/revelation/issues>`_.


.. toctree::
  :maxdepth: 2
  :hidden:
